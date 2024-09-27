import argparse
import copy
import hashlib
import json
import os
import pathlib
import shutil

from dataclasses import dataclass


@dataclass
class RuntimePrefs:
    verbosity: int
    delete_on_target: bool
    rescan: bool


CACHE_DIR_KEY = "cache_dirs"
ST_PAIRS_KEY = "st_pairs"
IGNORE_KEY = "ignore"


def validate_sync_prefs(sync_prefs: dict[str, dict[str, str] | list[str]], rt_prefs: RuntimePrefs) -> bool:
    """`validate_sync_prefs()`: Validates syncfile syntax

    Args:
        sync_prefs (dict[str, dict[str, str]  |  list[str]]): Dictionary read from
                                                              the given syncfile
        rt_prefs (RuntimePrefs): Preferences determined by command line args

    Returns:
        bool: `True` if the given dictionary is valid, else `False`
    """
    test_dict: dict[str, bool] = {
        "Validate top level keys": (
            CACHE_DIR_KEY in sync_prefs.keys() and
            ST_PAIRS_KEY in sync_prefs.keys() and
            IGNORE_KEY in sync_prefs.keys())
    }
    cache_dirs: dict[str, str] = sync_prefs[CACHE_DIR_KEY]
    st_pairs: dict[str, str] = sync_prefs[ST_PAIRS_KEY]
    ignores: list[str] = sync_prefs[IGNORE_KEY]

    test_dict["Validate pref key values are correct type"] = (
        isinstance(cache_dirs, dict) and
        isinstance(st_pairs, dict) and
        isinstance(ignores, list))
    for src, dest in st_pairs.items():
        test_dict[f"Validate {src} from src:target pairs has cache"] = src in cache_dirs.keys()
        test_dict[f"Validate {src} exists"] = pathlib.Path(src).exists()
        test_dict[f"Validate {src} cache file exists"] = pathlib.Path(cache_dirs[src]).exists()
        test_dict[f"Validate {dest} exists"] = pathlib.Path(dest).exists()

    for test, result in test_dict.items():
        if rt_prefs.verbosity >= 2:
            print(f"{test}: {str(result)}")
        if not result:
            return False

    return True


def sync_path(src: str, dest: str, cache_file: str, ignores: list[str], rt_prefs: RuntimePrefs) -> None:
    """`sync_path()`: Syncs content from source directory to destination directory,
                      applying prefs as needed

    Args:
        src (str): Source directory
        dest (str): Destination directory
        cache_file (str): Cache file for information on `dest`
        ignores (list[str]): List of strings to ignore in filepaths when rescanning
        rt_prefs (RuntimePrefs): Preferences determined by command line args
    """
    cached_hashes: dict[str, list[str]] = {}
    src_hashes: dict[str, list[str]] = {}
    files_to_remove: list[str] = []
    src_path = pathlib.Path(src)
    dest_path = pathlib.Path(dest)

    if rt_prefs.verbosity >= 2:
        print(f"Reading cache file: {cache_file}")

    with open(cache_file, 'r', encoding="utf-8") as f:
        cached_hashes = json.loads(f.read())

    # Deep copy every existing cached file and remove them from the list as we discover them-
    # this is used to determine files that no longer exist and can be deleted and removed from the cache
    files_to_remove = copy.deepcopy(list(cached_hashes.keys()))

    if rt_prefs.verbosity >= 3:
        print(f"Cached hashes: {cached_hashes}")

    if rt_prefs.verbosity >= 1:
        print("Getting file hashes of src dir")

    if rt_prefs.rescan:
        if rt_prefs.verbosity >= 1:
            print("Rescanning src dir, this may take a while...")
        for src_file in src_path.rglob("*"):
            if src_file.is_dir():
                continue

            # Logic to check if one of the ignore keywords is anywhere in the path
            # TODO: Maybe make this regex?
            ignored = False
            for ignore in ignores:
                parent_path = src_file.parent.absolute().as_posix() + "/"
                if ignore in src_file.name or ignore in parent_path or ignore == src_file.absolute().as_posix():
                    ignored = True
                    break
            if ignored:
                continue

            relative_src_name = src_file.absolute().as_posix().replace(src_path.absolute().as_posix(), "")
            modified = str(os.path.getmtime(src_file.absolute().as_posix()))

            # If the cached hash has the same mtime, don't waste time re-hashing
            if relative_src_name in cached_hashes.keys() and cached_hashes[relative_src_name][1] == modified:
                if relative_src_name in files_to_remove:
                    files_to_remove.remove(relative_src_name)
                continue

            m = hashlib.md5()

            if rt_prefs.verbosity >= 2:
                print(f"Different mtime or new file - Reading bytes of {src_file.absolute()} to MD5 buffer")

            with src_file.open('rb') as f:
                m.update(f.read())

            src_hashes[relative_src_name] = [m.hexdigest(), str(os.path.getmtime(src_file.absolute().as_posix()))]

            # This will occur if the mtime is the different, but the hash is equivalent
            if ((relative_src_name in cached_hashes.keys()) and (src_hashes[relative_src_name][0] == cached_hashes[relative_src_name][0])):
                cached_hashes[relative_src_name] = src_hashes[relative_src_name]

            if relative_src_name in files_to_remove:
                files_to_remove.remove(relative_src_name)
    else:
        # Since rescanning is off and nothing was cached, do nothing
        if len(cached_hashes.keys()) <= 0:
            return

        for cached_file in cached_hashes.keys():
            src_file = pathlib.Path(f"{src_path.absolute().as_posix()}/{cached_file}")
            print(f"Checking {cached_file}")
            if src_file.exists():
                relative_src_name = src_file.absolute().as_posix().replace(src_path.absolute().as_posix(), "")
                modified = str(os.path.getmtime(src_file.absolute().as_posix()))

                # If the cached hash has the same mtime, don't waste time re-hashing
                if (cached_hashes[relative_src_name][1] == modified):
                    if relative_src_name in files_to_remove:
                        files_to_remove.remove(relative_src_name)
                    continue

                m = hashlib.md5()

                if rt_prefs.verbosity >= 2:
                    print(f"Different mtime - reading bytes of {src_file.absolute()} to MD5 buffer")

                with src_file.open('rb') as f:
                    m.update(f.read())

                src_hashes[relative_src_name] = m.hexdigest()

                # This will occur if the mtime is the different, but the hash is equivalent
                if ((relative_src_name in cached_hashes.keys()) and (src_hashes[relative_src_name][0] == cached_hashes[relative_src_name][0])):
                    cached_hashes[relative_src_name] = src_hashes[relative_src_name]

                if relative_src_name in files_to_remove:
                    files_to_remove.remove(relative_src_name)
            else:
                if rt_prefs.verbosity >= 2:
                    print(f"{src_file.absolute().as_posix()} does not exist, skipping and removing from cache")

    if rt_prefs.verbosity >= 3:
        print(f"Generated source hashes: {src_hashes}")

    # Build list of files whose generated hashes are different than the cached ones
    to_update: list[str] = []
    for file, file_hash in src_hashes.items():
        if ((file in cached_hashes.keys() and cached_hashes[file] != file_hash) or
                file not in cached_hashes.keys()):
            to_update.append(file)

    if rt_prefs.verbosity >= 0:
        print(f"{len(to_update)} file(s) to update")

    # Copy updated/new files
    for file in to_update:
        dest_file_path = pathlib.Path(f"{dest_path.absolute().as_posix()}/{file}")
        src_file_path = pathlib.Path(f"{src_path.absolute().as_posix()}/{file}")

        if not dest_file_path.parent.exists():
            dest_file_path.parent.mkdir(parents=True)

        if rt_prefs.verbosity >= 1:
            print(f"Copying {src_file_path} -> {dest_file_path}")

        try:
            shutil.copy(src_file_path.absolute(), dest_file_path.absolute())
        except Exception as e:
            print(f"ERROR: {e}")

    if rt_prefs.verbosity >= 2:
        print("Writing new cached src hashes to file")

    # Update cache values and add new ones
    for key, val in src_hashes.items():
        cached_hashes[key] = val

    # Remove files that were cached but no longer exist in the source
    for item in files_to_remove:
        cached_hashes.pop(item)
        if rt_prefs.delete_on_target:
            removed_item = f"{dest_path.absolute().as_posix()}{item}"
            if rt_prefs.verbosity >= 1:
                print(f"Deleting {removed_item}")
            os.remove(removed_item)

    # Write updated cache file
    os.remove(cache_file)
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(cached_hashes))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="pathsync.py",
        description="Syncs all files in specified paths to the matching file defined in the syncfile"
    )

    parser.add_argument(
        "syncfile",
        metavar="syncfile",
        type=str,
        help="Syncfile with all src:target pairs and corresponding cached hash locations",
    )

    verbosity_group = parser.add_mutually_exclusive_group()

    verbosity_group.add_argument(
        "-v",
        action='store_true',
        help="Verbose mode",
        required=False,
        default=False
    )

    verbosity_group.add_argument(
        "-vv",
        action='store_true',
        help="Extra verbose mode",
        required=False,
        default=False
    )

    verbosity_group.add_argument(
        "-vvv",
        action='store_true',
        help="Stupidly verbose mode",
        required=False,
        default=False
    )

    verbosity_group.add_argument(
        "-s",
        action='store_true',
        help="Silent mode",
        required=False,
        default=False
    )

    parser.add_argument(
        "-d",
        action='store_true',
        help="Delete files from target",
        required=False,
        default=False
    )

    parser.add_argument(
        "-r",
        "--rescan",
        action='store_true',
        help="Rescan full src directory",
        required=False,
        default=False
    )

    args = parser.parse_args()
    verbosity = 0
    if args.s:
        verbosity = -1
    elif args.v:
        verbosity = 1
    elif args.vv:
        verbosity = 2
    elif args.vvv:
        verbosity = 3

    prefs = RuntimePrefs(verbosity, args.d, args.rescan)

    sync_prefs: dict[str, dict[str, str]] = {}
    syncfile_path = pathlib.Path(args.syncfile)

    if syncfile_path.exists() and syncfile_path.is_file():
        with open(syncfile_path.absolute(), 'r', encoding='utf-8') as syncfile:
            sync_prefs = json.loads(syncfile.read())

        if validate_sync_prefs(sync_prefs, prefs):
            for src, dest in sync_prefs[ST_PAIRS_KEY].items():
                if prefs.verbosity >= 0:
                    print(f"Syncing {src} -> {dest}")
                sync_path(
                    src=src,
                    dest=dest,
                    cache_file=sync_prefs[CACHE_DIR_KEY][src],
                    ignores=sync_prefs[IGNORE_KEY],
                    rt_prefs=prefs)

            if prefs.verbosity >= 0:
                print("Done!")
        else:
            print("ERROR: Sync prefs invalid, check extra verbose logging for more details")
    else:
        print("ERROR: Syncfile path either does not exist or is not a file")
