import os
import shutil


def copy_files_recursive(source_dir: str, dest_dir: str) -> None:
    if not os.path.exists(source_dir):
        raise ValueError(f"source directory does not exist: {source_dir}")
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    for entry in os.listdir(source_dir):
        source_path = os.path.join(source_dir, entry)
        dest_path = os.path.join(dest_dir, entry)
        if os.path.isfile(source_path):
            print(f" * copy {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            print(f" * mkdir {dest_path}")
            copy_files_recursive(source_path, dest_path)


def copy_static_to_public(source_dir: str, dest_dir: str) -> None:
    if os.path.exists(dest_dir):
        print(f"Deleting {dest_dir}...")
        shutil.rmtree(dest_dir)
    print(f"Copying {source_dir} -> {dest_dir}")
    copy_files_recursive(source_dir, dest_dir)
