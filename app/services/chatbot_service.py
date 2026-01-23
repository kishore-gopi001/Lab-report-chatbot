import sqlite3
from typing import Any
from contextlib import contextmanager

from database.db import get_connection
from database.repository import (
    get_abnormal_labs_by_subject,
    get_all_labs_by_subject
)
from ai.llm_client import generate_ai_summary
from app.vector.vector_store import search_intent   # ✅ NEW (VECTOR DB)


# ---------------- CONSTANTS ----------------

DISCLAIMER = (
    "This explanation is for informational purposes only. "
    "It does not provide medical diagnosis or treatment advice."
)

MIN_CONFIDENCE = 0.50  # 🔒 safety threshold


# ---------------- DB UTILITIES ----------------

@contextmanager
def get_pooled_connection():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def _execute_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    with get_pooled_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


# ---------------- QUERY TEMPLATES ----------------

QUERY_LABS_BY_SUBJECT = """
SELECT subject_id, hadm_id, test_name, value, unit,
       gender, status, reason
FROM lab_interpretations
WHERE subject_id = ?
ORDER BY processed_time DESC
"""

QUERY_ABNORMAL_LABS = """
SELECT subject_id, hadm_id, test_name, value, unit,
       gender, status, reason
FROM lab_interpretations
WHERE subject_id = ?
  AND status IN ('ABNORMAL', 'CRITICAL')
ORDER BY processed_time DESC
"""

QUERY_CRITICAL_LABS = """
SELECT subject_id, hadm_id, test_name, value, unit,
       gender, status, reason
FROM lab_interpretations
WHERE subject_id = ?
  AND status = 'CRITICAL'
ORDER BY processed_time DESC
"""


# ---------------- BASIC CHATBOT DATA ----------------

def get_patient_labs(subject_id: int):
    return _execute_query(QUERY_LABS_BY_SUBJECT, (subject_id,))


def get_patient_abnormal(subject_id: int):
    return _execute_query(QUERY_ABNORMAL_LABS, (subject_id,))


def get_patient_critical(subject_id: int):
    return _execute_query(QUERY_CRITICAL_LABS, (subject_id,))


# ---------------- AI SUMMARY (CACHED) ----------------

_AI_SUMMARY_CACHE: dict[int, dict] = {}


def generate_ai_summary_background(subject_id: int):
    if subject_id in _AI_SUMMARY_CACHE:
        return

    labs = get_abnormal_labs_by_subject(subject_id, limit=5)

    if not labs:
        _AI_SUMMARY_CACHE[subject_id] = {
            "subject_id": subject_id,
            "summary": "No abnormal or critical lab findings were detected.",
            "disclaimer": DISCLAIMER
        }
        return

    summary_text = generate_ai_summary(labs)

    _AI_SUMMARY_CACHE[subject_id] = {
        "subject_id": subject_id,
        "summary": summary_text.strip(),
        "disclaimer": DISCLAIMER
    }


def get_ai_summary_from_cache(subject_id: int):
    return _AI_SUMMARY_CACHE.get(subject_id)


# ---------------- HUMAN + AI CHATBOT (WITH SCORE) ----------------

def answer_user_question(subject_id: int, question: str) -> dict:
    """
    Hybrid chatbot:
    - Vector DB for intent detection + score
    - SQLite for truth
    - Safe medical behavior
    """

    question_clean = question.lower().strip()
    labs = get_all_labs_by_subject(subject_id)

    if not labs:
        return {
            "answer": "No laboratory data is available for this subject.",
            "confidence_score": 1.0
        }

    # =====================================================
    #  VECTOR SEARCH (INTENT + SCORE)
    # =====================================================

    intent_result = search_intent(question_clean)
    intent = intent_result["intent"]
    score = round(intent_result["score"], 2)

    if score < MIN_CONFIDENCE:
        return {
            "answer": (
                "I am not confident enough to answer this question "
                "based on the available laboratory data."
            ),
            "confidence_score": score
        }

    # =====================================================
    #  PRE-COMPUTE DB STRUCTURES
    # =====================================================

    test_names = sorted({l["test_name"] for l in labs})

    abnormal_tests = sorted({
        l["test_name"]
        for l in labs
        if l["status"] in ("ABNORMAL", "CRITICAL")
    })

    critical_labs = {}
    for l in labs:
        if l["status"] == "CRITICAL":
            critical_labs[l["test_name"]] = f"{l['value']} {l['unit']}"

    lab_lookup = {l["test_name"].lower(): l for l in labs}

    # =====================================================
    #  ROUTING BY INTENT
    # =====================================================

    if intent == "list_tests":
        answer = (
            "The following laboratory tests were performed:\n- "
            + "\n- ".join(test_names)
        )

    elif intent == "abnormal_labs":
        answer = (
            "The abnormal laboratory tests include:\n- "
            + "\n- ".join(abnormal_tests)
            if abnormal_tests
            else "All laboratory values are within expected ranges."
        )

    elif intent == "critical_labs":
        answer = (
            "Critical laboratory results:\n"
            + "\n".join(f"- {k}: {v}" for k, v in critical_labs.items())
            if critical_labs
            else "No critical laboratory values were detected."
        )

    elif intent == "specific_test":
        found = False
        for name, lab in lab_lookup.items():
            if name in question_clean:
                answer = (
                    f"{lab['test_name']} result:\n"
                    f"- Value: {lab['value']} {lab['unit']}\n"
                    f"- Status: {lab['status']}\n"
                    f"- Interpretation note: {lab['reason']}"
                )
                found = True
                break

        if not found:
            answer = "That laboratory test was not found for this subject."

    else:
        answer = (
            "I can help explain laboratory test results only. "
            "Please consult a clinician for diagnosis or treatment."
        )

    # =====================================================
    #  FINAL RESPONSE
    # =====================================================

    return {
        "answer": answer,
        "confidence_score": score
    }
