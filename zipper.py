import argparse
import os
import shutil

parser = argparse.ArgumentParser(
    prog="zipper.py", description="Zips all subdirectories in the indicated directory"
)

parser.add_argument(
    "defaultPath",
    metavar="BaseDir",
    type=str,
    help="Base directory containing subdirs to zip",
    nargs="?",
    default=".",
)
parser.add_argument(
    "zipPath",
    metavar="ZipPath",
    type=str,
    help="Where to place the zips",
    nargs="?",
    default="zipped",
)
args = parser.parse_args()

zip_path = args.zipPath.rstrip("/")
default_path = args.defaultPath.rstrip("/")

dirs = [dir for dir in os.listdir(f"{default_path}") if os.path.isdir(dir)]

if not os.path.exists(zip_path):
    os.mkdir(zip_path)

for dir in dirs:
    print(f"Zipping: {dir}")
    shutil.make_archive(f"{zip_path}/{dir}", "zip", dir)
