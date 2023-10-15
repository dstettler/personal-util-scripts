#!/usr/bin/env python3
import argparse
import os
import subprocess
import time


parser = argparse.ArgumentParser(
    prog="batch-dl.py",
    description="Downloads list of files using youtube-dl [REQUIRES youtube-dl TO BE INSTALLED AND ON PATH]",
)

parser.add_argument(
    "batchfile",
    metavar="BatchFile",
    type=str,
    help="Base directory containing subdirs to zip",
    nargs="?",
    default="batch.txt",
)
args = parser.parse_args()

batchfile = args.batchfile

if not os.path.exists(batchfile):
    exit("Specified batch file does not exist!")

urls = []

with open(batchfile, mode="r", encoding="utf-8") as f:
    for line in f.readlines():
        urls.append(line)

# Prune empty lines
whitespace = []
for i, url in enumerate(urls):
    if url == "\n" or url == "":
        whitespace.append(i)

urls = [url for i, url in enumerate(urls) if i not in whitespace]

if len(urls) < 1:
    exit("Batch file empty!")

unix_timestamp = str(int(time.time()))
if not os.path.exists(unix_timestamp):
    os.mkdir(unix_timestamp)

os.chdir(unix_timestamp)

# Attempt to download 3 videos at a time, note this will require all 3 to finish before moving to the next 3
# I know this can be done more professionally, but I never really need to download enough videos at once for this
# to be an issue.
for i, url in enumerate(urls):
    if i % 3 != 0:
        continue

    proc = subprocess.Popen(["youtube-dl", url])
    if i + 1 < len(urls):
        proc2 = subprocess.Popen(["youtube-dl", urls[i + 1]])
        if i + 2 < len(urls):
            proc3 = subprocess.Popen(["youtube-dl", urls[i + 2]])
            proc3.communicate()
        proc2.communicate()
    proc.communicate()
