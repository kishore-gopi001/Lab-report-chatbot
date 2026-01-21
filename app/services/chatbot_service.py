from app.db import get_db


def get_patient_labs(subject_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_id, hadm_id, test_name, value, unit, gender, status, reason
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
        SELECT subject_id, hadm_id, test_name, value, unit, gender, status, reason
        FROM lab_interpretations
        WHERE subject_id = ?
          AND status IN ('ABNORMAL', 'CRITICAL')
    """, (subject_id,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_patient_critical(subject_id: int):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject_id, hadm_id, test_name, value, unit, gender, status, reason
        FROM lab_interpretations
        WHERE subject_id = ?
          AND status = 'CRITICAL'
    """, (subject_id,))

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
