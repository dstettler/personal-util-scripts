#!/usr/bin/env python3
import argparse
import os
import shutil
import signal
import time
import sys
import csv

parser = argparse.ArgumentParser(
    prog="av1-convert.py", description="Converts all files in a subdirectory "
)

parser.add_argument(
    "inDir",
    metavar="inDir",
    type=str,
    help="Directory to recursively scan for conversions",
    nargs="?",
    default=".",
)
parser.add_argument(
    "outDir",
    metavar="outDir",
    type=str,
    help="Location of transcoded files",
    nargs="?",
    default="av1-out",
)

parser.add_argument(
    "-p",
    "--progress-file",
    type=str,
    help="File to save/restore progress",
    required=False
)


read_files: list[str] = []
progress_file = None


def exit_signal(sig, frame):
    if progress_file is not None:
        print(f"Writing to {progress_file}")
        start = time.time()
        with open(progress_file, 'w', encoding='utf-8') as f:
            for file in read_files:
                f.write(file + ",")
        end = time.time()
        print(f"Done writing {progress_file}, took {end - start}s, {len(read_files)} files")
    sys.exit(0)


if __name__ == "__main__":
    args = parser.parse_args()

    in_dir = args.inDir.rstrip("/")
    out_dir = args.outDir.rstrip("/")
    progress_file = args.progress_file

    signal.signal(signal.SIGINT, exit_signal)

    if os.path.isfile(progress_file):
        print(f"Reading from {progress_file}")
        start = time.time()
        with open(progress_file, 'r', encoding='utf-8') as f:
            lines = f.read()
            read_files = lines.split(',')
        end = time.time()
        print(f"Done Reading {progress_file}, took {end - start}s, {len(read_files)} files")

    print(f"Done reading {progress_file}")

    


