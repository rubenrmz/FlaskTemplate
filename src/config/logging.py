# src/config/logging.py
import logging
import os
from logging.handlers import RotatingFileHandler
from src.config.settings import Config


def setup_logging(app) -> None:
    """Configura logging para Flask. Archivo en producción, consola en desarrollo."""
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    formatter  = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    if Config.FLASK_ENV == 'production':
        os.makedirs('logs', exist_ok=True)
        # Rotación para evitar que el log llene el disco: 10MB x 5 archivos.
        handler = RotatingFileHandler(
            'logs/app.log', maxBytes=10 * 1024 * 1024, backupCount=5
        )
    else:
        handler = logging.StreamHandler()

    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)