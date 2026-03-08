import sqlite3
import os
import sys

# Add backend to path for auth utilities
sys.path.append(os.path.join(os.getcwd(), "app", "backend"))
from auth import get_password_hash

db_path = os.path.join(os.getcwd(), "data", "hr_database.db")

def generate_accounts():
    if not os.path.exists(db_path):
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Fetch all employees
    cursor.execute("SELECT id, name FROM employees")
    employees = cursor.fetchall()
    
    default_password = get_password_hash("welcome123")
    
    accounts_created = 0
    for emp_id, name in employees:
        # Create username: lowercase first name or full name without spaces
        username = name.split()[0].lower() if name else "user"
        
        # Check if username exists (simple deduplication)
        # In a real app we'd use name.lower().replace(' ', '.')
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
            # Skip if something is still conflicting (e.g. employee_id already assigned)
            pass

    conn.commit()
    conn.close()
    print(f"Successfully generated {accounts_created} employee accounts.")
    print("Default password for all accounts: welcome123")

if __name__ == "__main__":
    generate_accounts()
