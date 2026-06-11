# Building Anna Tools — The Correct Workflow

This document reflects what actually works, verified on Anna.app with a live agent.

## The three layers

```
┌─────────────────────────────────────────┐
│  Anna App (manifest.json)               │  User #mentions in chat
│  bundles tools + prompt instructions    │
└────────────────┬────────────────────────┘
                 │
    ┌────────────┴────────────┐
    ▼                         ▼
┌──────────┐           ┌──────────────┐
│  Tool    │           │  Skill       │
│  (.py)   │           │  (SKILL.md)  │
│  runs    │           │  teaches     │
│  code    │           │  when to call│
└──────────┘           └──────────────┘
```

| Layer | What it is | This repo |
|-------|-----------|-----------|
| **Tool** | Long-running process, JSON-RPC 2.0 over stdin/stdout | `executas/calc/calc_plugin.py` |
| **Skill** | Markdown recipe the LLM reads on demand | `skills/calc-helper/SKILL.md` |
| **App** | Manifest bundling tools + system prompt | `manifest.json` |

Start with a **Tool**. Add a **Skill** when you need to teach Anna *when* to call it. Wrap in an **App** when you want a `#mention`-able product.

---

## Tool protocol (non-negotiable)

Every Anna Tool must:

1. **Loop on stdin** — `for line in sys.stdin:` — never exit after one request
2. **JSON-RPC only on stdout** — all logs go to **stderr**
3. **`flush()`** after every stdout write
4. Implement **`describe`** (return manifest), **`invoke`** (run tool), optional **`health`**

```python
for line in sys.stdin:
    req = json.loads(line.strip())
    payload = handle(req)
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), **payload}) + "\n")
    sys.stdout.flush()
```

See [Executa intro](https://anna.partners/developers/tools/executa-intro) for the full spec.

---

## Development workflow (every new tool)

### Step 1 — Write the plugin

Copy `executas/calc/` as your starting point. Implement `describe` / `invoke` / `health`.

### Step 2 — Test locally (before touching Anna)

```bash
./scripts/smoke-test.sh
```

Or manually:

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | python3 executas/calc/calc_plugin.py
```

### Step 3 — Mint on Executa Hub

Go to [anna.partners/executa](https://anna.partners/executa) → **My Tools** → create tool → click **Mint** for Tool ID.

| Hub field | Calculator value |
|-----------|-----------------|
| Name | `Calculator` |
| Distribution Type | `local` (for local dev) |
| Executable Name | `calc-plugin` |
| Supports Executa Protocol | checked |
| Manifest JSON | Copy from `calc_plugin.py` MANIFEST dict |

Save the minted Tool ID (e.g. `tool-yourhandle-calci-abc123`).

### Step 4 — Install to Anna

```bash
echo '{"tool_id": "YOUR-MINTED-TOOL-ID"}' > anna.local.json
./scripts/install-direct-to-anna.sh
```

This copies your plugin into `~/.anna/executa/` where Anna.app actually loads tools from.

### Step 5 — Restart Anna.app

Fully quit (Cmd+Q), reopen. Check **Agents → Executa: 1/1 running**.

### Step 6 — Test in chat

```
Use the calc tool with action evaluate and expression 17*23
Show my recent calculator history
```

History only works if the **tool** ran — the LLM cannot fake it.

### Step 7 — Add Skill (optional)

Set on the machine running Anna.app:

```bash
export MATRIX_SKILLS_DIR=/path/to/anna-experiments/skills
```

Restart Anna.app. The skill teaches Anna when to call your tool.

---

## What NOT to do (lessons learned)

| Wrong approach | Why it fails |
|---------------|-------------|
| `uv tool install .` + Hub Distribution = **UV** | Anna tries PyPI (`uv tool install calc-executa`), not your local file install |
| **Rediscover Local** only | Scans `~/.anna/executa/bin` — empty until you install there |
| `export MATRIX_SKILLS_DIR` in a random terminal | Must be set in Anna.app's environment, then restart |
| Assuming correct math = tool ran | LLMs can do basic arithmetic without your plugin |

### The right install path for local development

**`./scripts/install-direct-to-anna.sh`** → installs to `~/.anna/executa/` → restart Anna.app.

Alternative for Hub-driven install: Distribution Type = **`local`**, archive path = `dist/calc-executa-dev.tar.gz` (build with `./scripts/build-local-archive.sh`).

---

## How to tell the tool actually ran

| Signal | Tool ran | LLM only |
|--------|----------|----------|
| Agents → Executa | `1/1 running` | `not installed` |
| `~/.anna/executa/bin/calc-plugin` exists | Yes | No |
| "Show calculator history" | Lists expressions | Makes something up |
| Chat response | Tool call indicator | Emoji + LaTeX prose |

---

## Where Anna loads tools from

Anna.app scans `~/.anna/executa/bin/` on startup. The install script creates:

```
~/.anna/executa/
├── bin/calc-plugin          → shim to current version
└── tools/{tool_id}/
    ├── current → dev
    └── dev/
        ├── calc_plugin.py
        ├── manifest.json
        └── bin/calc-plugin
```

Your git repo is **not** scanned. Files must be in `~/.anna/executa/`.

---

## Further reading

- [Anna Concepts](https://anna.partners/developers/overview/concepts)
- [Python quickstart](https://anna.partners/developers/tools/executa-python)
- [Skill format](https://anna.partners/developers/skills/skill-format)
- [Example plugins repo](https://github.com/whtcjdtc2007/anna-executa-examples)
