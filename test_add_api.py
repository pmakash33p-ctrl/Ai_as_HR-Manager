import requests
import json

base_url = "http://localhost:8000"

# 1. Login to get admin token
login_data = {
    "username": "admin",
    "password": "hr123"
}
login_resp = requests.post(f"{base_url}/api/login", data=login_data)
if login_resp.status_code != 200:
    print(f"Login failed: {login_resp.text}")
    exit()

token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. Add employee
new_emp = {
    "name": "Manual Test Employee",
    "email": "manual@test.com",
    "department": "Engineering",
    "position": "Manual Tester",
    "salary": 750000,
    "join_date": "2024-03-03"
}
add_resp = requests.post(f"{base_url}/api/employee", headers=headers, json=new_emp)
print(f"Add status: {add_resp.status_code}")
print(f"Add response: {add_resp.text}")

# 3. Verify in DB
import sqlite3
import os
db_path = os.path.join(os.getcwd(), "data", "hr_database.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM employees WHERE name='Manual Test Employee'")
row = cursor.fetchone()
if row:
    print(f"Verified in DB: ID={row[0]}, Name={row[1]}")
    # Cleanup
    cursor.execute("DELETE FROM employees WHERE id=?", (row[0],))
    cursor.execute("DELETE FROM leave_balance WHERE employee_id=?", (row[0],))
    conn.commit()
    print("Cleaned up manual test.")
else:
    print("Not found in DB")
conn.close()
