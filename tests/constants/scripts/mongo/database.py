"""Database Testing Setup/Seed information"""


import os
from fnmatch import fnmatch
from typing import List

from tests.constants.database import base_test_script_dir


def append_path_to_doc_filename_list(files: List[str], base_path: str) -> List[str]:
    result_files = []

    for filename in files:
        if fnmatch(filename, "*.json"):
            result_files.append(os.path.join(base_path, filename))

    return result_files


def get_document_seed_files() -> List[str]:
    """Get a list of seed files to be run on tests"""
    base_dir = base_test_script_dir(db_type="mongo", action="seed")

    for _, _, files in os.walk(base_dir):
        return append_path_to_doc_filename_list(files=files, base_path=base_dir)
