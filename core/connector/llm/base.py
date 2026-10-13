from pydantic import SecretStr
from pydantic_settings import BaseSettings
from abc import ABC, abstractmethod

from core.connector.config import LlmProvider


class LlmSettings(BaseSettings):
    base_url: str
    api_key: SecretStr
    model: str
    timeout: float = 60.0


class LlmConnector(ABC):
    def __init__(self, settings: LlmSettings) -> None:
        self._settings = settings

    @property
    @abstractmethod
    def provider(self) -> LlmProvider: ...

    @property
    def model(self) -> str:
        return self._settings.model
