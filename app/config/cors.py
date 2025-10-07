# app/config/cors.py
from app.config.settings import Config
 
def get_cors_config():
    is_production = Config.FLASK_ENV == 'production'
    
    return {
        r"/api/v1/*": {
            "origins": _get_origins(is_production),
            "methods": ["GET", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False,
            "max_age": 3600 if is_production else 7200
        }
    }

def _get_origins(is_production):
    if is_production:
        return ["https://app.test/"]
    return ["http://localhost:5000"]