# src/config/logging.py
import logging
import os
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
        handler = logging.FileHandler('logs/app.log')
    else:
        handler = logging.StreamHandler()

    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)