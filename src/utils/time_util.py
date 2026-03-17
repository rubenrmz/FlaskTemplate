# src/utils/time_util.py
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from src.config.settings import Config

logger = logging.getLogger(__name__)


def now() -> datetime:
    """Retorna datetime actual en el timezone configurado."""
    return datetime.now(ZoneInfo(Config.APP_TIMEZONE))


def now_iso() -> str:
    """Retorna datetime actual como string ISO 8601 con timezone."""
    return now().isoformat()