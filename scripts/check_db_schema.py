from database.db import get_connection

def check_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        print("--- Tables ---")
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]}")
        
        print("\n--- Indexes ---")
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    check_db()
