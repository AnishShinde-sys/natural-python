# Stage 1: Build CPython
FROM debian:bullseye-slim AS python-builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy CPython source code
COPY cpython-main\ 2/ /cpython/

# Build Python
WORKDIR /cpython
RUN ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make install

# Stage 2: Runtime environment
FROM debian:bullseye-slim

# Copy Python build from builder stage
COPY --from=python-builder /usr/local /usr/local

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up the backend application
WORKDIR /app
COPY . /app/

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 