# src/middleware/gateway_auth.py
"""
Consume la identidad inyectada por el gateway (nginx/openresty) tras validar el JWT.

La app NO valida el JWT: confía en los headers de identidad SOLO si el secreto
compartido (X-Gateway-Secret) coincide. Falla cerrado — sin secreto válido, 401.

Uso en una ruta:
    from src.middleware.gateway_auth import require_gateway_identity, get_current_user

    @bp.route('/perfil')
    @require_gateway_identity
    def perfil():
        user = get_current_user()        # {"id": ..., "roles": [...], "email": ...}
        return jsonify(user)

    @bp.route('/admin')
    @require_gateway_roles('admin')
    def admin():
        ...
"""
import hmac
import logging
from functools import wraps
from flask import request, jsonify, g
from src.config.settings import Config

logger = logging.getLogger(__name__)


def _authenticate_gateway():
    """Valida el secreto compartido y carga la identidad en g. Retorna response de error o None."""
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
    g.gateway_user = {
        "id":    user_id,
        "roles": [r.strip() for r in roles_raw.split(',') if r.strip()],
        "email": request.headers.get(Config.GATEWAY_HEADER_EMAIL),
    }
    return None


def require_gateway_identity(f):
    """Exige identidad válida inyectada por el gateway. Deja el usuario en g."""
    @wraps(f)
    def decorated(*args, **kwargs):
        error = _authenticate_gateway()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated


def require_gateway_roles(*required_roles):
    """Como require_gateway_identity, pero además exige al menos uno de los roles dados."""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            error = _authenticate_gateway()
            if error:
                return error
            if not set(g.gateway_user["roles"]).intersection(required_roles):
                logger.warning(f"Roles insuficientes desde {request.remote_addr}")
                return jsonify({"success": False, "error": "Permisos insuficientes"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


def get_current_user():
    """Identidad inyectada por el gateway para el request actual, o None."""
    return getattr(g, "gateway_user", None)
