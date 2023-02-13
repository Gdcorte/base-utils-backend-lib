"""MySql utilities"""

import contextlib
import logging
from os import environ
from typing import Iterator, cast

from MySQLdb import Connection
from MySQLdb import connect as db_connect
from MySQLdb.cursors import DictCursor
from pydantic import BaseModel, Extra

logger = logging.getLogger("MySql Global Helper")


class BaseSqlHandlerException(Exception):
    """Base SQL Exception"""


class SqlConnParamsMissingException(BaseSqlHandlerException):
    """Exception thrown when connection parameters are unavailable"""


class MySqlConnectParams(BaseModel, extra=Extra.allow):
    """SQL connect parameters model"""

    user: str
    password: str
    host: str
    port: int


class SqlConnector:
    """Base class to handle SQL connections"""

    use_root: bool
    db_name: str | None

    def __init__(self, use_root: bool = False, db_name: str | None = None) -> None:
        self.use_root = use_root
        self.db_name = db_name

    def db_params_from_env_file(self) -> MySqlConnectParams:
        """
        This method gets the credentials from an environment file.
        Note that a KeyError Exception will be raised if
        environment variables are not present on the format:
        - MYSQL_USER
        - MYSQL_PASSWORD
        - MYSQL_HOST
        - MYSQL_PORT
        """
        try:
            credentials = MySqlConnectParams(
                user=environ["MYSQL_USER"],
                password=environ["MYSQL_PASSWORD"],
                host=environ["MYSQL_HOST"],
                port=environ["MYSQL_PORT"],
                database=self.db_name,
            )

            if self.use_root:
                credentials.user = "root"

            return credentials
        except Exception as exc:
            logger.error("Could not find ENV variables to connect")
            raise SqlConnParamsMissingException(
                "Unable to retrieve connection parameters",
            ) from exc

    def connect(self, params: MySqlConnectParams | None = None):
        """
        Estabilished a new connection to the database and returns the instance to that connection.
        Credentials should follow the format: MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT
        """

        credentials = params
        if not credentials:
            credentials = self.db_params_from_env_file()

        conn = db_connect(cursorclass=DictCursor, **credentials.dict(exclude_none=True))

        return cast(Connection, conn)

    @staticmethod
    def get_cursor(conn: Connection) -> DictCursor:
        """
        Returns a cursor from a connection
        """
        return conn.cursor()

    @contextlib.contextmanager
    def perform_statement(self) -> Iterator[DictCursor]:
        """
        Provides a cursor inside a context for statements queries.
        INFO: This does not commit to the DB
        """
        try:
            # Open new connection and cursor for operations
            conn = self.connect()
            cursor = self.get_cursor(conn=conn)

            yield cursor
        finally:
            # Now close them!
            cursor.close()
            conn.close()

    @contextlib.contextmanager
    def perform_operation(self) -> Iterator[DictCursor]:
        """
        Provides a cursor inside a context for operations.
        WARN: This will commit all operations on context close without errors
        """
        try:
            # Open new connection and cursor for operations
            conn = self.connect()
            cursor = self.get_cursor(conn=conn)

            yield cursor

            conn.commit()
        finally:
            # Now close them!
            cursor.close()
            conn.close()


class SqlHelper(SqlConnector):
    """
    Super class from SqlConnector which specifies one DB for operations on startup
    """

    def __init__(self, db_name: str | None = None) -> None:
        database = db_name or environ["MYSQL_DB"]
        super().__init__(db_name=database)
