# src/api/socket_events.py
import logging
from flask import request as flask_request
from flask_socketio import emit

logger = logging.getLogger(__name__)


def register_socket_events(socketio) -> None:
    """
    Registra todos los eventos de SocketIO.

    Uso en src/__init__.py cuando WS_ENABLED=true:
        from src.api.socket_events import register_socket_events
        register_socket_events(socketio)
    """

    @socketio.on("connect")
    def on_connect(auth):
        """Cliente conectado — enviar estado inicial si aplica."""
        try:
            logger.debug(f"Cliente conectado: {flask_request.sid}")
            # emit("evento:sync", data, to=flask_request.sid)
        except Exception:
            logger.error("Error en evento connect", exc_info=True)
            emit("error", {"message": "Error al conectar"})

    @socketio.on("disconnect")
    def on_disconnect():
        """Cliente desconectado."""
        logger.debug(f"Cliente desconectado: {flask_request.sid}")

    @socketio.on("ping")
    def on_ping():
        """Heartbeat para verificar conexión activa."""
        emit("pong")