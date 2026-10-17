"""Migration scripts in scripts/migrations/ (LP-0002-01)."""
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
