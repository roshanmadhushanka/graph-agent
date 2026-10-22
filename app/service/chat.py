from app.protocols import AgentModel, Message
from langgraph.checkpoint.base import BaseCheckpointSaver
from app.graph import build_chat_graph
from app.tools import Tool

class ChatService:
    def __init__(self, llm: AgentModel, checkpointer: BaseCheckpointSaver, system: str | None = None,
                 tools: list[Tool] | None = None) -> None:
        self._graph = build_chat_graph(llm, checkpointer, system, tools=tools)

    def send(self, conversation_id: str, role: str, prompt: str) -> str:
       result = self._graph.invoke(
           {"messages": [Message(role=role, content=prompt)]},
           config={"configurable": {"thread_id": conversation_id}}
       )
       return result["messages"][-1]["content"]

