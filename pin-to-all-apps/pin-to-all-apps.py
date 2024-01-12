# No shebang because this will exclusively be run on Windows
import argparse
import pathlib
import platform
import os
import win32com.client as win32

if __name__ == "__main__":
    if platform.system() != "Windows":
        exit("This can only be run on Windows!")

    parser = argparse.ArgumentParser(
        prog="pin-to-all-apps.py", description="Creates/removes a Windows shortcut in %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs for target file"
    )

    parser.add_argument(
        "target",
        metavar="Target",
        type=str,
        help="File to create shortcut for"
    )

    args = parser.parse_args()

    target = pathlib.Path(args.target)
    appdata = pathlib.Path(os.getenv("APPDATA") + "\\Microsoft\\Windows\\Start Menu\\Programs")
    new_name = ""

    pinned_dir = pathlib.Path(f"{appdata.as_posix()}/Pinned")
    if not pinned_dir.exists():
        os.mkdir(pinned_dir.as_posix())

    if not target.exists():
        exit("Target file does not exist! Cannot create shortcut!")

    if target.is_file():
        new_name = target.name.rsplit('.', 1)[0] + ".lnk"
    else:
        new_name = target.name + ".lnk"

    new_name = pinned_dir.as_posix() + "/" + new_name

    if pathlib.Path(new_name).exists():
        os.remove(new_name)
    else:
        shell = win32.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(new_name)
        shortcut.IconLocation = target.as_posix()
        shortcut.Targetpath = target.as_posix()
        shortcut.save()
