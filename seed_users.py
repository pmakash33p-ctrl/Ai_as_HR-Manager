import sqlite3
import sys
import os
# Add the directory containing auth.py to sys.path
sys.path.append(os.path.join(os.getcwd(), "app", "backend"))
from auth import get_password_hash

def seed():
    # Consistent database path in the root 'data' directory
    os.makedirs("data", exist_ok=True)
    db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table if not exists (redundant but safe)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('hr','employee'))
        );
    ''')

    # Add HR user
    hr_pass = get_password_hash("hr123")
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ("admin", hr_pass, "hr"))
        print("Added HR user: admin / hr123")
    except sqlite3.IntegrityError:
        print("HR user already exists")

    # Add Employee user
    emp_pass = get_password_hash("emp123")
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                       ("john", emp_pass, "employee"))
        print("Added Employee user: john / emp123")
    except sqlite3.IntegrityError:
        print("Employee user already exists")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()
