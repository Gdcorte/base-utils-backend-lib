from os import environ, getenv

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from gdcbeutils.database.mongodb import (
    BaseMongoDbHelper,
    DuplicateDocumentFoundException,
    MongoConnectionHelper,
    MongoDbSetupException,
)
from gdcbeutils.database.testing.decorator import (
    decorate_test_mongo_db_create,
    decorate_test_mongo_db_with_seed,
)
from tests.constants.scripts.mongo.database import get_document_seed_files


def test_raises_if_env_var_is_missing():
    """It will raise if environment variables are missing"""
    if getenv("MONGO_HOST"):
        del environ["MONGO_HOST"]
    if getenv("MONGO_PORT"):
        del environ["MONGO_PORT"]
    if getenv("MONGO_USER"):
        del environ["MONGO_USER"]
    if getenv("MONGO_PASSWORD"):
        del environ["MONGO_PASSWORD"]

    connection_helper = MongoConnectionHelper("test")

    with pytest.raises(MongoDbSetupException):
        connection_helper.db_params_from_env_file()


def test_can_read_env_var():
    connection_helper = MongoConnectionHelper("test")

    db_params = connection_helper.db_params_from_env_file()

    assert db_params.host == environ["MONGO_HOST"]
    assert db_params.port == environ["MONGO_PORT"]
    assert db_params.user == environ["MONGO_USER"]
    assert db_params.password == environ["MONGO_PASSWORD"]


def test_can_create_conn_string_with_srv():
    environ["MONGO_USE_SRV"] = "True"

    connection_helper = BaseMongoDbHelper()

    db_params = connection_helper.db_params_from_env_file()

    conn_string = connection_helper.build_conn_string(
        credentials=db_params,
    )

    assert conn_string == "mongodb+srv://user:test@127.0.0.1"


def test_can_create_connection_to_db():
    connection_helper = BaseMongoDbHelper()

    with connection_helper.perform_root_operation() as client:
        assert isinstance(client, MongoClient)


def test_can_create_db_client():
    connection_helper = BaseMongoDbHelper()

    with connection_helper.perform_operation() as client:
        assert isinstance(client, Database)


def test_can_create_collection_client():
    connection_helper = BaseMongoDbHelper("collection")

    with connection_helper.perform_collection_operation() as client:
        assert isinstance(client, Collection)


def test_collection_client_raise_if_none():
    connection_helper = BaseMongoDbHelper()

    with pytest.raises(MongoDbSetupException):
        with connection_helper.perform_collection_operation():
            pass


def test_duplicate_document_exception_has_key_and_message():
    exc = DuplicateDocumentFoundException(message="oh no!", key=1)

    assert exc.key == 1
    assert str(exc) == "oh no!"


@decorate_test_mongo_db_create()
def test_can_insert_single_document():
    """db client can insert a single document"""
    collection = "test"
    mongo_helper = BaseMongoDbHelper(collection=collection)

    test = {"_id": "only", "hello": "world"}
    mongo_helper.insert_single_document(test)

    with mongo_helper.perform_collection_operation() as cursor:
        result = cursor.find_one({"_id": "only"})

        assert result == test


@decorate_test_mongo_db_with_seed(mongo_seed_files=get_document_seed_files())
def test_can_populate_db_with_seed():
    """DB can be seeded before execution"""
    collection = "test"
    mongo_helper = BaseMongoDbHelper(collection=collection)

    with mongo_helper.perform_collection_operation() as cursor:
        result = cursor.find()

        all_results = list(result)
        assert len(all_results) == 29


@decorate_test_mongo_db_with_seed(mongo_seed_files=[])
def test_seed_with_empty_list_will_not_break():
    """Seed can be empty for testing"""
    collection = "test"
    mongo_helper = BaseMongoDbHelper(collection=collection)

    with mongo_helper.perform_collection_operation() as cursor:
        result = cursor.find()

        all_results = list(result)
        assert len(all_results) == 0
