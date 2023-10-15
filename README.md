# personal-util-scripts
This repo contains exactly what it says: some personal utility scripts I've written that I like to use, but always seem to end up misplacing.
Keeping an organized central location makes sense, and hey, if someone else wants to use these go ahead!

For the sake of convenience, I'll add on the argument lists of each of the scripts as I add them here:

## `batch-dl.py`
**NOTE: This requires an existing installation of youtube-dl on your PATH**
```
usage: batch-dl.py [-h] [BatchFile]

Downloads list of files using youtube-dl [REQUIRES youtube-dl TO BE INSTALLED AND ON PATH]

positional arguments:
  BatchFile   Base directory containing subdirs to zip

options:
  -h, --help  show this help message and exit
```

## `rename.py`
```
usage: rename.py [-h] [-t TARGET_DIR] [-e EXCLUDE] [-v] [-y] regex new-name

Renames all files in a target directory

positional arguments:
  regex                 Base directory containing subdirs to zip
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