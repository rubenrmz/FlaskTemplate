import os
from dotenv import load_dotenv

class Config:
    ## Inicializacion de variables de entorno (Flask ENV)
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Configuración API
    EXTERNAL_API_URL_BASE = os.getenv('EXTERNAL_API_URL_BASE', 'http://127.0.0.1:5000')
    REQUEST_TIMEOUT = os.getenv('REQUEST_TIMEOUT', 30)
    
    # Configuración DB
    DB_HOST = os.getenv('DB_HOST', '')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_DATABASE = os.getenv('DB_DATABASE', '')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    
    # Configuración Logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
