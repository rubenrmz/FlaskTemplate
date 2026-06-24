# src/__init__.py
import logging
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from src.config import Config, cors, limiter, apply_security_headers, setup_logging, get_cors_config
from src.api import api_bp

logger = logging.getLogger(__name__)

def create_app():
    """Factory de la aplicación Flask."""
    Config.validate()

    app = Flask(__name__)
    app.config.from_object(Config)

    # ProxyFix: confía en los headers X-Forwarded-* solo si hay proxies declarados.
    # Necesario para que remote_addr (logs + rate limiting) refleje la IP real del
    # cliente detrás de nginx/openresty. Con 0 no se aplica (previene spoofing).
    if Config.TRUSTED_PROXY_COUNT > 0:
        n = Config.TRUSTED_PROXY_COUNT
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=n, x_proto=n, x_host=n, x_prefix=n)

    # Extensiones core
    cors.init_app(app, resources=get_cors_config())
    limiter.init_app(app)

    # Database (opcional)
    # Modo A (ORM_ENABLED=false): PyMySQL — la conexión se configura al importar extensions.py
    # Modo B (ORM_ENABLED=true): SQLAlchemy + flask-marshmallow
    if Config.DB_ENABLED and Config.ORM_ENABLED:
        from src.config.extensions import db, ma
        if db is None:
            raise ImportError("Flask-SQLAlchemy no está instalado. Instálalo o desactiva ORM_ENABLED.")
        db.init_app(app)
        if ma is not None:
            ma.init_app(app)

    # Mail (opcional)
    if Config.MAIL_ENABLED:
        from src.config.extensions import mail
        if mail is None:
            raise ImportError("Flask-Mailman no está instalado. Instálalo o desactiva MAIL_ENABLED.")
        mail.init_app(app)

    # Redis (opcional)
    if Config.REDIS_ENABLED:
        from src.config.extensions import init_redis
        if init_redis() is None:
            raise RuntimeError("Redis no disponible. Verifica la conexión o desactiva REDIS_ENABLED.")

    # Sockets (opcional)
    if Config.WS_ENABLED:
        from src.config.extensions import socketio
        from src.api.socket_events import register_socket_events
        ws_origins = [o.strip() for o in Config.CORS_ORIGINS.split(',') if o.strip()]
        socketio.init_app(
            app,
            message_queue=Config.get_redis_uri(),
            cors_allowed_origins=ws_origins,
            async_mode="gevent",
            logger=False,
            engineio_logger=False,
        )
        register_socket_events(socketio)
        logger.info("WebSockets inicializados")

    # Seguridad y logging
    apply_security_headers(app)
    setup_logging(app)
    register_error_handlers(app)

    # Blueprints
    app.register_blueprint(api_bp, url_prefix=Config.API_PREFIX)

    logger.info(f"App iniciada en modo {Config.FLASK_ENV}")
    return app


def register_error_handlers(app):
    """Respuestas JSON consistentes para errores comunes. Evita fugas de stack traces."""

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"success": False, "error": "Recurso no encontrado"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"success": False, "error": "Método no permitido"}), 405

    @app.errorhandler(413)
    def payload_too_large(_e):
        return jsonify({"success": False, "error": "Payload demasiado grande"}), 413

    @app.errorhandler(429)
    def rate_limited(_e):
        return jsonify({"success": False, "error": "Demasiadas solicitudes"}), 429

    @app.errorhandler(500)
    def internal_error(_e):
        logger.error("Error interno no controlado", exc_info=True)
        return jsonify({"success": False, "error": "Error interno del servidor"}), 500
