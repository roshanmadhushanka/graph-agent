from typing import Protocol, runtime_checkable, TypedDict


class Message(TypedDict):
    role: str
    content: str


@runtime_checkable
class Conversational(Protocol):
    def ask(self, user: str, *, system: str | None = None, history: list[Message] | None = None) -> str: ...


@runtime_checkable
class ConversationStore(Protocol):
    def save(self, conversation_id: str, role: str, content: str) -> None: ...

    def history(self, conversation_id: str) -> list[Message]: ...
