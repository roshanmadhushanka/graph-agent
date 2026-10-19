import psycopg
from psycopg.rows import dict_row
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from core.connector.db.base import DbSettings
from app.protocols import Message
from langgraph.checkpoint.postgres import PostgresSaver


class PostgresSettings(DbSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
        extra="ignore"
    )
    host: str = "localhost"
    port: int = 5432
    user: str
    password: SecretStr
    database: str


def create_postgres_checkpointer(settings: PostgresSettings | None = None) -> PostgresSaver:
    settings = settings or PostgresSettings()
    conn = psycopg.connect(
        host=settings.host,
        port=settings.port,
        user=settings.user,
        password=settings.password.get_secret_value(),
        dbname=settings.database,
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row
    )
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return checkpointer


class PostgresConversationStore:
    def __init__(self, settings: PostgresSettings | None = None) -> None:
        self._settings = settings or PostgresSettings()
        self._conn = psycopg.connect(
            host=self._settings.host,
            port=self._settings.port,
            user=self._settings.user,
            password=self._settings.password.get_secret_value(),
            dbname=self._settings.database,
            autocommit=True
        )
        with self._conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages
                (
                    id
                    BIGINT
                    GENERATED
                    ALWAYS AS
                    IDENTITY
                    PRIMARY
                    KEY,
                    conversation_id
                    TEXT
                    NOT
                    NULL,
                    role
                    TEXT
                    NOT
                    NULL,
                    content
                    TEXT
                    NOT
                    NULL,
                    created_at
                    TIMESTAMPTZ
                    NOT
                    NULL
                    DEFAULT
                    now
                (
                )
                    )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_messages_conv "
                "ON messages (conversation_id, id)"
            )

    def save(self, conversation_id: str, role: str, content: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (%s, %s, %s)""",
                (conversation_id, role, content),
            )

    def history(self, conversation_id: str) -> list[Message]:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT role, content
                FROM messages
                WHERE conversation_id = %s
                ORDER BY id ASC""",
                (conversation_id,)
            )
            return [Message(role=role, content=content) for role, content in cur.fetchall()]
