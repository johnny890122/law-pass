"""
Unit tests for services/progress.py — REQ-012.
Uses mongomock to avoid hitting a real MongoDB instance.
"""
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from bson import ObjectId


# ---------------------------------------------------------------------------
# Helpers for building fake records
# ---------------------------------------------------------------------------

def _date_str(days_ago: int = 0) -> str:
    return (datetime.utcnow().date() - timedelta(days=days_ago)).strftime("%Y-%m-%d")


def _record(days_ago: int, questions: int, total_score: float, laws: list, mastered: int) -> dict:
    return {
        "date": _date_str(days_ago),
        "questions_answered": questions,
        "total_score": total_score,
        "laws_covered": laws,
        "mastered_count": mastered,
    }


# ---------------------------------------------------------------------------
# _fill_date_gaps
# ---------------------------------------------------------------------------

class TestFillDateGaps:
    def setup_method(self):
        from services.progress import _fill_date_gaps
        self._fn = _fill_date_gaps

    def test_7_day_range_fills_gaps(self):
        records = [
            _record(6, 5, 4.0, ["l1"], 2),
            _record(4, 3, 3.0, ["l2"], 2),
            _record(0, 2, 2.0, ["l3"], 3),
        ]
        result = self._fn(records, 7)
        assert len(result) == 7

    def test_gap_days_have_zero_values(self):
        records = [
            _record(6, 5, 5.0, [], 0),
            _record(0, 1, 1.0, [], 0),
        ]
        result = self._fn(records, 7)
        gaps = [r for r in result if r["questions_answered"] == 0]
        assert len(gaps) == 5

    def test_all_time_no_records_returns_single_today(self):
        result = self._fn([], None)
        assert len(result) == 1
        assert result[0]["date"] == _date_str(0)

    def test_avg_score_rate_computed_correctly(self):
        records = [_record(0, 4, 3.0, [], 0)]  # 3/4 * 100 = 75.0
        result = self._fn(records, 1)
        assert result[-1]["avg_score_rate"] == 75.0

    def test_zero_questions_has_none_avg(self):
        result = self._fn([], 3)
        for r in result:
            assert r["avg_score_rate"] is None


# ---------------------------------------------------------------------------
# get_daily_chart_data
# ---------------------------------------------------------------------------

class TestGetDailyChartData:
    def setup_method(self):
        from services.progress import get_daily_chart_data, _fill_date_gaps
        self._chart = get_daily_chart_data
        self._fill = _fill_date_gaps

    def test_parallel_arrays_same_length(self):
        records = self._fill([], 7)
        chart = self._chart(records)
        assert len(chart["labels"]) == len(chart["questions_data"]) == len(chart["score_data"]) == 7

    def test_score_data_values_match_records(self):
        raw = [_record(0, 2, 1.5, [], 0)]  # 75.0%
        records = self._fill(raw, 1)
        chart = self._chart(records)
        assert chart["score_data"][-1] == 75.0


# ---------------------------------------------------------------------------
# _compute_streak (via get_progress_summary)
# Tests streak logic using mocked DB calls.
# ---------------------------------------------------------------------------

class TestComputeStreak:
    def _make_streak_mock(self, days_with_activity: list[int]):
        """
        Return a mock for user_daily_stats_collection.find_one that returns a record
        for any date that is `days_ago` in days_with_activity.
        """
        active_dates = {_date_str(d) for d in days_with_activity}

        def _find_one(query, *args, **kwargs):
            date = query.get("date")
            if date in active_dates:
                return {"date": date, "questions_answered": 1}
            return None

        mock_col = MagicMock()
        mock_col.find_one.side_effect = _find_one
        return mock_col

    def test_three_consecutive_days(self):
        from services.progress import _compute_streak
        col = self._make_streak_mock([0, 1, 2])
        with patch("services.progress.user_daily_stats_collection", col):
            assert _compute_streak(ObjectId()) == 3

    def test_gap_resets_streak_to_one(self):
        from services.progress import _compute_streak
        # Today active, yesterday missing, two days ago active
        col = self._make_streak_mock([0, 2])
        with patch("services.progress.user_daily_stats_collection", col):
            assert _compute_streak(ObjectId()) == 1

    def test_no_activity_returns_zero(self):
        from services.progress import _compute_streak
        col = self._make_streak_mock([])
        with patch("services.progress.user_daily_stats_collection", col):
            assert _compute_streak(ObjectId()) == 0


# ---------------------------------------------------------------------------
# get_progress_summary — empty DB
# ---------------------------------------------------------------------------

class TestGetProgressSummaryEmpty:
    def test_all_zeros_on_empty_db(self):
        from services.progress import get_progress_summary

        empty_col = MagicMock()
        empty_col.find.return_value.sort.return_value = []
        empty_col.find_one.return_value = None
        empty_col.count_documents.return_value = 0

        with patch("services.progress.user_daily_stats_collection", empty_col), \
             patch("services.progress.user_progress_collection", empty_col):
            result = get_progress_summary(str(ObjectId()), 7)

        assert result["streak"] == 0
        assert result["questions_answered"] == 0
        assert result["avg_score_rate"] == 0.0
        assert result["laws_covered"] == 0
        assert result["mastered_count"] == 0
        assert len(result["daily_records"]) == 7


# ---------------------------------------------------------------------------
# avg_score_rate calculation
# ---------------------------------------------------------------------------

class TestAvgScoreRate:
    def test_two_answers(self):
        from services.progress import _fill_date_gaps
        # 0.5 + 1.0 = 1.5 total over 2 questions → 75%
        records = [_record(0, 2, 1.5, [], 0)]
        filled = _fill_date_gaps(records, 1)
        assert filled[-1]["avg_score_rate"] == 75.0


# ---------------------------------------------------------------------------
# laws_covered deduplication
# ---------------------------------------------------------------------------

class TestLawsCoveredDeduplication:
    def test_same_law_across_two_days_counted_once(self):
        from services.progress import get_progress_summary

        fake_records = [
            {"date": _date_str(1), "questions_answered": 1, "total_score": 1.0,
             "laws_covered": ["law_abc"], "mastered_count": 0},
            {"date": _date_str(0), "questions_answered": 1, "total_score": 1.0,
             "laws_covered": ["law_abc", "law_xyz"], "mastered_count": 1},
        ]

        find_mock = MagicMock()
        find_mock.sort.return_value = fake_records

        col = MagicMock()
        col.find.return_value = find_mock
        col.find_one.return_value = None
        col.count_documents.return_value = 0

        with patch("services.progress.user_daily_stats_collection", col), \
             patch("services.progress.user_progress_collection", col):
            result = get_progress_summary(str(ObjectId()), 7)

        assert result["laws_covered"] == 2  # law_abc + law_xyz, not 3
