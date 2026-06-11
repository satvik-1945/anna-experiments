# Team Briefing — Anna Calculator Demo

Use this for your NR Discord presentation.

## 30-second pitch

> Anna lets you extend AI with **real code**. We built a calculator Tool — a Python process that speaks JSON-RPC over stdin. Anna calls it, gets a deterministic answer. No hallucinated math. Add a Skill (markdown) and the agent knows *when* to use it. Bundle into an App and users `#mention` it from chat.

## What we built

| Component | File | One-liner |
|-----------|------|-----------|
| Tool | `executas/calc/calc_plugin.py` | Safe arithmetic via JSON-RPC stdio |
| Skill | `skills/calc-helper/SKILL.md` | Teaches Anna when to call the tool |
| App | `manifest.json` | Bundles both for `#calc-buddy` |

## Architecture (one slide)

```
User: "What is 17 × 23?"
        ↓
Anna LLM picks tool "calc"
        ↓
Spawns calc_plugin.py (JSON-RPC invoke)
        ↓
Returns { result: 391 }
        ↓
Anna: "391"
```

**Key insight:** The LLM decides *when* to call. The Tool decides *what the answer is*.

## Live demo script (5 minutes)

| Step | Do | Show |
|------|-----|------|
| 1 | `./scripts/smoke-test.sh` | Plugin works locally |
| 2 | Show `calc_plugin.py` stdin loop | "This is the Anna protocol contract" |
| 3 | Show Agents dashboard | Executa: 1/1 running |
| 4 | Chat: "Use calc tool to evaluate 17*23" | Tool call → 391 |
| 5 | Chat: "Show calculator history" | Proves tool ran (LLM can't fake this) |
| 6 | Show `SKILL.md` | "Skill = prompt-as-code, no process" |

## Tool vs Skill vs App

| | Tool | Skill | App |
|--|------|-------|-----|
| Form | Python process | Markdown file | JSON manifest |
| Runs code? | Yes | No | No (metadata) |
| When to use | Computation, APIs, side effects | Recipes, runbooks | End-user product |

**Rule:** Start with the smallest unit. Tool → Skill → App.

## The install workflow (what actually works)

1. Write plugin → `./scripts/smoke-test.sh`
2. Mint Tool ID at anna.partners/executa
3. `./scripts/install-direct-to-anna.sh` (installs to `~/.anna/executa/`)
4. Restart Anna.app
5. Test in chat

**Do not rely on** `uv tool install` + UV distribution for local dev — Anna pulls from PyPI, not your repo.

## Q&A prep

**Q: Do we need an SDK?**
No. JSON-RPC over stdin. Any language.

**Q: How is this different from MCP?**
Similar transport idea (stdio + JSON), but Anna-specific protocol (`describe`/`invoke`/`health`) and Hub lifecycle.

**Q: Can the LLM just do math?**
Yes — that's why we demo history. Only the Tool has session memory.

**Q: How do we ship to other users?**
Publish via Executa Hub (distribution: local archive or binary). See [docs/ANNA_TOOLS.md](ANNA_TOOLS.md).

## Repo link

Point teammates to:
- [README.md](../README.md) — quick start
- [docs/ANNA_TOOLS.md](ANNA_TOOLS.md) — full workflow
- [docs/BUILD_NEW_TOOL.md](BUILD_NEW_TOOL.md) — copy for next tool
