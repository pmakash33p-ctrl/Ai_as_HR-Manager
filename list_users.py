import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
db_path = os.path.join(PROJECT_ROOT, "data", "hr_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT username, role FROM users")
users = cursor.fetchall()
print(f"Users found: {users}")
conn.close()
