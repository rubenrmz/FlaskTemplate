# app/config/logging.py
import os, logging
from app.config.settings import Config

def setup_logging(app):
    """Configura logging para Flask"""
    
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_level = getattr(logging, Config.LOG_LEVEL.upper())
    
    # Configurar formato
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
