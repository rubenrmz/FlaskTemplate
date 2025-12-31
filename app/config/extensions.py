# app/config/extensions.py
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import Config

# Core (siempre requeridos)
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"],
    storage_uri=Config.get_redis_uri(),
)

# Opcionales
db = None
ma = None
mail = None
redis_client = None

def init_redis():
    global redis_client
    from app.config import Config
    
    try:
        import redis as redis_lib
        if Config.REDIS_ENABLED:
            redis_client = redis_lib.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            redis_client.ping()
    except ImportError:
        pass
    except Exception:
        redis_client = None
    
    return redis_client

# SQLAlchemy, Marshmallow, Mail...
try:
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass
    db = SQLAlchemy(model_class=Base)
except ImportError:
    pass

try:
    from flask_marshmallow import Marshmallow
    ma = Marshmallow()
except ImportError:
    pass

try:
    from flask_mailman import Mail
    mail = Mail()
except ImportError:
    pass