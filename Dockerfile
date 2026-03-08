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

# Start your app
CMD ["python", "app/backend/main.py"]