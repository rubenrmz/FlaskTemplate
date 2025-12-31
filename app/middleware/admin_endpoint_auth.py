# app/middleware/admin_auth.py
import logging
from functools import wraps
from flask import request, jsonify
from app.config import Config

logger = logging.getLogger(__name__)

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-Admin-Key')
        if api_key != Config.ADMIN_SECRET_KEY:
            logger.warning(f"Intento de acceso admin no autorizado desde {request.remote_addr}")
            return jsonify({"error": "No autorizado"}), 401
        return f(*args, **kwargs)
    return decorated
