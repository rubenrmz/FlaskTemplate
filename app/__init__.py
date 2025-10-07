from flask import Flask
from app.config.settings import Config
from app.config.logging import setup_logging
from app.api.routes.routes import api_bp
from app.config.extensions import db, ma, cors, limiter
from app.config.cors import get_cors_config
from app.config.security import apply_security_headers

def create_app():
    app = Flask(__name__)
    
    # Carga las vaiables de entorno
    app.config.from_object(Config)
    
    # Inicializar CORS
    cors.init_app(app, resources=get_cors_config())
    
    # Limitador
    limiter.init_app(app)
    
    # Security
    apply_security_headers(app)
    
    # Incializa logs
    setup_logging(app)
    
    # Inicializar base de datos
    db.init_app(app)
    ma.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app