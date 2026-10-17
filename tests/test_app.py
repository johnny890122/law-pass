# IMPORTANT: Set MONGO_URI *before* any app import so the Database singleton
# picks up the test database on first initialization.
import os
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/patent_act_test")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-not-for-production")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")

import pytest
from pymongo.errors import DuplicateKeyError

from app import app as flask_app
from db.models import Database


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    flask_app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False})
    yield flask_app


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session", autouse=True)
def drop_test_db():
    """Drop the throw-away test database after the entire session."""
    yield
    db = Database()
    db.client.drop_database("patent_act_test")


# ── Tests ────────────────────────────────────────────────────────────────────

class TestHealthEndpoint:
    """Smoke-test: the app boots and the /health route responds."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body_is_ok(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert data is not None
        assert data.get("status") == "ok"


class TestMongoDBConnectivity:
    """Integration tests: prove the live MongoDB container is reachable."""

    def test_ping_succeeds(self):
        """Server-side ping must succeed without raising."""
        db = Database()
        result = db.client.admin.command("ping")
        assert result.get("ok") == 1.0

    def test_write_and_read_roundtrip(self):
        """Insert a doc, read it back, assert contents match."""
        db = Database()
        col = db.db["ci_health_check"]

        inserted = col.insert_one({"source": "pytest-ci", "status": "ok"})
        assert inserted.inserted_id is not None

        doc = col.find_one({"_id": inserted.inserted_id})
        assert doc is not None
        assert doc["status"] == "ok"
        assert doc["source"] == "pytest-ci"

        col.drop()

    def test_index_creation_does_not_raise(self):
        """Database.init_db() must complete without throwing."""
        db = Database()
        db.init_db()  # idempotent; safe to call multiple times

    @pytest.mark.parametrize("collection, index_name, docs", [
        ("laws", "article_number_lang_type_unique",
         [{"article_number": "第1條", "lang": "zh-TW", "type": "patent-act"}] * 2),
        ("user_daily_stats", "user_id_date_law_type_unique",
         [{"user_id": "dup-user", "date": "2026-01-01", "law_type": "patent-act"}] * 2),
        # LP-0005 D32: users without an email block email_1 (distinct usernames get past username_1)
        ("users", "email_1",
         [{"username": "dup-no-email-a"}, {"username": "dup-no-email-b"}]),
    ])
    def test_init_db_raises_when_unique_index_blocked(self, collection, index_name, docs):
        """A duplicate key must fail startup loudly, naming the index (LP-0001-01)."""
        db = Database()
        db.init_db()
        col = db.db[collection]
        col.drop_index(index_name)
        col.insert_many([dict(doc) for doc in docs])
        try:
            with pytest.raises(DuplicateKeyError, match=index_name):
                db.init_db()
        finally:
            col.delete_many({"$or": docs})
            db.init_db()


class TestAuthRoutes:
    """Basic auth-flow smoke tests that don't require a real user."""

    def test_login_page_is_accessible(self, client):
        response = client.get("/auth/login")
        assert response.status_code == 200

    def test_unauthenticated_dashboard_redirects(self, client):
        response = client.get("/")
        # Expect a redirect to /login for unauthenticated requests.
        assert response.status_code in (301, 302)
