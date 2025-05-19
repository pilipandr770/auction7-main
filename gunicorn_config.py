import os
import multiprocessing

# Bind host and port (use 5050 for development)
bind = "0.0.0.0:" + os.environ.get("PORT", "5050")

# Workers and threads - detect CPU count but safer values for Windows
workers = 2  # Simplified for Windows
threads = 2
worker_class = "gevent"  # Better for handling asynchronous requests

# Timeouts - increase to prevent 502 errors
timeout = 300  # Increased timeout for handling longer requests
keepalive = 120

# Graceful shutdown and restart
graceful_timeout = 120
max_requests = 1000
max_requests_jitter = 50  # Add jitter to prevent all workers restarting at once

# Log settings
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Connection handling - simpler for Windows
forwarded_allow_ips = "*"  # Important for proxied setups
max_requests_jitter = 50

# Additional parameters
forwarded_allow_ips = "*"
proxy_allow_ips = "*"
