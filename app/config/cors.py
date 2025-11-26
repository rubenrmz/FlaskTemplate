# app/config/cors.py
from app.config.settings import Config

def get_cors_config():
    return {
        r"/*": {
            "origins": _get_origins(),
            "methods": _get_methods(),
            "allow_headers": Config.CORS_ALLOW_HEADERS,
            "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS,
            "max_age": Config.CORS_MAX_AGE
        }
    }

def _get_origins():
    origins_str = Config.CORS_ORIGINS
    
    origins = [origin.strip() for origin in origins_str.split(',')]
    
    return [origin for origin in origins if origin]

def _get_methods():
    methods = Config.CORS_METHODS
    
    methods_list = [method.strip() for method in methods.split(',')]
    
    if "OPTIONS" not in methods_list:
        methods_list.append("OPTIONS")
    
    return methods_list