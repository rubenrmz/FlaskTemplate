# app/config/settings.py
import os

class Config:
    # ===========================================
    # FLASK
    # ===========================================
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'dev-secret-key-change-in-production')
    APP_NAME = os.getenv('APP_NAME', 'flask_app')
    MA_ENABLED = os.getenv('MA_ENABLED', 'False').lower() in ['true', '1', 'yes']

    # ===========================================
    # DATABASE (opcional)
    # ===========================================
    DB_ENABLED = os.getenv('DB_ENABLED', 'False').lower() in ['true', '1', 'yes']
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_DATABASE = os.getenv('DB_DATABASE', 'test')
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')

    # Construir URI solo si está habilitado
    if DB_ENABLED:
        _driver = 'postgresql+psycopg2' if DB_TYPE == 'postgresql' else 'mysql+pymysql'
        SQLALCHEMY_DATABASE_URI = f'{_driver}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    else:
        SQLALCHEMY_DATABASE_URI = None

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ===========================================
    # SMTP / EMAIL (opcional)
    # ===========================================
    MAIL_ENABLED = os.getenv('MAIL_ENABLED', 'False').lower() in ['true', '1', 'yes']
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 1025)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or None
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or None
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@tuapp.com')
    MAIL_TIMEOUT = int(v) if (v := os.getenv('MAIL_TIMEOUT')) else None
    MAIL_MAX_EMAILS = int(v) if (v := os.getenv('MAIL_MAX_EMAILS')) else None
    MAIL_ASCII_ATTACHMENTS = os.getenv('MAIL_ASCII_ATTACHMENTS', 'False').lower() == 'true'

    # ===========================================
    # EXTERNAL SERVICES
    # ===========================================
    EXTERNAL_API_URL_BASE = os.getenv('EXTERNAL_API_URL_BASE', '')
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT') or 30)
    FRONTEND_URL_BASE = os.getenv('FRONTEND_URL_BASE', 'http://localhost:3000')

    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() in ['true', '1', 'yes']
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT') or 6379)
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD') or None
    REDIS_DB = int(os.getenv('REDIS_DB') or 0)
    
    @classmethod
    def get_redis_uri(cls):
        if not cls.REDIS_ENABLED:
            return "memory://"
        if cls.REDIS_PASSWORD:
            from urllib.parse import quote
            password = quote(cls.REDIS_PASSWORD, safe='')
            return f"redis://:{password}@{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        return f"redis://{cls.REDIS_HOST}:{cls.REDIS_PORT}/{cls.REDIS_DB}"
        
    # ===========================================
    # LOGGING
    # ===========================================
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # ===========================================
    # CORS
    # ===========================================
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000')
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET')
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = int(os.getenv('CORS_MAX_AGE') or 3600)

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
        if Config.FLASK_ENV == 'production':
            if Config.SECRET_KEY == 'dev-secret-key-change-in-production':
                raise ValueError("SECRET_KEY debe configurarse en producción")
            if Config.CORS_ORIGINS in ['*', 'http://localhost:3000']:
                raise ValueError("CORS_ORIGINS debe configurarse en producción")
