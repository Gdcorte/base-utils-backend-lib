"""Decorators for DB testing"""
from typing import List

from gdcbeutils.database.testing.context import (
    test_db_create,
    test_db_with_seed,
    test_db_with_setup,
    test_mongo_db,
    test_mongo_db_with_seed,
)


def decorate_test_db_create(db_name: str | None = None):
    """Decorator to setup/teardown empty DB"""

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with test_db_create(db_name=db_name):
                func(*args, **kwargs)

        return wrapper

    return decorated_func


def decorate_test_db_with_setup(
    sql_setup_files: List[str],
    db_name: str | None = None,
):
    """Decorator to setup/teardown empty DB"""

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with test_db_with_setup(db_name=db_name, sql_setup_files=sql_setup_files):
                func(*args, **kwargs)

        return wrapper

    return decorated_func


def decorate_test_db_with_seed(
    sql_setup_files: List[str],
    sql_seed_files: List[str],
    db_name: str | None = None,
):
    """Decorator to setup/teardown empty DB"""

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with test_db_with_seed(
                db_name=db_name,
                sql_setup_files=sql_setup_files,
                sql_seed_files=sql_seed_files,
            ):
                func(*args, **kwargs)

        return wrapper

    return decorated_func


def decorate_test_mongo_db_create(db_name: str | None = None):
    """Decorator to setup/teardown seeded mongo DB"""

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with test_mongo_db(db_name=db_name):
                func(*args, **kwargs)

        return wrapper

    return decorated_func


def decorate_test_mongo_db_with_seed(
    mongo_seed_files: List[str], db_name: str | None = None
):
    """Decorator to setup/teardown seeded mongo DB"""

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with test_mongo_db_with_seed(
                db_name=db_name,
                seed_files=mongo_seed_files,
            ):
                func(*args, **kwargs)

        return wrapper

    return decorated_func
