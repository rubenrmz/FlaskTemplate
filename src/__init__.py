# src/__init__.py
import logging
from flask import Flask
from src.config import Config, cors, limiter, apply_security_headers, setup_logging, get_cors_config
from src.api import api_bp

logger = logging.getLogger(__name__)

def create_app(config_class=Config):
    """Factory de la aplicación Flask."""
    config_class.validate()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensiones core
    cors.init_app(app, resources=get_cors_config())
    limiter.init_app(app)

    # Database (opcional)
    if config_class.DB_ENABLED:
        from src.config.extensions import db
        if db is None:
            raise ImportError("Flask-SQLAlchemy no está instalado. Instálalo o desactiva DB_ENABLED.")
        db.init_app(app)

    # Marshmallow (opcional)
    if config_class.MA_ENABLED:
        from src.config.extensions import ma
        if ma is None:
            raise ImportError("Flask-Marshmallow no está instalado. Instálalo o desactiva MA_ENABLED.")
        ma.init_app(app)

    # Mail (opcional)
    if config_class.MAIL_ENABLED:
        from src.config.extensions import mail
        if mail is None:
            raise ImportError("Flask-Mailman no está instalado. Instálalo o desactiva MAIL_ENABLED.")
        mail.init_app(app)

    # Redis (opcional)
    if config_class.REDIS_ENABLED:
        from src.config.extensions import init_redis
        if init_redis() is None:
            raise RuntimeError("Redis no disponible. Verifica la conexión o desactiva REDIS_ENABLED.")

    # Seguridad y logging
    apply_security_headers(app)
    setup_logging(app)

    # Blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    logger.info(f"App iniciada en modo {config_class.FLASK_ENV}")
    return app