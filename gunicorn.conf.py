import os

# Gunicorn configuration
bind = f"0.0.0.0:{int(os.environ.get('PORT', 10000))}"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
errorlog = "-"
accesslog = "-"
capture_output = True