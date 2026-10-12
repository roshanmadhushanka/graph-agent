from collections.abc import Callable

from config import DbProvider
from core.connector.config import AppSettings, LlmProvider
from core.connector.llm.lmstudio import LmStudioConnector
from core.protocols import Conversational, ConversationStore
from db.postgres import PostgresConversationStore
from db.sqlite import SqliteConversationStore

_LLM: dict[LlmProvider, Callable[[], Conversational]] = {
    LlmProvider.LM_STUDIO: LmStudioConnector
}

_STORE: dict[DbProvider, Callable[[], ConversationStore]] = {
    DbProvider.POSTGRESQL: PostgresConversationStore,
    DbProvider.SQLITE: SqliteConversationStore
}


def create_llm(provider: LlmProvider | None) -> Conversational:
    return _LLM[provider or AppSettings.llm_provider]()


def create_store(provider: DbProvider | None) -> ConversationStore:
    return _STORE[provider or AppSettings.db_provider]()
