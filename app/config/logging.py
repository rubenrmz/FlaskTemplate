# app/config/logging.py
import os
import logging
from app.config import Config


def setup_logging(app):
    """Configura logging para Flask"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Limpiar handlers existentes (evita duplicados)
    root_logger.handlers.clear()

    if Config.FLASK_ENV == 'production':
        # Crear directorio si no existe
        os.makedirs('logs', exist_ok=True)
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)