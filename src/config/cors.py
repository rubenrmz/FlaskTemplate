# src/config/cors.py
from src.config.settings import Config


def get_cors_config() -> dict:
    """Retorna configuración de CORS para flask-cors."""
    return {
        r"/*": {
            "origins":             _get_origins(),
            "methods":             _get_methods(),
            "allow_headers":       Config.CORS_ALLOW_HEADERS,
            "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS,
            "max_age":             Config.CORS_MAX_AGE,
        }
    }


def _get_origins() -> list:
    """Parsea CORS_ORIGINS separados por coma."""
    return [o.strip() for o in Config.CORS_ORIGINS.split(',') if o.strip()]


def _get_methods() -> list:
    """Parsea CORS_METHODS y garantiza que OPTIONS siempre esté incluido."""
    methods = [m.strip().upper() for m in Config.CORS_METHODS.split(',') if m.strip()]
    if "OPTIONS" not in methods:
        methods.append("OPTIONS")
    return methods