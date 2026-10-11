from pydantic_settings import SettingsConfigDict
from core.connector.db.base import DbSettings


class PostgresSettings(DbSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
        extra="ignore"
    )
    database: str = "postgres"
