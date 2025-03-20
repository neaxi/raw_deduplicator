"""mamuti deduplikator for raw photo filtering"""

import traceback

from pathlib import Path
import sys


def pick_folder():
    """let user pick source folder, remove whitespaces, determine if it exists
    verify "orf" folder exists, within source folder
    if it does not, prompt user again"""
    valid_src = False
    valid_dst = False

    print(f"Current folder: {Path('').absolute()}")
    while not (valid_src and valid_dst):
        print("")
        src = input("Provide source folder: ")
        src = Path(src.strip())  # if not provided, uses pwd
        if src.exists():
            valid_src = True
        else:
            print(f'Path "{src}" does not exists.\nTry again:')
            continue

        target = Path(src, "orf")  # case not handled, Windows doesn't care
        if target.exists():
            valid_dst = True
        else:
            print(f'ORF folder "{target}" not found.\nTry again:')
            continue
    return src, target


def identify_files_for_removal(src, target):
    """check files in both folders, find which extras are in ORF,
    case should be ignored on Windows => not handled"""
    jpgs = [file for file in src.iterdir() if file.suffix in (".jpg", ".JPG")]
    # .orf case not handled, Windows doesn't care
    orf_removal = [f.name.lower() for f in target.iterdir()]

    # filter the removal list, so only entries which does not have
    # a matching jpg will remain
    for jpg in jpgs:
        if f"{jpg.stem.lower()}.orf" in orf_removal:
            orf_removal.pop(orf_removal.index(f"{jpg.stem.lower()}.orf"))

    for_removal = [Path(target, f"{filename}") for filename in orf_removal]
    return for_removal


def pprint_list_of_files(files):
    """find longest name, add 3 spaces, print in COLS columns"""
    COLS = 3
    folder = set(file.parent for file in files)
    if not len(folder) == 1:
        raise AttributeError("Files should be ALWAYS from one folder only")

    print(
        f"Identified {len(files)} files for removal in folder {next(iter(folder)).absolute()}"
    )

    filenames_only = [file.name for file in files]
    longest = max(map(len, filenames_only))
    for idx, i in enumerate(filenames_only):
        print(f"{i:<{longest + 3}}", end="")
        if idx % COLS == 0 and idx != 0:
            print("")
    print("")


def confirm_prompt(msg=None):
    """is users response in valid answers"""
    valid = ["y", "Y", "yes", "Yes", "YES"]
    if not msg:
        msg = "Do you confirm?"
    resp = input(f"\n{msg} [{'/'.join(valid)}]: ")
    return resp.strip() in valid


def delete_files(files: list[Path]):
    """delete whatever file was provided in the input list"""
    print("Deleting...")
    for file in files:
        if file.is_file():
            print(file)
            file.unlink()


# D:\_hack_crack_dev\mamuti_orf_deduplikator\testdir
def main():
    """THE APP"""
    # identify folders
    dir_source, dir_target = pick_folder()

    # identify files
    targeted_files = identify_files_for_removal(dir_source, dir_target)
    if not targeted_files:
        print("No files detected for deletion")
        sys.exit(1)

    pprint_list_of_files(targeted_files)

    # commence deletion
    if confirm_prompt():
        delete_files(targeted_files)
        print("Deletion complete")
    else:
        print("Deletion aborted.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBye.")
    except SystemExit:
        # raised intentionally
        pass
    except BaseException:
        # somethings broken. print traceback, instruct user
        traceback.print_exc()
        print("\nSCRIPT CRASHED .. please send the output above to developer")
    finally:
        # prevent closing the terminal window
        _ = input()
