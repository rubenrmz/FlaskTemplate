# src/api/auth_routes.py
"""
Endpoints de login JWT. Se registran SOLO cuando AUTH_MODE=jwt (ver src/__init__.py).

Flujo:
    POST /auth/login    {username, password}  → {access_token, refresh_token}
    POST /auth/refresh  {refresh_token}        → {access_token}

verify_credentials() es un STUB: impleméntalo contra tu store de usuarios.
"""
import logging
from flask import Blueprint, request, jsonify
from src.config.extensions import limiter
from src.config.settings import Config
from src.middleware.jwt_auth import create_access_token, create_refresh_token, decode_token, pyjwt

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


def verify_credentials(username, password):
    """
    STUB — IMPLEMENTAR. Valida credenciales y retorna el usuario o None.

    Retorno esperado: {"id": ..., "roles": [...], "email": ...} | None

    Ejemplo con DB (Modo A PyMySQL) + hash de werkzeug:
        from werkzeug.security import check_password_hash
        from src.config.extensions import get_db
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password_hash, roles, email FROM users WHERE username=%s", (username,))
            row = cur.fetchone()
        if row and check_password_hash(row["password_hash"], password):
            return {"id": row["id"], "roles": row["roles"].split(','), "email": row["email"]}
        return None
    """
    logger.error("verify_credentials() no está implementado.")
    return None


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_LOGIN)
def login():
    """Valida credenciales y emite access + refresh token."""
    data     = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "username y password son requeridos"}), 400

    user = verify_credentials(username, password)
    if not user:
        logger.warning(f"Login fallido para '{username}' desde {request.remote_addr}")
        return jsonify({"success": False, "error": "Credenciales inválidas"}), 401

    return jsonify({
        "success":       True,
        "access_token":  create_access_token(user["id"], user.get("roles"), user.get("email")),
        "refresh_token": create_refresh_token(user["id"]),
    }), 200


@auth_bp.route('/auth/refresh', methods=['POST'])
@limiter.limit(Config.RATE_LIMIT_LOGIN)
def refresh():
    """Emite un nuevo access token a partir de un refresh token válido."""
    data  = request.get_json(silent=True) or {}
    token = data.get('refresh_token')
    if not token:
        return jsonify({"success": False, "error": "refresh_token requerido"}), 400

    try:
        payload = decode_token(token, expected_type="refresh")
    except pyjwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "Refresh token expirado"}), 401
    except pyjwt.PyJWTError:
        return jsonify({"success": False, "error": "Refresh token inválido"}), 401

    return jsonify({
        "success":      True,
        "access_token": create_access_token(payload["sub"]),
    }), 200
