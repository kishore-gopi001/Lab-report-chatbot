from database.db import get_connection

INSERT_SQL = """
INSERT INTO lab_interpretations (
    subject_id,
    hadm_id,
    test_name,
    value,
    unit,
    gender,
    status,
    reason,
    processed_time,
    reviewed
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

def insert_lab_results_bulk(records: list[tuple]):
    if not records:
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(INSERT_SQL, records)
    conn.commit()
    conn.close()


def clear_lab_interpretations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lab_interpretations")
    conn.commit()
    conn.close()


def get_abnormal_labs_by_subject(subject_id: int):
    """
    Fetch abnormal and critical labs for a patient
    to be used by the AI explanation layer.
    """

    query = """
    SELECT
        test_name,
        value,
        unit,
        status
    FROM lab_interpretations
    WHERE subject_id = ?
      AND status IN ('ABNORMAL', 'CRITICAL')
    ORDER BY processed_time DESC
    """

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, (subject_id,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "test_name": r[0],
            "value": r[1],
            "unit": r[2],
            "status": r[3]
        }
        for r in rows
    ]
