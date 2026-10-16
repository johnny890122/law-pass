"""
Question Inventory Service - Manages question pool for quiz sessions.
Question generation is admin-only via CLI scripts; users cannot trigger generation.
"""
import logging
import random
from typing import List, Dict, Literal
from db.models import questions_collection, user_progress_collection, laws_collection

logger = logging.getLogger(__name__)

class QuestionInventory:
    """Manages question inventory for quiz sessions."""

    def count_available_questions(
        self,
        question_type: Literal["MCQ", "ShortAnswer", "Mixed"],
        session_mode: Literal["new", "review", "mixed"],
        lang: str = 'zh-TW',
        user_id: str = None,
        law_type: str = None
    ) -> int:
        """
        Count available questions based on type and session mode for a specific user.
        OPTIMIZED: Batch fetch all progress records to avoid N+1 queries.

        Args:
            question_type: Type of questions to count
            session_mode: Session mode (new/review/mixed)
            lang: Language filter
            user_id: User ID for filtering progress (required for multi-user)
            law_type: Law type filter (e.g., "patent-act")

        Returns:
            Count of available questions
        """
        if law_type is None:
            from services.auth import get_current_law_type
            law_type = get_current_law_type()

        type_filter = {}
        if question_type == "MCQ":
            type_filter["type"] = "MCQ"
        elif question_type == "ShortAnswer":
            type_filter["type"] = "ShortAnswer"

        lang_filter = {}
        if lang and lang != 'both':
            lang_filter['lang'] = lang

        law_ids = [
            str(law["_id"])
            for law in laws_collection.find({"type": law_type}, {"_id": 1})
        ]

        if not law_ids:
            logger.warning(f"No laws found for type: {law_type}")
            return 0

        all_questions = list(questions_collection.find({
            **type_filter,
            "is_deleted": False,
            **lang_filter,
            "law_id": {"$in": law_ids}
        }, {"_id": 1}))

        question_ids = [str(q["_id"]) for q in all_questions]

        progress_filter = {"question_id": {"$in": question_ids}}
        if user_id:
            from bson import ObjectId as OID
            progress_filter["user_id"] = OID(user_id) if isinstance(user_id, str) else user_id

        progress_records = list(user_progress_collection.find(progress_filter))
        progress_map = {p["question_id"]: p for p in progress_records}

        if session_mode == "new":
            count = 0
            for qid in question_ids:
                progress = progress_map.get(qid)
                if not progress or (progress.get("correct_streak", 0) == 0 and not progress.get("needs_review", True)):
                    count += 1
            return count

        elif session_mode == "review":
            count = 0
            for qid in question_ids:
                progress = progress_map.get(qid)
                if progress and progress.get("needs_review", False):
                    count += 1
            return count

        else:  # mixed
            new_count = 0
            review_count = 0
            for qid in question_ids:
                progress = progress_map.get(qid)
                if not progress or (progress.get("correct_streak", 0) == 0 and not progress.get("needs_review", True)):
                    new_count += 1
                if progress and progress.get("needs_review", False):
                    review_count += 1
            return min(new_count, review_count) * 2

    def fetch_questions(
        self,
        question_type: Literal["MCQ", "ShortAnswer", "Mixed"],
        session_mode: Literal["new", "review", "mixed"],
        count: int,
        lang: str = 'zh-TW',
        user_id: str = None,
        law_type: str = None
    ) -> List[Dict]:
        """
        Fetch questions from database based on type and mode for a specific user.

        Args:
            question_type: Type of questions to fetch
            session_mode: Session mode (new/review/mixed)
            count: Number of questions to fetch
            lang: Language filter
            user_id: User ID for filtering progress (required for multi-user)
            law_type: Law type filter (e.g., "patent-act")

        Returns:
            List of question documents with full details
        """
        if law_type is None:
            from services.auth import get_current_law_type
            law_type = get_current_law_type()

        if session_mode == "mixed":
            new_count = count // 2
            review_count = count - new_count
            new_qs = self._fetch_by_mode(question_type, "new", new_count, lang, user_id, law_type)
            review_qs = self._fetch_by_mode(question_type, "review", review_count, lang, user_id, law_type)
            return new_qs + review_qs
        else:
            return self._fetch_by_mode(question_type, session_mode, count, lang, user_id, law_type)

    def _fetch_by_mode(
        self,
        question_type: Literal["MCQ", "ShortAnswer", "Mixed"],
        session_mode: Literal["new", "review"],
        count: int,
        lang: str = 'zh-TW',
        user_id: str = None,
        law_type: str = None
    ) -> List[Dict]:
        """
        Internal helper to fetch questions by specific mode for a specific user.
        OPTIMIZED: Batch fetch all progress records to avoid N+1 queries.
        """
        if law_type is None:
            from services.auth import get_current_law_type
            law_type = get_current_law_type()

        type_filter = {}
        if question_type == "MCQ":
            type_filter["type"] = "MCQ"
        elif question_type == "ShortAnswer":
            type_filter["type"] = "ShortAnswer"

        lang_filter = {}
        if lang and lang != 'both':
            lang_filter['lang'] = lang

        law_ids = [
            str(law["_id"])
            for law in laws_collection.find({"type": law_type}, {"_id": 1})
        ]

        if not law_ids:
            logger.warning(f"No laws found for type: {law_type}")
            return []

        all_questions = list(questions_collection.find({
            **type_filter,
            "is_deleted": False,
            **lang_filter,
            "law_id": {"$in": law_ids}
        }))

        question_ids = [str(q["_id"]) for q in all_questions]
        progress_filter = {"question_id": {"$in": question_ids}}
        if user_id:
            from bson import ObjectId as OID
            progress_filter["user_id"] = OID(user_id) if isinstance(user_id, str) else user_id

        progress_records = list(user_progress_collection.find(progress_filter))
        progress_map = {p["question_id"]: p for p in progress_records}

        filtered_questions = []
        for q in all_questions:
            qid = str(q["_id"])
            progress = progress_map.get(qid)

            if session_mode == "new":
                if not progress or (progress.get("correct_streak", 0) == 0 and not progress.get("needs_review", True)):
                    filtered_questions.append(q)
            elif session_mode == "review":
                if progress and progress.get("needs_review", False):
                    filtered_questions.append(q)

        if len(filtered_questions) > count:
            result = random.sample(filtered_questions, count)
        else:
            result = filtered_questions

        for q in result:
            q["_id"] = str(q["_id"])

        return result

    def get_session_questions(
        self,
        question_type: Literal["MCQ", "ShortAnswer", "Mixed"],
        session_mode: Literal["new", "review", "mixed"],
        count: int,
        lang: str = 'zh-TW',
        user_id: str = None,
        law_type: str = None
    ) -> tuple[List[Dict], bool]:
        """
        Main entry point for getting session questions.

        Rules:
        - available >= n: Return n questions directly
        - available < n: Return empty list (caller should return 400 to user)

        Args:
            question_type: Type of questions
            session_mode: Session mode (new/review/mixed)
            count: Number of questions requested (n)
            lang: Language filter
            user_id: User ID for filtering progress (required for multi-user)
            law_type: Law type filter (e.g., "patent-act")

        Returns:
            Tuple of (questions list, False).
            Empty list means insufficient questions — caller must reject the request.
        """
        if law_type is None:
            from services.auth import get_current_law_type
            law_type = get_current_law_type()

        available = self.count_available_questions(question_type, session_mode, lang, user_id, law_type)
        logger.info(f"User {user_id}: Available={available}, Requested={count}, type={question_type}, mode={session_mode}, law={law_type}")

        if available < count:
            logger.warning(f"Insufficient questions: available={available}, requested={count}")
            return [], False

        questions = self.fetch_questions(question_type, session_mode, count, lang, user_id, law_type)
        return questions, False
