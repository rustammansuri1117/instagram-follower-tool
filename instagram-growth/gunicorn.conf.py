import os

# Render binds to 0.0.0.0 on the port provided by $PORT (defaults to 10000)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = 4
timeout = 120
accesslog = "-"
errorlog = "-"
