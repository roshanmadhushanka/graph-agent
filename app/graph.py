import operator
from typing import Annotated, TypedDict, Literal, NotRequired

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from core.protocols import Conversational, Message

SUMMARIZE_PROMPT = """
    You maintain a running summary of a conversation. Merge the existing summary with the new messages into one concise summary.
    Keep names, facts, decisions and open questions. Reply with the summary only.
"""


class ChatState(TypedDict):
    messages: Annotated[list[Message], operator.add]
    summary: NotRequired[str]
    summarized_count: NotRequired[int]

def _render(messages: list[Message]) -> str:
    return "\n".join(f"{message["role"]}: {message["content" ]}" for message in messages)

def build_chat_graph(
        llm: Conversational,
        checkpointer: BaseCheckpointSaver,
        system: str | None = None,
        *,
        max_unsummarized: int = 10,
        keep_recent: int = 4
):
    def route(state: ChatState) -> Literal["summarize", "chat"]:
        unsummarized = len(state["messages"]) - state.get("summarized_count", 0)
        return "summarize" if unsummarized >= max_unsummarized else "chat"

    def summarize_node(state: ChatState) -> dict:
        start = state.get("summarized_count", 0)
        cut = len(state["messages"]) - keep_recent
        old_summary = state.get("summary", "")

        prompt = (
            f"Existing summary:\n{old_summary or '(none)'}\n\n"
            f"New messages:\n{_render(state["messages"][start:cut])}"
        )
        new_summary = llm.ask(prompt, system=SUMMARIZE_PROMPT)
        print(f"Summarizing messages:\n>>>>{new_summary}<<<")
        return {"summary": new_summary, "summarized_count": cut}

    def chat_node(state: ChatState) -> dict:
        *history, last = state["messages"]
        answer = llm.ask(last["content"], system=system, history=history)
        return {"messages": [Message(role="assistant", content=answer)]}

    graph = StateGraph(ChatState)
    graph.add_node("summarize", summarize_node)
    graph.add_node("chat", chat_node)
    graph.add_conditional_edges(START, route, ["summarize", "chat"])
    graph.add_edge("summarize", "chat")
    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)
    return graph.compile(checkpointer=checkpointer)
