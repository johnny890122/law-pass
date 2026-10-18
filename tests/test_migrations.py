"""Migration scripts in scripts/migrations/ (LP-0002-01), and init_db()'s email_1 rebuild (LP-0009)."""
import importlib.util
import os
from pathlib import Path

import pytest

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/patent_act_test")

from db.models import Database  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts" / "migrations"


def _load(filename):
    spec = importlib.util.spec_from_file_location(filename[:-3], SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def database():
    client = Database().client
    database = client["patent_act_test_migrations"]
    client.drop_database(database.name)
    yield database
    client.drop_database(database.name)


def test_remove_username_only_users(database):
    migration = _load("20261016_remove_username_only_users.py")
    legacy = database.users.insert_one({"username": "legacy", "display_name": "Legacy"}).inserted_id
    kept = database.users.insert_one({"username": "kept", "display_name": "Kept", "email": "kept@example.com"}).inserted_id
    for name in migration.PER_USER:
        database[name].insert_many([{"user_id": legacy}, {"user_id": kept}])

    expected = {**{name: 1 for name in migration.PER_USER}, "users": 1}
    assert migration.migrate(database, apply=False) == expected
    assert database.users.count_documents({}) == 2
    assert all(database[name].count_documents({}) == 2 for name in migration.PER_USER)

    assert migration.migrate(database, apply=True) == expected
    assert [user["_id"] for user in database.users.find()] == [kept]
    for name in migration.PER_USER:
        assert [doc["user_id"] for doc in database[name].find()] == [kept]

    assert migration.migrate(database, apply=True) == {**{name: 0 for name in migration.PER_USER}, "users": 0}


def test_remove_username_only_users_keeps_line_accounts(database):  # LP-0009
    migration = _load("20261016_remove_username_only_users.py")
    legacy = database.users.insert_one({"username": "legacy"}).inserted_id
    google = database.users.insert_one({"username": "g", "email": "g@example.com", "line_user_id": None}).inserted_id
    line = database.users.insert_one({"username": "l", "email": None, "line_user_id": "U-line"}).inserted_id
    for name in migration.PER_USER:
        database[name].insert_many([{"user_id": legacy}, {"user_id": google}, {"user_id": line}])

    assert migration.migrate(database, apply=True) == {**{name: 1 for name in migration.PER_USER}, "users": 1}
    assert sorted(user["_id"] for user in database.users.find()) == sorted([google, line])
    for name in migration.PER_USER:
        assert sorted(doc["user_id"] for doc in database[name].find()) == sorted([google, line])


def test_init_db_rebuilds_email_index_as_partial():  # LP-0009
    db = Database()
    users = db.users_collection
    assert db.db.name.endswith("_test"), "this test drops users; point MONGO_URI at a *_test database"
    users.drop()
    users.create_index("email", unique=True)  # the pre-LP-0009 email_1
    users.insert_many([{"username": "a", "email": "a@example.com"}, {"username": "b", "email": "b@example.com"}])
    try:
        db.init_db()

        indexes = users.index_information()
        assert indexes["email_1"]["partialFilterExpression"] == {"email": {"$type": "string"}}
        assert indexes["line_user_id_1"]["unique"]
        assert indexes["line_user_id_1"]["partialFilterExpression"] == {"line_user_id": {"$type": "string"}}
        assert users.count_documents({}) == 2

        db.init_db()

        assert users.index_information() == indexes
    finally:
        users.delete_many({})
