from collections.abc import Callable

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from core.connector.config import AppSettings, LlmProvider
from core.connector.config import DbProvider
from core.connector.db.postgres import PostgresConversationStore, create_postgres_checkpointer
from core.connector.db.sqlite import SqliteConversationStore
from core.connector.llm.lmstudio import LmStudioConnector
from app.protocols import Conversational, ConversationStore

_LLM: dict[LlmProvider, Callable[[], Conversational]] = {
    LlmProvider.LM_STUDIO: LmStudioConnector
}

_STORE: dict[DbProvider, Callable[[], ConversationStore]] = {
    DbProvider.POSTGRESQL: PostgresConversationStore,
    DbProvider.SQLITE: SqliteConversationStore
}

_CHECKPOINT: dict[DbProvider, Callable[[], BaseCheckpointSaver]] = {
    DbProvider.MEMORY: InMemorySaver,
    DbProvider.POSTGRESQL: create_postgres_checkpointer,
}


def create_llm(provider: LlmProvider | None = None) -> Conversational:
    return _LLM[provider or AppSettings().llm_provider]()


def create_store(provider: DbProvider | None = None) -> ConversationStore:
    return _STORE[provider or AppSettings().db_provider]()


def create_checkpointer(provider: DbProvider | None = None) -> BaseCheckpointSaver:
    return _CHECKPOINT[provider or AppSettings().db_provider]()
