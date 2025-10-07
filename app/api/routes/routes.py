# app/api/routes/routes.py
import time
from flask import Blueprint, jsonify
from app.config.settings import Config
from app.config.logging import get_logger
from app.config.extensions import db
from sqlalchemy import text

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

@api_bp.route('/health/db', methods=['GET'])
def database_health_detailed():
    """Healthcheck detallado con info del pool"""
    
    try:
        start = time.time()
        version = db.session.execute(text('SELECT VERSION()')).scalar()
        query_time = (time.time() - start) * 1000
        
        return jsonify({
            'success': True, 
            'response_time_ms': round(query_time, 2),
            'Versión MySQL': version
        }), 200
    except Exception as e:
        logger.error('[routes.py]: %s', str(e))
        return jsonify({
            'success': False, 
            'error': 'Ha ocurrido un error.'
        }), 400
    