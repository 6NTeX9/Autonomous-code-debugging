import json
import logging
from typing import Dict, Set, Any
from fastapi import WebSocket

logger = logging.getLogger("debugging_agent.ws")

class WebSocketManager:
    def __init__(self):
        # session_id -> Set[WebSocket]
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"WebSocket client connected to session {session_id}")

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"WebSocket client disconnected from session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any]):
        if session_id in self.active_connections:
            dead_connections = set()
            for ws in self.active_connections[session_id]:
                try:
                    await ws.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending ws message: {e}")
                    dead_connections.add(ws)
            for ws in dead_connections:
                self.disconnect(session_id, ws)

ws_manager = WebSocketManager()
