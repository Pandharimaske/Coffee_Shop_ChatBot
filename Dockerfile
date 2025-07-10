# Use an official Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]