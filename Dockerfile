# Use a lightweight Python base
FROM python:3.10-slim

# Set the folder inside Docker
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your whole project
COPY . .

# Expose port 8000
EXPOSE 8000

# Start your app: Seed the DB, then Seed Users, then start the Backend
CMD python data/seed_db.py && python seed_users.py && python app/backend/main.py