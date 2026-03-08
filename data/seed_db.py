import sqlite3
import random
from datetime import datetime, timedelta

def create_database():
    conn = sqlite3.connect('data/hr_database.db')
    cursor = conn.cursor()

    # Drop tables if they exist
    cursor.execute("DROP TABLE IF EXISTS employees")
    cursor.execute("DROP TABLE IF EXISTS leave_balance")
    cursor.execute("DROP TABLE IF EXISTS leave_requests")
    cursor.execute("DROP TABLE IF EXISTS payroll")
    cursor.execute("DROP TABLE IF EXISTS policies")

    # Create tables
    cursor.execute('''
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        department TEXT,
        position TEXT,
        salary REAL,
        join_date TEXT,
        status TEXT DEFAULT 'Active',
        performance_rating TEXT,
        leave_status TEXT DEFAULT 'In Office'
    )
    ''')

    cursor.execute('''
    CREATE TABLE leave_balance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        annual INTEGER DEFAULT 20,
        sick INTEGER DEFAULT 10,
        casual INTEGER DEFAULT 5,
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        leave_type TEXT,
        status TEXT DEFAULT 'Pending',
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE payroll (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        month TEXT,
        year INTEGER,
        base_salary REAL,
        bonus REAL DEFAULT 0,
        net_pay REAL,
        status TEXT DEFAULT 'Paid',
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        content TEXT
    )
    ''')

    # Seed 60+ employees
    departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
    positions = {
        'Engineering': ['Software Engineer', 'Senior Engineer', 'DevOps', 'QA'],
        'Marketing': ['Manager', 'Specialist', 'Analyst'],
        'Sales': ['Executive', 'Manager', 'Lead'],
        'HR': ['Manager', 'Associate'],
        'Finance': ['Accountant', 'Controller'],
        'Operations': ['Coordinator', 'Manager']
    }

    names = ["John Doe", "Jane Smith", "Michael Johnson", "Emily Davis", "Chris Wilson", "Sarah Miller", 
             "David Brown", "Anna Jones", "James Taylor", "Linda Garcia", "Robert Martinez", "Barbara Robinson",
             "William Clark", "Elizabeth Rodriguez", "Joseph Lewis", "Susan Lee", "Charles Walker", "Jessica Hall",
             "Christopher Allen", "Margaret Young", "Daniel Hernandez", "Sandra King", "Matthew Wright", "Ashley Lopez",
             "Anthony Hill", "Dorothy Scott", "Mark Green", "Lisa Adams", "Donald Baker", "Nancy Gonzalez",
             "Steven Nelson", "Karen Carter", "Paul Mitchell", "Betty Perez", "Andrew Roberts", "Helen Turner",
             "Joshua Phillips", "Sandra Campbell", "Kevin Parker", "Donna Evans", "Brian Edwards", "Carol Collins",
             "Edward Stewart", "Ruth Sanchez", "Ronald Morris", "Sharon Rogers", "Timothy Reed", "Michelle Cook",
             "Jason Morgan", "Laura Bell", "Jeffrey Murphy", "Sarah Bailey", "Ryan Rivera", "Kimberly Cooper",
             "Gary Richardson", "Deborah Cox", "Nicholas Howard", "Jessica Ward", "Eric Torres", "Shirley Peterson"]

    for i, name in enumerate(names):
        dept = random.choice(departments)
        pos = random.choice(positions[dept])
        # Indian Salary Standards: ₹3,00,000 to ₹25,00,000 (Rounded to nearest 10,000)
        salary = round(random.randint(300000, 2500000), -4)
        email = f"{name.lower().replace(' ', '.')}@example.com"
        join_date = (datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d')
        
        # New metrics
        perf_ratings = ['Excellent', 'Good', 'Satisfactory', 'Needs Improvement']
        perf = random.choices(perf_ratings, weights=[20, 50, 20, 10])[0]
        status = random.choices(['In Office', 'On Leave'], weights=[90, 10])[0]
        
        cursor.execute("INSERT INTO employees (name, email, department, position, salary, join_date, performance_rating, leave_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (name, email, dept, pos, salary, join_date, perf, status))
        emp_id = cursor.lastrowid
        
        # Seed leave balance
        cursor.execute("INSERT INTO leave_balance (employee_id, annual, sick, casual) VALUES (?, ?, ?, ?)",
                       (emp_id, 20, 10, 5))
        
        # Seed payroll
        cursor.execute("INSERT INTO payroll (employee_id, month, year, base_salary, bonus, net_pay) VALUES (?, ?, ?, ?, ?, ?)",
                       (emp_id, 'February', 2026, salary/12, random.randint(0, 1000), (salary/12) + random.randint(0, 1000)))

    # Seed policies
    policies = [
        ('Leave', 'Employees are entitled to 20 days of annual leave per year. Requests should be submitted 2 weeks in advance.'),
        ('Holiday', 'The office is closed on public holidays. Extra holidays are announced by HR via email.'),
        ('Conduct', 'Maintain professional behavior at all times. Diversity and inclusion are core values.'),
        ('Remote Work', 'Flexible work options are available depending on the department role.')
    ]
    cursor.executemany("INSERT INTO policies (category, content) VALUES (?, ?)", policies)

    conn.commit()
    conn.close()
    print("Database initialized with 60+ employees.")

if __name__ == "__main__":
    create_database()
