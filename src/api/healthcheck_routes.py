# src/api/healthcheck_routes.py
import time, logging
from flask import Blueprint, jsonify
from src.config.extensions import check_db_connection
from src.middleware.key_auth import require_admin_key
from src.utils.time_util import now_iso

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica que la app esté en línea."""
    return jsonify({
        'success':   True,
        'status':    'healthy',
        'service':   'App Healthcheck',
        'timestamp': now_iso(),
    }), 200


@health_bp.route('/health/db', methods=['GET'])
@require_admin_key
def database_health():
    """Verifica conectividad y tiempo de respuesta de la base de datos."""
    try:
        start        = time.perf_counter()
        version      = check_db_connection()
        query_time   = (time.perf_counter() - start) * 1000

        return jsonify({
            'success':          True,
            'status':           'healthy',
            'service':          'DB Healthcheck',
            'timestamp':        now_iso(),
            'response_time_ms': round(query_time, 2),
            'db_version':       version,
        }), 200

    except Exception:
        logger.error("Error en health check de DB", exc_info=True)
        return jsonify({
            'success': False,
            'status':  'unhealthy',
            'service': 'DB Healthcheck',
            'error':   'Base de datos no disponible.',
        }), 503