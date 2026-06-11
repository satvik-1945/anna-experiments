#!/usr/bin/env python3
"""calc — a CS-101 Anna Executa plugin with safe arithmetic evaluation."""
from __future__ import annotations

import ast
import json
import operator
import sys
from typing import Any

MANIFEST = {
    "name": "calc",
    "display_name": "Calculator",
    "version": "1.0.0",
    "description": "Evaluate arithmetic expressions and track calculation history.",
    "tools": [
        {
            "name": "calc",
            "description": "Evaluate math expressions or return recent calculation history.",
            "parameters": [
                {
                    "name": "action",
                    "type": "string",
                    "description": "One of: evaluate, history",
                    "required": True,
                },
                {
                    "name": "expression",
                    "type": "string",
                    "description": "Arithmetic expression (required for evaluate)",
                    "required": False,
                },
                {
                    "name": "limit",
                    "type": "integer",
                    "description": "Max history entries to return (default 10)",
                    "required": False,
                },
            ],
        }
    ],
}

_BIN_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARY_OPS: dict[type, Any] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_HISTORY: list[dict[str, Any]] = []
_MAX_HISTORY = 50


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return float(_UNARY_OPS[type(node.op)](_safe_eval(node.operand)))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return float(_BIN_OPS[type(node.op)](left, right))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")


def evaluate_expression(expression: str) -> dict[str, Any]:
    expr = expression.strip()
    if not expr:
        raise ValueError("expression must not be empty")
    tree = ast.parse(expr, mode="eval")
    result = _safe_eval(tree)
    entry = {"expression": expr, "result": result}
    _HISTORY.append(entry)
    if len(_HISTORY) > _MAX_HISTORY:
        del _HISTORY[:- _MAX_HISTORY]
    return entry


def get_history(limit: int = 10) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be at least 1")
    return {"entries": _HISTORY[-limit:]}


def invoke(tool: str, args: dict[str, Any]) -> dict[str, Any]:
    if tool != "calc":
        raise ValueError(f"unknown tool: {tool}")

    action = args.get("action", "")
    if action == "evaluate":
        expression = args.get("expression")
        if not expression:
            raise ValueError("expression is required for evaluate")
        return {"success": True, "data": evaluate_expression(str(expression))}
    if action == "history":
        limit = int(args.get("limit", 10))
        return {"success": True, "data": get_history(limit)}
    raise ValueError(f"unknown action: {action}")


def handle(req: dict[str, Any]) -> dict[str, Any]:
    method = req.get("method")
    if method == "describe":
        return {"result": MANIFEST}
    if method == "invoke":
        params = req.get("params") or {}
        try:
            return {"result": invoke(params.get("tool", ""), params.get("arguments") or {})}
        except ValueError as exc:
            return {"error": {"code": -32601, "message": str(exc)}}
        except Exception as exc:  # noqa: BLE001
            return {"error": {"code": -32603, "message": str(exc)}}
    if method == "health":
        return {"result": {"status": "ready"}}
    return {"error": {"code": -32601, "message": f"unknown method: {method}"}}


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            payload = {"error": {"code": -32700, "message": str(exc)}}
            req_id = None
        else:
            payload = handle(req)
            req_id = req.get("id")
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, **payload}) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
