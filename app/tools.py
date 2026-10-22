import ast
import operator
from dataclasses import dataclass
from typing import Any
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable[..., str]


def get_current_time(timezone: str) -> str:
    print("Calling tool: get_current_time")
    return datetime.now(ZoneInfo(timezone)).strftime("%Y-%m-%d %H:%M:%S %Z")


_OPERATORS: dict[type, Callable[..., Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _evaluate(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculate(expression: str) -> str:
    print("Calling tool: calculate")
    return str(_evaluate(ast.parse(expression, mode="eval").body))


TOOLS = [
    Tool(
        name="get_current_time",
        description="Get the current date and time in an IANA timezone",
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone, e.g. America/Chicago or Asia/Colombo",
                }
            },
            "required": ["timezone"]
        },
        func=get_current_time
    ),
    Tool(
        name="calculate",
        description="Evaluate arithemetic expressions with +, -, *, /, **, and % operators",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "e.g. (17 * 23) / 4"
                }
            },
            "required": ["expression"]
        },
        func=calculate
    )
]
