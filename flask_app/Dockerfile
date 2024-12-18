FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client python3-dev libpq-dev postgresql postgresql-contrib build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV FLASK_APP=flask_app/run.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Expose port 5001
EXPOSE 5001

# Run Flask on port 5001
CMD ["python", "flask_app/run.py"]