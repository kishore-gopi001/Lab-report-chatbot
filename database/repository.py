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
    """
    Insert multiple lab interpretation records in a single transaction.
    """
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
