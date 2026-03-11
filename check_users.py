import sqlite3
import os

# Get database path dynamically
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "data", "hr_database.db")

if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch username, role, and password hash (if exists)
    cursor.execute("SELECT username, role, password FROM users")
    rows = cursor.fetchall()
    
    if rows:
        print("Users in database:")
        for row in rows:
            print(f"Username: {row[0]}, Role: {row[1]}, Password Hash: {row[2]}")
    else:
        print("No users found in the database.")
    
    conn.close()