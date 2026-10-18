"""Authentication service for multi-user support."""

import secrets
from dataclasses import asdict
from functools import wraps
from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for, request
from pymongo.errors import DuplicateKeyError
from typing import Optional, Dict, List
from db.models import users_collection, laws_collection, LAW_TYPES, UserModel
from datetime import datetime


# OIDC clients. Authlib reads <NAME>_CLIENT_ID and <NAME>_CLIENT_SECRET from app.config
# once create_app() calls oauth.init_app().
# Google (LP-0002-01), from GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.
oauth = OAuth()
oauth.register(
    'google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email'},  # no profile: Google profile data is never stored
)
# LINE Login (LP-0009), from LINE_CLIENT_ID and LINE_CLIENT_SECRET. No discovery: LINE's
# advertises ES256, but web-login ID tokens are HS256 keyed by the channel secret,
# which create_app() installs as the only key. Scope openid alone: no profile, no email.
oauth.register(
    'line',
    authorize_url='https://access.line.me/oauth2/v2.1/authorize',
    access_token_url='https://api.line.me/oauth2/v2.1/token',
    issuer='https://access.line.me',
    id_token_signing_alg_values_supported=['HS256'],
    client_kwargs={'scope': 'openid'},
)


def get_current_user() -> Optional[str]:
    """
    Return user_id from session, or None if not logged in.
    
    Returns:
        str: user_id if logged in, None otherwise
    """
    return session.get('user_id')


def get_current_user_info() -> Optional[Dict]:
    """
    Return full user info dict from session.
    
    Returns:
        dict: User info with keys: user_id, username, display_name
        None: If not logged in
    """
    if 'user_id' not in session:
        return None
    
    return {
        'user_id': session['user_id'],
        'username': session['username'],
        'display_name': session['display_name']
    }


def login_required(f):
    """
    Decorator to require login for protected routes.
    Redirects to login page if not authenticated.
    Preserves the original URL to redirect back after login.
    
    Usage:
        @app.route('/protected')
        @login_required
        def protected_route():
            return "You are logged in"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Save the URL user was trying to access
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def new_username() -> str:
    """Random name a self-signup starts with, as both username and display_name."""
    return f"learner-{secrets.token_hex(3)}"


def find_or_create_user(claims: Dict) -> Optional[Dict]:
    """
    Return the user for verified Google ID-token claims, signing them up on first sign-in.
    An unverified or missing email gets None, and nothing is written.
    
    Args:
        claims: ID-token claims (Authlib's token['userinfo'])
        
    Returns:
        dict: Existing or newly created user document, None if the email is not verified
    """
    if claims.get('email_verified') is not True:
        return None
    email = (claims.get('email') or '').strip().lower()
    if not email:
        return None
    return _find_or_create('email', email)


def find_or_create_line_user(claims: Dict) -> Optional[Dict]:
    """
    Return the user for verified LINE ID-token claims, keyed by `sub`, signing them up on first sign-in.
    A missing or empty `sub` gets None, and nothing is written. Profile claims are ignored.
    """
    sub = claims.get('sub')
    if not isinstance(sub, str) or not sub:
        return None
    return _find_or_create('line_user_id', sub)


def _find_or_create(field: str, value: str) -> Dict:
    """Find the user whose identity `field` equals `value`, or insert one with a fresh random name."""
    user = users_collection.find_one({field: value})
    if user:
        return user

    # ponytail: 5 tries in a 16.7M-name space; a 6th clash surfaces as a 500
    for _ in range(5):
        name = new_username()
        user = asdict(UserModel(username=name, display_name=name, **{field: value}))
        try:
            users_collection.insert_one(user)  # adds user['_id']
            return user
        except DuplicateKeyError as e:
            if field in (e.details or {}).get('keyPattern', {}):
                # Lost a same-identity race: use the account that won
                return users_collection.find_one({field: value})
            # username clash: draw another name
    raise RuntimeError("No free random username after 5 tries")


def create_session(user: Dict) -> None:
    """
    Create a Flask session for the authenticated user.
    Updates last_login timestamp in database.
    
    Args:
        user: User document from database
    """
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']
    session['display_name'] = user['display_name']
    
    # Update last_login timestamp
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'last_login': datetime.utcnow()}}
    )


def clear_session() -> None:
    """Clear the current Flask session (logout)."""
    session.clear()


# ============================================================================
# Law Type Management (NEW for multi-law support)
# ============================================================================

def get_current_law_type() -> str:
    """
    Get current law type from session, default to patent-act.
    
    Returns:
        str: Current law type (e.g., "patent-act")
    """
    return session.get('current_law_type', 'patent-act')


def set_current_law_type(law_type: str) -> bool:
    """
    Set current law type in session.
    
    Args:
        law_type: Law type to set (must be valid type in LAW_TYPES)
        
    Returns:
        bool: True if successful, False if invalid law type
    """
    if law_type not in LAW_TYPES:
        return False
    
    session['current_law_type'] = law_type
    return True


def get_available_law_types() -> List[Dict]:
    """
    Get list of available law types with article counts.
    
    Returns:
        list: List of dicts with keys: type, name_zh, name_en, count_zh_tw, count_en
        
    Example:
        [
            {
                "type": "patent-act",
                "name_zh": "專利法",
                "name_en": "Patent Law",
                "count_zh_tw": 168,
                "count_en": 168
            }
        ]
    """
    result = []
    
    for law_type, info in LAW_TYPES.items():
        # Count articles for this law type
        count_zh_tw = laws_collection.count_documents({
            "type": law_type,
            "lang": "zh-TW"
        })
        count_en = laws_collection.count_documents({
            "type": law_type,
            "lang": "en"
        })
        
        result.append({
            "type": law_type,
            "name_zh": info["name_zh"],
            "name_en": info["name_en"],
            "count_zh_tw": count_zh_tw,
            "count_en": count_en,
            "total": count_zh_tw + count_en
        })
    
    return result
