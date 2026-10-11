from typing import Protocol, runtime_checkable

@runtime_checkable
class Conversational(Protocol):

    def ask(self, user: str, *, system: str | None = None) -> str: ...