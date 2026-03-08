# Setup Instructions: AI HR Manager

This project is an advanced, role-based AI HR Manager built with FastAPI, SQLite, and vanilla HTML/JS/CSS.

## Prerequisites
1. **Python 3.10+**: Confirm by typing `python --version` in your terminal.`
2. **VS Code Extensions**: (Optional but Recommended)
   - "Python" by Microsoft
   - "SQLite Viewer" to inspect the database.

## Installation & Setup

### Step 1: Open Project in VS Code
- Open VS Code.
- Go to `File -> Open Folder...` and select the **AI as HR Manager (Anti-G)** directory.

### Step 2: Open VS Code Terminal
- Press ``Ctrl + ` `` (backtick) or go to `Terminal -> New Terminal`.

### Step 3: Install Dependencies
Copy and paste this into your VS Code terminal:
```bash
pip install fastapi uvicorn requests python-multipart pyjwt passlib[bcrypt]
```

### Step 4: Verify Database
The database is already seeded, but if you want to reset it, run:
```bash
python data/seed_db.py
```
2. You should see a message confirming: `Database initialized with 60+ employees.`

## Running the Application

### Step 5: Start the Backend Server
In your terminal, run the following:
```bash
python app/backend/main.py
```
- You should see: `INFO: Uvicorn running on http://0.0.0.0:8000`.
- **Note**: Keep this terminal open while using the app.

### Step 6: Access the Frontend
Open your browser and go to:
**[http://localhost:8000/index.html](http://localhost:8000/index.html)**


## Default Login Credentials
- **HR Admin Portal**:
  - Username: `admin`
  - Password: `welcome123`
- **Employee Portal**:
  - Username: Use any username from [employee_credentials.txt](file:///d:/Design%20Project/AI%20as%20HR%20Manager%20(Anti-G)/employee_credentials.txt)
  - Password: `welcome123`

## Usage
- **HR Dashboard**: View system-wide metrics, monitor real-time AI conversation logs, and view detailed employee profiles.
- **Employee Dashboard**: View your personal profile, check your leave balances, and chat with the AI Concierge to apply for leave.
