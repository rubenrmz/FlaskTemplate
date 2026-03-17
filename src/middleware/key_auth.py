# src/middleware/key_auth.py
import logging
from functools import wraps
from flask import request, jsonify
from src.config.settings import Config

logger = logging.getLogger(__name__)


def require_admin_key(f):
    """Valida que el header X-Admin-Key coincida con ADMIN_SECRET_KEY."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-Admin-Key')

        if not api_key:
            logger.warning(f"Acceso admin sin key desde {request.remote_addr}")
            return jsonify({"success": False, "error": "No autorizado"}), 401

        if api_key != Config.ADMIN_SECRET_KEY:
            logger.warning(f"Acceso admin con key inválida desde {request.remote_addr}")
            return jsonify({"success": False, "error": "No autorizado"}), 401

        return f(*args, **kwargs)
    return decorated