import logging
import sqlite3
from typing import List, Tuple

from chat_app.config import config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db: str = config.db_path):
        self.db = db
        self.conn = None
        self.cursor = None

    def start(self):
        logger.info("Starting database connection.")
        self._connect()
        self._init_db()

    def stop(self):
        logger.info("Closing database connection.")
        self.cursor.close()
        self.conn.close()

    def _connect(self):
        """Establishes a connection to the SQLite database."""  # AI generated doc-string
        try:
            self.conn = sqlite3.connect(self.db)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def _init_db(self):
        # messages table to store chat history
        # each message has a client_id, role (user/ai), content, and timestamp
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # conversations table to track the latest response_id per client.
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                client_id TEXT PRIMARY KEY,
                last_response_id TEXT
            )
            """
        )
        self.conn.commit()

    def get_last_response_id(self, client_id: str) -> str | None:
        """Retrieve the last response ID for a client, or None if not found."""  # AI generated doc-string
        self.cursor.execute(
            "SELECT last_response_id FROM conversations WHERE client_id = ?",
            (client_id,),
        )
        row = self.cursor.fetchone()

        return row[0] if row else None

    def save_last_response_id(self, client_id: str, response_id: str) -> None:
        """Save the last response ID for a client, or update if it already exists."""  # AI generated doc-string
        self.cursor.execute(
            """
            INSERT INTO conversations (client_id, last_response_id)
            VALUES (?, ?)
            ON CONFLICT(client_id) DO UPDATE SET last_response_id = excluded.last_response_id
            """,
            (client_id, response_id),
        )
        self.conn.commit()

    def save_message(self, client_id: str, role: str, content: str) -> None:
        """Persist a single message to the DB."""  # AI generated doc-string
        self.cursor.execute(
            "INSERT INTO messages (client_id, role, content) VALUES (?, ?, ?)",
            (client_id, role, content),
        )
        self.conn.commit()

    def load_history(self, client_id: str) -> List[Tuple[str, str]]:
        """Load all messages for a client ordered oldest->newest.
        Returns a list of tuples (role, content).
        """
        self.cursor.execute(
            "SELECT role, content FROM messages WHERE client_id = ? ORDER BY id ASC",
            (client_id,),
        )
        rows = self.cursor.fetchall()

        return rows
