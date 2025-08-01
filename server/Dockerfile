# Use Python 3.12 runtime (more stable for production)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for file storage
RUN mkdir -p /app/data/files

# Set environment variables for cloud deployment
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8080
ENV CLOUD_DEPLOYMENT=true
ENV USE_SUPABASE=true
ENV USER_DATA_DIR=/app/data
ENV FILES_DIR=/app/data/files

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/health || exit 1

# Expose port
EXPOSE 8080

# Use Gunicorn for production with proper timeout and worker configuration
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --timeout 0 --access-logfile - --error-logfile - main:socket_app