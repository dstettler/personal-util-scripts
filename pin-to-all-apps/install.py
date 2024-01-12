import argparse
import ctypes
import os
import pathlib
import shutil
import sys

# To avoid UAC escalation on the entire script, just use it to run the reg command
def import_regfile(path: str):
    ctypes.windll.shell32.ShellExecuteW(None, "runas", "C:\\Windows\\System32\\reg.exe", " ".join(["import", path]), None, 1)

REMOVE_NAME = "/reg/remove.reg"
ADD_NAME = "/reg/add.reg"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="install.py", description="(Un)Installs a regkey to run the pin-to-all-apps.py helper program to quickly pin programs to Windows' all apps menu from the File Explorer"
    )

    parser_mode_group = parser.add_mutually_exclusive_group()
    parser_mode_group.required = True

    parser_mode_group.add_argument("-r", "--remove", action="store_true", help="Remove and delete regkey")
    parser_mode_group.add_argument("-a", "--add", action="store_true", help="Generate and add regkey")

    parser.add_argument(
        "--leave-artifacts",
        action='store_true',
        help="Leave created shortcuts in place",
        required=False
    )

    args = parser.parse_args()

    filepath = pathlib.Path(__file__).parent.resolve().as_posix()

    if args.remove == True:
        import_regfile(f"{filepath}{REMOVE_NAME}")

        # ignore_errors only in the event the files have become read-only for some reason
        shutil.rmtree(f"{filepath}/reg", ignore_errors=True)

        # Remove all pinned shortcuts
        pinned_dir = pathlib.Path(os.getenv("APPDATA") + "\\Microsoft\\Windows\\Start Menu\\Programs\\Pinned")
        if pinned_dir.exists() and not args.leave_artifacts:
            shutil.rmtree(pinned_dir.as_posix())
    else:
        reg_path = pathlib.Path(f"{filepath}/reg")
        if reg_path.exists():
            files = [f for f in reg_path.iterdir() if f.is_file()]
            for f in files:
                os.remove(f.as_posix())
        else:
            os.mkdir("reg")
        
        interpreter_path = (sys.exec_prefix + "\\pythonw.exe").replace("\\", "\\\\")
        pin_path = pathlib.Path(f"{filepath}/pin-to-all-apps.py").as_posix().replace("/", "\\\\")
        print(f"Interpreter at: {interpreter_path}\nFilepath at: {pin_path}")

        # Write regfiles

        add_content = f"""Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\*\shell\Pin to All Apps]
@="(Un)pin to/from All Apps"

[HKEY_CLASSES_ROOT\*\shell\Pin to All Apps\command]
@="\\"{interpreter_path}\\" \\"{pin_path}\\" \\"%1\\""

"""
        remove_content = """Windows Registry Editor Version 5.00

[-HKEY_CLASSES_ROOT\*\shell\Pin to All Apps\command]
[-HKEY_CLASSES_ROOT\*\shell\Pin to All Apps]

"""

        with open(f"{filepath}{ADD_NAME}", "w") as add, open(f"{filepath}{REMOVE_NAME}", "w") as remove:
            add.writelines(add_content)
            remove.writelines(remove_content)

        import_regfile(f"{filepath}{ADD_NAME}")
        