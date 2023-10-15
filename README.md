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