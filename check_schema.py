import sqlite3
import os

# Get project root directory
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "hr_database.db")

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(employees)")
    rows = cursor.fetchall()

    print("Employees table schema:\n")

    if not rows:
        print("Employees table does not exist.")
    else:
        for row in rows:
            print(row)

    conn.close()