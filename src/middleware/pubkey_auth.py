# src/middleware/pubkey_auth.py
"""
Estrategia de auth 'jwt_pubkey': verificación de un JWT asimétrico (RS256/ES256/EdDSA).

El token lo emite un servicio centralizado (rust-axum) firmando con su llave PRIVADA.
La app solo tiene la llave PÚBLICA: verifica firma/exp (+ iss/aud opcionales) pero
NO emite tokens ni hace login. Requiere PyJWT[crypto].

Se usa vía el selector unificado (src/middleware/auth.py) cuando AUTH_MODE=jwt_pubkey.
"""
import logging
from functools import wraps
from flask import request, jsonify, g
from src.config.settings import Config

logger = logging.getLogger(__name__)

try:
    import jwt as pyjwt
except ImportError:
    pyjwt = None

# Cache de la llave pública (se lee una sola vez).
_public_key = None


def _load_public_key():
    """Carga la llave pública desde JWT_PUBLIC_KEY (inline) o JWT_PUBLIC_KEY_PATH (archivo)."""
    global _public_key
    if _public_key is not None:
        return _public_key
    if Config.JWT_PUBLIC_KEY:
        # Permite PEM en una sola línea con \n escapados en el .env.
        _public_key = Config.JWT_PUBLIC_KEY.replace('\\n', '\n')
    elif Config.JWT_PUBLIC_KEY_PATH:
        with open(Config.JWT_PUBLIC_KEY_PATH, 'r', encoding='utf-8') as f:
            _public_key = f.read()
    return _public_key


def decode_token(token):
    """Verifica firma/exp del JWT asimétrico. Lanza pyjwt.PyJWTError si es inválido."""
    kwargs = {"algorithms": [Config.JWT_ALGORITHM]}
    options = {}
    if Config.JWT_AUDIENCE:
        kwargs["audience"] = Config.JWT_AUDIENCE
    else:
        options["verify_aud"] = False
    if Config.JWT_ISSUER:
        kwargs["issuer"] = Config.JWT_ISSUER
    kwargs["options"] = options
    return pyjwt.decode(token, _load_public_key(), **kwargs)


def authenticate():
    """Verifica el Bearer token con la llave pública y carga g.current_user.

    Retorna una response de error (tupla) si falla, o None si la auth es válida.
    """
    if pyjwt is None:
        logger.error("AUTH_MODE=jwt_pubkey pero PyJWT[crypto] no está instalado.")
        return jsonify({"success": False, "error": "Auth no disponible"}), 500

    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return jsonify({"success": False, "error": "Token ausente"}), 401

    token = header[7:].strip()
    try:
        data = decode_token(token)
    except pyjwt.ExpiredSignatureError:
        return jsonify({"success": False, "error": "Token expirado"}), 401
    except pyjwt.PyJWTError:
        logger.warning(f"JWT asimétrico inválido desde {request.remote_addr}")
        return jsonify({"success": False, "error": "Token inválido"}), 401

    g.current_user = {
        "id":    data.get("sub"),
        "roles": data.get(Config.JWT_ROLES_CLAIM, []),
        "email": data.get("email"),
    }
    return None


def require_pubkey_jwt(f):
    """Fuerza la estrategia jwt_pubkey en una ruta, sin importar AUTH_MODE."""
    @wraps(f)
    def decorated(*args, **kwargs):
        error = authenticate()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated
