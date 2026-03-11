import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "hr_database.db")

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, position, salary FROM employees ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()

    print("Latest 5 employees:")
    for row in rows:
        print(f"ID={row[0]}, Name={row[1]}, Position={row[2]}, Salary={row[3]}")

    conn.close()