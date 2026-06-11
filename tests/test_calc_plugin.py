"""Unit tests for the calc Executa plugin."""
import importlib.util
import json
import sys
from pathlib import Path

PLUGIN_PATH = Path(__file__).resolve().parents[1] / "executas" / "calc" / "calc_plugin.py"


def _load_plugin():
    spec = importlib.util.spec_from_file_location("calc_plugin", PLUGIN_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_describe():
    mod = _load_plugin()
    resp = mod.handle({"method": "describe", "id": 1})
    assert resp["result"]["name"] == "calc"
    assert resp["result"]["tools"][0]["name"] == "calc"


def test_evaluate():
    mod = _load_plugin()
    mod._HISTORY.clear()
    resp = mod.handle(
        {
            "method": "invoke",
            "id": 2,
            "params": {
                "tool": "calc",
                "arguments": {"action": "evaluate", "expression": "2+3*4"},
            },
        }
    )
    assert resp["result"]["success"] is True
    assert resp["result"]["data"]["result"] == 14.0


def test_history():
    mod = _load_plugin()
    mod._HISTORY.clear()
    mod.invoke("calc", {"action": "evaluate", "expression": "1+1"})
    mod.invoke("calc", {"action": "evaluate", "expression": "2+2"})
    resp = mod.handle(
        {
            "method": "invoke",
            "id": 3,
            "params": {
                "tool": "calc",
                "arguments": {"action": "history", "limit": 2},
            },
        }
    )
    entries = resp["result"]["data"]["entries"]
    assert len(entries) == 2
    assert entries[-1]["result"] == 4.0


def test_rejects_unsafe_expression():
    mod = _load_plugin()
    resp = mod.handle(
        {
            "method": "invoke",
            "id": 4,
            "params": {
                "tool": "calc",
                "arguments": {"action": "evaluate", "expression": "__import__('os').system('ls')"},
            },
        }
    )
    assert "error" in resp


def test_json_rpc_roundtrip():
    mod = _load_plugin()
    req = {"jsonrpc": "2.0", "method": "health", "id": 99}
    resp = mod.handle(req)
    frame = json.dumps({"jsonrpc": "2.0", "id": req["id"], **resp})
    parsed = json.loads(frame)
    assert parsed["result"]["status"] == "ready"
