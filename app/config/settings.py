import os

class Config:
    ## Inicializacion de variables de entorno (Flask ENV)
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


    EXTERNAL_API_URL_BASE = os.getenv('EXTERNAL_API_URL_BASE', 'http://127.0.0.1:5000')
    REQUEST_TIMEOUT = os.getenv('REQUEST_TIMEOUT', 30)
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Configuración global
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
