from typing import Protocol, runtime_checkable, TypedDict, Any, NotRequired
from app.tools import Tool


class ToolCall(TypedDict):
    id: str
    name: str
    arguments: dict[str, Any]


class Message(TypedDict):
    role: str
    content: str
    tool_calls: NotRequired[list[ToolCall]]
    tool_call_id: NotRequired[str]


@runtime_checkable
class Conversational(Protocol):
    def ask(self, user: str, *, system: str | None = None, history: list[Message] | None = None) -> str: ...


@runtime_checkable
class ConversationStore(Protocol):
    def save(self, conversation_id: str, role: str, content: str) -> None: ...

    def history(self, conversation_id: str) -> list[Message]: ...


@runtime_checkable
class ToolCalling(Protocol):
    def ask_with_tools(self, messages: list[Message], tools: list[Tool], *, system: str | None = None) -> Message: ...


@runtime_checkable
class AgentModel(Conversational, ToolCalling, Protocol):
    """A protocol representing an agent model that can engage in conversation and call tools."""
