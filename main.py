""" mamuti deduplikator v1 """

import traceback

from pathlib import Path
import sys


def pick_folder():
    """let user pick source folder, remove whitespaces, determine if it exists
    if it does not, prompt user again"""
    valid_src = False
    valid_dst = False
    while not (valid_src and valid_dst):
        print("")
        src = input("Provide source folder: ")
        src = Path(src.strip())
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
    """chcek files in both folders, find which extras are in ORF,
    case should be ignored on Windows => not handled"""
    jpgs = [file.stem for file in src.iterdir() if file.suffix in (".jpg", ".JPG")]
    orfs = [file.stem for file in target.iterdir() if file.suffix in (".orf", ".ORF")]

    orf_extras = set(orfs) - set(jpgs)
    # .orf case not handled, Windows doesn't care
    for_removal = [Path(target, f"{filename}.orf") for filename in orf_extras]
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
        input("No files detected for deletion")
        sys.exit(1)

    pprint_list_of_files(targeted_files)

    # commence deletion
    if confirm_prompt():
        delete_files(targeted_files)
        input("Deletion complete")
    else:
        input("Deletion aborted.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBye.")
    except SystemExit:
        # raised intentionaly
        pass
    except BaseException:
        # somethings broken. hang so the traceback can be copied out
        traceback.print_exc()
        input("\nSCRIPT CRASHED .. please send the output above to developer")
