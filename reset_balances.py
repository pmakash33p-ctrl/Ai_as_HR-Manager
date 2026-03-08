import sqlite3
import os

db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Reset balances for all employees to 10 sick and 20 annual
cursor.execute("UPDATE leave_balance SET sick = 10, annual = 20")
# Clear leave requests to start fresh
cursor.execute("DELETE FROM leave_requests")

conn.commit()
conn.close()
print("Leave balances reset and requests cleared.")
