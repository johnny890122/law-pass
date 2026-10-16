"""
Progress Service — daily stats upsert and progress summary queries for REQ-012.
"""
import logging
from datetime import datetime, timedelta
from bson import ObjectId

from db.models import (user_daily_stats_collection, user_progress_collection,
                       user_law_stats_collection, laws_collection, questions_collection)

logger = logging.getLogger(__name__)


def upsert_daily_stats(user_id: ObjectId, law_id: str, score: float, law_type: str = 'patent-act') -> None:
    """Upsert the user_daily_stats document for today (UTC). Non-fatal on error."""
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        law_ids_for_type = [str(law['_id']) for law in laws_collection.find({'type': law_type}, {'_id': 1})]
        question_ids_for_type = [str(q['_id']) for q in questions_collection.find(
            {'law_id': {'$in': law_ids_for_type}}, {'_id': 1})]
        mastered_count = user_progress_collection.count_documents({
            "user_id": user_id,
            "question_id": {"$in": question_ids_for_type},
            "correct_streak": {"$gte": 3}
        })
        user_daily_stats_collection.update_one(
            {"user_id": user_id, "date": today, "law_type": law_type},
            {
                "$inc": {"questions_answered": 1, "total_score": score},
                "$addToSet": {"laws_covered": law_id},
                "$set": {"mastered_count": mastered_count, "law_type": law_type}
            },
            upsert=True
        )
    except Exception as e:
        logger.warning(f"upsert_daily_stats failed for user {user_id}: {e}")


def _get_legacy_totals(user_id: ObjectId, law_type: str = None) -> dict:
    """
    Compute aggregate totals from user_law_stats + user_progress for users who have
    answered questions before user_daily_stats was introduced.
    Returns the same keys used by get_progress_summary metrics (excluding streak/daily).
    """
    if law_type:
        law_ids_for_type = [str(law['_id']) for law in laws_collection.find({'type': law_type}, {'_id': 1})]
        law_stats = list(user_law_stats_collection.find({"user_id": user_id, "law_id": {"$in": law_ids_for_type}}))
        question_ids_for_type = [str(q['_id']) for q in questions_collection.find(
            {'law_id': {'$in': law_ids_for_type}}, {'_id': 1})]
        mastered_count = user_progress_collection.count_documents({
            "user_id": user_id,
            "question_id": {"$in": question_ids_for_type},
            "correct_streak": {"$gte": 3}
        })
    else:
        law_stats = list(user_law_stats_collection.find({"user_id": user_id}))
        mastered_count = user_progress_collection.count_documents({
            "user_id": user_id,
            "correct_streak": {"$gte": 3}
        })
    total_questions = sum(s.get("attempt_count", 0) for s in law_stats)
    total_score = sum(s.get("total_score", 0.0) for s in law_stats)
    avg_score_rate = round(total_score / total_questions * 100, 1) if total_questions > 0 else 0.0
    laws_covered_count = len(law_stats)
    return {
        "total_questions": total_questions,
        "avg_score_rate": avg_score_rate,
        "laws_covered_count": laws_covered_count,
        "mastered_count": mastered_count,
    }


def get_progress_summary(user_id: str, range_days: int | None, law_type: str = 'patent-act') -> dict:
    """
    Return aggregated progress metrics for the given user, time range, and law type.

    range_days=None means all-time.
    When user_daily_stats has no records yet, falls back to user_law_stats / user_progress.
    is_legacy=True signals the template to show an explanatory note.
    """
    object_user_id = ObjectId(user_id)

    query: dict = {"user_id": object_user_id, "law_type": law_type}
    if range_days is not None:
        cutoff = (datetime.utcnow() - timedelta(days=range_days - 1)).strftime("%Y-%m-%d")
        query["date"] = {"$gte": cutoff}

    records = list(
        user_daily_stats_collection.find(query).sort("date", 1)
    )

    # Aggregate totals from daily stats
    total_questions = sum(r.get("questions_answered", 0) for r in records)
    total_score_sum = sum(r.get("total_score", 0.0) for r in records)
    avg_score_rate = round(total_score_sum / total_questions * 100, 1) if total_questions > 0 else 0.0

    all_laws: set = set()
    for r in records:
        all_laws.update(r.get("laws_covered", []))
    laws_covered_count = len(all_laws)

    mastered_count = records[-1].get("mastered_count", 0) if records else 0

    # If no daily stats exist yet for this law_type, fall back to legacy collections
    is_legacy = total_questions == 0
    if is_legacy:
        legacy = _get_legacy_totals(object_user_id, law_type)
        total_questions = legacy["total_questions"]
        avg_score_rate = legacy["avg_score_rate"]
        laws_covered_count = legacy["laws_covered_count"]
        mastered_count = legacy["mastered_count"]

    streak = _compute_streak(object_user_id, law_type)
    daily_records = _fill_date_gaps(records, range_days)

    return {
        "streak": streak,
        "questions_answered": total_questions,
        "mastered_count": mastered_count,
        "avg_score_rate": avg_score_rate,
        "laws_covered": laws_covered_count,
        "daily_records": daily_records,
        "is_legacy": is_legacy,
    }


def _compute_streak(user_id: ObjectId, law_type: str = 'patent-act') -> int:
    """Count consecutive days with at least one question answered for law_type, ending today (UTC)."""
    today = datetime.utcnow().date()
    streak = 0
    cursor_date = today
    while True:
        date_str = cursor_date.strftime("%Y-%m-%d")
        record = user_daily_stats_collection.find_one(
            {"user_id": user_id, "date": date_str, "law_type": law_type, "questions_answered": {"$gt": 0}}
        )
        if not record:
            break
        streak += 1
        cursor_date -= timedelta(days=1)
    return streak


def _fill_date_gaps(records: list, range_days: int | None) -> list:
    """
    Return a continuous list of daily records from start_date to today (UTC).
    Missing days are filled with zero values.
    """
    today = datetime.utcnow().date()

    if range_days is not None:
        start_date = today - timedelta(days=range_days - 1)
    elif records:
        start_date = datetime.strptime(records[0]["date"], "%Y-%m-%d").date()
    else:
        start_date = today

    record_map = {r["date"]: r for r in records}
    filled = []
    cursor = start_date
    while cursor <= today:
        date_str = cursor.strftime("%Y-%m-%d")
        if date_str in record_map:
            r = record_map[date_str]
            q = r.get("questions_answered", 0)
            s = r.get("total_score", 0.0)
            filled.append({
                "date": date_str,
                "questions_answered": q,
                "avg_score_rate": round(s / q * 100, 1) if q > 0 else 0.0,
            })
        else:
            filled.append({"date": date_str, "questions_answered": 0, "avg_score_rate": None})
        cursor += timedelta(days=1)
    return filled


def get_daily_chart_data(daily_records: list) -> dict:
    """Extract parallel arrays suitable for Chart.js from filled daily records."""
    labels = [r["date"] for r in daily_records]
    questions_data = [r["questions_answered"] for r in daily_records]
    score_data = [r["avg_score_rate"] for r in daily_records]
    return {"labels": labels, "questions_data": questions_data, "score_data": score_data}
