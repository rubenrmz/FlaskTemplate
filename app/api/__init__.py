# app/api/__init__.py
"""
Punto de entrada principal para todos los blueprints de la API.

Este módulo centraliza el registro de todos los sub-blueprints,
permitiendo un único punto de registro en la aplicación Flask.

Uso en app.py:
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
"""

from flask import Blueprint

# Blueprint principal que agrupa todos los endpoints de la API
api_bp = Blueprint('api', __name__)

# ============== Registro de sub-blueprints ==============

from .healthcheck_routes import health_bp

api_bp.register_blueprint(health_bp)
# más blueprints aquí ->