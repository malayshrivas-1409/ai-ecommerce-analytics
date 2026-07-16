# Base Image
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/

# Create logs folder
RUN mkdir logs

# Start application
CMD ["python", "app/generator.py"]