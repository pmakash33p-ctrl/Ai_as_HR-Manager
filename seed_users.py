import sqlite3
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "app", "backend"))
from app.backend.auth import get_password_hash
from app.backend.db_service import HRDatabase

def seed():
    # Initialize DB to create tables like 'users'
    db = HRDatabase()

    db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # HR Admin
    admin_hash = get_password_hash("hr123")
    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                   ("admin", admin_hash, "hr"))

    # Fetch all employees to create their accounts dynamically
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    
    default_password = get_password_hash("welcome123")
    accounts_created = 0
    
    for emp_id, name in employees:
        username = name.split()[0].lower() if name else "user"
        base_username = username
        counter = 1
        while True:
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                break
            username = f"{base_username}{counter}"
            counter += 1

        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, employee_id)
                VALUES (?, ?, ?, ?)
            """, (username, default_password, "employee", emp_id))
            accounts_created += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f"User accounts synced with database. Generated {accounts_created} dynamic employee accounts.")

if __name__ == "__main__":
    seed()