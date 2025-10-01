import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === BINDING ===
# Regularmente no debe ser expuesta directamente, si no a traves de NGINX
bind = "127.0.0.1:5000" # Indica el port

# === WORKERS ===
# Para el manejo de paralelismo o concurrencia (define segun las necesidades de la app y evitar bottlenecks)
workers = 4
worker_class = "gevent"  # Manejo de SSE
worker_connections = 100  # Suficiente para 3 usuarios

# === TIMEOUTS PARA 6,000 CONSULTAS ===
# 6000 consultas × 1 seg = 6000 seg = 100 min = 1h 40min
timeout = 30000  # 2.3 horas (con margen de seguridad)
graceful_timeout = 30000
keepalive = 300

# === LOGS ===
accesslog = os.path.join(BASE_DIR, "logs", "access.log")
errorlog = os.path.join(BASE_DIR, "logs", "error.log")
loglevel = os.getenv("LOG_LEVEL", "INFO")

# === PID ===
pidfile = os.path.join(BASE_DIR, "gunicorn.pid")

# === NOMBRE DEL PROCESO ===
proc_name = "flask_app-production"

# === PERFORMANCE ===
preload_app = True
reload = False # NO permite cambios en tiempo de ejecución

# === WORKER RESTART ===
max_requests = 1000
max_requests_jitter = 100