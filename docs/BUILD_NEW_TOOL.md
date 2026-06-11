# Building Your Next Anna Tool

Copy the calculator pattern. Every new tool follows the same skeleton.

## 1. Scaffold

```bash
cp -r executas/calc executas/my-tool
```

Edit `executas/my-tool/my_tool_plugin.py` (rename from `calc_plugin.py`):

- Update `MANIFEST` (name, tools, parameters)
- Implement `invoke()` with your logic
- Keep the stdin loop unchanged

## 2. File checklist

```
executas/my-tool/
├── my_tool_plugin.py    # JSON-RPC loop + your logic
├── executa.json         # { "tool_id": "tool-dev-my-tool", "type": "python" }
└── pyproject.toml       # package name + entry point (optional for local install)
```

## 3. The plugin skeleton

```python
MANIFEST = {
    "name": "my-tool",
    "display_name": "My Tool",
    "version": "1.0.0",
    "description": "What it does.",
    "tools": [{
        "name": "my-tool",
        "description": "One-line description for the LLM.",
        "parameters": [
            {"name": "action", "type": "string", "required": True},
            # ... your params
        ],
    }],
}

def invoke(tool: str, args: dict) -> dict:
    action = args.get("action")
    if action == "do_thing":
        return {"success": True, "data": {"result": "..."}}
    raise ValueError(f"unknown action: {action}")

def handle(req: dict) -> dict:
    method = req.get("method")
    if method == "describe":
        return {"result": MANIFEST}
    if method == "invoke":
        params = req.get("params") or {}
        try:
            return {"result": invoke(params.get("tool", ""), params.get("arguments") or {})}
        except ValueError as exc:
            return {"error": {"code": -32601, "message": str(exc)}}
    if method == "health":
        return {"result": {"status": "ready"}}
    return {"error": {"code": -32601, "message": f"unknown method: {method}"}}

def main() -> None:
    for line in sys.stdin:
        # ... parse, handle, write, flush (copy from calc_plugin.py)
```

## 4. Test locally

Add smoke tests to `scripts/smoke-test.sh` or create `tests/test_my_tool_plugin.py`.

```bash
./scripts/smoke-test.sh
```

## 5. Register and install

1. Mint at [anna.partners/executa](https://anna.partners/executa)
2. Save Tool ID to `anna.local.json`
3. Update `scripts/install-direct-to-anna.sh` to point at your plugin path, or generalize it to accept a tool name argument
4. Run install, restart Anna.app, test in chat

## 6. Add a Skill (optional)

```
skills/my-tool-helper/SKILL.md
```

Frontmatter + body that tells Anna when and how to call your tool. See `skills/calc-helper/SKILL.md`.

## 7. Bundle into an App (optional)

Update `manifest.json`:

```json
{
  "schema": 1,
  "required_executas": [{ "tool_id": "your-minted-tool-id" }],
  "system_prompt_addendum": "Instructions when user #mentions your app."
}
```

## Design tips

- Use an `action` discriminator on one tool instead of many tiny tools
- Never use `eval()` on user input — parse safely (see calculator's `ast` approach)
- Logs to **stderr** only
- Keep the stdin loop — it is the most common bug when plugins show as "Stopped"
