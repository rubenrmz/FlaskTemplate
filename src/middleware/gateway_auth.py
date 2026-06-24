# src/middleware/gateway_auth.py
"""
Estrategia de auth 'gateway': consume la identidad inyectada por nginx/openresty
tras validar el JWT en el edge. La app NO valida el JWT: confía en los headers de
identidad SOLO si el secreto compartido (X-Gateway-Secret) coincide. Fail-closed.

Normalmente se usa vía el selector unificado:
    from src.middleware.auth import require_auth, require_roles, get_current_user

Este módulo expone authenticate() para que src/middleware/auth.py despache a él
cuando AUTH_MODE=gateway. Los decoradores require_gateway_* fuerzan esta estrategia
sin importar AUTH_MODE (útil para un endpoint que siempre es edge-auth).
"""
import hmac
import logging
from functools import wraps
from flask import request, jsonify, g
from src.config.settings import Config

logger = logging.getLogger(__name__)


def authenticate():
    """Valida el secreto compartido y carga la identidad en g.current_user.

    Retorna una response de error (tupla) si falla, o None si la auth es válida.
    """
    secret   = request.headers.get(Config.GATEWAY_SECRET_HEADER, '')
    expected = Config.GATEWAY_SHARED_SECRET or ''

    # Fail-closed: sin secreto configurado o sin coincidencia → no se confía en los headers.
    if not expected or not hmac.compare_digest(secret, expected):
        logger.warning(f"Gateway secret inválido o ausente desde {request.remote_addr}")
        return jsonify({"success": False, "error": "No autorizado"}), 401

    user_id = request.headers.get(Config.GATEWAY_HEADER_USER_ID)
    if not user_id:
        logger.warning(f"Gateway sin identidad ({Config.GATEWAY_HEADER_USER_ID}) desde {request.remote_addr}")
        return jsonify({"success": False, "error": "Identidad no provista por el gateway"}), 401

    roles_raw = request.headers.get(Config.GATEWAY_HEADER_ROLES, '')
    g.current_user = {
        "id":    user_id,
        "roles": [r.strip() for r in roles_raw.split(',') if r.strip()],
        "email": request.headers.get(Config.GATEWAY_HEADER_EMAIL),
    }
    return None


def require_gateway_identity(f):
    """Fuerza la estrategia gateway en una ruta, sin importar AUTH_MODE."""
    @wraps(f)
    def decorated(*args, **kwargs):
        error = authenticate()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated


def require_gateway_roles(*required_roles):
    """Como require_gateway_identity, pero además exige al menos uno de los roles dados."""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            error = authenticate()
            if error:
                return error
            if not set(g.current_user["roles"]).intersection(required_roles):
                logger.warning(f"Roles insuficientes desde {request.remote_addr}")
                return jsonify({"success": False, "error": "Permisos insuficientes"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper
