"""
Frontend Routes - Serves HTML templates for the web interface.
All routes require authentication (multi-user support).
"""
from datetime import datetime
from bson import ObjectId
from flask import Blueprint, render_template, request, jsonify
from db.models import user_ui_flags_collection
from services.auth import login_required, get_current_user, get_current_law_type
from services.progress import get_progress_summary, get_daily_chart_data

frontend_bp = Blueprint('frontend', __name__)

THEMES = ('light', 'dark')


@frontend_bp.app_context_processor
def inject_theme():
    """`theme` for base.html's data-theme: the learner's stored choice, else light (LP-0004-09)."""
    user_id = get_current_user()
    flags = user_ui_flags_collection.find_one({'user_id': ObjectId(user_id)}, {'theme': 1}) if user_id else None
    return {'theme': 'dark' if flags and flags.get('theme') == 'dark' else 'light'}


@frontend_bp.route('/api/ui-flags/theme', methods=['PUT'])
def save_theme():
    """
    Save the learner's theme: JSON {"theme": "light" | "dark"} (LP-0004-09).
    Signed out gets 401 JSON, not login_required's redirect, which fetch would follow silently.
    """
    user_id = get_current_user()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json(silent=True)
    theme = data.get('theme') if isinstance(data, dict) else None
    if theme not in THEMES:
        return jsonify({'error': 'theme 必須是 light 或 dark'}), 400
    user_ui_flags_collection.update_one(
        {'user_id': ObjectId(user_id)},
        {'$set': {'theme': theme, 'updated_at': datetime.utcnow()}},
        upsert=True,
    )
    return jsonify({'theme': theme})


@frontend_bp.route('/')
@login_required
def dashboard():
    """
    S-01 Home / Dashboard
    Entry point showing the five all-time progress numbers for the current
    law type, the start block, and tips (LP-0004-07).
    Requires authentication.
    """
    summary = get_progress_summary(get_current_user(), None, get_current_law_type())
    return render_template('dashboard.html', summary=summary)


@frontend_bp.route('/laws')
@login_required
def laws_browser():
    """
    S-07 Law Article Browser
    Paginated list of all law articles with search and filter capabilities.
    Requires authentication.
    """
    return render_template('laws.html')


@frontend_bp.route('/laws/<law_id>')
@login_required
def law_detail(law_id):
    """
    S-08 Law Article Detail
    Single article view with question history and related questions.
    Requires authentication.
    """
    return render_template('law_detail.html', law_id=law_id)


@frontend_bp.route('/quiz/config')
@login_required
def quiz_config():
    """
    S-02 Quiz Config
    Configuration page for starting a new quiz session.
    Requires authentication.
    """
    return render_template('quiz_config.html')


@frontend_bp.route('/quiz/session/<session_id>')
@login_required
def quiz_session(session_id):
    """
    S-04, S-05 Quiz Session
    Question display and answer submission page.
    Handles both MCQ and Short Answer question types.
    Requires authentication.
    """
    return render_template('quiz_session.html')


@frontend_bp.route('/my-questions')
@login_required
def my_questions():
    """
    My Questions Page
    Display starred questions and wrong answers with tab switching.
    Requires authentication.
    """
    return render_template('my_questions.html')


@frontend_bp.route('/progress')
@login_required
def progress_page():
    """
    S-12 Personal Progress Page
    Shows daily-aggregated study metrics and trend charts.
    Requires authentication.
    """
    user_id = get_current_user()
    range_param = request.args.get('range', '7')
    if range_param == 'all':
        range_days = None
    else:
        try:
            range_days = int(range_param)
            if range_days not in (7, 30):
                range_days = 7
                range_param = '7'
        except ValueError:
            range_days = 7
            range_param = '7'

    law_type = get_current_law_type()
    summary = get_progress_summary(user_id, range_days, law_type)
    chart_data = get_daily_chart_data(summary['daily_records'])
    return render_template(
        'progress.html',
        summary=summary,
        chart_data=chart_data,
        selected_range=range_param
    )


@frontend_bp.route('/question-bank')
@login_required
def question_bank():
    """
    Question Bank Page
    Display all questions in the database for the current law type.
    Requires authentication.
    """
    return render_template('question_bank.html')
