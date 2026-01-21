from app.db import get_db


def report_summary():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT status, COUNT(*) AS count
        FROM lab_interpretations
        GROUP BY status
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def report_by_lab():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            test_name,
            status,
            COUNT(DISTINCT subject_id) AS patient_count
        FROM lab_interpretations
        WHERE status IN ('ABNORMAL', 'CRITICAL')
        GROUP BY test_name, status
        ORDER BY patient_count DESC
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def report_by_gender():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            gender,
            status,
            COUNT(DISTINCT subject_id) AS patient_count
        FROM lab_interpretations
        WHERE status IN ('ABNORMAL', 'CRITICAL')
        GROUP BY gender, status
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def unreviewed_critical():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM lab_interpretations
        WHERE status = 'CRITICAL'
          AND reviewed = 0
    """)

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
