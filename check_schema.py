import sqlite3
import os

db_path = r'd:\Design Project\AI as HR Manager (Anti-G)\data\hr_database.db'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(employees)")
    rows = cursor.fetchall()
    print("Employees table schema:")
    for row in rows:
        print(row)
    conn.close()
