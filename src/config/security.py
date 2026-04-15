# src/config/security.py
from src.config.settings import Config


def apply_security_headers(app) -> None:
    """Aplica headers de seguridad a todas las respuestas HTTP."""
    is_production = Config.FLASK_ENV == 'production'

    @app.after_request
    def set_headers(response):
        response.headers['X-Frame-Options']           = 'DENY'
        response.headers['X-Content-Type-Options']    = 'nosniff'
        response.headers['Referrer-Policy']           = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy']   = "default-src 'self'"
        response.headers['Permissions-Policy']        = 'geolocation=(), microphone=(), camera=()'

        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        return response