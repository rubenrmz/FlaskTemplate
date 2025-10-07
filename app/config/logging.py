# app/config/logging.py
import os, logging
from app.config.settings import Config

def setup_logging(app):
    """Configura logging para Flask"""
    log_level = getattr(logging, Config.LOG_LEVEL.upper())
    formatter = logging.Formatter(Config.LOG_FORMAT)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    if Config.FLASK_ENV == 'production':
        # Solo archivo
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        # Solo consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)