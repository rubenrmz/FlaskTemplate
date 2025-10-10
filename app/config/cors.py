# app/config/cors.py
from app.config.settings import Config

def get_cors_config():
    return {
        r"/api/v1/*": {
            "origins": _get_origins(),
            "methods": Config.CORS_METHODS,
            "allow_headers": Config.CORS_ALLOW_HEADERS,
            "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS,
            "max_age": Config.CORS_MAX_AGE
        }
    }

def _get_origins():
    origins_str = Config.CORS_ORIGINS
    
    origins = [origin.strip() for origin in origins_str.split(',')]
    
    return [origin for origin in origins if origin]