# 20-Minute Anna Presentation — Speaking Script

Read this aloud in Discord voice. ~20 minutes + Q&A.

**Preflight:** Run `./scripts/presentation-preflight.sh` before joining voice.

---

## If agent is offline (opening line)

> Anna team is scaling servers before the hackathon — agent might be offline. I'll show the full build either way; live chat is a bonus.

---

## Part 1 — Intro (2 min)

> Hey everyone — thanks for joining. Quick pre-hackathon session: I built my **first Anna Tool**, a calculator, and I want to share what I actually learned — not just docs, but what works on a real machine.
>
> I'm also participating in the hackathon and looking to meet people and form teams. Stick around after if you want to build together.
>
> Anna's team is updating and scaling servers right now so nothing crashes during the hackathon — if my agent is offline tonight, that's why. The build process still applies.

---

## Part 2 — What is Anna? Three layers (4 min)

> Anna is not just a chatbot. It's a platform where you extend AI with **your own capabilities**. There are three building blocks:

| Layer | What it is | File | Runs code? |
|-------|-----------|------|------------|
| **Tool** (Executa) | Backend the agent **calls** | `.py` (any language) | **Yes** |
| **Skill** | Recipe the LLM **reads** | `SKILL.md` | No |
| **App** | Product users **install** from Anna Hub | `manifest.json` | No — bundles Tools + Skills |

**Say this line clearly:**

> **Tool = the engine. Skill = the instruction manual. App = the product you ship for the hackathon.**

**Build order:**

1. **Tool first** — prove your code runs
2. **Skill second** — teach Anna when to use it
3. **App last** — bundle for Hub / install / `#mention` in chat

> For the hackathon you need a full **App** on the Anna Hub that people can discover and install. Under the hood, that App references your Tool(s) and optionally Skill(s).

Docs: https://anna.partners/developers/overview/concepts

---

## Part 3 — What is a Tool technically? (3 min)

> A Tool is surprisingly simple. **No SDK.** Anna spawns your program and talks to it over **stdin/stdout** using **JSON-RPC 2.0**.
>
> You implement three methods:
> - `describe` — here are my tools and parameters
> - `invoke` — run this with these args
> - `health` — optional liveness check
>
> The number one rule: your process must **keep looping on stdin**. Never exit after one request. All logs go to **stderr**, not stdout.

**Screen share:** `executas/calc/calc_plugin.py` — scroll to `main()` (lines 129–143)

> This loop IS the Anna protocol. About 120 lines for a full calculator.

> If you can write a CLI that reads JSON lines and prints JSON lines, you can ship an Anna Tool — Python, Node, Go, anything.

---

## Part 4 — My calculator (4 min)

> I started with the smallest useful thing — a **CS 101 calculator** — so I understood the protocol before the hackathon.

**Screen share — repo structure:**

```
executas/calc/calc_plugin.py   → Tool (backend)
skills/calc-helper/SKILL.md    → Skill (when to call calc)
manifest.json                  → App (hackathon packaging)
```

**Tool actions:**

| Action | What it does |
|--------|-------------|
| `evaluate` | Safe math via Python `ast` — not raw `eval()` |
| `history` | Session memory — proof the tool ran, not the LLM |

**Screen share:** `skills/calc-helper/SKILL.md`

> Skill is **prompt-as-code**. Markdown with YAML frontmatter. It tells Anna: when user asks math, call the calc tool — never guess numbers.

**Screen share:** `manifest.json`

> Lists `required_executas` — your minted Tool ID — plus `system_prompt_addendum`. User `#mentions` the app in chat and Anna loads your tools and instructions.

> I read the docs, planned the structure, built Tool first, added Skill, wrote the App manifest, and tested locally before touching Anna.

---

## Part 5 — The install lesson (3 min)

> Here's what tripped me up — and what you should skip.

**Wrong path:**

- `uv tool install .` in your repo
- Hub Distribution = **UV**
- Click **Rediscover Local**
- Expect Anna to scan your git folder

**Why it failed:**

> UV distribution tells Anna to install from **PyPI**, not your laptop. Rediscover scans `~/.anna/executa/bin/` — which was empty. Chat still answered math — but that was the **LLM guessing**, not my tool.

**Right path:**

```bash
./scripts/smoke-test.sh
# Mint Tool ID at anna.partners/executa
./scripts/install-direct-to-anna.sh
# Cmd+Q Anna.app, reopen
```

**Analogy:**

> Writing code in GitHub is like building an extension. **Install direct to Anna** is installing it into the browser. Anna reads `~/.anna/executa/bin/`, not your repo.

**Proof test in chat:**

> "Show my recent calculator history" — only the Tool has that memory. The LLM cannot fake it.

---

## Part 6 — Live demo (4 min)

### If agent is Online

| Step | Do | Say |
|------|-----|-----|
| 1 | `./scripts/smoke-test.sh` | Protocol works before Anna |
| 2 | Agents dashboard → Executa **1/1 running** | Installed on the agent |
| 3 | Chat: `Use the calc tool to evaluate 17*23` | 391 from real code |
| 4 | Chat: `Show my recent calculator history` | Proves tool ran |

### If agent is Offline (fallback)

| Step | Do | Say |
|------|-----|-----|
| 1 | `./scripts/smoke-test.sh` | Same |
| 2 | `echo '{"jsonrpc":"2.0","method":"describe","id":1}' \| ~/.anna/executa/bin/calc-plugin` | This is what Anna calls internally |
| 3 | Show SKILL.md + manifest.json | Skill + App layer |

---

## Part 7 — Hackathon + teams (2 min)

> For the hackathon you need an **Anna App** on the Hub — installable, with your Tools bundled. Start small:
>
> 1. One Tool that does one thing well
> 2. One Skill for the workflow
> 3. App manifest + listing
>
> My calculator repo is a copy-paste template — see `docs/BUILD_NEW_TOOL.md`.
>
> I'm looking for teammates — backend, UI bundle, or domain ideas. Drop your idea in chat or stay in voice after.

---

## Part 8 — Close (1 min)

> Summary: Anna = **Tool + Skill + App**. Build Tool first. Install to `~/.anna/executa/`. Test with history, not just math.
>
> Repo and docs in Discord. Questions?

---

## Q&A cheat sheet

| Question | Answer |
|----------|--------|
| Skill or Tool first? | **Tool first** — Skill without Tool has nothing to call |
| Need an SDK? | No — JSON-RPC over stdio |
| vs MCP? | Similar transport; Anna has its own protocol + Hub |
| How to publish? | Mint on Executa Hub → App manifest → Hub listing |
| Agent offline? | Server updates; local demo still works |

---

## Read verbatim if nervous (one paragraph)

> Anna has three layers: Tools run your code, Skills teach the AI when to use them, and Apps bundle everything into something users install from the Hub — that's the hackathon deliverable. I built a calculator Tool in Python — it speaks JSON-RPC over stdin, no SDK. I added a Skill in markdown and an App manifest. The lesson that saved me: your repo isn't enough — you install the plugin into `~/.anna/executa/` on your Mac, restart Anna.app, then chat can call your code. I tried UV and Rediscover first; direct install worked. My repo is the template — copy it for your hackathon tool. Looking for teammates tonight.
