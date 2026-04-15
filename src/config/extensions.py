# src/config/extensions.py
import logging
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.config.settings import Config

logger = logging.getLogger(__name__)

# ===========================================
# CORE (siempre requeridos)
# ===========================================
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT_DEFAULT],
    storage_uri=Config.get_redis_uri(),
)

db           = None
redis_client = None
ma           = None
mail         = None
socketio     = None

# ===========================================
# DATABASE — elegir modo en settings.py
# ===========================================
# Modo A: PyMySQL directo (sin ORM)
# - Ideal para queries simples y arquitectura repo/*_queries.py
# - Menor overhead, control total del SQL
# - Usar: get_db() como context manager en los queries
#
# Modo B: SQLAlchemy (con ORM)
# - Ideal para modelos complejos con relaciones y migraciones
# - Descomentar bloque SQLAlchemy y comentar bloque PyMySQL
# - Requiere: Flask-SQLAlchemy en requirements.txt

# --- Modo A: PyMySQL directo ---
if Config.DB_ENABLED:
    try:
        import pymysql
        from contextlib import contextmanager

        def get_connection():
            """Abre una conexión directa a MySQL."""
            return pymysql.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_DATABASE,
                port=int(Config.DB_PORT),
                cursorclass=pymysql.cursors.DictCursor,
            )


        @contextmanager
        def get_db():
            """Context manager para queries. Cierra la conexión al salir."""
            conn = get_connection()
            try:
                yield conn
            finally:
                conn.close()


        def check_db_connection():
            """Valida que la base de datos sea accesible al arrancar."""
            try:
                with get_db() as conn:
                    conn.cursor().execute("SELECT 1")
                logger.info("Base de datos conectada OK")
            except Exception as e:
                logger.error(f"Error al conectar DB: {type(e).__name__}: {e}")
                raise RuntimeError("Base de datos no disponible.") from e

    except ImportError:
        logger.error("PyMySQL no está instalado. Instálalo o desactiva DB_ENABLED.")

# --- Modo B: SQLAlchemy (ORM) ---
# Descomentar este bloque y comentar Modo A para usar ORM
# Requiere: Flask-SQLAlchemy, y driver mysql o postgresql en requirements.txt
#
# try:
#     from flask_sqlalchemy import SQLAlchemy
#     from sqlalchemy.orm import DeclarativeBase
#
#     class Base(DeclarativeBase):
#         pass
#
#     db = SQLAlchemy(model_class=Base)
# except ImportError:
#     logger.error("Flask-SQLAlchemy no está instalado. Instálalo o desactiva DB_ENABLED.")

# ===========================================
# REDIS (opcional)
# ===========================================
def init_redis():
    """Inicializa Redis con connection pool. Reutiliza si ya existe."""
    global redis_client
    if redis_client is not None:
        return redis_client
    try:
        import redis as redis_lib
        if Config.REDIS_ENABLED:
            pool = redis_lib.ConnectionPool(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD,
                db=Config.REDIS_DB,
                decode_responses=True,
                max_connections=20,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            redis_client = redis_lib.Redis(connection_pool=pool)
            redis_client.ping()
            logger.info("Redis conectado con pool OK")
    except ImportError:
        logger.error("redis no está instalado. Instálalo o desactiva REDIS_ENABLED.")
    except Exception as e:
        logger.error(f"Redis error: {type(e).__name__}: {e}")
        redis_client = None
    return redis_client


# ===========================================
# MARSHMALLOW (opcional)
# ===========================================
try:
    from flask_marshmallow import Marshmallow
    ma = Marshmallow()
except ImportError:
    pass


# ===========================================
# MAIL (opcional)
# ===========================================
try:
    from flask_mailman import Mail
    mail = Mail()
except ImportError:
    pass

# ===========================================
# WEBSOCKETS (opcional)
# ===========================================
# Requiere: gevent, flask-socketio, simple-websocket en requirements.txt
# Activar: WS_ENABLED=true en .env
try:
    from flask_socketio import SocketIO
    socketio = SocketIO()
except ImportError:
    socketio = None