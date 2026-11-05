"""gunicorn settings. Run with: gunicorn -c gunicorn.conf.py "app:create_app()"."""

import os

bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"

# One worker = one copy of the model in memory. Threads keep /health responsive
# while a request is generating; generation itself is serialized by a lock.
workers = 1
worker_class = "gthread"
threads = int(os.getenv("THREADS", "4"))

# CPU inference can take minutes. With gthread this is the worker heartbeat
# limit, so long requests are not killed the way the 30s default killed them.
timeout = int(os.getenv("REQUEST_TIMEOUT", "600"))
graceful_timeout = 30

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()
