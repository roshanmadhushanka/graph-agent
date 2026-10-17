from enum import StrEnum
from pydantic_settings import BaseSettings, SettingsConfigDict


class LlmProvider(StrEnum):
    LM_STUDIO = "lm-studio"


class DbProvider(StrEnum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MEMORY = "memory"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    llm_provider: LlmProvider = LlmProvider.LM_STUDIO
    db_provider: DbProvider = DbProvider.SQLITE
