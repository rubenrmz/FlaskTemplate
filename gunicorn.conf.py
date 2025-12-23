# gunicorn.conf.py
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ===========================================
# BINDING
# ===========================================
# Dirección y puerto donde Gunicorn escucha conexiones
# En producción, usar socket unix: unix:/run/gunicorn.sock
bind = f"127.0.0.1:{os.getenv('FLASK_PORT', '5000')}"

# ===========================================
# WORKERS
# ===========================================
# Número de workers para manejar requests
# Recomendado: (CPU cores * 2) + 1
workers = int(os.getenv("GUNICORN_WORKERS", "3"))

# Tipo de worker según la necesidad:
# - sync: requests simples, CPU-bound (1 request a la vez por worker)
# - gthread: I/O moderado (usar con threads)
# - gevent: alta concurrencia, WebSockets, SSE
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")

# Threads por worker (solo aplica para gthread)
threads = int(os.getenv("GUNICORN_THREADS", "2"))

# Conexiones máximas por worker (solo aplica para gevent)
worker_connections = int(os.getenv("GUNICORN_WORKER_MAX_CONNECTIONS", "1000"))

# ===========================================
# TIMEOUTS
# ===========================================
# Tiempo máximo en segundos para que un worker responda
# Si se excede, el worker es reiniciado
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))

# Tiempo de gracia para terminar requests pendientes al reiniciar
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))

# Tiempo de espera para conexiones keep-alive
keepalive = int(os.getenv("GUNICORN_KEEP_ALIVE", "5"))

# ===========================================
# LOGGING
# ===========================================
# Directorio de logs (se crea si no existe)
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Archivo de logs de acceso (requests entrantes)
accesslog = os.path.join(logs_dir, "access.log")

# Archivo de logs de errores
errorlog = os.path.join(logs_dir, "error.log")

# Nivel de log: DEBUG | INFO | WARNING | ERROR | CRITICAL
loglevel = os.getenv("LOG_LEVEL", "INFO").lower()

# ===========================================
# PROCESO
# ===========================================
# Nombre del proceso (visible en ps, htop)
proc_name = os.getenv("APP_NAME", "flask_app")
daemon = os.getenv("GUNICORN_DAEMON", "False").lower() in ["true", "1", "yes"]

# ===========================================
# PERFORMANCE
# ===========================================
# Carga la app antes de hacer fork de workers
# Reduce memoria compartida, pero requiere reinicio completo para cambios
preload_app = True
reload = False

# ===========================================
# WORKER LIFECYCLE
# ===========================================
# Requests máximos antes de reiniciar un worker (previene memory leaks)
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))

# Variación aleatoria para evitar reinicio simultáneo de workers
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))