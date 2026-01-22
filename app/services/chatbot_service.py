from app.db import get_db
from database.repository import get_abnormal_labs_by_subject
from ai.llm_client import generate_ai_summary


# ---------------- BASIC CHATBOT DATA ----------------

def get_patient_labs(subject_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_id, hadm_id, test_name, value, unit,
               gender, status, reason
        FROM lab_interpretations
        WHERE subject_id = ?
        ORDER BY processed_time DESC
    """, (subject_id,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_patient_abnormal(subject_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_id, hadm_id, test_name, value, unit,
               gender, status, reason
        FROM lab_interpretations
        WHERE subject_id = ?
          AND status IN ('ABNORMAL', 'CRITICAL')
        ORDER BY processed_time DESC
    """, (subject_id,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_patient_critical(subject_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_id, hadm_id, test_name, value, unit,
               gender, status, reason
        FROM lab_interpretations
        WHERE subject_id = ?
          AND status = 'CRITICAL'
        ORDER BY processed_time DESC
    """, (subject_id,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ---------------- NON-BLOCKING AI LAYER ----------------

_AI_SUMMARY_CACHE = {}

def generate_ai_summary_background(subject_id: int):
    if subject_id in _AI_SUMMARY_CACHE:
        return

    labs = get_abnormal_labs_by_subject(subject_id)
    labs = labs[:5]  # limit for performance

    summary = generate_ai_summary(labs)


    _AI_SUMMARY_CACHE[subject_id] = {
        "subject_id": subject_id,
        "summary": summary,
        "disclaimer": (
            "This explanation is for informational purposes only. "
            "It does not provide medical diagnosis or treatment advice."
        )
    }


def get_ai_summary_from_cache(subject_id: int):
    return _AI_SUMMARY_CACHE.get(subject_id)
