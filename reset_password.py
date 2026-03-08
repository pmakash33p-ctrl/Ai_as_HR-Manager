import sqlite3
import os
import sys

# Add app/backend to sys.path to import auth
sys.path.append(os.path.join(os.getcwd(), 'app', 'backend'))
from auth import get_password_hash

db_path = os.path.join(os.getcwd(), 'data', 'hr_database.db')
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
    sys.exit(1)

new_password = "welcome123"
hashed_password = get_password_hash(new_password)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if john exists
cursor.execute("SELECT id FROM users WHERE username='john'")
user = cursor.fetchone()

if user:
    cursor.execute("UPDATE users SET password_hash=? WHERE username='john'", (hashed_password,))
    conn.commit()
    print("Successfully reset password for user 'john' to 'welcome123'")
else:
    print("User 'john' not found in database.")

conn.close()
