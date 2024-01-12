# Prerequisites:
Please run `python -m pip install pywin32` in order to install the necessary win32 library.

# `install.py`
```
usage: install.py [-h] (-r | -a) [--leave-artifacts]

(Un)Installs a regkey to run the pin-to-all-apps.py helper program to quickly pin programs to Windows' all apps menu
from the File Explorer

options:
  -h, --help         show this help message and exit
  -r, --remove       Remove and delete regkey
  -a, --add          Generate and add regkey
  --leave-artifacts  Leave created shortcuts in place
```

# `pin-to-all-apps.py`
```
usage: pin-to-all-apps.py [-h] Target

Creates/removes a Windows shortcut in %APPDATA%\Microsoft\Windows\Start Menu\Programs for target file

positional arguments:
  Target      File to create shortcut for

options:
  -h, --help  show this help message and exit
```