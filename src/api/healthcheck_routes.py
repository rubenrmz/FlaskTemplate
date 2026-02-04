# src/api/routes/routes.py
import time, logging
from flask import Blueprint, jsonify
from src.config.extensions import db
from src.middleware.key_auth import require_admin_key

logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar el estado de la app
    """
    return jsonify({
        'success': True,
        'status': 'healthy',
        'service': 'App Healthcheck'
    }), 200

@health_bp.route('/health/db', methods=['GET'])
@require_admin_key
def database_health_detailed():
    """
    Endpoint para verificar el estado de la DB
    """
    
    try:
        start = time.time()
        version = db.session.execute(text('SELECT VERSION()')).scalar()
        query_time = (time.time() - start) * 1000
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'service': 'DB Healthcheck',
            'response_time_ms': round(query_time, 2),
            'db_info': version
        }), 200
    except Exception as e:
        logger.error(str(e))
        return jsonify({
            'success': False,
            'error': 'Ha ocurrido un error.'
        }), 503
    finally:
        db.session.remove()
    