FROM python:3.9-slim

WORKDIR /app

# Copy requirements and download script first
COPY requirements.txt download_models.py ./

# Install build dependencies and requirements
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libpq-dev && \
    pip install --upgrade pip && \
    pip install wheel && \
    # Install numpy first
    pip install numpy==1.23.5 && \
    # Then install other requirements
    pip install --no-cache-dir -r requirements.txt && \
    # Download models during build
    python download_models.py && \
    # Cleanup
    apt-get purge -y build-essential python3-dev && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_TIMEOUT=120
ENV GUNICORN_WORKERS=2

# Expose port
EXPOSE 5000

# Create gunicorn config
RUN echo "timeout = 120\nworkers = 2\nworker_class = 'sync'\nworker_connections = 1000" > gunicorn.conf.py

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "--bind", "0.0.0.0:5000", "app:app"]