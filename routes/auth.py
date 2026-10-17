"""Authentication routes for multi-user support."""

from urllib.parse import urlparse, urljoin
from authlib.common.errors import AuthlibBaseError
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from joserfc.errors import JoseError
from services.auth import oauth, find_or_create_user, create_session, clear_session, get_current_user_info


def _is_safe_redirect_url(target: str) -> bool:
    """Return True only if target is a relative URL on the same host."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def _safe_next(target: str) -> str:
    """Return target if it is a same-host URL, else the dashboard (prevents open redirect)."""
    return target if target and _is_safe_redirect_url(target) else url_for('frontend.dashboard')

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET'])
def login():
    """Show login page."""
    # If already logged in, redirect to dashboard
    if get_current_user_info():
        return redirect(url_for('frontend.dashboard'))
    
    return render_template('login.html', next_url=_safe_next(request.args.get('next', '')))


@auth_bp.route('/google', methods=['GET'])
def google_login():
    """Start Google sign-in: remember the validated 'next', then redirect to Google."""
    if get_current_user_info():
        return redirect(url_for('frontend.dashboard'))
    session['login_next'] = _safe_next(request.args.get('next', ''))
    # After an intentional logout, let the learner pick any Google account; otherwise Google may sign in silently
    prompt = {'prompt': 'select_account'} if session.pop('choose_account', False) else {}
    return oauth.google.authorize_redirect(url_for('auth.google_callback', _external=True), **prompt)


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    """
    Finish Google sign-in. Authlib checks state, exchanges the code, and verifies
    the ID token. Any verified email gets a session, and a first sign-in creates the account.
    A refusal writes nothing.
    """
    next_url = _safe_next(session.pop('login_next', ''))
    try:
        token = oauth.google.authorize_access_token()
    except (AuthlibBaseError, JoseError):
        # Cancel (?error=), missing or replayed state, token exchange or ID-token verification failure
        flash('登入失敗，請重試', 'error')
        return redirect(url_for('auth.login'))

    user = find_or_create_user(token.get('userinfo') or {})
    if not user:
        flash('此 Google 帳號的電子郵件尚未驗證，無法登入', 'error')
        return redirect(url_for('auth.login'))

    create_session(user)
    return redirect(next_url)


@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Clear session and redirect to login page. The next sign-in shows Google's account chooser."""
    clear_session()
    session['choose_account'] = True  # one-time flag, popped by google_login (LP-0006)
    flash('已登出', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/current', methods=['GET'])
def current():
    """
    Return current logged-in user info as JSON.
    Useful for frontend checks.
    
    Returns:
        JSON: { user_id, username, display_name } if logged in
        JSON: { error: "Not authenticated" } with 401 if not logged in
    """
    user_info = get_current_user_info()
    
    if not user_info:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(user_info)
