# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS dependencies (if needed, e.g., for numpy, etc.)
RUN apt-get update && apt-get install -y build-essential libffi-dev curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full app
COPY . .

# Optional: copy .env file if used at build time
# COPY .env .env

# Set environment variables (you can also do this in the deployment platform)
ENV PYTHONUNBUFFERED=1

# Expose FastAPI app on port 8000
EXPOSE 8000

# Run the FastAPI app using uvicorn
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000"]