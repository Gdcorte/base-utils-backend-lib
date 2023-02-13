import contextlib
import logging
import urllib.parse
from os import environ, getenv
from typing import Any, Dict, Iterator

from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

logger = logging.getLogger("Mongo Global Helper")


class MongoDbException(Exception):
    pass


class MongoDbSetupException(MongoDbException):
    pass


class DocumentNotFoundException(MongoDbException):
    pass


class DuplicateDocumentFoundException(MongoDbException):
    key: str

    def __init__(self, message: str, key: str, *args: object) -> None:
        self.key = key
        super().__init__(message, *args)


class MongoConnectParams(BaseModel):
    user: str
    password: str
    host: str
    port: str


class MongoConnectionHelper:
    collection: str | None
    database: str

    def __init__(self, database: str, collection: str | None = None) -> None:
        self.collection = collection
        self.database = database

    def db_params_from_env_file(self) -> MongoConnectParams:
        """
        This method gets the credentials from an environment file.

        WARN: Note that a KeyError Exception will be raised
        if environment variables are not present on the format:
        - MONGO_USER
        - MONGO_PASSWORD
        - MONGO_HOST
        - MONGO_PORT
        """
        try:
            return MongoConnectParams(
                user=environ["MONGO_USER"],
                password=environ["MONGO_PASSWORD"],
                host=environ["MONGO_HOST"],
                port=environ["MONGO_PORT"],
            )

        except Exception as exc:
            logger.error("Could not find ENV variables to connect")
            raise MongoDbSetupException(
                "Unable to retrieve connection parameters",
            ) from exc

    def build_conn_string(self, credentials: MongoConnectParams) -> str:
        username = urllib.parse.quote_plus(credentials.user)
        password = urllib.parse.quote_plus(credentials.password)

        conn_string = (
            f"mongodb://{username}:{password}@{credentials.host}:{credentials.port}"
        )

        if getenv("MONGO_USE_SRV", "") == "True":
            conn_string = f"mongodb+srv://{username}:{password}@{credentials.host}"

        return conn_string

    def connect(self, params: MongoConnectParams | None = None) -> MongoClient:
        """
        Estabilished a new connection to the database and returns the instance to that connection.
        Credentials should follow the format: MONGO_USER, MONGO_PASSWORD, MONGO_HOST, MONGO_PORT
        """
        credentials = params
        if not credentials:
            credentials = self.db_params_from_env_file()

        conn_string = self.build_conn_string(credentials=credentials)
        client = MongoClient(conn_string)

        return client

    @contextlib.contextmanager
    def perform_root_operation(self) -> Iterator[MongoClient]:
        client = self.connect()

        try:
            yield client
        finally:
            client.close()

    @contextlib.contextmanager
    def perform_operation(self) -> Iterator[Database]:
        with self.perform_root_operation() as cursor:
            db = cursor[self.database]

            yield db

    @contextlib.contextmanager
    def perform_collection_operation(self) -> Iterator[Collection]:
        if not self.collection:
            raise MongoDbSetupException(
                "Collection was not setup, unable to use this method",
            )

        with self.perform_operation() as cursor:
            collection = cursor[self.collection]

            yield collection

    def insert_single_document(self, document: Dict[str, Any]) -> None:
        with self.perform_collection_operation() as cursor:
            cursor.insert_one(document)


class BaseMongoDbHelper(MongoConnectionHelper):
    def __init__(
        self, collection: str | None = None, db_name: str | None = None
    ) -> None:
        database = db_name or environ["MONGO_DB"]
        super().__init__(database, collection)
