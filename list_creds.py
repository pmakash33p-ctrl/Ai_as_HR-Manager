import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "data", "hr_database.db")

def list_creds():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.username, e.name, e.position 
        FROM users u 
        JOIN employees e ON u.employee_id = e.id 
        WHERE u.role = 'employee'
        ORDER BY e.name
    """)
    rows = cursor.fetchall()
    
    output = "EMPLOYEE LOGIN CREDENTIALS\n"
    output += "===========================\n"
    output += "Default Password for all: welcome123\n\n"
    output += f"{'USERNAME':<20} | {'NAME':<30} | {'POSITION':<20}\n"
    output += "-" * 75 + "\n"
    
    for user, name, pos in rows:
        output += f"{user:<20} | {name:<30} | {pos:<20}\n"
    
    with open("employee_credentials.txt", "w") as f:
        f.write(output)
    
    conn.close()
    print("Generated employee_credentials.txt")

if __name__ == "__main__":
    list_creds()
