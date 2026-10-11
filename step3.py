import re
import json
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

MODEL = "qwen/qwen3.5-9b"
THINK = re.compile(r"<think>(.*?)</think>", re.DOTALL)
ITEMS = {
    "SKU-4471": {"desc": "Chicken breast 40lb case", "cost": 62.10, "list": 84.00, "floor_margin": 0.14},
}

def ask(system: str, user: str) -> tuple[str, str]:
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    message = response.choices[0].message
    content = message.content or ""

    reasoning = getattr(message, "reasoning_content", None)
    if not reasoning:
        match = THINK.search(content)
        reasoning = match.group(1).strip() if match else ""

    answer = THINK.sub("", content).strip()
    return reasoning, answer



class State(TypedDict, total=False):
    request: dict
    context: dict
    answer: str
    recommendation: dict


if __name__ == "__main__":
    builder = StateGraph(State)
    builder.add_node("analyze", analyze)
    builder.add_edge(START, "analyze")
    builder.add_edge("analyze", END)
    graph = builder.compile()

    result = graph.invoke({"question": "Cost $62.10, price $69. What is margin %?"})
    print(result)
