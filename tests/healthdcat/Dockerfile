FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy test files
COPY . /app/tests/

# Create reports directory
RUN mkdir -p /app/reports

# Set environment variables
ENV PYTHONPATH=/app
ENV CKAN_URL=http://ckan:5000

# Default command
CMD ["python", "-m", "pytest", "/app/tests/test_healthdcat_e2e.py", "-v"]