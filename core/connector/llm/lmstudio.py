import json

from openai.types import FunctionParameters
from openai.types.chat.chat_completion_message_function_tool_call_param import Function
from openai.types.shared_params import FunctionDefinition
from pydantic import SecretStr
from pydantic_settings import SettingsConfigDict
from core.connector.llm.base import LlmSettings, LlmConnector
from core.connector.config import LlmProvider
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionToolMessageParam, ChatCompletionAssistantMessageParam, ChatCompletionMessageFunctionToolCall, \
    ChatCompletionMessageFunctionToolCallParam, ChatCompletionUserMessageParam, ChatCompletionFunctionToolParam
from openai import OpenAI
from typing import cast, Any
from app.protocols import Message, ToolCall
from app.tools import Tool


class LmStudioSettings(LlmSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LMSTUDIO_",
        extra="ignore"
    )
    base_url: str = "http://localhost:1234/v1"
    api_key: SecretStr = SecretStr("lm-studio")
    model: str = "qwen/qwen3.5-9b"


def _to_openai_messages(messages: list[Message], system: str | None) -> list[ChatCompletionMessageParam]:
    result: list[ChatCompletionMessageParam] = []
    if system:
        result.append(ChatCompletionSystemMessageParam(role="system", content=system))
    for msg in messages:
        if msg["role"] == "tool":
            result.append(ChatCompletionToolMessageParam(
                role="tool",
                tool_call_id=msg["tool_call_id"],
                content=msg["content"]
            ))
        elif msg.get("tool_calls"):
            result.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                content=msg["content"] or None,
                tool_calls=[
                    ChatCompletionMessageFunctionToolCallParam(
                        id=call["id"],
                        type="function",
                        function=Function(
                            name=call["name"],
                            arguments=json.dumps(call["arguments"])
                        )
                    ) for call in msg["tool_calls"]
                ]
            ))
        elif msg["role"] == "assistant":
            result.append(ChatCompletionAssistantMessageParam(
                role="assistant",
                content=msg["content"]
            ))
        elif msg["role"] == "system":
            result.append(ChatCompletionSystemMessageParam(
                role="system",
                content=msg["content"]
            ))
        else:
            result.append(ChatCompletionUserMessageParam(
                role="user",
                content=msg["content"]
            ))

    return result


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

    def ask_with_tools(self, messages: list[Message], tools: list[Tool], *, system: str | None = None) -> Message:
        response = self._client.chat.completions.create(
            model=self._settings.model,
            messages=_to_openai_messages(messages, system=system),
            tools=[
                ChatCompletionFunctionToolParam(
                    type="function",
                    function=FunctionDefinition(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.parameters
                    )
                ) for tool in tools
            ]
        )
        reply = response.choices[0].message
        message = Message(role="assistant", content=reply.content or "")
        if reply.tool_calls:
            message["tool_calls"] = [
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(call.function.arguments or "{}")
                ) for call in reply.tool_calls if isinstance(call, ChatCompletionMessageFunctionToolCall)]
        return message
