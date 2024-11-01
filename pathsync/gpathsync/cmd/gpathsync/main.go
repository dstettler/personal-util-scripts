package main

import (
	"bufio"
	"crypto/md5"
	"encoding/hex"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	pathsync "pathsync/pkg"
	"regexp"
	"strings"

	"github.com/alecthomas/kong"
	"google.golang.org/protobuf/proto"
	"gopkg.in/yaml.v3"
)

// Keep a version of the protobuf saved in case any future edits need to be made.
const CachefileVersion int32 = 2

type TargetInfo struct {
	Source      string `yaml:"src"`
	Target      string `yaml:"target"`
	TargetCache string `yaml:"cache,omitempty"`
}

type Syncfile struct {
	Targets []TargetInfo `yaml:"pairs,flow"`
	Ignores []string     `yaml:"ignore,omitempty"`
}

var CLI struct {
	Syncfile  string `arg:"" help:"Path of syncfile with all src:target pairs and corresponding cached hash locations"`
	Silent    bool   `short:"s" optional:"" help:"Silent mode"`
	Delete    bool   `short:"d" optional:"" help:"Delete files from target"`
	Rescan    bool   `short:"r" optional:"" help:"Rescan full src directory"`
	Verbosity int    `type:"counter" short:"v" optional:"" help:"Verbosity counter" default:"0"`
}

// Returns tuple of MD5 hash of file at path and nil, or an empty string and an error.
func md5Hash(path string) (string, error) {
	hasher := md5.New()
	if b, err := os.ReadFile(path); err == nil {
		if _, hashErr := hasher.Write(b); hashErr != nil {
			return "", hashErr
		}
	} else {
		return "", err
	}

	return hex.EncodeToString(hasher.Sum(nil)), nil
}

// Copies file using readers/writers.
func copyFile(src, dest string) error {
	srcFi, srcFiErr := os.Open(src)
	if srcFiErr != nil {
		return srcFiErr
	}

	destFi, destFiErr := os.Create(dest)
	if destFiErr != nil {
		return destFiErr
	}

	writer := bufio.NewWriter(destFi)
	reader := bufio.NewReader(srcFi)

	if _, err := reader.WriteTo(writer); err != nil {
		srcFi.Close()
		destFi.Close()

		return err
	}

	srcFi.Close()
	destFi.Close()

	return nil
}

func syncFileOrDir(
	path string,
	isDir bool,
	pair *TargetInfo,
	ignores []string,
	inMessage *pathsync.Cache2,
	newCaches map[string]*pathsync.Cache2_Pairs,
	err error) error {
	if err != nil {
		return err
	}

	if !isDir {
		filepathWithoutBase := path[len(pair.Source):]
		newPath := filepath.Join(pair.Target, filepathWithoutBase)

		// Ensure all platforms use forward slashes for paths.
		filepathWithoutBase = strings.Replace(filepathWithoutBase, "\\", "/", -1)

		// Skip this file if it matches any regex provided in the ignores list.
		for _, ignoreString := range ignores {
			match, _ := regexp.MatchString(ignoreString, filepathWithoutBase)

			if match {
				if CLI.Verbosity >= 3 {
					fmt.Println("Regex matched:", ignoreString, ". Skipping", filepathWithoutBase)
				}

				return nil
			}
		}

		if info, statErr := os.Stat(path); statErr == nil {
			// Check if file is in cache, and if so, if the cached modified time is equal to the found modified time.
			// If they are equivalent then skip re-hashing file.
			if val, valPresent := inMessage.Cache[filepathWithoutBase]; valPresent && val.Modified == info.ModTime().Unix() {
				if CLI.Verbosity >= 3 {
					fmt.Println("ModTimes match. skipping", filepathWithoutBase)
				}

				newCaches[filepathWithoutBase] = inMessage.Cache[filepathWithoutBase]
			} else if hash, hashErr := md5Hash(path); hashErr == nil {
				cachePair := pathsync.Cache2_Pairs{Hash: hash, Modified: info.ModTime().Unix()}
				newCaches[filepathWithoutBase] = &cachePair

				if !valPresent || val.Hash != hash {
					// Since the new hash is different, we know the file needs to be (re-)copied
					if CLI.Verbosity >= 1 {
						fmt.Println("Copying", path, " -> ", newPath)
					}
					if err := copyFile(path, newPath); err != nil {
						return err
					}
				} else if CLI.Verbosity >= 3 {
					fmt.Println("Timestamps differ but hashes are identical. Skipping", filepathWithoutBase)
				}
			}
		} else {
			return statErr
		}
	} else {
		// Since dirs will always be read before their children, ensure the dir is created on the target before attempting to
		// write children to nonexistent paths.
		dirWithoutBase := path[len(pair.Source):]
		newDir := filepath.Join(pair.Target, dirWithoutBase)
		if _, err := os.Stat(newDir); errors.Is(err, fs.ErrNotExist) {
			if mkErr := os.MkdirAll(newDir, os.ModePerm); mkErr != nil {
				return mkErr
			}
		} else {
			return err
		}
	}

	return nil
}

// Syncs all files in the source directory specified in the given pair.
func sync(pair *TargetInfo, ignores []string) {
	newCaches := make(map[string]*pathsync.Cache2_Pairs)
	cachefileName := pair.TargetCache
	if cachefileName == "" {
		cachefileName = filepath.Join(pair.Target, "cache")
	}
	var inMessage pathsync.Cache2

	// Read existing cache file to protobuf message
	if fBytes, err := os.ReadFile(cachefileName); err == nil {
		proto.Unmarshal(fBytes, &inMessage)
	} else if _, err := os.Stat(cachefileName); !errors.Is(err, os.ErrNotExist) {
		// Cachefile does not exist, so create an empty message to compare against
		inMessage.Version = CachefileVersion
		inMessage.Cache = make(map[string]*pathsync.Cache2_Pairs)
	}

	// Verify cachefile version.
	// TODO: Perform these updates automatically when encountered.
	if inMessage.Version < CachefileVersion {
		if CLI.Verbosity >= 1 {
			fmt.Println(
				"ERROR: Cachefile:",
				cachefileName,
				"is of invalid previous version",
				inMessage.Version,
				", upgrade all caches to version",
				CachefileVersion,
				"with the utility")
		}

		return
	}

	if CLI.Rescan {
		// Recursively discover each file in src
		walkErr := filepath.WalkDir(pair.Source, func(path string, d fs.DirEntry, err error) error {
			return syncFileOrDir(path, d.IsDir(), pair, ignores, &inMessage, newCaches, err)
		})
		if walkErr != nil && CLI.Verbosity >= 1 {
			fmt.Println("ERROR: Error ocurred syncing", pair.Source, ":", walkErr)
		}
	} else {
		// Only check files in existing cache
		for path := range inMessage.Cache {
			syncFileOrDir(filepath.Join(pair.Source, path), false, pair, ignores, &inMessage, newCaches, nil)
		}
	}

	// Check existing cache for orphaned entries, and optionally delete them if the flag is set.
	for k := range inMessage.Cache {
		if _, found := newCaches[k]; !found && CLI.Delete {
			if CLI.Verbosity >= 2 {
				fmt.Println(k, "does not exist, deleting file and removing from cache")
			}

			// Join paths and normalize slash direction
			orphanedTargetPath := filepath.Join(pair.Target, k)
			orphanedTargetPath = strings.Replace(orphanedTargetPath, "\\", "/", -1)
			os.Remove(orphanedTargetPath)

			// Remove directory if it is now empty
			orphanedDirTargetDir := filepath.Dir(orphanedTargetPath)
			filesInDir, _ := os.ReadDir(orphanedDirTargetDir)
			if len(filesInDir) == 0 {
				if CLI.Verbosity >= 2 {
					fmt.Println("Removing empty dir:", orphanedDirTargetDir)
				}

				os.Remove(orphanedDirTargetDir)
			}
		}
	}

	outMessage := pathsync.Cache2{Version: CachefileVersion, Cache: newCaches}
	if out, err := proto.Marshal(&outMessage); err == nil {
		os.WriteFile(cachefileName, out, 0644)
	} else if CLI.Verbosity >= 2 {
		fmt.Println("ERROR: Error encoding protobuf-", err)
	}
}

func validateSyncLocations(file *Syncfile) bool {
	allValid := true
	for _, target := range file.Targets {
		if _, err := os.Stat(target.Source); errors.Is(err, os.ErrNotExist) {
			if CLI.Verbosity >= 2 {
				fmt.Println("ERROR: Specified source", target.Source, "does not exist")
			}

			allValid = allValid && false
		}
	}

	return allValid
}

func main() {
	kong.Parse(&CLI, kong.Description("Simplistic file syncing utility"))

	if CLI.Silent {
		CLI.Verbosity = -1
	}

	if info, err := os.Stat(CLI.Syncfile); errors.Is(err, os.ErrNotExist) || info.IsDir() {
		panic("ERROR: Syncfile either does not exist or is directory")
	}

	var syncfile Syncfile
	if b, err := os.ReadFile(CLI.Syncfile); err == nil {
		if err := yaml.Unmarshal(b, &syncfile); err != nil {
			if CLI.Verbosity > 2 {
				fmt.Println(err)
			}
			panic("ERROR: Error unmarshalling syncfile")
		}
	}

	if !validateSyncLocations(&syncfile) {
		panic("ERROR: Error validating locations. Read verbose logs for more info")
	}

	for _, pair := range syncfile.Targets {
		if CLI.Verbosity >= 0 {
			fmt.Println("Syncing", pair.Source, " -> ", pair.Target)
		}

		sync(&pair, syncfile.Ignores)
	}
}
