import sqlite3
import os

db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT username, role FROM users")
users = cursor.fetchall()
print(f"Users found: {users}")
conn.close()
