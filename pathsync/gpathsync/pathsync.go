package main

import (
	"errors"
	"fmt"
	"os"

	"github.com/alecthomas/kong"
	"gopkg.in/yaml.v3"
)

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

func sync(pair *TargetInfo, ignores []string) {

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
