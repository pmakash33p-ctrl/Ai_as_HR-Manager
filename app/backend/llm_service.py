import json
import re
from datetime import datetime, timedelta

class LLMService:
    def __init__(self, model=None, url=None):
        pass

    def parse_natural_dates(self, text):
        """Extracts dates like 'March 3', 'tomorrow', or 'coming Wednesday' and returns as YYYY-MM-DD."""
        months = {
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
            'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }
        weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6,
            'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6
        }
        
        # Reference date from system time (2026-03-05)
        # However, to be robust for any execution time:
        today = datetime.now()
        # For this project context, if it's 2025, we might want to force 2026 as per previous logic
        # but let's use the actual current date if it's 2026 already.
        # Based on logs, today is 2026-03-05.
        
        results = []
        text_low = text.lower()

        # 1. Look for YYYY-MM-DD
        iso_pattern = r"(\d{4}-\d{2}-\d{2})"
        iso_dates = re.findall(iso_pattern, text)
        if iso_dates:
            return iso_dates

        # 2. Relative terms: today, tomorrow
        if "today" in text_low:
            results.append(today.strftime("%Y-%m-%d"))
        if "tomorrow" in text_low or "tommorow" in text_low:
            tomorrow = today + timedelta(days=1)
            results.append(tomorrow.strftime("%Y-%m-%d"))

        # 3. Weekdays (e.g., "coming Wednesday", "on Friday")
        for day_name, day_idx in weekdays.items():
            if re.search(rf"\b{day_name}\b", text_low):
                days_ahead = day_idx - today.weekday()
                if days_ahead <= 0: # Target day already happened this week or is today
                    days_ahead += 7
                target_date = today + timedelta(days=days_ahead)
                results.append(target_date.strftime("%Y-%m-%d"))

        # 4. Look for Month Day (e.g., March 3)
        month_names = "|".join(months.keys())
        pattern = rf"\b({month_names})[a-z]*\s+0?(\d{{1,2}})(?:st|nd|rd|th)?\b|\b0?(\d{{1,2}})(?:st|nd|rd|th)?\s+({month_names})[a-z]*\b"
        matches = re.findall(pattern, text_low)
        
        for m in matches:
            if m[0]: # Month Day
                month_str = months[m[0][:3]]
                day_str = m[1].zfill(2)
            else: # Day Month
                month_str = months[m[3][:3]]
                day_str = m[2].zfill(2)
            
            # Assume 2026 for this project context
            results.append(f"2026-{month_str}-{day_str}")

        # 5. Numeric dates: MM/DD or MM-DD or MM/DD/YYYY
        # full pattern: \b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])(?:[/-](\d{2,4}))?\b
        numeric_pattern = r"\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12][0-9]|3[01])(?:[/-](\d{2,4}))?\b"
        num_matches = re.findall(numeric_pattern, text_low)
        for nm in num_matches:
            m_str = nm[0].zfill(2)
            d_str = nm[1].zfill(2)
            y_str = nm[2]
            if not y_str:
                y_str = "2026"
            elif len(y_str) == 2:
                y_str = "20" + y_str
            results.append(f"{y_str}-{m_str}-{d_str}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_results = []
        for r in results:
            if r not in seen:
                unique_results.append(r)
                seen.add(r)
        
        return unique_results

    def query(self, prompt, context=""):
        """Professional Rule-based HR Assistance with Deep Debugging"""
        p_low = prompt.lower()
        
        print(f"DEBUG: Input Context: '{context}'")
        print(f"DEBUG: Input Prompt: '{prompt}'")

        # Robust name extraction from context
        name = "valued employee"
        emp_data = {}
        try:
            if "Employee: " in context:
                # Format: "Employee: {"id": 21, "name": "Daniel Hernandez", ...}, Balance: ..."
                parts = context.split(", Balance: ")
                emp_part = parts[0].replace("Employee: ", "").strip()
                emp_data = json.loads(emp_part)
                # Check for 'full_name' first (used in DB), then fallback to 'name'
                name = emp_data.get("full_name") or emp_data.get("name", "valued employee")
                print(f"DEBUG: Extracted Name: '{name}'")
            else:
                print("DEBUG: 'Employee: ' tag NOT found in context")
        except Exception as e:
            print(f"DEBUG: Name extraction error: {e}")

        # Move dates extraction up so it can be used in triggers
        dates = self.parse_natural_dates(prompt)

        # 1. Leave Balance Queries
        if "balance" in p_low or "how many days" in p_low or "leave left" in p_low:
            try:
                bal_part = context.split("Balance: ")[1].split(", Rules:")[0].strip()
                bal = json.loads(bal_part)
                return f"Hello {name}, according to our records, you currently have {bal.get('annual', 0)} days of annual leave and {bal.get('sick', 0)} days of medical leave remaining. Is there anything else you would like to know?"
            except Exception as e:
                print(f"DEBUG: Balance parsing error: {e}")
                return f"Hello {name}, I've reviewed your records. You have an active leave balance available. Would you like me to process a specific request for you?"

        # 2. Leave Application
        if dates or any(word in p_low for word in ["apply", "request", "take", "leave", "medical", "sick", "annual", "vacation", "personal"]):
            # dates = self.parse_natural_dates(prompt) # Already extracted above
            
            # 1. First, check if a leave type is mentioned in the current prompt
            leave_type = None
            if any(word in p_low for word in ["medical", "sick", "doctor", "health"]): leave_type = "Medical"
            elif any(word in p_low for word in ["annual", "vacation", "holiday", "trip"]): leave_type = "Annual"
            elif any(word in p_low for word in ["personal", "family", "urgent"]): leave_type = "Personal"

            # 2. If no dates in prompt, BUT a leave type WAS provided, check recent history for dates
            if len(dates) < 2 and leave_type and "Recent History:" in context:
                try:
                    hist_str = context.split("Recent History: ")[1]
                    hist = json.loads(hist_str)
                    for chat in hist:
                        past_dates = self.parse_natural_dates(chat.get("message", ""))
                        if len(past_dates) >= 1:
                            if len(past_dates) == 1:
                                dates = [past_dates[0], past_dates[0]]
                            else:
                                dates = past_dates
                            print(f"DEBUG: Found dates in history: {dates}")
                            break
                except Exception as e:
                    print(f"DEBUG: History parsing error: {e}")

            print(f"DEBUG: Dates found: {dates}, Leave Type: {leave_type}")

            if len(dates) >= 1:
                # Support single-day leave (start and end are the same)
                if len(dates) == 1:
                    print(f"DEBUG: Single date found, treating as one-day leave: {dates[0]}")
                    dates = [dates[0], dates[0]]
                
                # Determine if dates came from history
                from_history = False
                if self.parse_natural_dates(prompt) == []:
                    from_history = True
                
                if not leave_type:
                    print("DEBUG: Asking for leave type clarification")
                    context_msg = "based on our previous discussion" if from_history else "for the date mentioned"
                    if dates[0] == dates[1]:
                        return f"I can certainly help you with that, {name}. I've noted the date {dates[0]} {context_msg}. Could you please specify if this is for **Medical**, **Annual**, or **Personal** leave so I can finalize the request?"
                    return f"I can certainly help you with that, {name}. I've noted the dates from {dates[0]} to {dates[1]} {context_msg}. Could you please specify if this is for **Medical**, **Annual**, or **Personal** leave so I can finalize the request?"
                
                print(f"DEBUG: Processing {leave_type} leave from {dates[0]} to {dates[1]}")
                # We include the ISO dates in the confirmation message so the action extractor can pick it up
                if dates[0] == dates[1]:
                    confirmation = f"Certainly, {name}. I have initiated your **{leave_type}** leave request for **{dates[0]}**"
                else:
                    confirmation = f"Certainly, {name}. I have initiated your **{leave_type}** leave request for the period **{dates[0]} to {dates[1]}**"
                if from_history:
                    confirmation += " based on our previous interaction"
                return confirmation + ". This has been logged in the system for processing. (Processed) Your leave has been recorded."
            
            if leave_type:
                return f"I've noted that you'd like to take **{leave_type}** leave, {name}. Could you please specify the start and end dates in YYYY-MM-DD format so I can process this for you?"
            
            return f"I can certainly help you apply for leave, {name}. Could you please specify the start and end dates (YYYY-MM-DD) and whether this is for **Medical**, **Annual**, or **Personal** reasons?"

        # 3. Salary / Payroll
        if any(word in p_low for word in ["salary", "pay", "money", "compensation"]):
            return f"Greetings {name}, your payroll information is processed securely. You can view your latest payslip details in your dashboard sidebar. For {name} in the {emp_data.get('department', 'company')} team, we ensure all transactions are transparent."

        # 4. Gratitude / Appreciation
        appreciation_keywords = ["thank you", "thanks", "great", "appreciate", "thx", "helpful", "awesome", "perfect", "good job"]
        if any(word in p_low for word in appreciation_keywords):
            print(f"DEBUG: Appreciation detected for {name}")
            return f"You are very welcome, {name}! It's a pleasure to assist you. I'm glad I could help with your request. Is there anything else you'd like to check or apply for today?"

        # Default Professional Fallback
        return f"Greetings {name}, I am your AI HR Assistant. It's a pleasure to assist a member of our {emp_data.get('department', 'team')}. How may I assist you today with leave applications, payroll reviews, or general company information?"

    def extract_action(self, response_text):
        action_data = None
        dates = self.parse_natural_dates(response_text)
        
        # Extract leave type from the AI's confirmation message
        leave_type = "Annual" # default
        low_res = response_text.lower()
        if "medical" in low_res or "sick" in low_res: leave_type = "Medical"
        elif "personal" in low_res: leave_type = "Personal"

        # Only extract if the AI confirmed with (Processed) or "initiated"
        is_confirmed = "(Processed)" in response_text or "initiated" in response_text.lower()
        
        if is_confirmed and len(dates) >= 1 and ("leave" in response_text.lower() or "recorded" in response_text.lower()):
            # Handle both single date and date range
            start_date = dates[0]
            end_date = dates[1] if len(dates) >= 2 else dates[0]
            action_data = {
                "action": "apply_leave",
                "start_date": start_date,
                "end_date": end_date,
                "leave_type": leave_type
            }
        
        return action_data
