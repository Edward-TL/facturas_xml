"""
Functions that helps in little common tasks
"""

from pathlib import Path
import shutil
from os import listdir
from os.path import exists as path_exists
from os import remove as os_remove
import os
from dotenv import dotenv_values

def parent_dir() -> str:
    """Return the parent directory, so the folder can be added as needed"""
    return str(Path("./").parent.absolute())

def get_config(path: str) -> dict:
    """Given the path of the .env file, file return the values as a dictionary"""
    return dotenv_values(path)


def get_files(path: str, file_extension: str = '.xlsx', drop_if_contains:str | None = None) -> list[str]:
    """
    From a path, returns only the files that ends with `file_end`, like:
    '.parquet', '.xlsx', '.png', '.env', '.csv'

    If drop_if_contains is not `None`, exclude the file if contains the text passed.
    """

    # Grants a file extension and that path exists
    if (
        (file_extension.startswith('.')) or ('.' in file_extension)
        ) and (
            path_exists(path)
            ):

        # Exclude some cases
        if drop_if_contains is not None:
            return [
                file for file in listdir(path)\
                    if (
                        file.endswith(file_extension)
                        ) and (
                            drop_if_contains not in file
                            )
                    ]
        # Return everything
        return [file for file in listdir(path) if file.endswith(file_extension)]
    
    if '.' not in file_extension:
        raise ValueError(f"{file_extension} is not a file extension. Check the the value and the missing '.'")
    
    if path_exists(path) is False:
        raise ValueError(f"Path: `{path}` does not exist")


def list_directories(path: str):
    """Return a list of absolute paths of directories directly under the given path."""
    path = os.path.abspath(path)
    return [
        os.path.join(path, item)
        for item in os.listdir(path)
        if os.path.isdir(os.path.join(path, item))
    ]


def copy_directory(source_path, destination_path):
    """
    If destintation_path exists, will delete all and copy the
    source_path into destintation_path
    """
    if path_exists(destination_path):
        os_remove(destination_path)
    shutil.copytree(source_path, destination_path)


def flat_list(matrix:list):
    """Flats a list of lists (matrix)"""
    return [item for row in matrix for item in row]


def get_all_files_in(root_path: str | Path, file_type: str) -> list[str]:
    """
    Returns a list of all XML files in all folders stored at the root path
    
    :xml_root_path: str | Path
    :return: list[str]
    """
    files_in_root = [
            f"{root_path}/{file}" \
            for file in get_files(root_path, file_extension=file_type)
    ]

    files_in_folders = [
        [
            f"{facturas_dir}/{file}" \
            for file in get_files(facturas_dir, file_extension=file_type)
        ] for facturas_dir in list_directories(root_path)
    ]
    
    if len(files_in_root) > 0 and len(files_in_folders) > 0:
        files_in_root = flat_list(files_in_root)
        files_in_folders = flat_list(files_in_folders)

        return files_in_root + files_in_folders

    if len(files_in_folders) > 0:
        files_in_folders = flat_list(files_in_folders)

    return flat_list(files_in_root)