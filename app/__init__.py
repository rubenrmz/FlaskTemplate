# app/__init__.py
from flask import Flask
from app.config import Config, get_cors_config, apply_security_headers, setup_logging
from app.config import db, ma, cors, limiter
from app.api.template_routes import api_bp


def create_app(config_class=Config):
    """
    Factory de la aplicación Flask.
    
    Args:
        config_class: Clase de configuración (permite override para testing)
    
    Returns:
        Instancia de Flask configurada
    """
    # Validar configuración crítica antes de iniciar
    config_class.validate()
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Extensiones
    cors.init_app(app, resources=get_cors_config())
    limiter.init_app(app)
    # db.init_app(app)
    # ma.init_app(app)

    # Seguridad y logging
    apply_security_headers(app)
    setup_logging(app)

    # Blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app