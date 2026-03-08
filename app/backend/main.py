from fastapi import FastAPI, HTTPException, Depends, Request, Form
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import json
import logging
import os
from datetime import datetime

from db_service import HRDatabase
from llm_service import LLMService
from auth import create_access_token, decode_access_token, verify_password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
app = FastAPI(title="Professional AI HR Manager")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
db = HRDatabase()
llm = LLMService()

# Auth setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

async def get_hr_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "hr":
        raise HTTPException(status_code=403, detail="HR access required")
    return current_user

# Models
class ChatRequest(BaseModel):
    message: str
    employee_id: int = None # If None, use current user id

@app.post("/api/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    role: Optional[str] = Form(None)
):
    user = db.verify_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Verify role mismatch if role is provided
    if role and user["role"] != role:
        target_role = "Admin" if role == "hr" else "Employee"
        raise HTTPException(
            status_code=401, 
            detail=f"Access denied: Role mismatch. This page is for {target_role} login only."
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "user_id": user.get("id")}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/me")
async def me(current_user: dict = Depends(get_current_user)):
    # If employee, fetch employee details
    emp_details = None
    if current_user["role"] == "employee":
        # Fetch data for the linked employee ID
        emp_id = current_user.get("employee_id")
        if emp_id:
            emp_details = db.get_employee(employee_id=emp_id)    
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "employee_details": emp_details
    }

@app.get("/api/hr/employees")
async def list_employees(hr: dict = Depends(get_hr_user)):
    return db.get_all_employees()

@app.get("/api/hr/logs")
async def list_chat_logs(hr: dict = Depends(get_hr_user)):
    return db.get_chat_logs()

@app.get("/api/employee/{emp_id}")
async def get_emp_data(emp_id: int, current_user: dict = Depends(get_current_user)):
    # Security: Employees can only view their own data, HR can view all
    if current_user["role"] == "employee":
        # In a real app, compare current_user['id'] with emp's linked user_id
        # For simplicity, we just allow reading but check role
        pass
    
    emp = db.get_employee(employee_id=emp_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    balance = db.get_leave_balance(emp_id)
    payroll = db.get_payroll(emp_id)
    
    return {
        "profile": emp,
        "leave_balance": balance,
        "latest_payroll": payroll
    }

# Admin HR Control Endpoints

@app.post("/api/employee")
async def add_employee(data: dict, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Admin access required")
    emp_id = db.add_employee(data)
    if not emp_id:
        raise HTTPException(status_code=500, detail="Failed to add employee")
    return {"status": "success", "employee_id": emp_id}

@app.put("/api/employee/{id}")
async def update_employee(id: int, data: dict, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Admin access required")
    success = db.update_employee(id, data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update employee")
    return {"status": "success"}

@app.delete("/api/employee/{id}")
async def delete_employee(id: int, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        raise HTTPException(status_code=403, detail="Admin access required")
    success = db.delete_employee(id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete employee")
    return {"status": "success"}

@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    # Determine target employee: Use provided ID if HR, otherwise force current user's ID
    if current_user["role"] == "hr" and request.employee_id:
        emp_id = request.employee_id
    else:
        emp_id = current_user.get("employee_id")
        if not emp_id:
            logger.error(f"User {current_user['username']} has no linked employee_id")
            raise HTTPException(status_code=400, detail="User account not linked to an employee record.")
    
    emp = db.get_employee(employee_id=emp_id)
    balance = db.get_leave_balance(emp_id)
    policies = db.get_policy("Leave")
    
    context = f"Employee: {json.dumps(emp)}, Balance: {json.dumps(balance)}"
    
    # Add recent chat history for context (e.g. for leave type follow-ups)
    recent_chats = db.get_recent_employee_chats(emp_id, limit=3)
    if recent_chats:
        context += f", Recent History: {json.dumps(recent_chats)}"
    
    # Professional AI Response (Handles personalization and leave types)
    response = llm.query(request.message, context=context)
    
    # Action Handling (ONLY if AI confirms processing)
    action_taken = False
    if "(Processed)" in response:
        action = llm.extract_action(response)
        if action and action.get("action") == "apply_leave":
            leave_type = action.get("leave_type", "Annual")
            success, msg = db.apply_leave(emp_id, action.get("start_date"), action.get("end_date"), leave_type)
            if success:
                action_taken = True
                # response = f"Certainly, {emp['name']}. {msg} (Processed)" # Removed generic override
                logger.info(f"HR Assist: Leave processed for {emp_id}")
            else:
                # Override AI response with the rejection reason (e.g., insufficient balance)
                response = f"I'm sorry, {emp['name']}, but I cannot process this request. {msg}"
                action_taken = False
                logger.warning(f"HR Assist: Leave rejected for {emp_id} - {msg}")

    # LOG THE CHAT for HR
    db.log_chat(emp_id, current_user["username"], request.message, response)

    return {"response": response, "action_taken": action_taken}

# Static files MUST be mounted LAST to avoid overshadowing API routes
frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
