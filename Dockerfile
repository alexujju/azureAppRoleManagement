# --- Stage 1: Build dependencies ---
    FROM python:3.11-slim AS builder
    WORKDIR /app
    
    # Install required system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libffi-dev openssl libssl-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # Copy dependencies file and install them
    COPY requirements.txt .
    RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
    
    # --- Stage 2: Final lightweight image ---
    FROM python:3.11-slim
    WORKDIR /app
    
    # Copy installed dependencies from builder stage
    COPY --from=builder /install /usr/local
    
    # Copy application code
    COPY . .
    
    # Set environment variables
    ENV FLASK_APP=app.py
    ENV FLASK_RUN_HOST=0.0.0.0
    
    # Expose the Flask port
    EXPOSE 5000
    
    # Run Flask when the container launches
    CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
    