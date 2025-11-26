import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === BINDING ===
bind = f"127.0.0.1:{os.getenv('FLASK_PORT') or '5000'}"

# === WORKERS ===
workers = int(os.getenv("GUNICORN_WORKERS") or "2")
worker_connections = int(os.getenv("GUNICORN_WORKER_MAX_CONNECTIONS") or "100")
worker_class = os.getenv("GUNICORN_WORKER_CLASS") or "gevent"

# === TIMEOUTS ===
timeout = int(os.getenv("GUNICORN_TIMEOUT") or "3000")
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT") or "3000")
keepalive = int(os.getenv("GUNICORN_KEEP_ALIVE") or "60")

# === LOGS ===
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
accesslog = os.path.join(BASE_DIR, "logs", "access.log")
errorlog = os.path.join(BASE_DIR, "logs", "error.log")
loglevel = os.getenv("LOG_LEVEL") or "ERROR"

# === DAEMON MODE ===
daemon = False  # CRÍTICO para Type=simple

# === NOMBRE DEL PROCESO ===
proc_name = "flask_app-production"

# === PERFORMANCE ===
preload_app = True
reload = False

# === WORKER RESTART ===
max_requests = 1000
max_requests_jitter = 100