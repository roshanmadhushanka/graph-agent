import sqlite3
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.protocols import Message


class SqliteSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SQLITE_",
        extra="ignore"
    )
    path: str = "chat.db"


class SqliteConversationStore:
    def __init__(self, settings: SqliteSettings | None = None) -> None:
        self._settings = settings or SqliteSettings()
        self._conn = sqlite3.connect(self._settings.path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    def save(self, conversation_id: str, role: str, content: str) -> None:
        self._conn.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )
        self._conn.commit()

    def history(self, conversation_id: str) -> list[Message]:
        rows = self._conn.execute(
            """
            SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id ASC""",
            (conversation_id,)
        ).fetchall()
        return [Message(role=role, content=content) for role, content in rows]