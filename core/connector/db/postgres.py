from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from core.connector.db.base import DbSettings
from core.protocols import Message


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


class PostgresConversationStore:
    def save(self, conversation_id: str, role: str, content: str) -> None: ...

    def history(self, conversation_id: str) -> list[Message]: ...
