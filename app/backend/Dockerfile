# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory to monorepo root
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire monorepo (to access shared resources)
COPY . .

# Install Python dependencies from backend requirements
RUN pip install --no-cache-dir -r app/backend/requirements.txt

# Set working directory to backend for running the app
WORKDIR /app/app/backend

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health/')"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
