from flask import Flask
from app.config.settings import Config
from app.config.logging import setup_logging
# from app.models import db
from app.api.routes import api_bp

def create_app():
    app = Flask(__name__)
    
    # Carga las vaiables de entorno
    app.config.from_object(Config)
    
    # Incializa logs
    setup_logging(app)
    
    # Inicializar base de datos
    # db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    return app