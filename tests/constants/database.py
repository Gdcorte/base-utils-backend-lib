"""Database Testing Setup/Seed information"""


import os
from fnmatch import fnmatch
from typing import List


def base_test_script_dir(db_type: str, action: str):
    cwd: str = os.getcwd()
    return os.path.join(cwd, "tests", "constants", "scripts", db_type, action)


def append_path_to_sql_filename_list(files: List[str], base_path: str) -> List[str]:
    result_files = []

    for filename in files:
        if fnmatch(filename, "*.sql"):
            result_files.append(os.path.join(base_path, filename))

    return result_files


def get_sql_setup_files() -> List[str]:
    """Get a list of setup files to be run on tests"""
    base_dir = base_test_script_dir(db_type="sql", action="setup")

    for _, _, files in os.walk(base_dir):
        return append_path_to_sql_filename_list(files=files, base_path=base_dir)


def get_sql_seed_files() -> List[str]:
    """Get a list of seed files to be run on tests"""
    base_dir = base_test_script_dir(db_type="sql", action="seed")

    for _, _, files in os.walk(base_dir):
        return append_path_to_sql_filename_list(files=files, base_path=base_dir)
