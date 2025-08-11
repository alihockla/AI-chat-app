import logging
from typing import Dict, List, Tuple, Optional
from fastapi import WebSocket
from chat_app.database.database import Database

logger = logging.getLogger(__name__)


class ChatManager:
    """
    Manages chat sessions, message storage, and websocket connections and all DB operations.
    """

    def __init__(self, db: Database):
        self.db = db
        self.active_connections: Dict[str, WebSocket] = {}
        # in-memory copy of history for quick access (optional, useful in a real/production app to improve performance)
        self.chat_history: Dict[str, List[Tuple[str, str]]] = {}

    async def connect(self, client_id: str, websocket: WebSocket) -> None:
        """
        Accept the websocket and stream history to client.

        We send each stored message prefixed with "HISTORY::" and a final "HISTORY_END"
        so the client can render history separately from live messages.
        """  # AI generated doc-string
        await websocket.accept()
        self.active_connections[client_id] = websocket

        # load history from DB and keep in memory
        history = self.db.load_history(client_id)
        self.chat_history[client_id] = history

        # Stream history messages with a prefix so client can distinguish them
        for role, content in history:
            await websocket.send_text(f"HISTORY::{role}: {content}")

        # mark the end of history
        await websocket.send_text("HISTORY_END")

    def disconnect(self, client_id: str) -> None:
        """Remove in-memory structures for a disconnected client."""  # AI generated doc-string
        self.active_connections.pop(client_id, None)
        self.chat_history.pop(client_id, None)

    def store_message(self, client_id: str, role: str, content: str) -> None:
        """Persist and update in-memory history."""  # AI generated doc-string
        # persist the message
        self.db.save_message(client_id, role, content)
        # update in-memory copy
        self.chat_history.setdefault(client_id, []).append((role, content))

    async def send_live_message(self, client_id: str, role: str, content: str) -> bool:
        """Send a live message to a connected client (returns True if sent)."""  # AI generated doc-string
        ws: Optional[WebSocket] = self.active_connections.get(client_id)
        if not ws:
            return False
        await ws.send_text(f"MESSAGE::{role}: {content}")
        return True

    def get_history(self, client_id: str) -> List[Tuple[str, str]]:
        """Return in-memory history if present, otherwise load from DB."""  # AI generated doc-string
        if client_id in self.chat_history:

            return self.chat_history[client_id]
        history = self.db.load_history(client_id)
        self.chat_history[client_id] = history
        return history

    def get_last_response_id(self, client_id):
        """Retrieve the last response ID for a client."""  # AI generated doc-string
        return self.db.get_last_response_id(client_id)

    def save_last_response_id(self, client_id, response_id):
        """Save the last response ID for a client."""  # AI generated doc-string
        logger.debug(f"Updating last response ID for {client_id} -> {response_id}")
        self.db.save_last_response_id(client_id, response_id)
