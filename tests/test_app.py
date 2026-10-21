# IMPORTANT: Set MONGO_URI *before* any app import so the Database singleton
# picks up the test database on first initialization.
import os
import re
from datetime import datetime, timedelta
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/patent_act_test")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-not-for-production")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault("LINE_CLIENT_ID", "1234567890")
os.environ.setdefault("LINE_CLIENT_SECRET", "test-line-channel-secret")

import pytest
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import app as flask_app
from db.models import Database, user_daily_stats_collection, user_ui_flags_collection


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
        # Distinct usernames get past username_1. LP-0009: the identity indexes are partial,
        # so only a repeated string clashes; email-less (LINE) users no longer block email_1.
        ("users", "email_1",
         [{"username": "dup-email-a", "email": "dup@example.com"},
          {"username": "dup-email-b", "email": "dup@example.com"}]),
        ("users", "line_user_id_1",
         [{"username": "dup-line-a", "line_user_id": "U-dup"},
          {"username": "dup-line-b", "line_user_id": "U-dup"}]),
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


# ── LP-0004-07: the dashboard ledger and the dense-tabbar shell ─────────────

ZEROS = {"連續練習天數": "0", "作答題數": "0", "掌握題數": "0", "平均得分率": "0.0%", "覆蓋法條數": "0"}


def _day(days_ago):
    return (datetime.utcnow().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _stats(user_id, days_ago, questions, total_score, laws, mastered, law_type="patent-act"):
    return {"user_id": user_id, "law_type": law_type, "date": _day(days_ago), "questions_answered": questions,
            "total_score": total_score, "laws_covered": laws, "mastered_count": mastered}


def _ledger(html):
    """Map each ledger label (tags such as <wbr> stripped) to its number."""
    ledger = {}
    for block in re.findall(r'<div class="metric"[^>]*>(.*?)</div>', html, re.S):
        value = re.search(r'<span class="metric-value">(.*?)</span>', block).group(1)
        label = re.search(r'<span class="metric-label">(.*?)</span>', block).group(1)
        ledger[re.sub(r"<[^>]+>", "", label)] = value
    return ledger


@pytest.fixture
def signed_in(app):
    """A fresh client signed in as a new user id, on patent-act."""
    client = app.test_client()
    user_id = ObjectId()
    with client.session_transaction() as session:
        session["user_id"] = str(user_id)
        session["current_law_type"] = "patent-act"
    yield client, user_id
    user_daily_stats_collection.delete_many({"user_id": user_id})
    user_ui_flags_collection.delete_many({"user_id": user_id})


class TestDashboard:
    """`/` renders the five all-time numbers for the session's law type."""

    def test_shows_all_time_numbers(self, signed_in):
        client, user_id = signed_in
        user_daily_stats_collection.insert_many([
            _stats(user_id, 1, 4, 3.0, ["A1", "A2"], 2),
            _stats(user_id, 0, 8, 6.0, ["A2", "A3"], 5),
        ])
        response = client.get("/")
        assert response.status_code == 200
        assert _ledger(response.get_data(as_text=True)) == {
            "連續練習天數": "2", "作答題數": "12", "掌握題數": "5", "平均得分率": "75.0%", "覆蓋法條數": "3",
        }

    def test_other_law_type_does_not_count(self, signed_in):
        client, user_id = signed_in
        user_daily_stats_collection.insert_one(_stats(user_id, 0, 8, 6.0, ["A1"], 5, law_type="administrative-appeal"))
        response = client.get("/")
        assert response.status_code == 200
        assert _ledger(response.get_data(as_text=True)) == ZEROS

    def test_no_records_shows_zeros_without_banner(self, signed_in):
        client, _ = signed_in
        html = client.get("/").get_data(as_text=True)
        assert _ledger(html) == ZEROS
        assert "以上數據為歷史累積總計" not in html


class TestShell:
    """Every page but login renders in the dense-tabbar shell, on tokens.css, with no MUI."""

    @pytest.mark.parametrize("path, active", [
        ("/", "首頁"),
        ("/laws", "法條瀏覽"),
        ("/laws/x", "法條瀏覽"),
        ("/quiz/config", None),
        ("/quiz/session/x", None),
        ("/my-questions", None),
        ("/question-bank", "題庫"),
        ("/progress", "我的進度"),
    ])
    def test_page_renders_in_shell(self, signed_in, path, active):
        client, _ = signed_in
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'class="shell"' in html
        assert "tokens.css" in html
        assert "muicss" not in html
        for label in ("首頁", "法條瀏覽", "題庫", "我的進度"):
            assert f"<span>{label}</span>" in html
        assert re.findall(r'nav-link active"[^>]*><span>(.*?)</span>', html) == ([active] if active else [])

    def test_login_renders_on_tokens(self, app):
        response = app.test_client().get("/auth/login")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "tokens.css" in html
        assert "muicss" not in html
        assert 'class="shell"' not in html


class TestUiFlags:
    """LP-0004-09: the theme is stored per user in user_ui_flags and rendered on <html> by the server."""

    def test_save_dark_then_light(self, signed_in):
        client, user_id = signed_in
        response = client.put("/api/ui-flags/theme", json={"theme": "dark"})
        assert response.status_code == 200
        assert response.get_json() == {"theme": "dark"}
        first = user_ui_flags_collection.find_one({"user_id": user_id})
        assert first["theme"] == "dark"
        assert isinstance(first["updated_at"], datetime)

        assert client.put("/api/ui-flags/theme", json={"theme": "light"}).get_json() == {"theme": "light"}
        docs = list(user_ui_flags_collection.find({"user_id": user_id}))
        assert len(docs) == 1
        assert docs[0]["theme"] == "light"
        assert docs[0]["updated_at"] >= first["updated_at"]

    @pytest.mark.parametrize("body", [
        {"json": {"theme": "blue"}},
        {"json": {"theme": "Dark"}},
        {"json": {}},
        {"json": {"theme": 1}},
        {"json": {"theme": None}},
        {"json": ["dark"]},
        {"data": "dark", "content_type": "text/plain"},
    ])
    def test_bad_value_writes_nothing(self, signed_in, body):
        client, user_id = signed_in
        response = client.put("/api/ui-flags/theme", **body)
        assert response.status_code == 400
        assert response.get_json() == {"error": "theme 必須是 light 或 dark"}
        assert user_ui_flags_collection.count_documents({"user_id": user_id}) == 0

    def test_signed_out_gets_401(self, app):
        before = user_ui_flags_collection.count_documents({})
        response = app.test_client().put("/api/ui-flags/theme", json={"theme": "dark"})
        assert response.status_code == 401
        assert response.get_json() == {"error": "Not authenticated"}
        assert user_ui_flags_collection.count_documents({}) == before

    @pytest.mark.parametrize("path", ["/", "/progress"])
    def test_renders_the_stored_dark(self, signed_in, path):
        client, user_id = signed_in
        user_ui_flags_collection.insert_one({"user_id": user_id, "theme": "dark", "updated_at": datetime.utcnow()})
        html = client.get(path).get_data(as_text=True)
        assert '<html lang="zh-TW" data-theme="dark">' in html
        assert 'aria-pressed="true"' in html

    def test_no_document_renders_light(self, signed_in):
        client, _ = signed_in
        html = client.get("/").get_data(as_text=True)
        assert '<html lang="zh-TW" data-theme="light">' in html
        assert 'aria-pressed="false"' in html

    def test_login_stays_light(self, app):
        response = app.test_client().get("/auth/login")
        assert response.status_code == 200
        assert "data-theme" not in response.get_data(as_text=True)
