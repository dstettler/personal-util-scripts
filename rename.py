#!/usr/bin/env python3
import argparse
import os
import re

parser = argparse.ArgumentParser(
    prog="rename.py", description="Renames all files in a target directory"
)

parser.add_argument(
    "-t",
    "--target-dir",
    type=str,
    help="Directory to check",
    required=False,
    default="."
)

parser.add_argument(
    "-e",
    "--exclude",
    help="Files to exclude",
    required=False,
    action='append'
)

parser.add_argument(
    "regex",
    metavar="regex",
    type=str,
    help="Base directory containing subdirs to zip",

)
parser.add_argument(
    "newname",
    metavar="new-name",
    type=str,
    help="The new name format. This will be using python regex format, so groups can be selected using '\\\\1' formatting",
)

parser.add_argument(
    "-v",
    action='store_true',
    help="Verbose mode",
    required=False
)

parser.add_argument(
    "-y",
    action='store_true',
    help="Override questioning",
    required=False
)

args = parser.parse_args()

target_dir = args.target_dir.rstrip("/")
excluded = args.exclude
reg = args.regex
new_name = args.newname
v = args.v
y = args.y

if excluded is None:
    excluded = []

target_contents = os.listdir(target_dir)
if len(target_contents) < 1:
    exit("Target directory empty")

target_files = [file for file in target_contents if (os.path.isfile(f"{target_dir}/{file}") and file not in excluded)]

final_vals = {}
for target in target_files:
    full_out = f"{target_dir}/{re.sub(reg, new_name, target)}"
    full_target = f"{target_dir}/{target}"

    # No need to print items that will remain the same
    if full_out == full_target:
        continue

    final_vals[full_target] = full_out
    if v is True:
        print(f"{full_target} -> {full_out}")

# If the user didn't ask for output why would they want to be asked a question?
if y is False and v is True:
    print("Is this ok? (Y/n)")
    ok = input()
    if ok.capitalize() == 'N':
        exit("Aborting")

for key, val in final_vals.items():
    os.rename(key, val)

if len(final_vals.keys()) < 1:
    print("No changes made")
else:
    print("Done")