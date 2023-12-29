#!/usr/bin/env python3
import argparse
import os
import subprocess

TEMPFILE_CONSTANT = "./concatfile.tmp"


def getItemsInDir(dir: str, excluded_types: list[str]) -> list[str]:
    items = os.listdir(dir)
    items = [
        f
        for f in items
        if os.path.isfile(f"{dir}/{f}") and (f.split(".")[-1] not in excluded_types)
    ]
    if len(items) < 1:
        exit("No items in target directory!")
    return items


def runFfmpeg(target_file: str, output_file: str) -> int:
    proc = subprocess.Popen(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            target_file,
            "-c",
            "copy",
            output_file
        ]
    )
    proc.wait()
    return proc.returncode


def createTempFile(base_dir: str, items: list[str]) -> None:
    with open(TEMPFILE_CONSTANT, "w") as f:
        for item in items:
            line = f"file '{base_dir}/{item}'\n"
            f.write(line)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="batch-concat.py",
        description=(
            "Uses FFmpeg (must be preinstalled) to concatenate videos "
            + "of the same aspect ratio in a given directory."
        ),
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Mode to run")
    subparsers.required = True

    parser_dir = subparsers.add_parser("dir")
    parser_dir.add_argument(
        "directory",
        metavar="directory",
        type=str,
        help=(
            "Directory to read files from. By default, all files in the directory "
            + "will be added to the list, so ensure the contents contain "
            + "only that which you intend to include."
        ),
    )
    parser_dir.add_argument(
        "-e",
        "--exclude",
        help=(
            "Filetypes to exclude. Can be a comma delimited "
            + "list, or use this argument multiple times for multiple types."
        ),
        required=False,
        action="append",
    )

    parser_file = subparsers.add_parser("file")
    parser_file.add_argument(
        "file",
        metavar="file",
        type=str,
        help=("Text file containing newline delimited list of files to concatenate."),
    )

    parser.add_argument(
        "newfile",
        metavar="new-file",
        type=str,
        help="Name/path for the new concatenated file.",
    )

    args = parser.parse_args()

    newfile_target = args.newfile
    ffmpeg_target = ""

    print(f"Creating file: {newfile_target}")

    if args.subcommand == "dir":
        target_dir: str = args.directory.rstrip("/")
        excluded_arg: list[str] = []
        if args.exclude is not None:
            excluded_arg = args.exclude

        excluded: list[str] = []
        for item in excluded_arg:
            if "," in item:
                split_items = item.split(",")
                for split_item in split_items:
                    excluded.append(split_item.lstrip('.'))
            else:
                excluded.append(item.lstrip('.'))

        print(f"Dir selected is: {target_dir}")
        print(f"Excluded filetypes are: {excluded}")
        if not os.path.exists(target_dir):
            exit("Invalid target directory!")

        print("Scanning dir...")
        files = getItemsInDir(target_dir, excluded)
        print(f"Writing temporary file to {TEMPFILE_CONSTANT}...")
        createTempFile(target_dir, files)
        ffmpeg_target = TEMPFILE_CONSTANT

    elif args.subcommand == "file":
        target_file: str = args.file
        print(f"Target file is: {target_file}")
        if not os.path.exists(target_file):
            exit("File does not exist!")
        
        empty = True
        with open(target_file, 'r') as f:
            data = f.read()
            if not (data.isspace() or data == ''):
                empty = False
        
        if empty:
            exit("Target file empty!")
        
        ffmpeg_target = target_file

    print("Running ffmpeg...")
    ret = runFfmpeg(ffmpeg_target, newfile_target)
    if ret == 0:
        print("Done!")
    else:
        exit(f"ERROR: FFmpeg error with return code {ret}. See output above for more details.")