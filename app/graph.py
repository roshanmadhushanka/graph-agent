import operator
from typing import Annotated, TypedDict, Literal, NotRequired

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.protocols import Conversational, Message
from app.tools import Tool

SUMMARIZE_PROMPT = """
    You maintain a running summary of a conversation. Merge the existing summary with the new messages into one concise summary.
    Keep names, facts, decisions and open questions. Reply with the summary only.
"""


class ChatState(TypedDict):
    messages: Annotated[list[Message], operator.add]
    summary: NotRequired[str]
    summarized_count: NotRequired[int]


def _render(messages: list[Message]) -> str:
    lines = []
    for message in messages:
        for call in message.get("tool_calls", []):
            lines.append(f"assistant called {call["name"]}({call["arguments"]})")
        if message["content"]:
            lines.append(f"{message["role"]}: {message["content"]}")
    return "\n".join(lines)


def build_chat_graph(
        llm: Conversational,
        checkpointer: BaseCheckpointSaver,
        system: str | None = None,
        *,
        tools: list[Tool] | None = None,
        max_unsummarized: int = 10,
        keep_recent: int = 4
):
    tools = tools or []
    tools_by_name = {t.name: t for t in tools}

    def route(state: ChatState) -> Literal["summarize", "agent"]:
        unsummarized = len(state["messages"]) - state.get("summarized_count", 0)
        return "summarize" if unsummarized >= max_unsummarized else "agent"

    def summarize_node(state: ChatState) -> dict:
        messages = state["messages"]
        start = state.get("summarized_count", 0)
        cut = len(messages) - keep_recent

        while cut > start and messages[cut]["role"] != "user":
            cut -= 1

        if cut < start:
            return {}

        prompt = (
            f"Existing summary:\n{state.get("summary") or '(none)'}\n\n"
            f"New messages:\n{_render(state["messages"][start:cut])}"
        )
        new_summary = llm.ask(prompt, system=SUMMARIZE_PROMPT)
        print(f"Summarizing messages:\n>>>>{new_summary}<<<")
        return {"summary": new_summary, "summarized_count": cut}

    def agent_node(state: ChatState) -> dict:
        start = state.get("summarized_count", 0)
        prompt_system = system or ""
        if summary := state.get("summary"):
            prompt_system += f"\n\nSummary of the earlier conversation:\n{summary}"

        reply = llm.ask_with_tools(state["messages"][start:], tools, system=prompt_system or None)
        return {"messages": [reply]}

    def should_continue(state: ChatState) -> str:
        return "tools" if state["messages"][-1].get("tool_calls") else END

    def tools_node(state: ChatState) -> dict:
        results: list[Message] = []
        for call in state["messages"][-1].get("tool_calls", []):
            tool = tools_by_name[call["name"]]
            if not tool:
                raise ValueError(f"Tool {call["name"]} not found")

            try:
                output = tool.func(**call["arguments"])
            except Exception as e:
                output = f"Error: {e}"
            results.append(
                Message(role="tool", content=output, tool_call_id=call["id"])
            )
        return {"messages": results}

    # def chat_node(state: ChatState) -> dict:
    #     *history, last = state["messages"]
    #     answer = llm.ask(last["content"], system=system, history=history)
    #     return {"messages": [Message(role="assistant", content=answer)]}

    graph = StateGraph(ChatState)
    graph.add_node("summarize", summarize_node)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.add_conditional_edges(START, route, ["summarize", "agent"])
    graph.add_edge("summarize", "agent")
    graph.add_conditional_edges("agent", should_continue, ["tools", END])
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=checkpointer)
