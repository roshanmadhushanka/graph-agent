from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from core.connector.llm.base import LlmSettings, LlmConnector
from core.connector.config import LlmProvider
from openai.types.chat import ChatCompletionMessageParam
from openai import OpenAI
from typing import cast

from app.protocols import Message


class LmStudioSettings(LlmSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LMSTUDIO_",
        extra="ignore"
    )
    base_url: str = "http://localhost:1234/v1"
    api_key: SecretStr = SecretStr("lm-studio")
    model: str = "qwen/qwen3.5-9b"


class LmStudioConnector(LlmConnector):

    def __init__(self, settings: LlmSettings | None = None) -> None:
        super().__init__(settings or LmStudioSettings())
        self._client = OpenAI(
            base_url=self._settings.base_url,
            api_key=self._settings.api_key.get_secret_value(),
            timeout=self._settings.timeout,
        )

    @property
    def provider(self) -> LlmProvider:
        return LlmProvider.LM_STUDIO

    def ask(self, user: str, *, system: str | None = None, history: list[Message] | None = None) -> str:
        messages: list[ChatCompletionMessageParam] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.extend(
            cast(ChatCompletionMessageParam, {"role": msg["role"], "content": msg["content"]}) for msg in history or [])
        messages.append({"role": "user", "content": user})

        response = self._client.chat.completions.create(
            model=self._settings.model,
            messages=messages,
        )
        return response.choices[0].message.content or ""
