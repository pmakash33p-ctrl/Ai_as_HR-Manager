import sqlite3
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "app", "backend"))
from app.backend.auth import get_password_hash

def seed():
    db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # HR Admin
    admin_hash = get_password_hash("hr123")
    cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", 
                   ("admin", admin_hash, "hr"))

    # Add multiple employees from your list
    employee_list = [("john", "welcome123", 21), ("jane", "welcome123", 56), ("susan", "welcome123", 122)]
    
    for username, password, emp_id in employee_list:
        p_hash = get_password_hash(password)
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role, employee_id) VALUES (?, ?, ?, ?)", 
                       (username, p_hash, "employee", emp_id))

    conn.commit()
    conn.close()
    print("User accounts synced with database.")

if __name__ == "__main__":
    seed()