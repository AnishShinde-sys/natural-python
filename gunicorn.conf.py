import os

# Gunicorn configuration
port = int(os.environ.get("PORT", 5000))
bind = f"0.0.0.0:{port}"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2