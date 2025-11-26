# app/config/settings.py
import os

class Config:
    ## Inicializacion de variables de entorno (Flask ENV)
    FLASK_ENV = os.getenv('FLASK_ENV') or 'development'
    DEBUG = (os.getenv('DEBUG') or 'False').lower() in ['true', '1', 'yes']
    SECRET_KEY = os.getenv('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración API
    EXTERNAL_API_URL_BASE = os.getenv('EXTERNAL_API_URL_BASE') or ''
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT') or '30')
    
    # Configuración DB
    DB_HOST = os.getenv('DB_HOST') or ''
    DB_USER = os.getenv('DB_USER') or ''
    DB_PASSWORD = os.getenv('DB_PASSWORD') or ''
    DB_PORT = int(os.getenv('DB_PORT') or '3306')
    DB_DATABASE = os.getenv('DB_DATABASE') or ''
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    
    # Configuración Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL') or 'DEBUG'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuración CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS') or '*'
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET, POST')
    CORS_ALLOW_HEADERS = ["Content-Type"]
    CORS_SUPPORTS_CREDENTIALS = False
    CORS_MAX_AGE = int(os.getenv('CORS_MAX_AGE') or '3600')
