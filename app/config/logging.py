import logging
from app.config.settings import Config


def setup_logging(app):
    """Configura logging para Flask"""
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/app.log')
        ]
    )
    app.logger.setLevel(Config.LOG_LEVEL)

def get_logger(name):
    """Obtiene logger para un módulo"""
    return logging.getLogger(name)
