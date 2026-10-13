from core.protocols import Conversational, ConversationStore

class ChatService:
    def __init__(self, llm: Conversational, store: ConversationStore, system: str | None = None) -> None:
        self._llm = llm
        self._store = store
        self._system = system

    def send(self, conversation_id: str, prompt: str) -> str:
        history = self._store.history(conversation_id)
        answer = self._llm.ask(prompt, system=self._system, history=history)
        self._store.save(conversation_id, "user", prompt)
        self._store.save(conversation_id, "assistant", answer)
        return answer