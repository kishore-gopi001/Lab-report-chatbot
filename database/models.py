from database.db import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        hadm_id INTEGER,
        test_name TEXT,
        value REAL,
        unit TEXT,
        gender TEXT,
        status TEXT,
        reason TEXT,
        processed_time TEXT,
        reviewed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()
