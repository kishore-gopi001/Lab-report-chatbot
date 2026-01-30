from database.db import get_connection

def analyze():
    conn = get_connection()
    cur = conn.cursor()
    
    print("--- Top 20 Labs with UNKNOWN Status ---")
    cur.execute("""
        SELECT test_name, COUNT(*) as c 
        FROM lab_interpretations 
        WHERE status = 'UNKNOWN' 
        GROUP BY test_name 
        ORDER BY c DESC 
        LIMIT 20
    """)
    
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} occurrences")
        
    conn.close()

if __name__ == "__main__":
    analyze_unknowns()
