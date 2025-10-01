# app/api/routes.py
import json, time
from flask import Blueprint, jsonify, Response
from app.config import get_logger

logger = get_logger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado del servicio
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'App Healthcheck',
        'version': '1.0'
    }), 200
