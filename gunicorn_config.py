import os
import multiprocessing

# Bind host and port (use 10000 for Render.com)
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")

# Workers and threads - optimized for Render.com
workers = 2  # Simplified for most environments
threads = 4
worker_class = "gevent"  # Better for handling asynchronous requests

# Timeouts - increased to prevent 502 errors on Render.com
timeout = 600  # Increased timeout for handling longer requests
keepalive = 120  # Keep connections alive
worker_connections = 1000

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
