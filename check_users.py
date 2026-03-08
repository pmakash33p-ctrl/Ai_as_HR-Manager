import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'data', 'hr_database.db')
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT username, role FROM users")
    rows = cursor.fetchall()
    print("Users in DB:")
    for row in rows:
        print(row)
    conn.close()
