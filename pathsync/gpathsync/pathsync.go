package main

import (
	"bytes"
	"crypto/md5"
	"encoding/gob"
	"encoding/hex"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"

	"./pathsync/cache"

	"github.com/alecthomas/kong"
	"gopkg.in/yaml.v3"
)

type CachePairs struct {
	Hash     string
	Modified int64
}

type TargetInfo struct {
	Source      string `yaml:"src"`
	Target      string `yaml:"target"`
	TargetCache string `yaml:"cache,omitempty"`
}

type Syncfile struct {
	Targets []TargetInfo `yaml:"pairs,flow"`
	Ignores []string     `yaml:"omitempty"`
}

var CLI struct {
	Syncfile  string `arg:"" help:"Path of syncfile with all src:target pairs and corresponding cached hash locations"`
	Silent    bool   `short:"s" optional:"" help:"Silent mode"`
	Delete    bool   `short:"d" optional:"" help:"Delete files from target"`
	Rescan    bool   `short:"r" optional:"" help:"Rescan full src directory"`
	Verbosity int    `type:"counter" short:"v" optional:"" help:"Verbosity counter" default:"0"`
}

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

func sync(pair *TargetInfo, ignores []string) {
	caches := make(map[string]CachePairs)

	walkErr := filepath.WalkDir(pair.Source, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if !d.IsDir() {
			filepathWithoutBase := path[len(pair.Source):]
			newPath := filepath.Join(pair.Target, filepathWithoutBase)

			if info, statErr := os.Stat(path); statErr == nil {
				if hash, hashErr := md5Hash(path); hashErr == nil {
					cachePair := CachePairs{Hash: hash, Modified: info.ModTime().Unix()}
					caches[path] = cachePair
				}
			}

			fmt.Println("Copying ", path, " -> ", newPath)
		} else {
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
	})
	if walkErr != nil {
		fmt.Println("ERROR: Error ocurred syncing ", pair.Source, ": ", walkErr)
	}

	message := &cache cache.Cache{
		version: 2,
		cache:   caches,
	}



	gobBuf := new(bytes.Buffer)
	encoder := gob.NewEncoder(gobBuf)

	if err := encoder.Encode(caches); err == nil {
		cachefile := pair.TargetCache
		if cachefile == "" {
			cachefile = filepath.Join(pair.Target, "cache")
		}
		os.WriteFile(cachefile, gobBuf.Bytes(), 0644)
	} else {
		fmt.Println("ERROR: Error encoding gob- ", err)
	}
}

func validateSyncLocations(file *Syncfile) bool {
	return true
}

func main() {
	kong.Parse(&CLI, kong.Description("Simplistic file syncing utility"))

	if info, err := os.Stat(CLI.Syncfile); errors.Is(err, os.ErrNotExist) || info.IsDir() {
		panic("ERROR: Syncfile either does not exist or is directory")
	}

	var syncfile Syncfile
	if b, err := os.ReadFile(CLI.Syncfile); err == nil {
		if err := yaml.Unmarshal(b, &syncfile); err != nil {
			if CLI.Verbosity > 0 {
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
			fmt.Println("Syncing ", pair.Source, " -> ", pair.Target)
		}

		sync(&pair, syncfile.Ignores)
	}
}
