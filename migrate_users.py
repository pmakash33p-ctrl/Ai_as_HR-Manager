import sqlite3
import os

db_path = r'd:\Design Project\AI as HR Manager (Anti-G)\data\hr_database.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'employee_id' not in columns:
            print("Adding employee_id column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN employee_id INTEGER")
            # Update John Doe (ID 21)
            cursor.execute("UPDATE users SET employee_id = 21 WHERE username = 'john'")
            conn.commit()
            print("Migration successful.")
        else:
            print("employee_id column already exists.")

    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
