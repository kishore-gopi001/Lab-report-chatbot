import sqlite3
from typing import Any
from contextlib import contextmanager

from database.db import get_connection
from database.repository import (
    get_abnormal_labs_by_subject,
    get_all_labs_by_subject
)
from ai.llm_client import generate_ai_summary


# ---------------- CONSTANTS ----------------

DISCLAIMER = (
    "This explanation is for informational purposes only. "
    "It does not provide medical diagnosis or treatment advice."
)


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


# ---------------- HUMAN-LIKE CHAT INTERACTION ----------------

def answer_user_question(subject_id: int, question: str) -> str:
    """
    Rule-based, safe, DB-grounded chatbot
    """

    question = question.lower().strip()
    labs = get_all_labs_by_subject(subject_id)

    if not labs:
        return "No laboratory data is available for this subject."

    # ---------------- NORMALIZATION ----------------

    aliases = {
        "hb": "hemoglobin",
        "platelet": "platelets",
        "wbc": "wbc",
        "rbc": "rbc",
    }
    for k, v in aliases.items():
        question = question.replace(k, v)

    # ---------------- PRE-COMPUTE ----------------

    test_names = sorted({l["test_name"] for l in labs})

    abnormal_tests = sorted({
        l["test_name"]
        for l in labs
        if l["status"] in ("ABNORMAL", "CRITICAL")
    })

    critical_labs = {}
    for l in labs:
        if l["status"] == "CRITICAL":
            # keep latest per test
            critical_labs[l["test_name"]] = f"{l['value']} {l['unit']}"

    lab_lookup = {
        l["test_name"].lower(): l
        for l in labs
    }

    # =====================================================
    # 🔥 INTENT 1 — LIST TESTS (HIGHEST PRIORITY)
    # =====================================================
    if any(
        phrase in question
        for phrase in (
            "what tests",
            "which tests",
            "what labs",
            "which labs",
            "tests were done",
            "labs were done",
            "list tests",
            "list labs",
            "show tests",
            "show labs",
            "all tests",
            "all labs",
        )
    ):
        return (
            "The following laboratory tests were performed:\n- "
            + "\n- ".join(test_names)
        )

    # =====================================================
    # INTENT 2 — CRITICAL
    # =====================================================
    if "critical" in question:
        if not critical_labs:
            return "No critical lab values were detected."

        return (
            "Critical lab results:\n"
            + "\n".join(f"- {k}: {v}" for k, v in critical_labs.items())
        )

    # =====================================================
    # INTENT 3 — ABNORMAL
    # =====================================================
    if "abnormal" in question:
        if not abnormal_tests:
            return "All lab values are within expected ranges."

        return (
            "The abnormal lab tests include:\n- "
            + "\n- ".join(abnormal_tests)
        )

    # =====================================================
    # INTENT 4 — SPECIFIC TEST
    # =====================================================
    for name_lower, lab in lab_lookup.items():
        if name_lower in question:
            return (
                f"{lab['test_name']} result:\n"
                f"- Value: {lab['value']} {lab['unit']}\n"
                f"- Status: {lab['status']}\n"
                f"- Interpretation note: {lab['reason']}"
            )

    # =====================================================
    # OUT OF SCOPE
    # =====================================================
    return (
        "I can help explain laboratory test results and values only. "
        "For medical diagnosis or treatment decisions, "
        "please consult a qualified healthcare professional."
    )
