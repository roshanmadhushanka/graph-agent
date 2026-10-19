from app.protocols import Conversational, Message
from langgraph.checkpoint.base import BaseCheckpointSaver
from app.graph import build_chat_graph

class ChatService:
    def __init__(self, llm: Conversational, checkpointer: BaseCheckpointSaver, system: str | None = None) -> None:
        self._graph = build_chat_graph(llm, checkpointer, system)

    def send(self, conversation_id: str, role: str, prompt: str) -> str:
       result = self._graph.invoke(
           {"messages": [Message(role=role, content=prompt)]},
           config={"configurable": {"thread_id": conversation_id}}
       )
       return result["messages"][-1]["content"]

