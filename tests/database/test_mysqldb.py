"""Mysql utilities test"""
from os import environ, getenv

import pytest
from MySQLdb.cursors import DictCursor

from gdcbeutils.database.mysqldb import (
    SqlConnector,
    SqlConnParamsMissingException,
    SqlHelper,
)
from gdcbeutils.database.testing.context import execute_sql_from_file_list
from gdcbeutils.database.testing.decorator import (
    decorate_test_db_create,
    decorate_test_db_with_seed,
    decorate_test_db_with_setup,
)
from tests.constants.database import get_sql_seed_files, get_sql_setup_files


def test_raises_if_env_var_is_missing():
    """It will raise if environment variables are missing"""
    if getenv("MYSQL_HOST"):
        del environ["MYSQL_HOST"]
    if getenv("MYSQL_PORT"):
        del environ["MYSQL_PORT"]
    if getenv("MYSQL_USER"):
        del environ["MYSQL_USER"]
    if getenv("MYSQL_PASSWORD"):
        del environ["MYSQL_PASSWORD"]

    connection_helper = SqlConnector()

    with pytest.raises(SqlConnParamsMissingException):
        connection_helper.db_params_from_env_file()


def test_can_get_connection_params_from_env_vars():
    """It can get connection parameters from env params"""

    connection_helper = SqlConnector()

    db_params = connection_helper.db_params_from_env_file()

    assert db_params.host == environ["MYSQL_HOST"]
    assert db_params.port == int(environ["MYSQL_PORT"])
    assert db_params.user == environ["MYSQL_USER"]
    assert db_params.password == environ["MYSQL_PASSWORD"]


def test_can_get_connection_params_from_env_vars_with_prefix():
    """It can get connection parameters from env params"""
    environ["MYSQL_UAU_HOST"] = "host"
    environ["MYSQL_UAU_PORT"] = "4567"
    environ["MYSQL_UAU_USER"] = "uauser"
    environ["MYSQL_UAU_PASSWORD"] = "such_pass"

    connection_helper = SqlConnector(prefix="UAU")

    db_params = connection_helper.db_params_from_env_file()

    assert db_params.host == environ["MYSQL_UAU_HOST"]
    assert db_params.port == int(environ["MYSQL_UAU_PORT"])
    assert db_params.user == environ["MYSQL_UAU_USER"]
    assert db_params.password == environ["MYSQL_UAU_PASSWORD"]


def test_can_create_connection_to_db():
    """It can crete a db connection"""
    connection_helper = SqlConnector()
    conn = connection_helper.connect()

    assert conn
    assert conn.open


def test_can_create_cursor_from_connection():
    connection_helper = SqlConnector()
    conn = connection_helper.connect()

    cursor = connection_helper.get_cursor(conn=conn)
    assert isinstance(cursor, DictCursor)


@decorate_test_db_with_setup(sql_setup_files=get_sql_setup_files())
def test_statement_context_will_not_commit():
    """Will not commit in statement context"""
    db_name = "test"
    sql_helper = SqlHelper(db_name=db_name)

    # This shuld not persist after the statement, since it is not commited
    with sql_helper.perform_statement() as cursor:
        sql = """INSERT INTO tests (test) VALUES ('ooooooops')"""
        cursor.execute(sql)

    with sql_helper.perform_statement() as cursor:
        cursor.execute("SELECT * FROM tests")
        result = cursor.fetchall()

        assert not result


@decorate_test_db_with_seed(
    sql_setup_files=get_sql_setup_files(),
    sql_seed_files=get_sql_seed_files(),
)
def test_statement_will_successfullt_perform_select_statement():
    """Will not commit in statement context"""
    db_name = "test"
    sql_helper = SqlHelper(db_name=db_name)

    with sql_helper.perform_statement() as cursor:
        cursor.execute("SELECT * FROM tests")
        result = cursor.fetchall()

        result_list = list(result)
        assert len(result_list)
        assert result_list[0]["test"] == "my test seed"


@decorate_test_db_with_setup(sql_setup_files=get_sql_setup_files())
def test_operation_context_will_commit_on_success():
    """Will commit in operation context"""
    db_name = "test"
    sql_helper = SqlHelper(db_name=db_name)

    # an operation should commit all statements after context is left
    with sql_helper.perform_operation() as cursor:
        sql = """INSERT INTO tests (test) VALUES ('ooooooops')"""
        cursor.execute(sql)

    with sql_helper.perform_statement() as cursor:
        cursor.execute("SELECT * FROM tests")
        result = cursor.fetchall()

        assert result


@decorate_test_db_with_setup(sql_setup_files=get_sql_setup_files())
def test_operation_context_will_not_commit_on_error():
    """Will not commit in operation context if error happen"""
    db_name = "test"
    sql_helper = SqlHelper(db_name=db_name)

    # an operation should commit all statements after context is left
    try:
        with sql_helper.perform_operation() as cursor:
            sql = """INSERT INTO tests (test) VALUES ('ooooooops')"""
            cursor.execute(sql)
            raise Exception("oops")
    except:  # noqa: E722
        pass

    with sql_helper.perform_statement() as cursor:
        cursor.execute("SELECT * FROM tests")
        result = cursor.fetchall()

        assert not result


def test_sql_executor_will_not_raise_when_no_files_are_passed():
    """Will not raise when no file is passed"""
    execute_sql_from_file_list(db_name="any", file_list=[])


@decorate_test_db_create()
def test_decorator_can_create_empty_db():
    """Decorator is able to create empty DB"""
    sql_helper = SqlHelper(db_name="test")

    with sql_helper.perform_operation() as cursor:
        sql = """SHOW TABLES"""
        cursor.execute(sql)
        result = cursor.fetchall()
        assert not result
