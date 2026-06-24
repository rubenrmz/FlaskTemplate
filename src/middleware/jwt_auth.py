# src/middleware/jwt_auth.py
"""
Estrategia de auth 'jwt': login dentro de la app, Bearer token en cada request.

Requiere PyJWT (descomentar en requirements.txt). Se usa vía el selector unificado
(src/middleware/auth.py) cuando AUTH_MODE=jwt, y emite tokens desde el blueprint
src/api/auth_routes.py.

Payload del access token:
    {"sub": <id>, "roles": [...], "email": ..., "type": "access", "iat": ..., "exp": ...}
"""
import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from src.config.settings import Config

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

try:
    import jwt as pyjwt
except ImportError:
    pyjwt = None


def _secret():
    """Clave de firma. Usa JWT_SECRET_KEY si está, si no cae a SECRET_KEY."""
    return Config.JWT_SECRET_KEY or Config.SECRET_KEY


def _now():
    return datetime.now(timezone.utc)


def create_access_token(identity, roles=None, email=None):
    """Genera un access token de corta duración."""
    payload = {
        "sub":                   str(identity),
        Config.JWT_ROLES_CLAIM:  roles or [],
        "email":                 email,
        "type":                  "access",
        "iat":                   _now(),
        "exp":                   _now() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES),
    }
    return pyjwt.encode(payload, _secret(), algorithm=ALGORITHM)


def create_refresh_token(identity):
    """Genera un refresh token de larga duración (solo sirve para renovar el access)."""
    payload = {
        "sub":  str(identity),
        "type": "refresh",
        "iat":  _now(),
        "exp":  _now() + timedelta(seconds=Config.JWT_REFRESH_TOKEN_EXPIRES),
    }
    return pyjwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token, expected_type=None):
    """Decodifica y valida firma/expiración. Lanza pyjwt.PyJWTError si es inválido."""
    data = pyjwt.decode(token, _secret(), algorithms=[ALGORITHM])
    if expected_type and data.get("type") != expected_type:
        raise pyjwt.InvalidTokenError("tipo de token incorrecto")
    return data


def authenticate():
    """Valida el Bearer token y carga la identidad en g.current_user.

    Retorna una response de error (tupla) si falla, o None si la auth es válida.
    """
    if pyjwt is None:
        logger.error("AUTH_MODE=jwt pero PyJWT no está instalado.")
        return jsonify({"success": False, "error": "Auth no disponible"}), 500

    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Token ausente"}), 401

    token = header[7:].strip()
    try:
        data = decode_token(token, expected_type="access")
    except pyjwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "Token expirado"}), 401
    except pyjwt.PyJWTError:
        logger.warning(f"JWT inválido desde {request.remote_addr}")
        return jsonify({"success": False, "error": "Token inválido"}), 401

    g.current_user = {
        "id":    data.get("sub"),
        "roles": data.get(Config.JWT_ROLES_CLAIM, []),
        "email": data.get("email"),
    }
    return None


def require_jwt(f):
    """Fuerza la estrategia jwt en una ruta, sin importar AUTH_MODE."""
    @wraps(f)
    def decorated(*args, **kwargs):
        error = authenticate()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated
