# app/config/security.py
from app.config.settings import Config

def apply_security_headers(app):
    """Configura headers de seguridad"""
    is_production = Config.FLASK_ENV == 'production'
    
    @app.after_request
    def set_headers(response):
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'no-referrer'
        
        if is_production:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        
        return response
