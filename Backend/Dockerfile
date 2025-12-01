# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create Python virtual environment
RUN python -m venv /venv

# Set PATH to use virtual environment
ENV PATH="/venv/bin:$PATH"

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
EXPOSE 8000

# Run database migrations and start the application
# The create_tables() function in app/database.py will also create tables if migrations haven't been run
CMD ["sh", "-c", "alembic upgrade head 2>/dev/null || echo 'No migrations to run or migration error (tables will be created by create_tables if needed)' && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

