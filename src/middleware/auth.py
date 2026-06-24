# src/middleware/auth.py
"""
Selector unificado de autenticación.

Las rutas usan SIEMPRE estos decoradores; el .env decide qué estrategia corre:
    AUTH_REQUIRED=true|false   → si false, @require_auth es no-op (API abierta)
    AUTH_MODE=gateway|jwt      → estrategia activa cuando AUTH_REQUIRED=true

Uso:
    from src.middleware.auth import require_auth, require_roles, get_current_user

    @bp.route('/perfil')
    @require_auth
    def perfil():
        return jsonify(get_current_user())   # {"id", "roles": [...], "email"}

    @bp.route('/admin')
    @require_roles('admin')
    def admin():
        ...
"""
import logging
from functools import wraps
from flask import g, jsonify
from src.config.settings import Config
from src.middleware import gateway_auth, jwt_auth

logger = logging.getLogger(__name__)

# Estrategia → función authenticate() que valida y carga g.current_user.
_AUTHENTICATORS = {
    "gateway": gateway_auth.authenticate,
    "jwt":     jwt_auth.authenticate,
}


def _authenticate():
    """Ejecuta el autenticador según AUTH_MODE. Retorna response de error o None."""
    if not Config.AUTH_REQUIRED:
        return None
    authn = _AUTHENTICATORS.get(Config.AUTH_MODE)
    if authn is None:
        logger.error(f"AUTH_MODE inválido en runtime: {Config.AUTH_MODE}")
        return jsonify({"success": False, "error": "Configuración de auth inválida"}), 500
    return authn()


def require_auth(f):
    """Exige autenticación válida según la estrategia activa."""
    @wraps(f)
    def decorated(*args, **kwargs):
        error = _authenticate()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated


def require_roles(*required_roles):
    """Como require_auth, pero además exige al menos uno de los roles dados."""
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            error = _authenticate()
            if error:
                return error
            # Con AUTH_REQUIRED=false no hay identidad: la verificación de rol se omite.
            if Config.AUTH_REQUIRED:
                user = get_current_user() or {}
                if not set(user.get("roles", [])).intersection(required_roles):
                    return jsonify({"success": False, "error": "Permisos insuficientes"}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper


def get_current_user():
    """Identidad autenticada del request actual, o None. {"id", "roles": [...], "email"}"""
    return getattr(g, "current_user", None)
