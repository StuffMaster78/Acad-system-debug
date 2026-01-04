"""
Gunicorn Configuration for Writing System

Optimized worker configuration for production deployment.
Calculates optimal worker count based on CPU cores.
"""

import multiprocessing
import os

# Calculate optimal workers: (2 * CPU cores) + 1
# Cap at 8 to prevent excessive memory usage
cpu_count = multiprocessing.cpu_count()
workers = min((cpu_count * 2) + 1, 8)

# Bind address
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")

# Worker class: 'sync' for standard, 'gevent' for async workloads
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Worker connections (only used with gevent/eventlet)
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", 1000))

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))  # Request timeout
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", 5))  # Keep-alive timeout
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", 30))  # Graceful shutdown timeout

# Worker lifecycle management
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", 1000))  # Restart workers after N requests (prevents memory leaks)
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", 50))  # Randomize restart to prevent thundering herd

# Preload app for faster worker startup
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "True") == "True"

# Logging
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # stdout or file path
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")  # stderr or file path
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info").lower()

# Process naming
proc_name = "writing_system"

# Server mechanics
daemon = False  # Don't daemonize (let supervisor/systemd handle it)
pidfile = os.getenv("GUNICORN_PIDFILE", None)  # Optional PID file
umask = 0o007  # File permissions
tmp_upload_dir = None  # Use system temp directory

# SSL (if using Gunicorn directly with SSL)
# keyfile = None
# certfile = None

# Performance tuning
limit_request_line = 4094  # Max request line size
limit_request_fields = 100  # Max request header fields
limit_request_field_size = 8190  # Max request header field size

