import requests
import json
import time
import os

def test_system():
    url = "http://localhost:8000"
    emp_id = 1
    
    print(f"--- AI HR Manager Health Check ---")
    
    try:
        # 1. Check if server is up
        print("1. Checking server status...")
        res = requests.get(url)
        print(f"   Status: {res.status_code} - {res.json()}")
        
        # 2. Fetch Employee Data
        print(f"2. Fetching stats for Employee {emp_id}...")
        res = requests.get(f"{url}/api/employee/{emp_id}")
        data = res.json()
        initial_balance = data['leave_balance']['annual']
        print(f"   Name: {data['profile']['name']}")
        print(f"   Initial Balance: {initial_balance} days")
        
        # 3. Test AI Query (Intent detection)
        print("3. Testing AI Chat (Leave Application)...")
        payload = {
            "message": "I want to apply for 2 days of leave from 2026-06-01 to 2026-06-02",
            "employee_id": emp_id
        }
        res = requests.post(f"{url}/api/chat", json=payload)
        response_data = res.json()
        print(f"   AI Response: {response_data['response']}")
        print(f"   Action Taken: {response_data['action_taken']}")
        
        # 4. Verify Database Update
        print("4. Verifying balance deduction...")
        time.sleep(1) # Wait for DB commit
        res = requests.get(f"{url}/api/employee/{emp_id}")
        new_balance = res.json()['leave_balance']['annual']
        print(f"   New Balance: {new_balance} days")
        
        if new_balance == initial_balance - 2:
            print("✅ SUCCESS: System is fully operational!")
        else:
            print(f"❌ ISSUE: Expected {initial_balance - 2} days, but got {new_balance}")
            
    except Exception as e:
        print(f"🔴 CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    test_system()
