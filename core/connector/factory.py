from collections.abc import Callable

from core.connector.config import AppSettings, LlmProvider
from core.connector.llm.lmstudio import LmStudioConnector
from core.protocols import Conversational

_LLM: dict[LlmProvider, Callable[[], Conversational]] = {
    LlmProvider.LM_STUDIO: LmStudioConnector
}


def create_llm(provider: LlmProvider | None) -> Conversational:
    return _LLM[provider or AppSettings.llm_provider]()
