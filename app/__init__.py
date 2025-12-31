# app/__init__.py
from flask import Flask
from app.config import Config, cors, limiter, apply_security_headers, setup_logging, get_cors_config
from app.api import api_bp
from app.middleware.origin_validation import RequireOriginMiddleware

def create_app(config_class=Config):
    """
    Factory de la aplicación Flask.
    """
    config_class.validate()
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensiones core
    cors.init_app(app, resources=get_cors_config())
    limiter.init_app(app)

    # Database (opcional)
    if config_class.DB_ENABLED:
        from app.config.extensions import db
        if db is None:
            raise ImportError("Flask-SQLAlchemy no está instalado. Instálalo o desactiva DB_ENABLED.")
        db.init_app(app)

    # Marshmallow (opcional)
    if config_class.MA_ENABLED:
        from app.config.extensions import ma
        if ma is None:
            raise ImportError("Flask-Marshmallow no está instalado. Instálalo o desactiva MA_ENABLED.")
        ma.init_app(app)

    # Mail (opcional)
    if config_class.MAIL_ENABLED:
        from app.config.extensions import mail
        if mail is None:
            raise ImportError("Flask-Mailman no está instalado. Instálalo o desactiva MAIL_ENABLED.")
        mail.init_app(app)

    # Redis (opcional)
    if config_class.REDIS_ENABLED:
        from app.config.extensions import init_redis
        redis_client = init_redis()
        if redis_client is None:
            raise ImportError("Redis no está disponible. Verifica la conexión o desactiva REDIS_ENABLED.")
        
    # Seguridad y logging
    apply_security_headers(app)
    setup_logging(app)

    # Blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app