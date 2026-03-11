import sqlite3
from app.backend.auth import verify_password, get_password_hash
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In app/backend/db_service.py
class HRDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Pointing to the root 'data' folder
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            self.db_path = os.path.join(base_dir, "data", "hr_database.db")
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        else:
            self.db_path = db_path
        
        logger.info(f"Connecting to database at: {self.db_path}")
        # Ensure users table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('hr','employee')),
                employee_id INTEGER
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                username TEXT,
                message TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        conn.close()
        if not os.path.exists(self.db_path):
            logger.error(f"Database file NOT FOUND at: {self.db_path}")

    def _get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def get_employee(self, employee_id=None, email=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if employee_id:
            cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
        elif email:
            cursor.execute("SELECT * FROM employees WHERE email = ?", (email,))
        else:
            return None
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_leave_balance(self, employee_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leave_balance WHERE employee_id = ?", (employee_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_payroll(self, employee_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM payroll WHERE employee_id = ? ORDER BY year DESC, month DESC LIMIT 1", (employee_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_policy(self, category):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM policies WHERE category LIKE ?", (f"%{category}%",))
        result = cursor.fetchall()
        conn.close()
        return [dict(row) for row in result]

    def apply_leave(self, employee_id, start_date, end_date, leave_type="Annual"):
        from datetime import datetime
        try:
            # Calculate days requested
            d1 = datetime.strptime(start_date, "%Y-%m-%d")
            d2 = datetime.strptime(end_date, "%Y-%m-%d")
            days_requested = (d2 - d1).days + 1
            if days_requested <= 0: return False, "Invalid date range."

            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Fetch current balance
            cursor.execute("SELECT * FROM leave_balance WHERE employee_id = ?", (employee_id,))
            balance_row = cursor.fetchone()
            
            if not balance_row:
                conn.close()
                return False, "Leave balance record not found."
                
            balance_dict = dict(balance_row)
            
            # Map leave type to column name
            col_map = {"Annual": "annual", "Medical": "sick", "Personal": "casual"}
            target_col = col_map.get(leave_type, "annual") # fallback
            
            available_days = balance_dict.get(target_col, 0)
            
            # STRICT VALIDATION: Prevent Negative Balance
            if days_requested > available_days:
                conn.close()
                return False, f"Insufficient balance. You requested {days_requested} days, but only have {available_days} days of {leave_type} leave."

            # If validation passes, process the request
            cursor.execute(
                "INSERT INTO leave_requests (employee_id, start_date, end_date, leave_type, status) VALUES (?, ?, ?, ?, ?)",
                (employee_id, start_date, end_date, leave_type, "Approved")
            )
            
            # Update balance
            cursor.execute(f"UPDATE leave_balance SET {target_col} = {target_col} - ? WHERE employee_id = ?", (days_requested, employee_id))
            
            conn.commit()
            conn.close()
            logger.info(f"Approved {days_requested} days of {leave_type} leave for employee {employee_id}")
            return True, "Your leave request has been successfully processed."
        except Exception as e:
            logger.error(f"Error applying leave: {e}")
            return False, f"System error occurred: {str(e)}"

    def create_user(self, username: str, password: str, role: str = "employee") -> bool:
        """Create a new user with hashed password.
        Returns True on success, False if username already exists.
        """
        try:
            password_hash = get_password_hash(password)
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            conn.commit()
            conn.close()
            logger.info(f"Created new user {username} with role {role}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"User {username} already exists")
            return False
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False

    def get_user_by_username(self, username: str) -> dict:
        """Fetch user by username."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, role, employee_id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def verify_user(self, username: str, password: str) -> dict:
        """Verify credentials and return user dict if valid, else None."""
        user = self.get_user_by_username(username)
        if user and verify_password(password, user["password_hash"]):
            return user
        return None

    def add_employee(self, data: dict):
        """Add a new employee and their associated records."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 1. Insert into employees
            cursor.execute("""
                INSERT INTO employees (name, email, department, position, salary, join_date, performance_rating, leave_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['name'], data['email'], data['department'],
                data['position'], data['salary'], data['join_date'],
                data.get('performance_rating', 'Satisfactory'),
                data.get('leave_status', 'In Office')
            ))
            emp_id = cursor.lastrowid
            
            # 2. Add default leave balance (20 annual, 10 sick)
            cursor.execute("INSERT INTO leave_balance (employee_id, annual, sick) VALUES (?, ?, ?)", (emp_id, 20, 10))
            
            conn.commit()
            conn.close()
            logger.info(f"Successfully added employee {data['name']} (ID: {emp_id})")
            return emp_id
        except Exception as e:
            logger.error(f"Error adding employee: {e}")
            return None

    def update_employee(self, emp_id: int, data: dict):
        """Update employee details."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            fields = []
            values = []
            for k, v in data.items():
                fields.append(f"{k} = ?")
                values.append(v)
            
            values.append(emp_id)
            query = f"UPDATE employees SET {', '.join(fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error updating employee {emp_id}: {e}")
            return False

    def delete_employee(self, emp_id: int):
        """Delete an employee and their associated metadata."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Clean up child tables
            cursor.execute("DELETE FROM leave_balance WHERE employee_id = ?", (emp_id,))
            cursor.execute("DELETE FROM leave_requests WHERE employee_id = ?", (emp_id,))
            cursor.execute("DELETE FROM chat_logs WHERE employee_id = ?", (emp_id,))
            cursor.execute("DELETE FROM payroll WHERE employee_id = ?", (emp_id,))
            
            # Delete employee
            cursor.execute("DELETE FROM employees WHERE id = ?", (emp_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting employee {emp_id}: {e}")
            return False

    def get_all_employees(self):
        """Return list of all employee records."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def log_chat(self, employee_id, username, message, response):
        """Log a chat interaction for HR review."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_logs (employee_id, username, message, response) VALUES (?, ?, ?, ?)",
                (employee_id, username, message, response)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging chat: {e}")
            return False

    def get_recent_employee_chats(self, employee_id: int, limit: int = 3):
        """Retrieve recent chat interactions for a specific employee to build context."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT message, response FROM chat_logs WHERE employee_id = ? ORDER BY timestamp DESC LIMIT ?", (employee_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [{"message": row["message"], "response": row["response"]} for row in rows]

    def get_chat_logs(self):
        """Retrieve all chat logs for HR review."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
