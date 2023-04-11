"""Contexts for database handling in tests"""
import contextlib
import json
import os
from os import environ
from typing import Iterator, List

from MySQLdb.cursors import DictCursor

from gdcbeutils.database.mongodb import MongoConnectionHelper
from gdcbeutils.database.mysqldb import SqlConnector, SqlHelper


@contextlib.contextmanager
def test_db_create(db_name: str | None = None) -> Iterator[None]:
    """Creates a DB with specified name and destroys it after use"""
    if not db_name:
        db_name = environ["MYSQL_DB"]

    db_helper = SqlConnector(use_root=True)
    conn = db_helper.connect()
    cursor = SqlConnector.get_cursor(conn=conn)

    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        # We need to grant priviledges for common user to perform operations
        cursor.execute(
            f"""GRANT ALL PRIVILEGES ON *.* TO '{environ["MYSQL_USER"]}'@'%'"""
        )
        cursor.execute("""FLUSH PRIVILEGES""")
        conn.commit()

        yield
    finally:
        # We want to make sure to drop this entire db after test
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        conn.commit()

        cursor.close()
        conn.close()


def execute_single_command(cursor: DictCursor, raw_command: str):
    """Executes a single command from the command read inside a file"""
    command = raw_command.strip("\n")
    if command:
        cursor.execute(command)


def execute_sql_from_file_list(file_list: List[str], db_name: str | None = None):
    """Given a file list, browse through the files and executes the sql statements there"""
    if not file_list:
        return

    sql_helper = SqlHelper(db_name)

    with sql_helper.perform_operation() as cursor:
        for filename in file_list:
            with open(filename, "r") as file:
                file_contents = file.read()
                sql_commands = file_contents.split(";")

                for raw_command in sql_commands:
                    execute_single_command(cursor=cursor, raw_command=raw_command)


@contextlib.contextmanager
def test_db_with_setup(
    sql_setup_files: List[str],
    db_name: str | None = None,
) -> Iterator[None]:
    """Creates a test DB and its structure from setup file"""
    if not db_name:
        db_name = environ["MYSQL_DB"]

    with test_db_create(db_name=db_name):
        execute_sql_from_file_list(db_name=db_name, file_list=sql_setup_files)

        yield


@contextlib.contextmanager
def test_db_with_seed(
    sql_setup_files: List[str],
    sql_seed_files=List[str],
    db_name: str | None = None,
) -> Iterator[None]:
    """Creates a test DB and its structure from setup file"""
    if not db_name:
        db_name = environ["MYSQL_DB"]

    with test_db_with_setup(db_name=db_name, sql_setup_files=sql_setup_files):
        execute_sql_from_file_list(db_name=db_name, file_list=sql_seed_files)

        yield


@contextlib.contextmanager
def test_mongo_db(db_name: str | None = None) -> Iterator[None]:
    if not db_name:
        db_name = environ["MYSQL_DB"]

    try:
        yield
    finally:
        mongo_helper = MongoConnectionHelper(db_name)
        with mongo_helper.perform_root_operation() as client:
            client.drop_database(db_name)


def insert_docs_from_file_list(file_list: List[str], db_name: str | None = None):
    """Given a file list, browse through the files and executes the sql statements there"""
    if not file_list:
        return

    for filename in file_list:
        with open(filename, "r") as file:
            file_contents = file.read()
            documents = json.loads(file_contents)
            collection = os.path.basename(filename).split(".")[0]

            mongo_helper = MongoConnectionHelper(
                database=db_name,
                collection=collection,
            )
            with mongo_helper.perform_collection_operation() as cursor:
                cursor.insert_many(documents=documents)


@contextlib.contextmanager
def test_mongo_db_with_seed(
    db_name: str | None = None,
    seed_files: List[str] | None = None,
) -> Iterator[None]:
    if not db_name:
        db_name = environ["MONGO_DB"]

    insert_docs_from_file_list(
        db_name=db_name,
        file_list=seed_files,
    )

    with test_mongo_db(db_name=db_name):
        yield
