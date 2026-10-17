"""Google sign-in with self-signup (LP-0002-01) and its full test list (LP-0005).

Google is never called. Discovery and the token exchange are stubbed on
oauth.google; the state and ?error= tests use real Authlib, which refuses
before any network call. The id_token tests stub only the HTTP token exchange
and sign ID tokens with a local key, so Authlib's real verification runs.
Comments name the LP-0005 case each test covers.
"""
import html
import importlib.util
import os
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/patent_act_test")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-not-for-production")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client-id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test-client-secret")

import pytest  # noqa: E402
from authlib.integrations.flask_client import OAuthError  # noqa: E402
from joserfc import jwt  # noqa: E402
from joserfc.jwk import RSAKey  # noqa: E402

from app import app as flask_app, create_app  # noqa: E402
from db.models import users_collection  # noqa: E402
from services import auth as auth_service  # noqa: E402
from services.auth import oauth  # noqa: E402

METADATA = {
    "issuer": "https://accounts.google.com",
    "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_endpoint": "https://oauth2.googleapis.com/token",
    "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
}
KEY = RSAKey.generate_key(2048, parameters={"kid": "test-key"})
OTHER_KEY = RSAKey.generate_key(2048, parameters={"kid": "test-key"})
# Authlib uses an inline "jwks" and never fetches. No jwks_uri, so a key refetch fails instead of going online.
TOKEN_METADATA = {
    **{k: v for k, v in METADATA.items() if k != "jwks_uri"},
    "id_token_signing_alg_values_supported": ["RS256"],
    "jwks": {"keys": [KEY.as_dict(private=False)]},
}
CALLBACK = "/auth/google/callback?code=test-code&state=test-state"
UNVERIFIED = "此 Google 帳號的電子郵件尚未驗證，無法登入"
FAILED = "登入失敗，請重試"


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()


@pytest.fixture
def users():
    assert users_collection.database.name.endswith("_test"), "these tests wipe users; point MONGO_URI at a *_test database"
    users_collection.delete_many({})
    yield users_collection
    users_collection.delete_many({})


@pytest.fixture
def alice(users):
    _id = users.insert_one({
        "email": "alice@example.com", "username": "alice", "display_name": "Alice Chen", "last_login": None,
    }).inserted_id
    return users.find_one({"_id": _id})


@pytest.fixture
def google(monkeypatch):
    """Stub Google's discovery document; call the result with the ID-token claims the callback should see."""
    monkeypatch.setattr(oauth.google, "load_server_metadata", lambda: METADATA)

    def returns_claims(**claims):
        monkeypatch.setattr(oauth.google, "authorize_access_token", lambda **kwargs: {"userinfo": claims})

    return returns_claims


@pytest.fixture
def id_token(monkeypatch):
    """Real ID-token verification. Call the result with the /auth/google response and claim overrides to finish sign-in."""
    monkeypatch.setattr(oauth.google, "load_server_metadata", lambda: TOKEN_METADATA)

    def finish(client, started, key=KEY, **overrides):
        params = parse_qs(urlparse(started.location).query)
        now = int(time.time())
        claims = {
            "iss": TOKEN_METADATA["issuer"], "aud": flask_app.config["GOOGLE_CLIENT_ID"], "sub": "google-sub-1",
            "email": "alice@example.com", "email_verified": True, "nonce": params["nonce"][0],
            "iat": now, "exp": now + 600, **overrides,
        }
        signed = jwt.encode({"alg": "RS256", "kid": "test-key"}, claims, key)
        token = {"access_token": "test-access-token", "token_type": "Bearer", "id_token": signed}
        monkeypatch.setattr(oauth.google, "fetch_access_token", lambda **kwargs: token)
        return client.get(f"/auth/google/callback?code=test-code&state={params['state'][0]}")

    return finish


def _session(client):
    with client.session_transaction() as session:
        return dict(session)


def _sign_in(client, google, email="alice@example.com"):
    google(email=email, email_verified=True)
    client.get(CALLBACK)


def _state(started):
    return parse_qs(urlparse(started.location).query)["state"][0]


def test_provisioned_verified_email_signs_in(client, alice, google):
    google(email="Alice@Example.com", email_verified=True, name="Someone Else")

    response = client.get(CALLBACK)

    assert response.status_code == 302
    assert response.location == "/"
    assert _session(client)["user_id"] == str(alice["_id"])
    stored = users_collection.find_one({"_id": alice["_id"]})
    assert stored["last_login"] is not None
    assert stored["display_name"] == "Alice Chen"


def test_new_email_signs_itself_up_once(client, alice, google):
    google(email="  Bob@Example.COM ", email_verified=True)

    response = client.get(CALLBACK)

    assert response.status_code == 302
    assert response.location == "/"
    bob = users_collection.find_one({"email": "bob@example.com"})
    assert re.fullmatch(r"learner-[0-9a-f]{6}", bob["username"])
    assert bob["display_name"] == bob["username"]
    assert bob["last_login"] is not None
    assert _session(client)["user_id"] == str(bob["_id"])

    client.get("/auth/logout")
    client.get(CALLBACK)

    # F44: signing in again after logout is the same account, and keeps its learner name
    assert _session(client)["user_id"] == str(bob["_id"])
    assert _session(client)["username"] == bob["username"]
    assert users_collection.count_documents({}) == 2


def test_random_name_clash_draws_another(client, alice, google, monkeypatch):
    names = iter(["alice", "learner-abc123"])
    monkeypatch.setattr(auth_service, "new_username", lambda: next(names))
    google(email="bob@example.com", email_verified=True)

    client.get(CALLBACK)

    assert users_collection.find_one({"email": "bob@example.com"})["username"] == "learner-abc123"
    assert users_collection.count_documents({}) == 2


def test_same_email_race_uses_the_winning_account(client, alice, google, monkeypatch):
    real_find_one = users_collection.find_one
    calls = []

    def find_one_missing_once(*args, **kwargs):
        calls.append(args)
        return None if len(calls) == 1 else real_find_one(*args, **kwargs)

    monkeypatch.setattr(users_collection, "find_one", find_one_missing_once)
    google(email="alice@example.com", email_verified=True)

    client.get(CALLBACK)

    assert _session(client)["user_id"] == str(alice["_id"])
    assert users_collection.count_documents({}) == 1


@pytest.mark.parametrize("claims", [
    {"email": "bob@example.com", "email_verified": False},
    {"email": "bob@example.com"},
    {"email_verified": True},
    {"email": "bob@example.com", "email_verified": "true"},  # A7: only boolean true counts
])
def test_unverified_email_is_refused(client, alice, google, claims):
    google(**claims)

    response = client.get(CALLBACK, follow_redirects=True)

    assert response.request.path == "/auth/login"
    assert UNVERIFIED in response.get_data(as_text=True)
    assert "user_id" not in _session(client)
    assert users_collection.count_documents({}) == 1


@pytest.mark.parametrize("callback", [
    CALLBACK,  # state Authlib never issued: forged or replayed
    "/auth/google/callback?error=access_denied&state=test-state",  # cancelled on Google's consent screen
])
def test_oauth_failure_is_refused(client, alice, callback):
    response = client.get(callback, follow_redirects=True)

    assert response.request.path == "/auth/login"
    assert FAILED in response.get_data(as_text=True)
    assert "user_id" not in _session(client)
    assert users_collection.find_one({"_id": alice["_id"]})["last_login"] is None


def test_username_login_is_gone(client, alice):
    response = client.post("/auth/login", data={"username": "alice"})

    assert response.status_code == 405
    assert "user_id" not in _session(client)


@pytest.mark.parametrize("next_param, landing", [
    ("https://evil.example", "/"),
    ("/laws", "/laws"),
])
def test_next_is_validated_through_the_round_trip(client, alice, google, next_param, landing):
    client.get("/auth/google", query_string={"next": next_param})
    google(email="alice@example.com", email_verified=True)

    assert client.get(CALLBACK).location == landing


def test_google_redirect_is_https_behind_heroku(client, google):
    response = client.get("/auth/google", headers={"X-Forwarded-Proto": "https"})

    assert response.location.startswith(METADATA["authorization_endpoint"])
    params = parse_qs(urlparse(response.location).query)
    assert params["redirect_uri"][0].startswith("https://")
    assert params["scope"] == ["openid email"]
    assert params["state"] and params["nonce"]


def test_add_user_lowercases_email_and_refuses_duplicates(users):
    script = Path(__file__).resolve().parent.parent / "scripts" / "add_user.py"
    spec = importlib.util.spec_from_file_location("add_user", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.add_user("  Bob@Example.COM ", "bob", "Bob Wu")
    assert users.find_one({"username": "bob"})["email"] == "bob@example.com"
    assert not module.add_user("bob@example.com", "bob2", "Bob Two")
    assert not module.add_user("not-an-email", "carol", "Carol")
    assert users.count_documents({}) == 1


# ── A. Sign-in outcomes ─────────────────────────────────────────────────────

def test_token_without_userinfo_is_refused(client, alice, google, monkeypatch):  # A6
    monkeypatch.setattr(oauth.google, "authorize_access_token", lambda **kwargs: {"access_token": "test-access-token"})

    response = client.get(CALLBACK, follow_redirects=True)

    assert UNVERIFIED in response.get_data(as_text=True)
    assert "user_id" not in _session(client)
    assert users_collection.count_documents({}) == 1


def test_five_name_clashes_fail_without_writing(client, alice, google, monkeypatch):  # A8: the known ceiling
    monkeypatch.setattr(auth_service, "new_username", lambda: "alice")
    google(email="bob@example.com", email_verified=True)

    with pytest.raises(RuntimeError, match="No free random username"):
        client.get(CALLBACK)  # TESTING propagates the error; in production it is a 500

    assert users_collection.count_documents({}) == 1


# ── B. OAuth protocol and real ID-token verification ────────────────────────

def test_signed_id_token_signs_in(client, alice, id_token):  # B9
    response = id_token(client, client.get("/auth/google"))

    assert response.location == "/"
    assert _session(client)["user_id"] == str(alice["_id"])


@pytest.mark.parametrize("overrides", [
    {"aud": "another-client-id"},  # B10
    {"iss": "https://evil.example"},  # B11
    {"iat": int(time.time()) - 1000, "exp": int(time.time()) - 200},  # B12: past the 120 s leeway
    {"key": OTHER_KEY},  # B13: same kid, different key
    {"nonce": "not-the-nonce-we-sent"},  # B14
])
def test_bad_id_token_is_refused(client, alice, id_token, overrides):
    response = id_token(client, client.get("/auth/google"), **overrides)

    assert response.location == "/auth/login"
    assert FAILED in client.get("/auth/login").get_data(as_text=True)
    assert "user_id" not in _session(client)
    assert users_collection.find_one({"_id": alice["_id"]})["last_login"] is None


def test_replayed_callback_is_refused(client, alice, id_token):  # B17
    started = client.get("/auth/google")
    id_token(client, started)

    response = client.get(f"/auth/google/callback?code=test-code&state={_state(started)}")

    assert response.location == "/auth/login"
    assert ("error", FAILED) in [tuple(flash) for flash in _session(client)["_flashes"]]
    assert _session(client)["user_id"] == str(alice["_id"])


def test_token_endpoint_failure_is_refused(client, alice, id_token, monkeypatch):  # B18
    started = client.get("/auth/google")

    def invalid_grant(**kwargs):
        raise OAuthError(error="invalid_grant")

    monkeypatch.setattr(oauth.google, "fetch_access_token", invalid_grant)
    response = client.get(f"/auth/google/callback?code=test-code&state={_state(started)}", follow_redirects=True)

    assert FAILED in response.get_data(as_text=True)
    assert "user_id" not in _session(client)


def test_two_tabs_each_sign_in_once(client, alice, id_token):  # B19
    first, second = client.get("/auth/google"), client.get("/auth/google")

    assert id_token(client, first).location == "/"
    assert id_token(client, second).location == "/"
    assert _session(client)["user_id"] == str(alice["_id"])


# ── C. Session and routing ──────────────────────────────────────────────────

def test_protected_page_round_trips_through_sign_in(client, alice, google):  # C22
    login = client.get(client.get("/laws").location)
    href = html.unescape(re.search(r'href="([^"]*/auth/google[^"]*)"', login.get_data(as_text=True)).group(1))

    client.get(href)
    google(email="alice@example.com", email_verified=True)

    assert urlparse(client.get(CALLBACK).location).path == "/laws"


def test_signed_in_user_skips_login_and_google(client, alice, google):  # C23
    _sign_in(client, google)

    assert client.get("/auth/login").location == "/"
    assert client.get("/auth/google").location == "/"


def test_login_next_is_used_once(client, alice, google):  # C24
    client.get("/auth/google", query_string={"next": "/laws"})
    google(email="alice@example.com", email_verified=True)

    assert client.get(CALLBACK).location == "/laws"
    assert "login_next" not in _session(client)
    assert client.get(CALLBACK).location == "/"


def test_current_user_endpoint(client, alice, google):  # C26
    assert client.get("/auth/current").status_code == 401

    _sign_in(client, google)

    assert client.get("/auth/current").get_json() == {
        "user_id": str(alice["_id"]), "username": "alice", "display_name": "Alice Chen",
    }


def test_session_cookie_flags(client, google, monkeypatch):  # C28
    cookie = client.get("/auth/google").headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie and "Secure" not in cookie

    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setattr(oauth, "app", oauth.app)  # create_app() re-points the shared oauth; restore it afterwards
    production_cookie = create_app().test_client().get("/auth/google").headers["Set-Cookie"]

    assert "Secure" in production_cookie


# ── D. Config ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("missing", ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"])
def test_startup_fails_without_google_config(monkeypatch, missing):  # D29
    monkeypatch.delenv(missing)

    with pytest.raises(RuntimeError, match=missing):
        create_app()


# ── F. Logout ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("method", ["get", "post"])
def test_logout_clears_the_user_and_says_so(client, alice, google, method):  # F38, F39
    _sign_in(client, google)

    response = getattr(client, method)("/auth/logout")

    assert response.location == "/auth/login"
    assert not {"user_id", "username", "display_name"} & set(_session(client))
    assert "已登出" in client.get("/auth/login").get_data(as_text=True)


def test_logout_clears_every_session_key(client, alice, google):  # F40
    started = client.get("/auth/google", query_string={"next": "/laws"})
    with client.session_transaction() as session:
        session["current_law_type"] = "administrative-appeal"

    client.get("/auth/logout")

    assert set(_session(client)) <= {"_flashes", "choose_account"}  # LP-0006 leaves the chooser flag
    response = client.get(f"/auth/google/callback?code=test-code&state={_state(started)}", follow_redirects=True)
    assert FAILED in response.get_data(as_text=True)
    assert "user_id" not in _session(client)


def test_after_logout_everything_needs_sign_in_again(client, alice, google):  # F41
    _sign_in(client, google)

    client.get("/auth/logout")

    assert client.get("/laws").location.startswith("/auth/login?next=")
    assert client.get("/auth/current").status_code == 401
    assert client.get("/api/quiz/available").location.startswith("/auth/login")


def test_logout_when_signed_out_is_harmless(client):  # F42
    response = client.get("/auth/logout", follow_redirects=True)

    assert response.request.path == "/auth/login"
    assert "已登出" in response.get_data(as_text=True)


def test_logout_writes_nothing(client, alice, google):  # F43
    _sign_in(client, google)
    before = users_collection.find_one({"_id": alice["_id"]})

    client.get("/auth/logout")

    assert users_collection.find_one({"_id": alice["_id"]}) == before
    assert users_collection.count_documents({}) == 1


def test_switching_accounts_after_logout(client, alice, google):  # F45
    _sign_in(client, google)
    with client.session_transaction() as session:
        session["current_law_type"] = "administrative-appeal"
    client.get("/auth/logout")

    _sign_in(client, google, "bob@example.com")

    session = _session(client)
    bob = users_collection.find_one({"email": "bob@example.com"})
    assert (session["user_id"], session["username"], session["display_name"]) == (str(bob["_id"]), bob["username"], bob["display_name"])
    assert "current_law_type" not in session


# ── LP-0006. Account chooser after logout ───────────────────────────────────

def _prompt(response):
    return parse_qs(urlparse(response.location).query).get("prompt")


def test_first_sign_in_after_logout_shows_the_account_chooser_once(client, alice, google):
    _sign_in(client, google)
    client.get("/auth/logout")

    assert _prompt(client.get("/auth/google")) == ["select_account"]
    assert _prompt(client.get("/auth/google")) is None


def test_sign_in_without_a_logout_lets_google_decide(client, google):
    assert _prompt(client.get("/auth/google")) is None
