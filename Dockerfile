FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python packages in two steps
COPY requirements.txt .

# First install spaCy and download model
RUN pip install --no-cache-dir spacy && \
    python -m spacy download en_core_web_sm

# Then install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set environment variables
ENV PORT=10000

# Expose port
EXPOSE ${PORT}

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]