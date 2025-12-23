# app/config/settings.py
import os


class Config:
    # ===========================================
    # FLASK
    # ===========================================
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    APP_NAME = os.getenv('APP_NAME', 'flask_app')

    # ===========================================
    # DATABASE
    # ===========================================
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_DATABASE = os.getenv('DB_DATABASE', '')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f'mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===========================================
    # EXTERNAL SERVICES
    # ===========================================
    EXTERNAL_API_URL_BASE = os.getenv('EXTERNAL_API_URL_BASE', '')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))

    # ===========================================
    # LOGGING
    # ===========================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # ===========================================
    # CORS
    # ===========================================
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE').split(',')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = int(os.getenv('CORS_MAX_AGE', '3600'))

    # ===========================================
    # RATE LIMITING
    # ===========================================
    RATE_LIMIT_DEFAULT = os.getenv('RATE_LIMIT_DEFAULT', '100 per hour')
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')

    # ===========================================
    # VALIDATION
    # ===========================================
    @staticmethod
    def validate():
        """Valida configuración crítica en producción"""
        if Config.FLASK_ENV == 'production':
            if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
                raise ValueError("SECRET_KEY debe configurarse en producción")
            if Config.CORS_ORIGINS in ['*', 'http://localhost:3000']:
                raise ValueError("CORS_ORIGINS debe configurarse en producción")