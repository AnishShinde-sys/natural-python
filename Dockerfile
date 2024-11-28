FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

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
    python -m spacy download en_core_web_sm && \
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

# Expose port
EXPOSE 10000

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]