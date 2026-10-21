"""
Gunicorn configuration for production deployment on Render.

This configuration is optimized for memory efficiency and performance:
- Uses gthread worker class for better RAM utilization
- 2 workers with 4 threads each (8 concurrent requests)
- Configured timeouts and graceful shutdown
"""

import multiprocessing

# Worker class: gthread is memory-efficient for I/O-bound Django apps
worker_class = 'gthread'

# Number of worker processes
# For Render's containerized environment, 2 workers balance CPU and memory
workers = 2

# Number of threads per worker
# 4 threads per worker = 8 concurrent requests total
threads = 4

# Worker connections
# Each thread can handle one connection at a time
worker_connections = 1000

# Maximum number of simultaneous client connections
max_requests = 1000

# Restart workers after this many requests to prevent memory leaks
max_requests_jitter = 50

# Timeout for silent workers (seconds)
timeout = 120

# Graceful timeout for worker shutdown (seconds)
graceful_timeout = 30

# Keepalive timeout (seconds)
keepalive = 5

# Worker lifecycle
# Prevent zombie processes
preload_app = True

# Worker reload mechanism
# Use graceful worker recycling
reload = False

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'dep_party_gunicorn'

# Bind address (Render sets PORT environment variable)
# This will be overridden by the PORT env var in production
bind = '0.0.0.0:8000'

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Environment
# Set to True in production for additional security
# This should be set via GUNICORN_RELOAD env var if needed
raw_env = [
    'DJANGO_SETTINGS_MODULE=core.settings',
]
