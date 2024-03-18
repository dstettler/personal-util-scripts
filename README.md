# personal-util-scripts
This repo contains exactly what it says: some personal utility scripts I've written that I like to use, but always seem to end up misplacing.
Keeping an organized central location makes sense, and hey, if someone else wants to use these go ahead!

For the sake of convenience, I'll add on the argument lists of each of the scripts as I add them here:

## `batch-concat.py`
**NOTE: This requires an existing installation of `ffmpeg` on your PATH**
```
usage: batch-concat.py [-h] {dir,file} ... new-file

Uses FFmpeg (must be preinstalled) to concatenate videos of the same aspect ratio in a given directory.

positional arguments:
  {dir,file}  Mode to run
  new-file    Name/path for the new concatenated file.

options:
  -h, --help  show this help message and exit
```
```
usage: batch-concat.py dir [-h] [-e EXCLUDE] directory

positional arguments:
  directory             Directory to read files from. By default, all files in the directory will be added to the
                        list, so ensure the contents contain only that which you intend to include.

options:
  -h, --help            show this help message and exit
  -e EXCLUDE, --exclude EXCLUDE
                        Filetypes to exclude. Can be a comma delimited list, or use this argument multiple times for
                        multiple types.
```
```
usage: batch-concat.py file [-h] file

positional arguments:
  file        Text file containing newline delimited list of files to concatenate.

options:
  -h, --help  show this help message and exit
```

## `batch-dl.py`
**NOTE: This requires an existing installation of `youtube-dl` on your PATH**
```
usage: batch-dl.py [-h] [BatchFile]

Downloads list of files using youtube-dl [REQUIRES youtube-dl TO BE INSTALLED AND ON PATH]

positional arguments:
  BatchFile   File with list of newline-delimited video URLs to download

options:
  -h, --help  show this help message and exit
```

## `rename.py`
```
usage: rename.py [-h] [-t TARGET_DIR] [-e EXCLUDE] [-v] [-y] regex new-name

Renames all files in a target directory

positional arguments:
  regex                 Regex to apply to target filenames
  new-name              The new name format. This will be using python regex format,
                        so groups can be selected using '\\1' formatting

options:
  -h, --help            show this help message and exit
  -t TARGET_DIR, --target-dir TARGET_DIR
                        Directory to check
  -e EXCLUDE, --exclude EXCLUDE
                        Files to exclude
  -v                    Verbose mode
  -y                    Override questioning
```
### Example Usage
`python rename.py -t ./ "(\w*).webp" "\\1.png"`

## `zipper.py`
```
usage: zipper.py [-h] [BaseDir] [ZipPath]

Zips all subdirectories in the indicated directory

positional arguments:
  BaseDir     Base directory containing subdirs to zip
  ZipPath     Where to place the zips

options:
  -h, --help  show this help message and exit
```
### Example Usage
`python zipper.py "." "./zipped"`
