# Anna Calculator

A reference implementation of an [Anna Executa](https://anna.partners/developers/tools/executa-intro) Tool — a safe arithmetic calculator the AI agent calls over JSON-RPC, plus an optional Skill that teaches Anna when to use it.

Built as a minimal, copy-paste template for building more Anna tools.

## What this repo contains

| Piece | Path | Role |
|-------|------|------|
| **Tool** | `executas/calc/calc_plugin.py` | Runnable plugin — Anna spawns it, sends JSON-RPC on stdin |
| **Skill** | `skills/calc-helper/SKILL.md` | Markdown recipe — tells Anna *when* to call the tool |
| **App manifest** | `manifest.json` | Bundles tool + prompt for `#calc-buddy` mentions |

## Quick start

```bash
# 1. Verify the plugin protocol locally
./scripts/smoke-test.sh

# 2. Mint your tool at anna.partners/executa, then save the Tool ID
cp anna.local.json.example anna.local.json   # paste your minted tool_id

# 3. Install into Anna (~/.anna/executa/)
./scripts/install-direct-to-anna.sh

# 4. Quit Anna.app (Cmd+Q), reopen, test in chat:
#    "Use the calc tool to evaluate 17*23"
```

## Documentation

| Doc | Audience |
|-----|----------|
| [docs/ANNA_TOOLS.md](docs/ANNA_TOOLS.md) | How Anna tools work + the correct install workflow |
| [docs/BUILD_NEW_TOOL.md](docs/BUILD_NEW_TOOL.md) | Copy the calculator pattern for your next tool |
| [docs/PRESENTATION_SCRIPT.md](docs/PRESENTATION_SCRIPT.md) | **20-min voice talk — read this aloud** |
| [docs/PRESENTER_CHECKLIST.md](docs/PRESENTER_CHECKLIST.md) | 5-min preflight checklist |
| [docs/TEAM_BRIEFING.md](docs/TEAM_BRIEFING.md) | Short demo outline |

## Project structure

```
anna-experiments/
├── executas/calc/           # Tool plugin (JSON-RPC over stdio)
├── skills/calc-helper/      # Skill (SKILL.md)
├── manifest.json            # Anna App manifest
├── app.json                 # App Store listing metadata
├── scripts/
│   ├── smoke-test.sh        # Local protocol tests
│   └── install-direct-to-anna.sh   # Install to ~/.anna/executa/
├── tests/
│   └── test_calc_plugin.py
└── docs/
```

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

## Links

- [Anna Developer Hub](https://anna.partners/developers/overview/welcome)
- [Executa Protocol](https://anna.partners/developers/tools/executa-intro)
- [Example plugins](https://github.com/whtcjdtc2007/anna-executa-examples)
