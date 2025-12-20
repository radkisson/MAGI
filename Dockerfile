# Dockerfile for RIN - Rhyzomic Intelligence Node

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Install the package
RUN pip install -e .

# Create data directory
RUN mkdir -p /app/data/logs /app/data/memory /app/data/cache /app/data/vectors

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data

# Expose port for API (if running in server mode)
EXPOSE 8000

# Run RIN
CMD ["python", "-m", "rin.main"]
