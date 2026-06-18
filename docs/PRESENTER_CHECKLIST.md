# Presenter Checklist — 5 Minutes Before Voice

## Terminal

```bash
cd ~/f/anna-experiments
./scripts/presentation-preflight.sh
```

## Tabs to open

| Tab | What |
|-----|------|
| 1 | This script: `docs/PRESENTATION_SCRIPT.md` |
| 2 | `executas/calc/calc_plugin.py` |
| 3 | `skills/calc-helper/SKILL.md` |
| 4 | `manifest.json` |
| 5 | https://anna.partners/agents |
| 6 | https://anna.partners/developers/overview/concepts |

## Anna.app

- [ ] Anna.app running (`pgrep Anna`)
- [ ] Agent shows **Online** on anna.partners/agents
- [ ] Executa shows **1/1 running** (or use offline fallback in script)

## Demo commands (copy-paste ready)

```bash
./scripts/smoke-test.sh
```

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | ~/.anna/executa/bin/calc-plugin
```

**Chat prompts:**

1. `Use the calc tool to evaluate 17*23`
2. `Show my recent calculator history`

## Timing (~20 min)

| Part | Min |
|------|-----|
| Intro | 2 |
| Three layers | 4 |
| Tool protocol | 3 |
| Calculator | 4 |
| Install lesson | 3 |
| Demo | 4 |
| Hackathon + close | 2 |
