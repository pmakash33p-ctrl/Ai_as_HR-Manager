import sqlite3
import os
import sys

# Add backend to path to import auth
sys.path.append(os.path.join(os.getcwd(), 'app', 'backend'))
from auth import get_password_hash

db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

new_hash = get_password_hash("welcome123")
cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
conn.commit()
print("Admin password reset to 'welcome123'")
conn.close()
