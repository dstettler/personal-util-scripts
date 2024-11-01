package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"

	pathsync "pathsync/pkg"

	"github.com/alecthomas/kong"
	"google.golang.org/protobuf/proto"
)

var CLI struct {
	Cachefile string `arg:"" help:"Path of cachefile to upgrade"`
	Verbosity int    `type:"counter" short:"v" optional:"" help:"Verbosity counter" default:"0"`
}

func convertJsonToVersion2(fileBytes []byte) []byte {
	jsonContent := make(map[string][]string)
	newPairs := make(map[string]*pathsync.Cache2_Pairs)

	if err := json.Unmarshal(fileBytes, &jsonContent); err != nil {
		panic(err)
	}

	for k, v := range jsonContent {
		var modified int64
		if intermediaryFloat, parseErr := strconv.ParseFloat(v[1], 64); parseErr == nil {
			modified = int64(intermediaryFloat)
		} else {
			panic(parseErr)
		}
		if CLI.Verbosity >= 2 {
			fmt.Println("Got file:", k, v[0], modified)
		}

		newPairs[k] = &pathsync.Cache2_Pairs{Hash: v[0], Modified: modified}
	}

	outMessage := pathsync.Cache2{Version: 2, Cache: newPairs}
	if out, err := proto.Marshal(&outMessage); err == nil {
		return out
	}

	return nil
}

func main() {
	kong.Parse(&CLI, kong.Description("Upgrades specified cachefile to the newest available version"))

	file, err := os.ReadFile(CLI.Cachefile)
	if err != nil {
		panic(err)
	}

	// If the file is the original JSON format
	if file[0] == '{' {
		newBytes := convertJsonToVersion2(file)

		newfile := fmt.Sprintf("%s%s", CLI.Cachefile, ".1")

		if CLI.Verbosity >= 1 {
			fmt.Println("Renaming", CLI.Cachefile, "to", newfile)
		}

		os.Rename(CLI.Cachefile, newfile)

		if CLI.Verbosity >= 1 {
			fmt.Println("Writing to ", CLI.Cachefile)
		}

		os.WriteFile(CLI.Cachefile, newBytes, 0644)
	}
}
