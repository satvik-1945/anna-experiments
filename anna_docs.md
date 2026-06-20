# Anna Developer Hub — full corpus

> Developer documentation for the Anna platform: build Tools (Executa plugins), Skills, and Anna Apps; the full Host API, Realtime event, and manifest reference. Every page below is plain Markdown — append `.md` to any `/developers/**` URL, or send `Accept: text/markdown`, to get the raw source instead of the JS-rendered HTML shell.



# === Overview ===

---
title: Welcome to the Anna Developer Hub
description: What you can build for Anna, and how to find your way around.
section: overview
slug: welcome
updated: 2026-04-23
estimated_minutes: 3
---

Anna is a universal AI agent — and almost everything she does at runtime is something a third-party developer can extend, replace, or compose.

This hub is the single source of truth for that work. It covers the two building blocks you can ship — **Executa** (the umbrella for both **Tools** and **Skills**) and **Anna Apps** — and walks you from "hello world" to a published listing in the App Store.

> [!IMPORTANT]
> **Executa = Tools + Skills.** They are two flavours of the same first-class object in Anna's catalogue, distribution pipeline, and developer Console. A *Tool* is an executable plugin process; a *Skill* is a declarative `SKILL.md` recipe. Both are stored as `Executa` records, both go through the same draft → version → visibility lifecycle, and both can be bundled into Anna Apps.

## Where to start

- **New to Anna?** Read [Concepts: Executa and Apps](/developers/overview/concepts) first. It's a 4-minute primer that prevents 90% of confusion.
- **Want to ship a Tool today?** Jump to a quickstart: [Python](/developers/tools/executa-python), [Node.js](/developers/tools/executa-nodejs), or [Go](/developers/tools/executa-go).
- **Prefer a declarative recipe?** Start with [What is a Skill](/developers/skills/skill-intro).
- **Building a curated experience?** Start with [What is an Anna App](/developers/apps/app-intro) and the [Manifest Reference](/developers/apps/app-manifest).

## What this hub is not

- It is **not** the Developer Console. The Console (at `/developer`) is where verified developers manage their own Executas and Apps once published; this hub is the public learning resource.
- It is **not** the API reference for end-user features. For Anna's user-facing docs see [docs.anna.partners](https://docs.anna.partners).

## Stay in the loop

- **Examples**: [`anna-executa-examples`](https://github.com/whtcjdtc2007/anna-executa-examples) — runnable Tool plugins in Python, Node.js, and Go.
- **Forum**: [forum.anna.partners](https://forum.anna.partners) — proposals, RFCs, show-and-tell.
- **Changelog**: linked from the Reference section as we ship platform updates.


---

---
title: Concepts: Executa (Tools + Skills) and Apps
description: One umbrella, two flavours, and the App that bundles them. The 4-minute version.
section: overview
slug: concepts
updated: 2026-04-23
estimated_minutes: 4
---

Anna exposes two extension surfaces:

- **Executa** — a single first-class capability the agent can call. An Executa is either a **Tool** (an executable process speaking JSON-RPC) or a **Skill** (a declarative `SKILL.md` recipe). Both share the same registry, draft/version/visibility lifecycle, and developer Console.
- **Anna App** — a curated bundle of one or more Executas (tools + skills) plus a prompt addendum, published to the App Store and `#mention`-able by the user.

> [!IMPORTANT]
> When this hub says "publish an Executa" or "Executa Hub", it means *either a Tool or a Skill*. The flavour is just an `executa_type` field on the record (`tool` or `skill`).

## At a glance

| Aspect | **Executa: Tool** | **Executa: Skill** | **Anna App** |
|---|---|---|---|
| **Form** | A standalone process speaking JSON-RPC | A folder containing `SKILL.md` | A manifest bundling Executas + prompt |
| **Language** | Any (Python, Node, Go, Rust, …) | Markdown (+ optional supporting files) | JSON manifest + linked Executa references |
| **How the agent uses it** | Called directly as a callable capability with a typed schema | Listed as a recipe the agent can consult on demand; the recipe text guides the agent, which then uses its built-in capabilities to act | Activated when the user `#mentions` it; brings its bundled Executas + prompt addendum into the turn |
| **Best for** | Side effects, network, file system, native APIs | Declarative recipes, prompts-as-code, reusable runbooks | Curated end-user experiences |
| **Distribution** | Source or signed binary in the Executa Hub | Markdown payload in the Executa Hub | The Anna App Store |

## Tools (executable Executa)

A **Tool** is the lowest-level Executa. You write a small program — in any language — that:

1. Reads JSON-RPC requests from stdin.
2. Implements at least two methods: `describe` (return your manifest) and `invoke` (run a tool).
3. Writes JSON-RPC responses to stdout. Logs go to stderr.

That's it. There is no SDK to learn and no runtime to embed. The protocol is documented in [Protocol Spec](/developers/tools/executa-protocol).

> [!TIP]
> If you can write a CLI in your favourite language, you can ship a Tool.

## Skills (declarative Executa)

A **Skill** is a folder containing a `SKILL.md` — a recipe written in Markdown. Skills are not callable capabilities of their own; instead, the agent is told *what skills exist* and *what each one is for*, and consults a skill's full body only when it decides the skill is relevant. The body then guides the agent, which carries out any actions using its built-in capabilities.

This means a Skill is essentially **prompt-as-code**: declarative knowledge the agent can pull in on demand, not a process that runs on its own.

Skills are the right choice when:

- The capability is mostly prompt + light orchestration (no compiled code of your own).
- You want to ship and version capabilities without building a binary.
- You want non-engineers to author plugins.

See [What is a Skill](/developers/skills/skill-intro) and [SKILL.md Format](/developers/skills/skill-format).

## Anna Apps

An **Anna App** is a curated bundle published to the App Store. A user installs it once; thereafter they can `#mention` the App in chat and Anna will:

- Activate **all** the App's required Executas (tools and/or skills) for that turn.
- Inject the App's `system_prompt_addendum` into the system prompt.
- Optionally wrap the user message with a prefix template.

Apps are how a domain expert ships an end-user experience — "Weekly Review Coach", "GitHub Triage Buddy" — without forcing each user to install a dozen separate Executas by hand.

## How they relate

```
+---------------------------+
|        Anna App           |  manifest + prompt addendum
|  (published in App Store) |
+-------------+-------------+
              │ bundles
              ▼
+---------------------------+        +---------------------------+
|   Executa (type: tool)    |  …or…  |   Executa (type: skill)   |
|   process + JSON-RPC      |        |   SKILL.md + metadata     |
+---------------------------+        +---------------------------+
              \\                                  /
               \\________ Executa Hub ___________/
                  (one catalogue, one wizard,
                   one draft → version flow)
```

You can ship a single Tool and stop there. You can ship a single Skill without ever touching JSON-RPC. You only need an App when you want to package an end-user experience.

## Next

- [Architecture & Lifecycle](/developers/overview/architecture)
- [Choosing What to Build](/developers/overview/choosing)


---

---
title: Architecture & Lifecycle
description: How an Executa call flows through Anna, from chat input to response.
section: overview
slug: architecture
updated: 2026-04-23
estimated_minutes: 5
---

This page is a map. If you've read [Concepts](/developers/overview/concepts) and you want to understand where your code runs, what it can see, and when it gets killed — start here.

## The runtime

Anna is composed of:

- A **frontend** (web/desktop/mobile) that drives chat.
- A **gateway / API** (`matrix-nexus`) that stores state, routes turns, and orchestrates tool calls.
- A **runtime** that hosts the LLM session and the tool executor (`matrix`).
- A **NATS** message bus for streaming, fan-out, and event delivery.
- An **Executa Hub** registry that catalogues installable Executas (both Tools and Skills).

Executas — both Tool and Skill flavours — are activated **inside the runtime**, on the same host. Apps don't run anywhere themselves; they're metadata + references that the runtime reads when the user `#mentions` them.

## Lifecycle of a Tool Executa call

1. **User turn arrives** — the runtime builds a system prompt, including any `@`-mentioned Executas and any `#`-mentioned Apps' contributions (system_prompt_addendum, required Executas).
2. **LLM emits a tool call** — for example `weather.lookup({ city: "Tokyo" })`.
3. **Runtime spawns the plugin process** if it isn't already warm. The binary lives wherever the user installed it; the platform passes credentials via environment variables (see [Credentials & OAuth](/developers/tools/executa-credentials)).
4. **Runtime sends `invoke`** as a single JSON-RPC line to the plugin's stdin.
5. **Plugin runs** — does its work, returns a JSON-RPC response on stdout. stderr is captured for debugging only.
6. **Runtime parses the response** and returns it to the LLM as a tool result.
7. **Process disposition**: short-lived plugins exit immediately; long-lived plugins (declared in the manifest) stay warm and serve the next call.

> [!NOTE]
> The runtime treats your stdout as a strict transport. Anything that isn't a valid JSON-RPC frame will fail the call. Always direct logs to stderr.

## Lifecycle of a Skill Executa call

Skills don't spawn processes of their own. The runtime discovers `SKILL.md` files at agent start (or loads them from the Executa record in the database), parses the frontmatter, and registers each skill as a LangChain `@tool`. When the LLM picks the skill, the tool **returns the skill's markdown body to the LLM**, decorated with an execution-mode hint and any declared dependencies.

The skill itself does *not* execute bash or Python directly. If the body contains a fenced bash/python block, the LLM reads it and — in a follow-up turn — calls the agent's built-in `exec` / `command` tools to run it inside the workspace sandbox. That keeps Skills fast and safe and lets the same skill be used from any execution backend.

## Lifecycle of an Anna App `#mention`

1. The user types `#weekly-review` in chat. The frontend resolves it against the user's installed apps and includes the `app_id` in the request.
2. The runtime loads the App's manifest, expands `required_executas` into active tools for the turn, and appends `system_prompt_addendum` (XML-fenced) to the system prompt.
3. From here, the lifecycle is identical to a normal turn — the LLM sees one or more new tools and may choose to call them.

## Concurrency & isolation

- Each Executa call runs in its **own process**. There is no shared state with the runtime beyond stdin/stdout and environment variables.
- Multiple plugins can be invoked **in parallel** within a single turn if the LLM emits parallel tool calls.
- The runtime applies a per-call timeout (default 30s; long-running plugins can declare a different limit in their manifest — see [Manifest Reference](/developers/apps/app-manifest)).

## What you can rely on

- Stdin / stdout / stderr.
- A working temp directory (`$TMPDIR`).
- Environment variables for credentials, declared in your manifest.
- Outbound network (subject to user/admin policy).

## What you can't rely on

- Persistent disk between calls (use the user's data directory only when explicitly granted).
- A specific operating system. Ship a single binary per platform if you depend on native code.
- Inter-tool messaging. Tools shouldn't call each other directly — let the LLM coordinate.


---

---
title: Choosing What to Build
description: Tool, Skill, or App? A short decision guide.
section: overview
slug: choosing
updated: 2026-04-23
estimated_minutes: 3
---

You usually know what you want Anna to do. The question is which surface to ship.

> [!NOTE]
> Tools and Skills are the two flavours of **Executa**. Picking between them is choosing the *shape* of an Executa, not picking a different system. See [Concepts](/developers/overview/concepts).

## Decision shortcut

> [!TIP]
> **Need to call a network API, run a binary, hold credentials, or stream results?** → Build a **Tool** Executa.
>
> **Want to encode a recipe, runbook, or prompts-as-code that the agent reads and acts on?** → Build a **Skill** Executa.
>
> **Want to package an end-user experience and have it appear in the App Store?** → Build an **Anna App** that bundles one or more Executas.

## Worked examples

| You want to… | Ship a… | Why |
|---|---|---|
| Query the GitHub API for issues | **Tool** Executa | Auth + network = process-level concern |
| Convert a CSV to a tidy chart | **Skill** Executa (e.g. `chart-generator`) | Mostly matplotlib glue the agent runs via `exec` |
| Bundle five Executas into a "Marketing Researcher" experience | **App** that bundles those Executas | Discovery + installability is the whole product |
| Add a `pdf.summarize` capability for everyone in the org | **Tool** Executa (or wrap in an App for a listing) | New capability, may need binary deps |
| Teach Anna a new "code review" workflow with prompts only | **Skill** Executa | Pure declarative; no native code |

## Cost / friction tradeoff

| | Tool Executa | Skill Executa | Anna App |
|---|---|---|---|
| Time to first run | medium (write + spawn a process) | low (one markdown file) | adds a few minutes on top of underlying Executas |
| Distribution effort | medium (binary builds, registry submission) | low (markdown payload) | high (review, listing assets) |
| Audience | technical | technical & non-engineer | end users |

Note that Tools *and* Skills go through the same Executa Hub publish flow (drafts, versions, visibility) — the cost difference above is in *authoring*, not in distribution mechanics.

## When in doubt

Build the smallest unit that solves your problem first, then promote upward:

1. Start with a **Skill** Executa to validate the workflow.
2. If you need real I/O, credentials, or streaming, extract that part into a **Tool** Executa.
3. When you're ready to publish to end users, wrap everything in an **App**.


---



# === Build a Tool ===

---
title: What is Executa
description: Anna's plugin extension system: standalone processes speaking JSON-RPC 2.0 over stdio.
section: tools
slug: executa-intro
updated: 2026-04-24
estimated_minutes: 5
---

**Executa** is Anna's plugin extension system. You write a small program in any language; it speaks **JSON-RPC 2.0** over **stdio**; the Anna Agent spawns it, asks what tools it provides, and exposes them to the LLM via NATS RPC.

There is **no SDK** and no embedded runtime. Anything that can read a line and print a line can be an Executa plugin.

## What you'll implement

Three JSON-RPC methods (the third is optional):

| Method | Purpose | Default timeout |
|---|---|---|
| `describe` | Return the manifest (name, version, tools, parameters, credentials) | 5 s |
| `invoke` | Execute one tool with a dict of arguments | 60 s (per-tool overridable) |
| `health` | Optional liveness probe | 3 s |

The Agent runtime handles transport, request IDs, error wrapping, restart, and credential injection.

> [!IMPORTANT]
> **Your plugin must be a long-running stdio server.** It has to keep reading stdin in a loop and only exit on stdin EOF (or when the Agent kills it). A process that exits after answering one `describe` or `invoke` is the single most common bug — the Agent UI will show your plugin as **Stopped** even though `describe` succeeded, and every call pays a fresh cold-start. See [Common pitfalls](#common-pitfalls) below.

## The smallest working plugin

```python
import json, sys

MANIFEST = {
    "name": "hello",
    "display_name": "Hello",
    "version": "0.1.0",
    "description": "Echo text back.",
    "tools": [{
        "name": "echo",
        "description": "Echo input back",
        "parameters": [
            {"name": "text", "type": "string", "description": "Input", "required": True}
        ],
    }],
}

def handle(req):
    method = req["method"]
    if method == "describe":
        return {"result": MANIFEST}
    if method == "invoke":
        params = req.get("params") or {}
        tool = params.get("tool")
        args = params.get("arguments") or {}
        if tool == "echo":
            return {"result": {"success": True, "data": {"text": args.get("text", "")}}}
        return {"error": {"code": -32601, "message": f"Unknown tool: {tool}"}}
    return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    req = json.loads(line)
    payload = handle(req)
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req.get("id"), **payload}) + "\n")
    sys.stdout.flush()
```

Key conventions visible above:

- **`for line in sys.stdin:`** — the loop is mandatory. Never exit after a single request.
- `sys.stdout.flush()` after every response — without it, line-buffered Python may withhold the response until the buffer fills.
- The `invoke` request carries `params.tool` (the tool name) and `params.arguments` (the LLM-supplied dict).
- A successful invoke returns `{"success": true, "data": {...}}` inside `result`. The Agent decodes this into an `InvokeResult` and forwards `data` to the LLM.
- Errors use the JSON-RPC 2.0 `error` frame with standard codes.
- All log lines go to **stderr** — anything on stdout that is not a JSON-RPC frame breaks the protocol.

## Common pitfalls

| Symptom | Root cause | Fix |
|---|---|---|
| UI shows **Stopped** even though `describe` returned a manifest | Process exits after one request instead of looping | Wrap request handling in `for line in sys.stdin:` (or equivalent) and only exit on EOF |
| Plugin shows up under **Extra Agent Plugins** instead of the user-installed card | The Agent installed the plugin under a `tool_id` that differs from the one the user minted on `/executa` (e.g. a dev-registered plugin with no `expected_tool_id`) | Install / register the plugin under the **minted** `tool_id` so the UI can join them — see [Publishing → Stabilise the manifest](/developers/tools/executa-publish#1-stabilise-the-manifest) |
| `describe timeout` on first run for big PyInstaller bundles | Cold start exceeds the default 5 s timeout | Slim the bundle, or rely on the Agent's binary-cold-start timeout (60 s) which kicks in on first scan |
| Garbled responses / `JSON parse error` in Agent logs | Plugin printed a banner / progress text on **stdout** | Move all human-readable logs to **stderr** |

Quick smoke test that catches the long-running bug locally:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"describe"}' | ./my-plugin &
PID=$!
sleep 2
if kill -0 $PID 2>/dev/null; then echo OK; else echo BUG: exited after one request; fi
kill $PID 2>/dev/null
```

## Where to go next

- **Pick a language**: [Python](/developers/tools/executa-python), [Node.js](/developers/tools/executa-nodejs), [Go](/developers/tools/executa-go).
- **Read the spec**: [Protocol Spec](/developers/tools/executa-protocol).
- **Add credentials**: [Credentials](/developers/tools/executa-credentials).
- **Ship a binary**: [Binary Distribution](/developers/tools/executa-binary).
- **Publish**: [Publishing](/developers/tools/executa-publish).

> [!NOTE]
> Runnable samples — including credential and OAuth examples — live in [`whtcjdtc2007/anna-executa-examples`](https://github.com/whtcjdtc2007/anna-executa-examples). Snippets in this hub are extracted from that repo so you can cross-check against working code.


---

---
title: Quickstart — Python
description: Build, smoke-test, and run a Python Executa plugin in under five minutes.
section: tools
slug: executa-python
updated: 2026-04-22
estimated_minutes: 5
---

This quickstart walks you through writing a Python plugin from scratch. You'll end with a working `text-tools` plugin that exposes two tools and passes a smoke test.

## Prerequisites

- Python 3.10+
- A terminal

## 1. Create the plugin

```bash
mkdir text-tools && cd text-tools
touch plugin.py
chmod +x plugin.py
```

```python
#!/usr/bin/env python3
"""text-tools — a tiny Anna Executa plugin."""
import json, sys, hashlib

MANIFEST = {
    "name": "text-tools",
    "display_name": "Text Tools",
    "version": "0.1.0",
    "description": "Reverse strings and hash text.",
    "author": "you@example.com",
    "tools": [
        {
            "name": "reverse",
            "description": "Reverse a string.",
            "parameters": [
                {"name": "text", "type": "string", "description": "Input text", "required": True}
            ],
        },
        {
            "name": "sha256",
            "description": "Compute SHA-256 of input text.",
            "parameters": [
                {"name": "text", "type": "string", "description": "Input text", "required": True}
            ],
        },
    ],
}

def invoke(tool: str, args: dict) -> dict:
    if tool == "reverse":
        return {"success": True, "data": {"output": args["text"][::-1]}}
    if tool == "sha256":
        return {"success": True, "data": {"output": hashlib.sha256(args["text"].encode()).hexdigest()}}
    raise ValueError(f"unknown tool: {tool}")

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
```

## 2. Smoke-test the protocol

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | python plugin.py
```

You should see the manifest. Now invoke a tool — note `params.tool` (not `params.name`):

```bash
echo '{"jsonrpc":"2.0","method":"invoke","id":2,"params":{"tool":"reverse","arguments":{"text":"anna"}}}' | python plugin.py
```

Expected response:

```json
{"jsonrpc": "2.0", "id": 2, "result": {"success": true, "data": {"output": "anna"}}}
```

> [!TIP]
> Always send protocol traffic through stdin and route logs to stderr (`print("debug", file=sys.stderr)`). Anything you `print()` to stdout that isn't a valid JSON-RPC message will be ignored — making it the #1 cause of "the plugin loaded but never replies".

## 3. Install on the Agent

Your Agent admin can register the plugin in one of three ways:

- **`uv tool install .`** — publishes a CLI entry point; the Agent picks it up via `uv` distribution.
- **`pipx install .`** — alternative for Python plugins.
- **Local archive** — build a `.tar.gz` (PyInstaller `--onedir` is the recommended path for plugins with native deps), copy it to the Agent, and paste the absolute archive path into the Executa admin form (`distribution_type: local`). The Agent runs the [full v2 install pipeline](/developers/tools/executa-binary#local-archive-distribution-no-urls-no-upload) (extract → versioned dir → atomic symlink), so multi-file binaries with `lib/`, `_internal/`, etc. all work.

See [Publishing](/developers/tools/executa-publish) for the public Hub flow.

## 4. Where to next

- **Add credentials** — [Credentials](/developers/tools/executa-credentials).
- **Ship a single-file binary** — [Binary Distribution](/developers/tools/executa-binary).
- **Read the full spec** — [Protocol Spec](/developers/tools/executa-protocol).
- **See it in context** — [`examples/python/example_plugin.py`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/python/example_plugin.py).


---

---
title: Quickstart — Node.js
description: Ship an Anna Executa plugin in JavaScript in under five minutes.
section: tools
slug: executa-nodejs
updated: 2026-04-22
estimated_minutes: 5
---

A Node.js Executa plugin is just a CLI that reads JSON lines and writes JSON lines.

## Prerequisites

- Node.js 18+
- A terminal

## 1. Scaffold the plugin

```bash
mkdir json-tools && cd json-tools
npm init -y
touch plugin.js && chmod +x plugin.js
```

```javascript
#!/usr/bin/env node
"use strict";
const readline = require("readline");

const MANIFEST = {
  name: "json-tools",
  display_name: "JSON Tools",
  version: "0.1.0",
  description: "Format JSON and base64-encode strings.",
  author: "you@example.com",
  tools: [
    {
      name: "format_json",
      description: "Pretty-print a JSON string.",
      parameters: [
        { name: "input", type: "string", description: "Raw JSON", required: true },
        { name: "indent", type: "integer", description: "Indent spaces", required: false, default: 2 },
      ],
    },
    {
      name: "b64",
      description: "Base64-encode a string.",
      parameters: [
        { name: "text", type: "string", description: "Input", required: true },
      ],
    },
  ],
};

function invoke(tool, args) {
  if (tool === "format_json") {
    return { success: true, data: { output: JSON.stringify(JSON.parse(args.input), null, args.indent ?? 2) } };
  }
  if (tool === "b64") {
    return { success: true, data: { output: Buffer.from(args.text, "utf8").toString("base64") } };
  }
  throw Object.assign(new Error(`unknown tool: ${tool}`), { code: -32601 });
}

function send(id, payload) {
  process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id, ...payload }) + "\n");
}

const rl = readline.createInterface({ input: process.stdin });
rl.on("line", (line) => {
  const trimmed = line.trim();
  if (!trimmed) return;
  let req;
  try {
    req = JSON.parse(trimmed);
  } catch (e) {
    return send(null, { error: { code: -32700, message: "parse error" } });
  }
  try {
    if (req.method === "describe") return send(req.id, { result: MANIFEST });
    if (req.method === "health") return send(req.id, { result: { status: "ready" } });
    if (req.method === "invoke") {
      const params = req.params || {};
      return send(req.id, { result: invoke(params.tool, params.arguments || {}) });
    }
    return send(req.id, { error: { code: -32601, message: `unknown method: ${req.method}` } });
  } catch (e) {
    send(req.id, { error: { code: e.code ?? -32603, message: e.message } });
  }
});
```

## 2. Smoke-test

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | node plugin.js
echo '{"jsonrpc":"2.0","method":"invoke","id":2,"params":{"tool":"b64","arguments":{"text":"anna"}}}' | node plugin.js
```

> [!WARNING]
> `console.log` writes to stdout. Anything you `console.log` mixes into protocol output and breaks the plugin. Use `console.error` (stderr) for logs.

## 3. Install on the Agent

Publish the binary entry point with `npm` (`bin` field in `package.json`) and register the plugin with `distribution_type: npm`. For local iteration, build a `.tar.gz` (e.g. `tar czf my-tool.tgz dist/`) and point the Agent at the archive path with `distribution_type: local` — the Agent runs the [full v2 install pipeline](/developers/tools/executa-binary#local-archive-distribution-no-urls-no-upload) and supports multi-file binaries (native addons in `node_modules/`, etc.).

## 4. Build a binary (optional)

Node 20+ ships [single-executable applications](https://nodejs.org/api/single-executable-applications.html) via `--experimental-sea-config`. For multi-platform CI the easiest route remains [`@yao-pkg/pkg`](https://github.com/yao-pkg/pkg):

```bash
npm install -g @yao-pkg/pkg
pkg plugin.js --targets node20-macos-arm64,node20-linux-x64,node20-win-x64 --out-path dist
```

See [Binary Distribution](/developers/tools/executa-binary) for the full matrix and signing guidance.

## 5. Where to next

- **Add credentials** — [Credentials](/developers/tools/executa-credentials).
- **Read the spec** — [Protocol Spec](/developers/tools/executa-protocol).
- **See it in context** — [`examples/nodejs/example_plugin.js`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/nodejs/example_plugin.js).


---

---
title: Quickstart — Go
description: Ship a single-binary Anna Executa plugin in Go.
section: tools
slug: executa-go
updated: 2026-04-22
estimated_minutes: 6
---

Go is the language of choice when you want **one statically linked binary per platform**. No interpreter, no runtime — just `chmod +x` and run.

## Prerequisites

- Go 1.21+
- A terminal

## 1. Scaffold

```bash
mkdir sysinfo-tool && cd sysinfo-tool
go mod init sysinfo-tool
touch main.go
```

```go
package main

import (
    "bufio"
    "crypto/sha256"
    "encoding/hex"
    "encoding/json"
    "fmt"
    "os"
    "runtime"
)

type Request struct {
    Jsonrpc string         `json:"jsonrpc"`
    Method  string         `json:"method"`
    ID      any            `json:"id"`
    Params  map[string]any `json:"params,omitempty"`
}

type Response struct {
    Jsonrpc string `json:"jsonrpc"`
    ID      any    `json:"id"`
    Result  any    `json:"result,omitempty"`
    Error   *Err   `json:"error,omitempty"`
}

type Err struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
}

var manifest = map[string]any{
    "name":         "sysinfo",
    "display_name": "System Info",
    "version":      "0.1.0",
    "description":  "Report OS info or hash a string.",
    "tools": []map[string]any{
        {"name": "os_info", "description": "Return host OS and arch.", "parameters": []map[string]any{}},
        {"name": "sha256", "description": "Hash a string with SHA-256.", "parameters": []map[string]any{
            {"name": "text", "type": "string", "description": "Input", "required": true},
        }},
    },
}

func invoke(tool string, args map[string]any) (any, *Err) {
    switch tool {
    case "os_info":
        return map[string]any{
            "success": true,
            "data":    map[string]string{"os": runtime.GOOS, "arch": runtime.GOARCH},
        }, nil
    case "sha256":
        text, _ := args["text"].(string)
        sum := sha256.Sum256([]byte(text))
        return map[string]any{
            "success": true,
            "data":    map[string]string{"output": hex.EncodeToString(sum[:])},
        }, nil
    }
    return nil, &Err{Code: -32601, Message: fmt.Sprintf("unknown tool: %s", tool)}
}

func main() {
    enc := json.NewEncoder(os.Stdout)
    s := bufio.NewScanner(os.Stdin)
    s.Buffer(make([]byte, 0, 1<<20), 1<<22)
    for s.Scan() {
        line := s.Bytes()
        if len(line) == 0 {
            continue
        }
        var req Request
        if err := json.Unmarshal(line, &req); err != nil {
            _ = enc.Encode(Response{Jsonrpc: "2.0", Error: &Err{Code: -32700, Message: err.Error()}})
            continue
        }
        resp := Response{Jsonrpc: "2.0", ID: req.ID}
        switch req.Method {
        case "describe":
            resp.Result = manifest
        case "health":
            resp.Result = map[string]string{"status": "ready"}
        case "invoke":
            tool, _ := req.Params["tool"].(string)
            args, _ := req.Params["arguments"].(map[string]any)
            result, errOut := invoke(tool, args)
            if errOut != nil {
                resp.Error = errOut
            } else {
                resp.Result = result
            }
        default:
            resp.Error = &Err{Code: -32601, Message: "unknown method: " + req.Method}
        }
        _ = enc.Encode(resp)
    }
}
```

## 2. Smoke-test

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | go run main.go
echo '{"jsonrpc":"2.0","method":"invoke","id":2,"params":{"tool":"os_info","arguments":{}}}' | go run main.go
```

A successful invoke returns `{"result": {"success": true, "data": {...}}}` — the wrapper the Agent decodes into `InvokeResult`.

## 3. Build native binaries

```bash
GOOS=darwin  GOARCH=arm64 go build -ldflags "-s -w" -o dist/sysinfo-darwin-arm64  main.go
GOOS=darwin  GOARCH=amd64 go build -ldflags "-s -w" -o dist/sysinfo-darwin-x86_64 main.go
GOOS=linux   GOARCH=amd64 go build -ldflags "-s -w" -o dist/sysinfo-linux-x86_64  main.go
GOOS=linux   GOARCH=arm64 go build -ldflags "-s -w" -o dist/sysinfo-linux-aarch64 main.go
GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o dist/sysinfo-windows-x86_64.exe main.go
```

File names follow the [platform key convention](/developers/tools/executa-binary#platform-keys) so the Agent's binary distribution can pick the right asset automatically. Full multi-platform Makefile in [`examples/go/Makefile`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/go/Makefile).

> [!TIP]
> `-ldflags "-s -w"` strips the symbol table and DWARF debug info; expect ~30 % smaller binaries.

## 4. Where to next

- **Add credentials** — [Credentials](/developers/tools/executa-credentials).
- **Cross-platform binaries** — [Binary Distribution](/developers/tools/executa-binary).
- **See it in context** — [`examples/go/main.go`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/go/main.go).


---

---
title: Protocol Specification
description: JSON-RPC 2.0 over stdio — the wire format an Executa plugin must speak.
section: tools
slug: executa-protocol
updated: 2026-04-24
estimated_minutes: 9
---

Anna's plugin protocol is **JSON-RPC 2.0 over stdio**, line-delimited (LF). It is intentionally minimal so that any language with stdin/stdout can implement it.

Protocol version: **1.1**.

## Transport

```
+----------+   stdin (request)    +----------+
|          | ------------------->|          |
|  Anna    |                     |  Plugin  |
|  Agent   |   stdout (response) |  Process |
|          | <-------------------|          |
|          |                     |          |
|          |   stderr (logs)     |          |
|          | <- - - - - - - - - -|          |
+----------+                     +----------+
```

### Constraints

1. **stdout is for protocol responses only.** Each line must be one JSON object. Non-JSON lines on stdout are tolerated (debug-logged) but are *never* interpreted as results.
2. **stderr is for logs.** The Agent captures it and surfaces it in the trace view.
3. **One message per line**, terminated by `\n`. No `Content-Length` headers.
4. **UTF-8** encoding.
5. **Single-line per response ≤ 2 MiB.** Beyond ~512 KiB use the [file transport](#file-transport) escape hatch.
6. **The plugin process is long-running.** It MUST keep reading stdin in a loop and only exit on stdin EOF (the Agent closes stdin to request shutdown) or on an explicit signal. A process that exits after sending a single response is a protocol violation — the Agent will mark it as **Stopped** and pay a fresh cold-start on every subsequent invocation. After writing each response, **flush stdout** before looping back to read the next request.

## Methods

### `describe`

Called once after the runtime spawns the plugin.

**Request:**

```json
{ "jsonrpc": "2.0", "method": "describe", "id": 1 }
```

**Response (Manifest):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "name": "my-tool",
    "display_name": "My Tool",
    "version": "1.0.0",
    "description": "What this plugin does.",
    "author": "Your Name",
    "homepage": "https://example.com/my-tool",
    "icon": "🔧",
    "category": "productivity",
    "license": "MIT",
    "tools": [
      {
        "name": "do_something",
        "description": "Description shown to the LLM.",
        "timeout": 60,
        "streaming": false,
        "parameters": [
          { "name": "input_text", "type": "string", "description": "Input.", "required": true },
          { "name": "count", "type": "integer", "description": "Repeat count.", "required": false, "default": 1 },
          { "name": "tags", "type": "array", "items": {"type": "string"}, "description": "Tag list.", "required": false }
        ]
      }
    ],
    "credentials": [
      {
        "name": "MY_API_KEY",
        "display_name": "My API Key",
        "description": "Get one at https://example.com/keys",
        "required": true,
        "sensitive": true
      }
    ],
    "runtime": { "type": "uv", "min_version": "0.1.0" }
  }
}
```

#### Manifest fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Lowercase kebab/snake label. **Not** the canonical identity — the registry mints a stable `tool_id` at publish time and the Agent joins installs to running plugins by that `tool_id`, so a mismatch between this `name` and the minted `tool_id` no longer matters. |
| `display_name` | string | no | Defaults to `name` |
| `version` | string | yes | SemVer (`MAJOR.MINOR.PATCH`) |
| `description` | string | yes | One-paragraph description |
| `author` | string | no | Free text |
| `homepage` | string | no | Documentation / source URL |
| `icon` | string | no | Emoji or URL (defaults to `🔧`) |
| `category` | string | no | Free-form grouping (`general` by default) |
| `license` | string | no | SPDX identifier |
| `tools` | list | yes | At least one tool definition |
| `credentials` | list | no | Declared secrets the Agent will inject — see [Credentials](/developers/tools/executa-credentials) |
| `runtime` | object | no | Free-form runtime hints (e.g. `{"type": "uv", "min_version": "0.1.0"}`) |

#### Tool definition

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Unique within the plugin |
| `description` | string | yes | Prompt the LLM uses to choose this tool |
| `parameters` | list | no | Empty list = no arguments |
| `timeout` | integer | no | Per-tool execute timeout in seconds (default 60) |
| `streaming` | boolean | no | Reserved for future use |

#### Parameter schema

Fields per parameter: `name`, `type`, `description`, `required` (default `true`), `default`, `enum`, plus `items` / `items_type` for arrays.

Supported `type` values: `string`, `integer`, `number`, `boolean`, `array`, `object`.

For `array`, declare element type either as the standard JSON Schema `"items": {"type": "string"}` or as the protocol shorthand `"items_type": "string"`. The Agent accepts both. If neither is provided, `array` defaults to a list of strings (so the LLM does not pass JSON-encoded strings).

### `invoke`

Invoke a tool. **Note the param shape uses `tool`, not `name`.**

**Request:**

```json
{
  "jsonrpc": "2.0",
  "method": "invoke",
  "id": 2,
  "params": {
    "tool": "do_something",
    "arguments": { "input_text": "hello", "count": 3 },
    "context": { "credentials": { "MY_API_KEY": "sk_..." } }
  }
}
```

`params.context.credentials` is injected by the Agent only when the user has configured the plugin's credentials. The LLM never sees this object.

**Successful response (`InvokeResult` shape):**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "success": true,
    "data": { "output": "hellohellohello" },
    "duration_ms": 12
  }
}
```

The Agent decodes `result` as `{success, data, error, duration_ms}`. Whatever you put under `data` is what the LLM will see. `duration_ms` is optional; the Agent measures wall-clock time on its end as well.

**Tool-level failure** (a recoverable error — the LLM should be told about it):

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": { "success": false, "error": "city not found" }
}
```

### `health`  *(optional)*

```json
{ "jsonrpc": "2.0", "method": "health", "id": 3 }
```

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": { "status": "ready", "message": "", "details": {} }
}
```

`status` must be one of `ready`, `error`, `initializing`. The runtime polls this when an admin triggers a health check; you may omit the method (the call returns method-not-found and is treated as healthy).

## JSON-RPC errors

For unrecoverable errors (parse failure, unknown method, runtime exception) return the standard JSON-RPC error frame:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": { "code": -32601, "message": "Unknown tool: do_something" }
}
```

| Code | Meaning |
|---|---|
| `-32700` | Parse error |
| `-32600` | Invalid request |
| `-32601` | Method / tool not found |
| `-32602` | Invalid params |
| `-32603` | Internal error |
| `-32000` to `-32099` | Implementation-defined server error |

> [!TIP]
> Use `result.success = false` for *expected* failures ("city not found", "rate limited"). Use the JSON-RPC `error` frame for *programmer* errors ("unknown tool", "missing argument"). The Agent treats them differently in the trace view.

## Default timeouts

| Method | Default | Override |
|---|---|---|
| `describe` | 5 s | not configurable |
| `health` | 3 s | not configurable |
| `invoke` | 60 s | per-tool via `tools[].timeout` |

If your plugin needs longer for a specific tool, declare `"timeout": 600` on that tool entry. Plugins exceeding their declared timeout receive `SIGTERM` and the request resolves with a JSON-RPC timeout error.

## Lifecycle

1. The Agent spawns the plugin executable with the user's environment.
2. It immediately sends `describe` and waits up to 5 s.
3. Each tool invocation sends `invoke`; per-tool timeouts apply.
4. On idle / shutdown the runtime sends `SIGTERM` and waits up to 5 s before `SIGKILL`.
5. If the process exits unexpectedly, the runtime restarts it with exponential backoff (up to 3 attempts).

> [!IMPORTANT]
> Handle `SIGTERM` cleanly. Flush buffers, close file handles. Exit non-zero only if you actually crashed.

## Protocol v2 — `initialize` & reverse RPC

Executa **2.0** adds an `initialize` capability handshake and a reverse-RPC channel that lets a plugin ask the host for LLM completions or persistent storage. v1 plugins keep working: if a plugin returns `method-not-found` on `initialize`, the host falls back to v1 transparently.

The wire details, error codes, and worked examples live in dedicated pages:

- [Lifecycle & Capability Negotiation](/developers/tools/executa-lifecycle) — `initialize` handshake, per-invoke context injection.
- [Sampling](/developers/tools/executa-sampling) — `sampling/createMessage` reverse RPC.
- [Persistent Storage](/developers/tools/executa-storage) — `storage/*` and `files/*` reverse RPCs (scope-parameterised: `user` / `app` / `tool`).

## File transport (large responses)

For results larger than ~512 KiB you can write the full JSON-RPC response to a temporary file and send a pointer instead:

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "__file_transport": "/tmp/executa-resp-XXXXXX.json"
}
```

The Agent reads the file, decodes the response inside it, then deletes the file. Use this when you would otherwise blow past the 2 MiB readline ceiling. See the Python sample's `send_response()` for a reference implementation: [`examples/python/example_plugin.py`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/python/example_plugin.py).

## Reference

The canonical Python implementation of the protocol lives in [`src/executa/protocol.py`](https://github.com/whtcjdtc2007/anna-executa-examples) (Anna Agent side). All field names, defaults, and error codes above match it exactly.


---

---
title: Lifecycle & Capability Negotiation
description: How the Agent spawns, initializes, calls, and shuts down an Executa plugin — including v2 reverse-RPC capability negotiation.
section: tools
slug: executa-lifecycle
updated: 2026-05-11
estimated_minutes: 7
---

Every Executa plugin runs as a **single, long-running process** that the Matrix Agent owns end-to-end. Understanding the five lifecycle phases — and the v2 capability handshake that gates [Sampling](/developers/tools/executa-sampling) and [Persistent Storage](/developers/tools/executa-storage) — is the prerequisite for everything beyond `invoke`.

![Executa plugin lifecycle](/static/images/developers/executa-lifecycle.svg)

## Five phases

| # | Phase | Direction | Default timeout | Notes |
|---|---|---|---|---|
| 1 | **spawn** | Agent → OS | — | Process started with the user's environment; stdin / stdout / stderr piped. |
| 2 | **initialize** | Agent → Plugin | `5 s` | v2 handshake. Plugin replying with `Method not found` (or timing out) silently downgrades the session to v1. |
| 3 | **describe** | Agent → Plugin | `5 s` (`60 s` on first launch of a binary onefile) | Returns the manifest. The Agent caches it for the rest of the process's life. |
| 4 | **invoke** | Agent → Plugin (loop) | `60 s` per tool, overridable | Hot path. Each request also unlocks **reverse RPC** if v2 was negotiated. |
| 5 | **shutdown** | Agent closes stdin → `SIGTERM` → `SIGKILL` | `5 s` grace | The plugin must keep reading stdin until EOF. Never `exit()` after a single response. |

> [!IMPORTANT]
> If your plugin terminates after one response, the Agent UI marks it **Stopped** even though `describe` returned a valid manifest, and every subsequent call pays a fresh cold-start. See [Common Pitfalls #1](/developers/tools/executa-pitfalls#plugin-process-exits-after-one-request).

The Agent also restarts the plugin with exponential backoff on unexpected exit (max **3 attempts**, base delay **1 s**).

## v2 capability handshake

The Agent always tries v2 first. The handshake exchanges two pieces of information:

- **what the host can do for the plugin** — sampling caps, file-transport support, etc.
- **what the plugin will use** — the subset of host capabilities it actually depends on.

### Request (Agent → Plugin)

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "method": "initialize",
  "params": {
    "protocolVersion": "2.0",
    "clientInfo": { "name": "matrix-agent", "version": "1.0" },
    "capabilities": {
      "sampling": {
        "modalities": ["text"],
        "maxTokensPerCall": 8192,
        "maxCallsPerInvoke": 8,
        "responseFormat": ["json_object", "json_schema"]
      },
      "fileTransport": true
    }
  }
}
```

### Response (Plugin → Agent)

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": {
    "protocolVersion": "2.0",
    "server_info": { "name": "my-tool", "version": "0.1.0" },
    "capabilities": { "sampling": {} }
  }
}
```

The plugin echoes the negotiated `protocolVersion` and lists the **subset** of host capabilities it intends to invoke. An empty object (`{}`) is fine — it means "I'm aware of this capability, no extra options."

### Fallback to v1

The Agent transparently falls back to protocol **1.1** when:

- the plugin times out on `initialize`,
- the response is a JSON-RPC error with code `-32601` (method not found),
- any other error frame is returned.

v1 plugins keep working, but **lose access to all reverse-RPC features** (sampling, storage, future logging/progress).

## Manifest declarations vs. runtime capabilities

The negotiation in `initialize` is necessary but not sufficient. To actually use a host capability the plugin must **also** declare it in the `describe` manifest:

```json
{
  "name": "my-tool",
  "version": "0.1.0",
  "host_capabilities": ["llm.sample", "storage.tool"],
  "tools": [ /* ... */ ]
}
```

| Capability string | Unlocks | Reverse RPC methods |
|---|---|---|
| `llm.sample` | [Sampling](/developers/tools/executa-sampling) | `sampling/createMessage` |
| `storage.user` | [APS](/developers/tools/executa-storage) — user drive | `storage/*`, `files/*` (with `scope: "user"`) |
| `storage.app` | APS — app namespace | `storage/*`, `files/*` |
| `storage.tool` | APS — tool-private namespace | `storage/*`, `files/*` |

Without the manifest declaration, Nexus refuses the corresponding reverse RPC at the gate (`-32008 not_negotiated` for sampling, `-32021 not_granted` for storage).

## Per-invoke context injection

Once v2 is live, every `invoke` request also carries a `context` block beside `tool` and `arguments`:

```json
{
  "method": "invoke",
  "params": {
    "tool": "summarize",
    "arguments": { "text": "…" },
    "context": {
      "credentials":    { "OPENAI_API_KEY": "sk-…" },
      "invoke_id":      "8f1c…",
      "sampling_token": "eyJ…",
      "storage_token":  "eyJ…"
    }
  }
}
```

| Field | Source | Used for |
|---|---|---|
| `credentials` | [Platform Authorization](/developers/tools/executa-authorization) + per-plugin overrides | Talking to third-party APIs |
| `invoke_id` | Auto-minted by the Agent (UUID hex) | Audit correlation; reverse-RPC budget keying |
| `sampling_token` | Nexus, JWT `aud=executa-sampling`, TTL 600 s | `sampling/createMessage` authorization |
| `storage_token`  | Nexus, JWT `aud=aps-storage`, TTL 600 s | `storage/*` & `files/*` authorization |

Tokens are bound to (`user_id`, `executa_tool_id`, `tool_invoke_id`) and expire shortly after the invoke completes — **never** persist them across invocations.

## Health probe (optional)

```json
{ "jsonrpc": "2.0", "method": "health", "id": 99 }
```

```json
{ "jsonrpc": "2.0", "id": 99,
  "result": { "status": "ready", "message": "", "details": {} } }
```

`status` is one of `ready`, `error`, `initializing`. Plugins that omit `health` are treated as healthy (the Agent receives `-32601` and ignores it).

## Shutdown contract

When the Agent wants the plugin gone, it:

1. closes stdin — your loop's `for line in sys.stdin:` should exit cleanly,
2. waits up to 5 s,
3. sends `SIGTERM`, waits another 5 s,
4. sends `SIGKILL`.

> [!TIP]
> Flush buffers and close file handles when stdin closes. Exit non-zero **only** if you actually crashed — the Agent treats non-zero as a fault and counts it against the restart budget.

## See also

- [Protocol Specification](/developers/tools/executa-protocol) — line-delimited JSON-RPC 2.0 wire format.
- [Sampling](/developers/tools/executa-sampling) — `sampling/createMessage` reverse RPC.
- [Persistent Storage](/developers/tools/executa-storage) — `storage/*` & `files/*` reverse RPC.
- [Common Pitfalls](/developers/tools/executa-pitfalls) — including the long-running-process bug.


---

---
title: Credentials
description: How plugins declare and consume API keys / tokens injected by the platform.
section: tools
slug: executa-credentials
updated: 2026-05-11
estimated_minutes: 6
---

Most useful tools need secrets — an API key, a bearer token. Anna stores those for the user (encrypted at rest), then injects them into every `invoke` call as part of the request payload.

## Declare credentials in the manifest

List every secret your plugin needs in the `credentials` field of `describe`:

```json
{
  "credentials": [
    {
      "name": "WEATHER_API_KEY",
      "display_name": "OpenWeatherMap API Key",
      "description": "Get one at https://openweathermap.org/api",
      "required": true,
      "sensitive": true
    },
    {
      "name": "WEATHER_UNITS",
      "display_name": "Temperature Units",
      "description": "metric / imperial / standard",
      "required": false,
      "sensitive": false,
      "default": "metric"
    }
  ]
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Identifier the Agent uses as the dict key when injecting (use `UPPER_SNAKE_CASE`) |
| `display_name` | string | no | Shown in the credential settings UI; defaults to `name` |
| `description` | string | no | Help text shown to users |
| `required` | boolean | no | Defaults to `true`; the plugin won't be enabled until required keys are set |
| `sensitive` | boolean | no | Defaults to `true`; sensitive values are encrypted at rest and rendered as password fields |
| `default` | string | no | Pre-filled value (only useful for non-sensitive options) |

> [!NOTE]
> The protocol does **not** model OAuth providers/scopes. If you need OAuth (Google, GitHub, Notion…), perform the flow inside your plugin's setup helper or via the platform's centralized authorization (see [Platform authorization](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/authorization.md)) and surface the resulting access token as a single sensitive credential.

## How credentials reach the plugin

When the user has configured the credentials, the Agent passes them inside every `invoke` request:

```json
{
  "jsonrpc": "2.0",
  "method": "invoke",
  "id": 7,
  "params": {
    "tool": "get_weather",
    "arguments": { "city": "Tokyo" },
    "context": {
      "credentials": {
        "WEATHER_API_KEY": "sk_live_…",
        "WEATHER_UNITS": "metric"
      }
    }
  }
}
```

`params.context.credentials` is **never** visible to the LLM. Read it inside your `invoke` handler.

### Python pattern

```python
def tool_get_weather(city: str, *, credentials: dict | None = None) -> dict:
    creds = credentials or {}
    # 1) Prefer Agent-injected credentials
    api_key = creds.get("WEATHER_API_KEY") or os.environ.get("WEATHER_API_KEY")
    units   = creds.get("WEATHER_UNITS")   or os.environ.get("WEATHER_UNITS", "metric")

    if not api_key:
        return {"success": False, "error": "WEATHER_API_KEY not configured"}

    # ... call the upstream API ...
    return {"success": True, "data": {"city": city, "units": units, "…": "…"}}


def handle_invoke(req_id, params):
    tool = params.get("tool")
    args = params.get("arguments") or {}
    creds = (params.get("context") or {}).get("credentials") or {}
    if tool == "get_weather":
        return {"id": req_id, "result": tool_get_weather(**args, credentials=creds)}
    …
```

### Node.js pattern

```javascript
function invoke(tool, args, context = {}) {
  const creds = context.credentials || {};
  if (tool === "list_messages") {
    const token = creds.GMAIL_ACCESS_TOKEN || process.env.GMAIL_ACCESS_TOKEN;
    if (!token) return { success: false, error: "GMAIL_ACCESS_TOKEN not configured" };
    // … fetch with `Authorization: Bearer ${token}`
    return { success: true, data: { messages: [/* … */] } };
  }
}
```

## Three-tier resolution

The Agent merges credentials from three sources before sending them in `context.credentials`:

1. **Platform authorization** — secrets the user configured once at `/settings/authorizations`.
2. **Plugin-level credentials** — secrets entered specifically for this plugin (REST: `PUT /api/v1/executas/my/{user_executa_id}/credentials`).
3. **Environment variables** — fallback that *your plugin* implements for local development (the Agent does not export envs from credentials).

## Local development

For local iteration there is no Agent running, so use environment variables and your plugin's fallback path:

```bash
WEATHER_API_KEY=your_key python plugin.py
GMAIL_ACCESS_TOKEN=ya29… node plugin.js
```

## Security guidelines

> [!WARNING]
> - **Never log secrets** — stderr is captured into traces.
> - **Never persist credentials to disk** from the plugin. The platform owns persistence.
> - **Treat credentials as request-scoped.** A long-running plugin may serve multiple users; do not cache credentials in module-level globals.
> - **Echo only redacted previews** in responses (e.g. `sk_…last4`) — anything you put in `result.data` is visible to the LLM.

## Reference

- Full sample with multi-credential support: [`docs/authorization.md`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/authorization.md).
- Per-language credential plugins: [`credential_plugin.py`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/python/credential_plugin.py), [`credential_plugin.js`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/nodejs/credential_plugin.js), [`credential_plugin.go`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/examples/go/credential_plugin.go).
- Google OAuth flow: `google_oauth_plugin.*` in each language directory.


---

---
title: Platform Authorization
description: Connect Google / X / GitHub / Notion / Slack once in Anna — every plugin that asks for the credential name receives it automatically.
section: tools
slug: executa-authorization
updated: 2026-05-11
estimated_minutes: 7
---

**Platform Authorization** is Anna's central credential broker. Users connect a third-party service **once** in `/settings/authorizations`; every Executa plugin that declares the same credential name is automatically wired up at invoke time — no per-plugin OAuth flow, no API key juggling.

This page explains how the broker works, which providers are first-class, and the conventions a plugin should follow to plug in for free.

![Platform Authorization: providers, resolution priority, plugin invoke](/static/images/developers/executa-authorization.svg)

## How a plugin gets credentials

Every plugin lists the secrets it needs in its `describe` manifest:

```json
{
  "credentials": [
    {
      "name": "GMAIL_ACCESS_TOKEN",
      "display_name": "Gmail Access Token",
      "description": "Auto-injected when the user has connected Google in /settings/authorizations.",
      "required": true,
      "sensitive": true
    }
  ]
}
```

When the Agent invokes a tool, it injects resolved values into `params.context.credentials` — the LLM never sees them:

```json
{
  "method": "invoke",
  "params": {
    "tool": "send_mail",
    "arguments": { "to": "…", "body": "…" },
    "context": {
      "credentials": { "GMAIL_ACCESS_TOKEN": "ya29.…" }
    }
  }
}
```

See the [Credentials](/developers/tools/executa-credentials) page for the full manifest schema.

## Resolution priority

For each name in `credentials[].name`, the resolver searches in this order:

| # | Source | When to use |
|---|---|---|
| 1 | **Platform credentials** | The user has connected this provider in `/settings/authorizations`. Highest priority. |
| 2 | **Plugin-level credentials** | The user pasted a value into the per-plugin settings dialog. |
| 3 | **Process environment** | Local-development fallback only — present when running the binary directly outside the Agent. |

The first hit wins. There is **no** tool-id allowlist: any plugin asking for `GMAIL_ACCESS_TOKEN` receives it, as long as the user has granted Google access.

## How a credential name maps to a provider

Each provider in the registry declares a `credential_mapping` from **plugin-facing names** to either a placeholder (`$access_token`) or a literal field key. Examples below are taken verbatim from `src/services/credential_providers.py`.

### Google (OAuth2)

```python
credential_mapping = {
    "GOOGLE_ACCESS_TOKEN":        "$access_token",
    "GMAIL_ACCESS_TOKEN":         "$access_token",
    "GOOGLE_WORKSPACE_CLI_TOKEN": "$access_token",
    "YOUTUBE_ACCESS_TOKEN":       "$access_token",
    "GOOGLE_DOCS_ACCESS_TOKEN":   "$access_token",
    "GOOGLE_SHEETS_ACCESS_TOKEN": "$access_token",
}
```

`$access_token` resolves to the live OAuth access_token, refreshed transparently if expired.

### X / Twitter (OAuth2 + PKCE)

```python
credential_mapping = {
    "TWITTER_ACCESS_TOKEN": "$access_token",
    "X_ACCESS_TOKEN":       "$access_token",
}
```

### GitHub / Notion / Slack (API key)

```python
# GitHub
{ "GITHUB_TOKEN": "GITHUB_TOKEN", "GITHUB_ACCESS_TOKEN": "GITHUB_TOKEN" }

# Notion
{ "NOTION_TOKEN": "NOTION_TOKEN", "NOTION_API_KEY": "NOTION_TOKEN" }

# Slack
{ "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN", "SLACK_TOKEN": "SLACK_BOT_TOKEN" }
```

The literal-key form maps the plugin's requested name to the underlying field stored in `user_platform_credentials.credentials_encrypted`.

## Supported providers (current registry)

| Provider | Auth | Recommended credential names |
|---|---|---|
| **Google** | OAuth2 (18 selectable scopes) | `GOOGLE_ACCESS_TOKEN`, `GMAIL_ACCESS_TOKEN`, `YOUTUBE_ACCESS_TOKEN`, `GOOGLE_DOCS_ACCESS_TOKEN`, `GOOGLE_SHEETS_ACCESS_TOKEN`, `GOOGLE_WORKSPACE_CLI_TOKEN` |
| **X (Twitter)** | OAuth2 + PKCE (20 scopes) | `TWITTER_ACCESS_TOKEN`, `X_ACCESS_TOKEN` |
| **GitHub** | API key (Personal Access Token) | `GITHUB_TOKEN`, `GITHUB_ACCESS_TOKEN` |
| **Notion** | API key (Integration Token) | `NOTION_TOKEN`, `NOTION_API_KEY` |
| **Slack** | API key (Bot User OAuth Token) | `SLACK_BOT_TOKEN`, `SLACK_TOKEN` |
| **OpenAI** | API key (BYO) | `OPENAI_API_KEY` |
| **Anthropic** | API key (BYO) | `ANTHROPIC_API_KEY` |

> [!TIP]
> Need to call an LLM as part of your tool? Don't ask for `OPENAI_API_KEY` — use [Sampling](/developers/tools/executa-sampling) instead. Sampling lets you call the user's preferred provider on their quota, with no API key shipped at all.

## API surface

Standard endpoints under `/api/v1/platform-credentials`:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/providers` | List all supported providers |
| `GET` | `/my` | Current user's authorization status across all providers |
| `GET` | `/my/{provider_id}` | Detail for one provider (scopes, email, last refresh) |
| `GET` | `/oauth/{provider_id}/authorize` | Begin OAuth flow (redirect) |
| `GET` | `/oauth/{provider_id}/callback` | OAuth callback handler |
| `PUT` | `/api-key/{provider_id}` | Set / update an API key |
| `GET` | `/api-key/{provider_id}/status` | Whether an API key is configured |
| `DELETE` | `/my/{provider_id}` | Disconnect (revokes upstream where supported) |
| `POST` | `/my/{provider_id}/refresh` | Force-refresh an OAuth token |

Plugins should not call these directly — they are for the Anna UI. Plugins receive the resolved value via `context.credentials` as shown above.

## Security model

- **Encrypted at rest.** All stored credentials use **AES-256-GCM** (`src/utils/credential_crypto.py`); the key is derived from `NEXUS_CREDENTIAL_KEY` (or `SECRET_KEY` as fallback).
- **LLM-isolated.** Credentials live in `params.context.credentials`, **never** in tool parameters. The LLM cannot see them and cannot leak them in conversation.
- **Least privilege.** OAuth flows ask only for scopes the user explicitly approves — e.g. Gmail read-only without send.
- **Auto-refresh.** OAuth `access_token`s are refreshed transparently using the stored `refresh_token` when expired.
- **Revocable.** Disconnecting a provider revokes the token upstream where the provider supports it (Google, Twitter, …).

## Author best practices

### 1 · Align names with `credential_mapping`

```jsonc
// ✅ Matches the registry — auto-injected for any user who has connected Google
{ "name": "GMAIL_ACCESS_TOKEN" }

// ❌ Custom name — the platform cannot map this; user must enter it manually
{ "name": "MY_GMAIL_KEY" }
```

### 2 · Read from `context` first, env as fallback

```python
def send_mail(args, *, credentials: dict | None = None):
    creds = credentials or {}
    token = creds.get("GMAIL_ACCESS_TOKEN") or os.environ.get("GMAIL_ACCESS_TOKEN")
    if not token:
        return {"success": False, "error": "GMAIL_ACCESS_TOKEN not configured"}
    # … use token …
```

### 3 · Never expose credentials as tool parameters

```jsonc
// ✅ Hidden from the LLM
{ "credentials": [{ "name": "GITHUB_TOKEN" }],
  "tools": [{ "name": "create_issue",
              "parameters": [{ "name": "title", "type": "string" }] }] }

// ❌ The LLM sees and can leak this
{ "tools": [{ "name": "create_issue",
              "parameters": [{ "name": "github_token", "type": "string" },
                             { "name": "title",        "type": "string" }] }] }
```

### 4 · Mark sensitive values

```json
{ "name": "API_SECRET", "sensitive": true }
```

`sensitive: true` switches the settings UI to a password input and keeps the value out of UI echoes.

### 5 · Provide clear acquisition instructions

```json
{
  "name": "GITHUB_TOKEN",
  "display_name": "Personal Access Token",
  "description": "GitHub → Settings → Developer settings → Personal access tokens (fine-grained recommended)"
}
```

## Adding a new provider

Adding a provider is a single registration in `src/services/credential_providers.py` — no DB schema change:

```python
_register(
    CredentialProviderDef(
        provider_id="my-service",
        name="My Service",
        icon="my-service",
        description="My Service API",
        website="https://my-service.com",
        auth_type="api_key",
        api_key_fields=[
            CredentialFieldDef(
                name="MY_SERVICE_TOKEN",
                display_name="API Token",
                description="Get one at https://my-service.com/settings/api",
            ),
        ],
        credential_mapping={ "MY_SERVICE_TOKEN": "MY_SERVICE_TOKEN" },
    )
)
```

Open a PR; the new tile shows up at `/settings/authorizations` automatically.

## See also

- [Credentials](/developers/tools/executa-credentials) — manifest schema for `credentials[]`
- [Sampling](/developers/tools/executa-sampling) — for LLM access without an API key
- [Common Pitfalls](/developers/tools/executa-pitfalls)


---

---
title: Sampling — LLM Calls Without an API Key
description: Let your plugin ask the host to perform an LLM completion on the user's behalf, with billing and model selection handled by Anna.
section: tools
slug: executa-sampling
updated: 2026-06-10
estimated_minutes: 11
---

Sampling lets your plugin invoke an LLM **on the user's behalf** without shipping your own API key, picking a model, or metering quota. The plugin describes the completion in protocol-neutral terms; Anna routes it through the user's preferred provider, charges the user's plan, and returns the result.

It's the Executa equivalent of MCP's [`sampling/createMessage`][mcp]. Available from protocol **v2** onward.

> **Need multi-turn agent runs with tool calls?** Sampling is one request → one response. For stateful, tool-using sessions (and parity with iframe anna-apps), see [Agent Sessions](/developers/tools/executa-agent).

[mcp]: https://modelcontextprotocol.io/

![Sampling reverse RPC flow](/static/images/developers/executa-sampling.svg)

## Why sampling exists

Without sampling, every plugin that wants to summarize / classify / plan would need to:

- ship its own API key (security & compliance liability),
- pick a model and chase deprecations,
- meter usage it cannot see (the user's plan, quotas, billing).

Sampling collapses all three into one capability advertised by the host.

## Three pre-conditions

End-to-end sampling needs **all** of the following:

1. **v2 negotiation.** The host sends `initialize`; the plugin replies with the same `protocolVersion: "2.0"` and lists `capabilities.sampling = {}`. See [Lifecycle](/developers/tools/executa-lifecycle#v2-capability-handshake).
2. **Manifest declaration.** The plugin's `describe` manifest includes `host_capabilities: ["llm.sample"]`. The Anna App publish validator rejects unknown capability strings.
3. **User grant.** The end user enabled sampling for this Executa in their Anna Admin panel. The grant carries `maxCalls` and `maxTokensTotal` per-invoke caps.

If any condition is missing, the host returns `-32008 SAMPLING_NOT_NEGOTIATED` and your reverse RPC is rejected before reaching a model.

## Wire protocol

After v2 is live, every `invoke` request also carries `invoke_id` and `sampling_token` inside `params.context` — see [Lifecycle](/developers/tools/executa-lifecycle#per-invoke-context-injection). While processing the invoke, your plugin **emits a reverse JSON-RPC request on stdout**:

```json
{
  "jsonrpc": "2.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      { "role": "user", "content": { "type": "text", "text": "Summarize:\n…" } }
    ],
    "maxTokens": 400,
    "systemPrompt": "You are a concise assistant.",
    "temperature": 0.3,
    "stopSequences": ["\n\n###"],
    "modelPreferences": {
      "hints": [{ "name": "claude-sonnet" }],
      "costPriority": 0.4,
      "speedPriority": 0.4,
      "intelligencePriority": 0.2
    },
    "includeContext": "none",
    "metadata": { "executa_invoke_id": "<the invoke_id>" }
  }
}
```

| Field | Required | Notes |
|---|---|---|
| `messages` | yes | Non-empty array, max **64** entries. Each entry is `{role, content:{type:"text", text}}`. Roles: `user`, `assistant`, `system`. |
| `maxTokens` | yes | Positive integer, capped at host's `maxTokensPerCall` (currently **8 192**). |
| `systemPrompt` | no | Plain text. |
| `temperature` | no | Number. |
| `stopSequences` | no | Array of strings. |
| `modelPreferences` | no | See [Model selection](#model-selection-precedence). Omit to use the user's saved preference. |
| `includeContext` | no | **Phase 1 only accepts `"none"`.** Plugins cannot read the conversation context. |
| `metadata` | no | Free dict. Convention: include `executa_invoke_id` for trace stitching. |
| `responseFormat` | no | Structured-output constraint — `{"type":"json_object"}` or `{"type":"json_schema", "json_schema":{…}}`. See [Structured output](#structured-output-responseformat). |
| `onUnsupported` | no | What to do when the selected model can't honour `json_schema`: `"error"` (default), `"json_object"`, or `"text"`. |

The host replies on stdin (the same channel) with the result:

```json
{
  "jsonrpc": "2.0",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "role": "assistant",
    "content": { "type": "text", "text": "…" },
    "model": "claude-3-5-sonnet-20241022",
    "stopReason": "endTurn",
    "usage": { "inputTokens": 312, "outputTokens": 187, "totalTokens": 499 },
    "_meta": { "provider": "anthropic", "latencyMs": 1432 }
  }
}
```

> [!IMPORTANT]
> The same stdin reader receives **both** Agent-initiated requests and host responses to your reverse RPCs. Distinguish them by the presence of a `method` field — responses have only `id` + `result|error`. The official SDKs do this for you.

## Model selection precedence

When the plugin sends `modelPreferences`, Nexus resolves the model in this order:

```
1. hints[*].name → first active model whose model_name CONTAINS the hint
                   (case-insensitive substring). With costPriority > 0,
                   ties break to cheapest.
2. (no hints / no match) → user.settings.preferred_model
3. (preferred_model unset) → default provider's cheapest active model
```

> [!TIP]
> Plugins should normally **omit `modelPreferences` entirely** so the user's saved preference applies. Hints are for tools whose quality strictly requires a particular model family.

## Structured output (`responseFormat`)

When your tool needs machine-readable output (extraction, classification, anything you'll `JSON.parse`), prompt engineering alone is fragile. `responseFormat` pushes the constraint down to the provider's decoding layer.

Two levels:

**L1 — JSON mode** (`json_object`). Guarantees syntactically valid JSON, no particular shape. Broadly compatible — works with any OpenAI-compatible model and is **not** capability-gated:

```json
{ "responseFormat": { "type": "json_object" } }
```

> [!NOTE]
> With `json_object` the provider requires the word "JSON" to appear in your prompt — keep an instruction like *"Reply with a JSON object containing …"* in the message or system prompt.

**L2 — strict JSON Schema** (`json_schema`). The model output conforms to your schema (provider-enforced constrained decoding):

```json
{
  "responseFormat": {
    "type": "json_schema",
    "json_schema": {
      "name": "summary_analysis",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "summary":  { "type": "string" },
          "keywords": { "type": "array", "items": { "type": "string" } },
          "sentiment": { "type": "string", "enum": ["positive", "neutral", "negative"] }
        },
        "required": ["summary", "keywords", "sentiment"],
        "additionalProperties": false
      }
    }
  },
  "onUnsupported": "json_object"
}
```

### Capability gating & downgrade

Not every model supports strict schemas. `json_schema` is gated on the selected model's `supports_structured_output` flag (set by the Anna admin per model; missing = unsupported). `json_object` is never gated. When the model can't honour `json_schema`, `onUnsupported` decides:

| `onUnsupported` | Behaviour |
|---|---|
| `"error"` *(default)* | Request fails with `-32010 SAMPLING_UNSUPPORTED_RESPONSE_FORMAT`; `error.data` carries `{requested, modelName}`. |
| `"json_object"` | Downgrade to L1 JSON mode. |
| `"text"` | Drop the constraint entirely — plain text generation. |

The host advertises support in its `initialize` request: `capabilities.sampling.responseFormat: ["json_object", "json_schema"]`. Hosts older than this feature simply ignore the params — design accordingly (or check the capability list).

### Schema hard limits

Validated twice (locally by the Matrix agent for fast failure, then authoritatively by Nexus). Violations are `-32004 SAMPLING_INVALID_REQUEST`:

| Limit | Value |
|---|---|
| Serialized schema size | ≤ **32 KB** |
| Nesting depth | ≤ **8** |
| Total nodes (objects + arrays + leaves) | ≤ **512** |
| `json_schema.name` | must match `^[a-zA-Z0-9_-]{1,64}$` |

### Reading the result

`content.text` **stays a string** — parse it yourself. When the request carried `responseFormat`, the response `_meta` gains an informational block:

```json
"_meta": {
  "responseFormat": {
    "requested": "json_schema",
    "applied": "json_object",
    "structuredValid": true,
    "downgraded": true
  }
}
```

- `applied` — what was actually sent to the provider (`null` if dropped via `"text"`).
- `structuredValid` — whether `content.text` parsed as JSON (informational only; **always run your own `json.loads` with a fallback**).
- `downgraded` — `true` when `applied != requested`.

```python
result = await sampling.create_message(
    messages=[...],
    max_tokens=512,
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "summary_analysis", "strict": True, "schema": SCHEMA},
    },
    on_unsupported="json_object",   # degrade gracefully instead of -32010
)
try:
    data = json.loads(result["content"]["text"])
except json.JSONDecodeError:
    data = None   # even with responseFormat, the final parse is yours
```

See the runnable [`summarize_structured` tool in sampling-summarizer](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/python/sampling-summarizer) for the full pattern.

### Testing locally

The dev harness validates `responseFormat` with the same rules as production and synthesises `_meta.responseFormat` in mock mode. To exercise your `onUnsupported` branches without a real model, drive the harness from a mock fixture whose responses omit `json_schema` support:

```bash
anna-app executa dev --dir ./my-plugin --mock-sampling ./sampling-fixture.jsonl
```

## Per-invoke caps

| Cap | Default | Where enforced |
|---|---|---|
| `maxTokens` per call | **8 192** | `DEFAULT_SAMPLING_MAX_TOKENS_PER_CALL` (host) |
| Calls per `invoke_id` | **8** | `sampling_grant.maxCalls`, host-capped at 8 |
| Total tokens per `invoke_id` | **32 000** | `sampling_grant.maxTokensTotal`, host-capped at 32 000 |
| `sampling_token` TTL | **600 s** | JWT `aud=executa-sampling` |
| `includeContext` values | only `"none"` | host rejects others as `-32004 SAMPLING_INVALID_REQUEST` |

Both call-count and total-token caps are **terminal** within the same `invoke_id` — your plugin cannot retry past them; it must shrink the workload or exit gracefully.

## Error codes

All sampling errors come back as JSON-RPC errors with stable codes:

| Code | Name | Meaning |
|---|---|---|
| `-32001` | `SAMPLING_NOT_GRANTED` | User has not enabled sampling for this Executa. |
| `-32002` | `SAMPLING_QUOTA_EXCEEDED` | User account quota exhausted. |
| `-32003` | `SAMPLING_PROVIDER_ERROR` | Upstream LLM provider failed. |
| `-32004` | `SAMPLING_INVALID_REQUEST` | Malformed params (e.g. `includeContext != "none"`, `messages` empty, `responseFormat` schema over limits). |
| `-32005` | `SAMPLING_TIMEOUT` | The completion did not finish in time. |
| `-32006` | `SAMPLING_MAX_CALLS_EXCEEDED` | Per-invoke call-count cap reached. |
| `-32007` | `SAMPLING_MAX_TOKENS_EXCEEDED` | Per-invoke cumulative token cap reached. |
| `-32008` | `SAMPLING_NOT_NEGOTIATED` | Host didn't negotiate v2, or manifest missing `host_capabilities: ["llm.sample"]`. |
| `-32009` | `SAMPLING_USER_DENIED` | User explicitly rejected this sampling request. |
| `-32010` | `SAMPLING_UNSUPPORTED_RESPONSE_FORMAT` | Model can't honour the requested `responseFormat` and `onUnsupported` is `"error"`. `data` = `{requested, modelName}`. |

The structured `error.data.errorCode` carries the symbolic name above for easy switch / match.

## Minimal Python example

```python
import json, sys, uuid, threading, queue

# Two queues — one for Agent requests, one for our own reverse-RPC responses.
agent_requests: queue.Queue = queue.Queue()
host_responses: dict[str, queue.Queue] = {}

def reader():
    for line in sys.stdin:
        msg = json.loads(line)
        if "method" in msg:                 # Agent → us
            agent_requests.put(msg)
        else:                               # response to a reverse RPC
            q = host_responses.pop(msg["id"], None)
            if q is not None:
                q.put(msg)

threading.Thread(target=reader, daemon=True).start()

def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n"); sys.stdout.flush()

def sample(invoke_id: str, prompt: str, *, max_tokens: int = 400) -> str:
    rid = str(uuid.uuid4())
    q: queue.Queue = queue.Queue()
    host_responses[rid] = q
    send({
        "jsonrpc": "2.0", "id": rid, "method": "sampling/createMessage",
        "params": {
            "messages": [{ "role": "user",
                           "content": { "type": "text", "text": prompt } }],
            "maxTokens": max_tokens,
            "includeContext": "none",
            "metadata": { "executa_invoke_id": invoke_id },
        },
    })
    resp = q.get(timeout=90)
    if "error" in resp:
        raise RuntimeError(resp["error"])
    return resp["result"]["content"]["text"]

while True:
    req = agent_requests.get()
    if req["method"] == "describe":
        send({"jsonrpc": "2.0", "id": req["id"], "result": {
            "name": "summarizer", "version": "0.1.0",
            "host_capabilities": ["llm.sample"],
            "tools": [{"name": "summarize", "description": "Summarize text",
                       "parameters": [{"name": "text", "type": "string", "required": True}]}],
        }})
    elif req["method"] == "initialize":
        send({"jsonrpc": "2.0", "id": req["id"], "result": {
            "protocolVersion": "2.0",
            "serverInfo": {"name": "summarizer", "version": "0.1.0"},
            "capabilities": {"sampling": {}},
        }})
    elif req["method"] == "invoke":
        ctx = (req["params"].get("context") or {})
        text = req["params"]["arguments"]["text"]
        try:
            summary = sample(ctx["invoke_id"], f"Summarize:\n{text}")
            send({"jsonrpc": "2.0", "id": req["id"],
                  "result": {"success": True, "data": {"summary": summary}}})
        except Exception as e:
            send({"jsonrpc": "2.0", "id": req["id"],
                  "result": {"success": False, "error": str(e)}})
```

For a polished version with retries, see the upstream
[`examples/python/sampling-summarizer/`](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/python/sampling-summarizer).

## SDK summary

| Language | Entry point |
|---|---|
| Python  | [`executa_sdk.SamplingClient.create_message`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/sdk/python/executa_sdk/sampling.py) |
| Node.js | [`new SamplingClient().createMessage()`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/sdk/nodejs/sampling.js) |
| Go      | [`sampling.New(nil).CreateMessage()`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/sdk/go/sampling/sampling.go) |

All three SDKs ship a single-reader / multi-writer dispatcher so you don't have to wire it yourself, and all three expose `responseFormat` / `onUnsupported` (Python: `response_format=` / `on_unsupported=` kwargs; Node: request options; Go: `ResponseFormat` / `OnUnsupported` struct fields).

## Common pitfalls

- **Don't `process.exit()` after writing the invoke result.** Sampling responses arrive asynchronously; exiting early drops in-flight reverse RPCs. Keep the long-running stdin loop. ([Pitfall #1](/developers/tools/executa-pitfalls#plugin-process-exits-after-one-request))
- **Always echo `invoke_id` in `metadata`.** Nexus uses it to attribute usage and enforce per-invoke caps.
- **Don't ship API keys.** If you reach for `OPENAI_API_KEY` from env, you almost certainly want sampling instead.
- **Treat `SAMPLING_MAX_TOKENS_EXCEEDED` and `SAMPLING_USER_DENIED` as terminal** — not retryable inside the same invoke.
- **Don't trust `structuredValid` as a parse.** It's informational; always `json.loads` with a fallback — and prefer `onUnsupported: "json_object"` over the default `"error"` unless your tool is useless without strict schemas.

## See also

- [Agent Sessions](/developers/tools/executa-agent) — multi-turn / tool-using extension of this same wire pattern
- [Lifecycle & Capability Negotiation](/developers/tools/executa-lifecycle)
- [Protocol Specification](/developers/tools/executa-protocol)
- [Persistent Storage](/developers/tools/executa-storage) — sister reverse-RPC capability
- [Common Pitfalls](/developers/tools/executa-pitfalls#sampling-host-capabilities-not-declared)


---

---
title: Agent Sessions — Multi-turn Tool-using Runs
description: Drive stateful, tool-using Anna Agent sessions from a stdio plugin via reverse JSON-RPC, with the same surface area as in-iframe anna-apps.
section: tools
slug: executa-agent
updated: 2026-05-15
estimated_minutes: 8
---

Sampling ([previous chapter](/developers/tools/executa-sampling)) is **one request → one response**. Agent sessions extend that pattern to **persistent threads, host-executed tools, streaming frames, and cancellation** — the same things an iframe `anna-app` can already do today.

The goal is **plugin/app parity**: a Python plugin and a TypeScript anna-app should be drop-in interchangeable for the same agentic workload. Available from protocol **v2.1** onward.

## Two API levels

| Level | Method                | Stateful? | Tool calls? | Use case                               |
|------:|-----------------------|:---------:|:-----------:|----------------------------------------|
|   L1  | `agent/complete`      |  no       |  no         | one-shot completion (sugar over sampling) |
|   L2  | `agent/session.*`     |  yes      |  yes        | multi-turn agent runs                  |

L1 is a convenience wrapper — if you only need single-turn text, prefer plain [sampling](/developers/tools/executa-sampling). L2 is what unlocks parity with anna-apps.

## Pre-conditions

End-to-end agent sessions need **all** of:

1. **v2 negotiation.** Same handshake as sampling — see [Lifecycle](/developers/tools/executa-lifecycle#v2-capability-handshake).
2. **Manifest declares both grants:**
   ```json
   { "host_capabilities": ["llm.sample", "llm.agent.auto"] }
   ```
   `llm.sample` unlocks L1 (`agent/complete`); `llm.agent.auto` unlocks L2 (`agent/session.*`). Without `llm.agent.auto` the host returns `-32041 AGENT_NOT_GRANTED`.
3. **User grant.** The end user enabled the agent capability for this Executa in Anna Admin. The grant carries the same per-invoke token caps as sampling, plus a `granted_tools` whitelist.

## Auth chain (no bearer token in the plugin)

Just like sampling, every `invoke` carries a `sampling_token` in `params.context`. The host uses **that token** to mint an `app_session_token` against nexus's `POST /copilot/app/sessions/from_sampling` endpoint, then **caches the token in-process** keyed by `(user_id, plugin_name)`. The plugin only ever sees opaque `app_session_uuid`s.

```
plugin                     matrix host                       nexus
  │                             │                              │
  │── agent/session.create ────►│                              │
  │  (sampling_token in ctx)    │── POST /sessions/            │
  │                             │     from_sampling            │
  │                             │     Bearer = sampling_token  │
  │                             │◄── {app_session_uuid, token, │
  │                             │     thread_id, ...}          │
  │                             │   (host caches token)        │
  │◄── {app_session_uuid, ...} ─│   (token stripped from result)│
```

This is **symmetric to sampling** — the plugin is never trusted with a long-TTL credential. The cache is bounded (LRU, ~4096 entries) and an `agent/session.delete` immediately evicts the entry.

## Reverse RPC methods

| Method                  | Purpose                                              |
|-------------------------|------------------------------------------------------|
| `agent/session.create`  | Mint an app session, return `{app_session_uuid, thread_id, agent_submode, granted_tools}` |
| `agent/session.run`     | Send a user message, receive an array of frames     |
| `agent/session.cancel`  | Abort an in-flight `run_id`                         |
| `agent/session.history` | (deferred — returns `[]` until v2.2)                |
| `agent/session.delete`  | Idempotent teardown; evicts the cached token        |
| `agent/complete`        | Single-turn completion (L1)                         |

### `agent/session.create` params

| Field             | Required | Notes                                                                  |
|-------------------|:--------:|-----------------------------------------------------------------------|
| `kind`            | yes      | `"agent"` (multi-turn agent) or `"fixed"` (single-tool agent)         |
| `agent_submode`   | for `kind=agent`  | `"auto"` (LLM picks tools) only in v2.1                  |
| `fixed_client_id` | for `kind=fixed`  | Tool's `client_id` to single-call against                |
| `label`           | no       | Free-text trace label                                                 |

### Frame shapes (from `agent/session.run`)

```json
{ "event": "delta",       "text": "..." }
{ "event": "tool_call",   "name": "search_web", "args": {...}, "call_id": "..." }
{ "event": "tool_result", "call_id": "...", "ok": true, "data": {...} }
{ "event": "final",       "text": "...", "usage": {...} }
```

## Streaming choice — buffered v2

`agent/session.run` is **buffered** in v2.1: the host accumulates SSE frames until `done=true`, then returns the whole array in a single JSON-RPC response. The SDK exposes them as `async for frame in session.run(...)` so business code does not change when the host switches to true real-time streaming in v2.2.

Hard cap: **4096 frames per run**. Exceeding returns `-32047 AGENT_RUN_TOO_LARGE`.

## Error codes

| Code     | Name                              | Meaning                                        |
|----------|-----------------------------------|------------------------------------------------|
| `-32041` | `AGENT_NOT_GRANTED`               | Manifest missing `llm.agent.auto`              |
| `-32042` | `AGENT_INVALID_SUBMODE`           | `kind=agent` without a valid submode           |
| `-32043` | `AGENT_FIXED_REQUIRES_CLIENT_ID`  | `kind=fixed` without `fixed_client_id`         |
| `-32044` | `AGENT_UNKNOWN_SESSION`           | `app_session_uuid` not in the host cache       |
| `-32045` | `AGENT_INVALID_UUID`              | uuid not owned by `(this user, this plugin)`   |
| `-32046` | `AGENT_NEXUS_ERROR`               | Upstream nexus failure                         |
| `-32047` | `AGENT_RUN_TOO_LARGE`             | Run exceeded the 4096-frame buffer cap         |
| `-32048` | `AGENT_TOOL_NOT_GRANTED`          | Requested a tool not in `granted_tools`        |

`AgentError` shares its base class with `SamplingError` in the Python / Node SDKs, so a single `except SamplingError` covers both surfaces.

## Minimal Python example

```python
import sys
from executa_sdk import (
    SamplingClient, AgentSessionClient, AgentError,
)

agent = AgentSessionClient()
sampling = SamplingClient()  # share the stdout writer
agent.attach_writer(_write_frame)
sampling.attach_writer(_write_frame)

# multi-turn (L2)
session = await agent.create(kind="agent", agent_submode="auto")
async for frame in session.run("Plan my week."):
    if frame["event"] == "delta":
        sys.stderr.write(frame["text"])
    elif frame["event"] == "tool_call":
        ...
await session.delete()

# single-turn (L1) — sugar over sampling
text = await agent.complete(prompt="Summarize: ...", max_tokens=200)
```

In your stdin dispatch loop, route responses by trying both clients in order:

```python
if not agent.dispatch_response(msg):
    sampling.dispatch_response(msg)
```

For a polished version (manifest, grant flags, both tools `ask_agent` and `ask_complete`), see the upstream [`examples/python/executa-agent-demo/`](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/python/executa-agent-demo).

## Symmetry with anna-app

Same lifecycle, same frame shapes, same grant gating — only the transport differs (postMessage in iframe, stdio JSON-RPC in plugin):

```ts
// inside an anna-app iframe
const session = await anna.agent.session({ submode: "auto" });
for await (const frame of session.run("Plan my week.")) {
  if (frame.event === "delta") process.stdout.write(frame.text);
}
await session.delete();
```

## SDK summary

| Language | Entry point                                                                                                                                       |
|----------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Python   | [`executa_sdk.AgentSessionClient`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/sdk/python/executa_sdk/agent.py)               |
| Node.js  | _(planned for v2.2)_                                                                                                                              |
| Go       | _(planned for v2.2)_                                                                                                                              |

## Common pitfalls

- **Always declare both `llm.sample` and `llm.agent.auto`.** L1 (`agent/complete`) is gated by `llm.sample`; L2 by `llm.agent.auto`. Missing either gives `-32041` with no further hint.
- **Never persist the `app_session_uuid` across plugin process restarts.** The host's token cache is in-process; a restart invalidates every uuid → next call returns `-32044 AGENT_UNKNOWN_SESSION`. Re-create on demand.
- **Don't `process.exit()` between `create` and `delete`.** Same rule as sampling — the dispatch loop must stay alive.
- **Treat `AGENT_RUN_TOO_LARGE` as terminal.** Shrink the workload (lower `max_tokens`, narrower toolset) rather than retrying.

## See also

- [Sampling — LLM Calls Without an API Key](/developers/tools/executa-sampling) — the L1 wire pattern this builds on
- [Lifecycle & Capability Negotiation](/developers/tools/executa-lifecycle)
- [Persistent Storage](/developers/tools/executa-storage) — sister reverse-RPC capability
- [App-Side LLM & Agent API](/developers/apps/llm-and-agent) — the same surface from the iframe-app side (parity reference)


---

---
title: Persistent Storage (APS)
description: Per-user durable KV + object store hosted by Anna — no cloud account, no DB, quota and access control enforced by the host.
section: tools
slug: executa-storage
updated: 2026-05-11
estimated_minutes: 9
---

**Anna Persistent Storage (APS)** gives an Executa plugin a small, durable, per-user **key/value + object** store hosted by Anna. There is no cloud account to provision, no credentials to ship, and no DB to run — quota and access control are enforced by Nexus.

Available from protocol **v2** onward.

![APS architecture: scopes, methods, REST mapping](/static/images/developers/executa-storage.svg)

## When to use APS

| Want to… | Use |
|---|---|
| Remember "where did the last run leave off" between invokes | KV (`storage/*`) |
| Cache an expensive computation (OCR, embeddings, derived JSON) | KV with `ttl_seconds` |
| Save a generated PDF / image / CSV the assistant can hand back to the user | Objects (`files/*`) |
| Drop a file into the **end user's drive** so other plugins can find it | Objects (`files/*` with `scope: "user"`) |

If your data is bigger than a few KB or is binary, prefer object storage — KV values are JSON and capped per-write.

## Three pre-conditions

End-to-end APS access requires **all** of:

1. **v2 negotiation.** Plugin echoes `protocolVersion: "2.0"` and exposes the storage capability in its `initialize` response (`capabilities.storage = {}` is sufficient).
2. **Manifest declaration.** `host_capabilities` lists at least one of `storage.user`, `storage.app`, `storage.tool` — only the declared scopes will be granted.
3. **User grant.** The end user enabled storage for this Executa in their Anna Admin panel. The grant pins `allowed_scopes`, `quotaBytes`, and `objectMaxBytes`.

If anything is missing, Nexus rejects the reverse RPC with `-32021 STORAGE_NOT_GRANTED`.

## Scopes

| Scope | Owner | Visibility |
|---|---|---|
| `user` | The end user | Their own dashboards & every plugin they grant. |
| `app`  | The Anna App bundle | Shared across the same app for one user. |
| `tool` | The Executa plugin | Strictly local to (user × executa). |

Defaults to `app` when `scope` is omitted. To write into the end user's drive, pass `scope: "user"` on the same `files/*` methods — the per-scope grant is enforced by the `storage_token`'s `allowed_scopes` claim, not by the method name.

> [!TIP]
> Prefer `tool` for transient state. Ask for `user` only when the user obviously benefits from cross-tool reuse — e.g. saving a generated PDF into their **My Files**.

## Wire protocol

After v2 is live, every `invoke` request also carries a short-lived `storage_token` inside `params.context` (see [Lifecycle](/developers/tools/executa-lifecycle#per-invoke-context-injection)). Reverse RPCs go out on the same stdin/stdout channel as sampling:

```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "method": "storage/set",
  "params": {
    "scope": "tool",
    "key":   "lastRun/cursor",
    "value": { "page": 7, "ts": "2026-05-01T11:22:33Z" },
    "ttl_seconds": 86400
  }
}
```

The Agent forwards every storage RPC over HTTP to Nexus's `/api/v1/storage/*` endpoints, attaching the `storage_token` as `Authorization: Bearer …`.

### Methods

| Method | Purpose | Body / query |
|---|---|---|
| `storage/get` | Read one JSON value by key | `key`, `scope` |
| `storage/set` | Write one JSON value | `key`, `value`, `ttl_seconds?`, `if_match?` |
| `storage/delete` | Soft-delete a key | `key`, `scope` |
| `storage/list` | List keys by prefix (paged) | `prefix`, `cursor?`, `limit?` |
| `files/upload_begin` | Mint a presigned PUT URL | `path`, `content_type`, `size_bytes` |
| `files/upload_complete` | Commit after PUT succeeds | `path`, `etag` |
| `files/download_url` | Mint a time-limited GET URL | `path` |
| `files/list` | List objects by prefix | `prefix`, `cursor?` |
| `files/delete` | Soft-delete an object | `path` |

Pass `scope: "user"` on any `files/*` method to target the user drive; the request is authorised iff the `storage_token`'s `allowed_scopes` claim includes `user`.

### Result shapes

| Method | Success result |
|---|---|
| `storage/get` (hit) | `{"value": …, "exists": true, "etag": "…"}` |
| `storage/get` (miss) | `{"value": null, "exists": false, "etag": null}` |
| `storage/set` | `{"etag": "…", "size_bytes": …}` |
| `storage/delete` | `{"deleted": true}` |
| `storage/list` | `{"items": [...], "next_cursor": …}` |
| `files/upload_begin` | `{"presigned_url": "https://…", "fields": {…}, "expires_at": …}` |
| `files/upload_complete` | `{"path": "…", "etag": "…", "size_bytes": …}` |
| `files/download_url` | `{"url": "https://…", "expires_at": …}` |

> [!IMPORTANT]
> The Agent normalises 404s on `storage/get` into `{"value": null, "exists": false}` so you can use the documented `cur["exists"]` pattern. **Do not** assume the value is missing just because `cur["value"]` is falsy — it may be a legitimate `0`, `""`, `false`, or `[]`.

## Optimistic concurrency

Always pass `if_match` (the previous `etag`) on overwrite to avoid lost updates:

```python
cur = await rpc("storage/get", { "scope": "tool", "key": "notes/123" })
notes = cur["value"] if cur["exists"] else []
notes.append({ "ts": now(), "text": new_text })

await rpc("storage/set", {
    "scope": "tool",
    "key":   "notes/123",
    "value": notes,
    "if_match": cur.get("etag"),     # missing on first write — that's fine
})
```

A failed precondition surfaces as `-32023 PRECONDITION_FAILED`; re-read and retry.

## Worked example — caching an OCR result

```python
import hashlib, json, sys, uuid, queue, threading

# (single-reader / dispatch boilerplate omitted — see Sampling page)

def cache_ocr(invoke_id: str, image_bytes: bytes) -> str:
    sha = hashlib.sha256(image_bytes).hexdigest()
    cur = rpc("storage/get", {"scope": "tool", "key": f"ocr/{sha}"})
    if cur["exists"]:
        return cur["value"]["text"]

    text = run_ocr(image_bytes)                   # expensive
    rpc("storage/set", {
        "scope": "tool",
        "key":   f"ocr/{sha}",
        "value": { "text": text, "ranAt": now_iso() },
        "ttl_seconds": 30 * 24 * 3600,            # 30 days
    })
    return text
```

For a runnable plugin, see the upstream
[`examples/python/storage-notebook/`](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/python/storage-notebook).

## Object uploads — two-step

Direct PUT to R2 is the recommended path for any binary or anything bigger than a few KB:

```text
①  files/upload_begin  ──▶  { presigned_url, fields, expires_at }
②  HTTP PUT to presigned_url with the bytes
③  files/upload_complete  ──▶  { path, etag, size_bytes }
```

The two-step shape lets the bytes go directly to R2 without round-tripping through the Agent's stdio. Skip step ③ and the object is silently garbage-collected after a few minutes.

## Quota & limits

| Limit | Default | Where set |
|---|---|---|
| Per-user total bytes | **5 GB** | `PlanMetric.storage_quota_bytes`, plan-overridable |
| Single KV value | **64 KB** (advisory; hard cap configured per env) | `STORAGE_ERR_VALUE_TOO_LARGE` if exceeded |
| Single object | per-grant `objectMaxBytes` | host returns `-32024 QUOTA_EXCEEDED` |
| Per-invoke storage RPCs | **200** (default `max_calls` in `storage_token`) | `STORAGE_ERR_RATE_LIMITED` if exceeded |
| `storage_token` TTL | **600 s** | JWT `aud=aps-storage` |

Treat `RATE_LIMITED` and `QUOTA_EXCEEDED` as **non-retryable** within the same invocation; treat `UPSTREAM_ERROR` as retryable with backoff.

## Error codes

| Code | Name | Meaning |
|---|---|---|
| `-32021` | `STORAGE_NOT_GRANTED` | Missing token, missing capability, or scope not allowed. |
| `-32022` | `NOT_FOUND` | Key / path does not exist (only surfaced where it's not normalised away). |
| `-32023` | `PRECONDITION_FAILED` | `if_match` etag mismatch. |
| `-32024` | `QUOTA_EXCEEDED` | Plan storage quota exhausted. |
| `-32025` | `VALUE_TOO_LARGE` | KV value above per-call ceiling. |
| `-32026` | `RATE_LIMITED` | Per-invoke RPC budget exhausted. |
| `-32027` | `INVALID_PATH` | Reserved / out-of-bucket path. |
| `-32028` | `INVALID_REQUEST` | Missing required field, wrong type. |
| `-32029` | `UPSTREAM_ERROR` | Network / 5xx from Nexus REST. |

## Built-in user-storage tools

For LangChain agents, Nexus auto-registers six high-level wrappers under the `user_storage_*` namespace:

```
user_storage_get / set / delete / list /
user_storage_files_save_text / user_storage_files_get_url
```

The agent never sees the raw RPC; the tool wraps each call in a soft **5-write / 20-read per-invocation** budget and returns the same JSON envelope as above. Users can disable these per-account via `UserSettings.disable_user_storage_tools`.

## Best practices

1. **Default to `tool` scope.** Move to `app` only when several views of the same Anna App share state, and `user` only when the data is genuinely user-owned.
2. **Encode metadata in the key, not the value.** `notes/{noteId}` is searchable via `storage/list`; embedded JSON fields are not.
3. **Keep individual KV values small** — anything bigger than a few KB belongs in objects.
4. **Always pass `if_match` on overwrite.** Lost updates are silent and miserable to debug.
5. **Set TTLs on cache-shaped data.** Quota is a finite resource shared with the user's other plugins.
6. **Treat the response as authoritative.** Always read back the `etag` after a write — never assume your client already knows it.

## See also

- [Lifecycle & Capability Negotiation](/developers/tools/executa-lifecycle)
- [Sampling](/developers/tools/executa-sampling) — sister reverse-RPC capability
- [Protocol Specification](/developers/tools/executa-protocol)
- [Common Pitfalls](/developers/tools/executa-pitfalls)


---

---
title: Binary Distribution
description: Ship one binary per platform — single-file or full multi-file bundle.
section: tools
slug: executa-binary
updated: 2026-05-11
estimated_minutes: 10
---

For end users, "install Python first" is a deal-breaker. Ship **one binary per platform** and the install becomes a single download. The Anna Agent has built-in `binary` distribution support that fetches the right asset for the current host — for both *single-file* binaries and *multi-file* bundles (binary + bundled `.so`/`.dylib` + data dirs).

## Single-file vs multi-file at a glance

| Scenario | Use | Archive shape |
|---|---|---|
| One self-contained binary (Go, Rust, PyInstaller `--onefile`, Node `pkg`) | Single-file | Raw binary, **or** `.tar.gz` / `.zip` containing the executable + `manifest.json` (recommended) |
| Binary + bundled libs / data / sub-tools | Multi-file | `.tar.gz` / `.zip` with `bin/` + `lib/` + `data/` + `manifest.json` declaring the entrypoint |

Multi-file is required whenever your binary needs to find its own bundled friends at runtime — PyInstaller `--onedir`, Electron-style apps, anything with native side-by-side `.so` / `.dylib` / DLLs.

> [!TIP]
> Even for single-file binaries we recommend the `.tar.gz` + `manifest.json` form rather than uploading a raw binary. The manifest pins your `name`, declares `permissions`, and travels with the binary so future re-publishes can't drift.

## Build matrix

| Language | Tool | Default output |
|---|---|---|
| Python | [PyInstaller](https://pyinstaller.org) `--onefile` or `--onedir` | Single executable, or directory of executable + libs |
| Node.js | [`@yao-pkg/pkg`](https://github.com/yao-pkg/pkg) (or Node 20+ SEA) | Single executable per platform |
| Go | `go build` | Native binary, no extras |
| Rust | `cargo build --release` | Native binary, no extras |

## Platform keys

The Agent auto-detects the host as `"{os}-{arch}"` (lowercase, normalized). Use these keys for your asset names and `binary_urls` map:

| Host | Platform key |
|---|---|
| macOS Apple Silicon | `darwin-arm64` |
| macOS Intel | `darwin-x86_64` |
| Linux x86_64 | `linux-x86_64` |
| Linux ARM64 | `linux-aarch64` |
| Linux ARMv7 | `linux-armv7l` |
| Windows x86_64 | `windows-x86_64` |
| Windows ARM64 | `windows-arm64` |

The Agent applies aliases so `amd64`/`x64` are folded into `x86_64` automatically. Resolution falls back from exact match → OS prefix (`darwin-*`) → wildcard (`*` / `any` / `universal`) → single-entry maps.

## `binary_urls` — value can be a string OR an asset dict

The simplest form is one URL per platform:

```json
{
  "binary_urls": {
    "darwin-arm64":  "https://example.com/v1/my-tool-darwin-arm64.tar.gz",
    "linux-x86_64":  "https://example.com/v1/my-tool-linux-x86_64.tar.gz",
    "windows-x86_64":"https://example.com/v1/my-tool-windows-x86_64.zip"
  }
}
```

For multi-file bundles or when you want sha256 verification, swap any value to an **asset dict**:

```json
{
  "binary_urls": {
    "darwin-arm64": {
      "url":        "https://example.com/v1/my-tool-darwin-arm64.tar.gz",
      "sha256":     "9b1f...c2",
      "size":       18_345_678,
      "entrypoint": "bin/my-tool",
      "format":     "tar.gz"
    },
    "linux-x86_64": "https://example.com/v1/my-tool-linux-x86_64.tar.gz"
  }
}
```

| Field | Required | What it does |
|---|---|---|
| `url` | yes | Where the Agent downloads from |
| `sha256` | optional but recommended | Agent rejects the install on mismatch |
| `size` | optional | Belt-and-braces size check |
| `entrypoint` | optional | Path inside the archive that becomes the launcher (multi-file only) |
| `format` | optional | `tar.gz` / `tgz` / `zip` / `raw`. Auto-inferred from URL suffix when omitted |

The Nexus UI exposes these fields under each platform row's **▾ Advanced** toggle.

## Multi-file binary layout

When the Agent installs a multi-file archive it lays it out like this:

```
~/.anna/executa/
  bin/my-tool                          → tools/{tool_id}/current/bin/my-tool
  tools/{tool_id}/
    v1.0.0/
      bin/my-tool                       ← entrypoint
      lib/                              ← .so / .dylib live here
      data/                              ← bundled data
      manifest.json
      INSTALL.json                      ← install metadata (auto-written)
    current  → v1.0.0                  ← atomic blue-green upgrade pointer
```

`bin/my-tool` in the user's PATH-style shim is a stable entry point that survives upgrades — `current` is rewritten atomically, so an in-flight invocation keeps reading the old version. Older versions are GC'd according to `EXECUTA_KEEP_VERSIONS` (default 2).

## Manifest `runtime.binary`

> [!IMPORTANT]
> **Always ship a `manifest.json` at the archive root** — even for single-file binaries. It pins the install identity and prevents three classes of silent breakage:
>
> 1. **`name` collisions in `bin/`.** The Agent creates `~/.anna/executa/bin/{name}` as the launcher shim, where `{name}` is the `executable_name` (or, when omitted, a slug derived from the package / URL — e.g. `https://.../my-tool-darwin-arm64.tar.gz` becomes `my`, which collides with every other tool whose URL stem starts the same way). Pass an explicit `executable_name` / `tool_id` to avoid the URL-derived fallback.
> 2. **Wrong entrypoint chosen.** Without an explicit entrypoint the Agent picks the only-or-first executable it finds in the archive, which is unpredictable for PyInstaller `--onedir`, Electron-style apps, and anything shipping helper binaries.
> 3. **Missing executable bit.** ZIP archives don't carry Unix permissions; without `permissions` the Agent only chmods the entrypoint to `0o755`, leaving auxiliary scripts (post-install hooks, sub-CLIs) at `0o644` and Permission-denied at runtime.

> [!IMPORTANT]
> **Identity is the server-minted `tool_id`.** The Agent UI joins user-installed tools to running plugins via the `tool_id` the platform passes at install time — it no longer reads a self-reported manifest `name` (neither the one your binary returns from `describe` nor the `name` in this `manifest.json`). Mismatches between those self-reported names and the `tool_id` no longer matter. See [Publishing → Stabilise the manifest](/developers/tools/executa-publish#1-stabilise-the-manifest).

Drop a `manifest.json` at the archive root:

```json
{
  "name": "tool-acme-my-tool-abcd1234",
  "version": "1.0.0",
  "runtime": {
    "binary": {
      "entrypoint": {
        "default":         "bin/my-tool",
        "windows-x86_64":  "bin/my-tool.exe",
        "windows-arm64":   "bin/my-tool.exe"
      },
      "lib_dirs":  ["lib"],
      "data_dirs": ["data"],
      "permissions": {
        "bin/my-tool":         "0o755",
        "bin/post-install.sh": "0o755"
      }
    }
  }
}
```

| Field | What it does |
|---|---|
| `name` | Human-facing label; conventionally the `tool_id` you minted on `/executa`. **Not** an identity check — the Agent joins installs to running plugins by the server-minted `tool_id` (see the note above), so a mismatch with the `name` your binary returns from `describe` is harmless. Still used as the `~/.anna/executa/bin/{name}` shim stem unless you pass `executable_name`. |
| `version` | Optional but recommended; written into `INSTALL.json` and used as the version-dir name when caller omits it |
| `runtime.binary.entrypoint` | Required for multi-file. String, or a `{ "default": "…", "darwin-arm64": "…", "windows-x86_64": "…" }` per-platform map (lookup order: full key → OS prefix → `default`) |
| `runtime.binary.lib_dirs` | Documentation only; the Agent already prepends `lib/` and `lib64/` automatically |
| `runtime.binary.data_dirs` | Documentation only; the Agent already exposes `EXECUTA_DATA` for the `data/` dir |
| `runtime.binary.permissions` | Map of relative path → octal mode. The entrypoint is `0o755` by default |

### Resolution fallback (when `manifest.json` is absent)

If you skip `manifest.json` (not recommended), the Agent walks five fallback levels in order:

1. `runtime.binary.entrypoint` from the archive `manifest.json` — *skipped, no manifest*
2. `entrypoint` from the asset dict in `binary_urls`
3. Standard locations in this order: `bin/{name}` → `bin/{name}.exe` → `{name}` → `{name}.exe` (where `{name}` is derived from the package or URL)
4. The **only** executable file in the archive
5. The **first** executable file (alphabetical), with a `WARN` log

Levels 4–5 are deliberately fuzzy because they're a last-resort. If your archive has more than one executable (very common for `--onedir`), level 5 is almost certainly going to pick the wrong one. **Provide a manifest.**

## Runtime environment your binary will see

Before launching the entrypoint the Agent injects:

| Variable | Value |
|---|---|
| `EXECUTA_HOME` | absolute path to `tools/{tool_id}/current/` |
| `EXECUTA_DATA` | `${EXECUTA_HOME}/data` (when it exists) |
| `LD_LIBRARY_PATH` | prepended `${EXECUTA_HOME}/lib` and `lib64` (Linux) |
| `DYLD_LIBRARY_PATH` | prepended `${EXECUTA_HOME}/lib` and `lib64` (macOS) |
| `PATH` | prepended `${EXECUTA_HOME}/share/bin` (when it exists; on Windows `lib/` is added too) |
| working directory | `EXECUTA_HOME` |

This means your binary can `dlopen("libfoo.so", ...)`, your Python launcher can `Path(os.environ["EXECUTA_DATA"]) / "config.toml"`, etc.

## Language guides

### Python — single file

```bash
pip install pyinstaller
pyinstaller --onefile --name my-tool plugin.py
# → dist/my-tool   (or my-tool.exe on Windows)
```

Smoke-test:

```bash
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | ./dist/my-tool
```

> [!WARNING]
> PyInstaller bundles imports it can detect statically. If you use dynamic imports (`importlib`), declare them with `--hidden-import` or PyInstaller will silently skip them.

### Python — with native dependencies

When your plugin imports something with C extensions (`numpy`, `playwright`, `cryptography` with hardware backends, etc.), PyInstaller `--onefile` may fail to bundle them or bloat to hundreds of MBs. Use `--onedir` and ship as a multi-file archive — see the [multi-file Python example](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/multifile-binary/python-pyinstaller-onedir).

### Node.js

```bash
npm install -g @yao-pkg/pkg
pkg plugin.js \
  --targets node20-macos-arm64,node20-macos-x64,node20-linux-x64,node20-win-x64 \
  --out-path dist
```

Native addons (`better-sqlite3`, `sharp`…) need extra prebuild config or a multi-file archive — see the `pkg` docs.

### Go

```bash
GOOS=darwin  GOARCH=arm64 go build -ldflags "-s -w" -o dist/my-tool-darwin-arm64  .
GOOS=darwin  GOARCH=amd64 go build -ldflags "-s -w" -o dist/my-tool-darwin-x86_64 .
GOOS=linux   GOARCH=amd64 go build -ldflags "-s -w" -o dist/my-tool-linux-x86_64  .
GOOS=linux   GOARCH=arm64 go build -ldflags "-s -w" -o dist/my-tool-linux-aarch64 .
GOOS=windows GOARCH=amd64 go build -ldflags "-s -w" -o dist/my-tool-windows-x86_64.exe .
```

`-s -w` strips the symbol table and DWARF debug info; expect ~30 % smaller binaries.

## CI: build-release.yml

The examples repo ships a [`build-release.yml`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/.github/workflows/build-release.yml) GitHub Actions workflow that builds all targets in a matrix and attaches them to the release. Copy it as a starting point and update the asset names to match the platform keys above.

## Code-signing (recommended)

| Platform | Recommendation |
|---|---|
| macOS | Apple Developer ID + `codesign` + `notarytool` for notarisation |
| Windows | Authenticode signing certificate (Sectigo, DigiCert, Azure Trusted Signing) |
| Linux | GPG-sign release archives; users verify with the published public key |

Unsigned binaries still run but trigger Gatekeeper / SmartScreen warnings on first launch. The Agent automatically clears `com.apple.quarantine` on macOS after extraction, so notarisation is the right long-term fix.

## Compatibility & rollback

- The new layout is on by default. Set the env var `EXECUTA_INSTALL_V2=0` on the Agent to fall back to the legacy "single executable in `bin/`" install path — the same archive will be re-extracted into the old shape.
- Existing legacy installs keep working: when a v2 install needs to write `bin/{name}` and finds a non-symlink there, it backs the old binary up to `~/.anna/executa/legacy-backup/` first.
- Keep the same `tool_id` across releases so `tools/{tool_id}/current` updates atomically; changing `tool_id` triggers a fresh install dir.

## Local archive distribution (no URLs, no upload)

`distribution_type: local` runs the **same v2 install pipeline** described above — extract → `tools/{tool_id}/v{version}/` → atomic `current` symlink → `bin/{name}` shim — but reads the archive from a **path on the Agent machine** instead of downloading from a URL. This is the recommended way to:

- Iterate locally on a multi-file binary (`build.sh` → `dist/plugin.tar.gz` → install) without first pushing to GitHub Releases.
- Distribute internally via NFS / shared filesystem when you can't (or won't) host an HTTPS URL.
- Install in air-gapped environments.

Form fields (Create Tool modal):

| Field | Local value |
|---|---|
| Distribution Type | `local` |
| Local Archive Path | Absolute path on the Agent host, e.g. `/Users/me/build/dist/my-tool.tar.gz` |
| Executable Name | Optional; defaults to the archive base name |
| Version | Optional; defaults to `dev` |

Same archive layout & entrypoint resolution rules as binary (see [Multi-file binary layout](#multi-file-binary-layout) and [Manifest `runtime.binary`](#manifest-runtimebinary)). All security checks (zip-slip, 5GB extract limit, `..` traversal) apply identically.

> [!NOTE]
> Sha-256 / size verification is **skipped** for local installs (the archive is on your own machine). If you need integrity checks for shared-filesystem distribution, host the file over HTTPS and use `binary` instead.

## Reference

- [Multi-file binary example (Python --onedir)](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/multifile-binary/python-pyinstaller-onedir)
- [`docs/binary-distribution.md`](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/binary-distribution.md) in the examples repo has per-language `build_binary.sh` scripts that emit the platform-key asset layout.


---

---
title: Image Generation — LLM Images Without an API Key
description: Ask the host to generate or edit images on the user's behalf, with provider selection, billing, and storage handled by Anna.
section: tools
slug: executa-image
updated: 2026-05-26
estimated_minutes: 8
---

Image generation lets your plugin produce — or restyle — images **on the user's behalf** without shipping a provider API key, without holding S3 credentials, and without metering quota. The plugin describes the image in protocol-neutral terms; Anna routes the call through the user's preferred image provider (DALL·E 3, Stable Diffusion XL, FLUX, …), charges the user's plan, uploads the result to host storage, and returns the URL.

Available from Executa protocol **v2** onward; companion to [Sampling](/developers/tools/executa-sampling) and [Storage](/developers/tools/executa-storage).

> [!TIP]
> If your tool only needs to **embed** an existing image (e.g. a brand logo the user uploaded), use [Host Upload](/developers/tools/executa-host-upload) instead — generation is for when the pixels do not exist yet.

## Three pre-conditions

End-to-end image generation requires **all** of:

1. **v2 negotiation.** The host sends `initialize`; the plugin replies with `protocolVersion: "2.0"` and lists `client_capabilities.image` (and `image.edit` if you use `image/edit`).
2. **Manifest declaration.** Your published manifest declares the capabilities it intends to use:
   ```json
   {
     "host_capabilities": ["llm.image", "llm.image.edit"]
   }
   ```
   The publish validator rejects unknown capability strings.
3. **User grant.** The end user enabled `image_grant.generate = true` (and `image_grant.edit = true`) for this Executa in their Anna Admin panel. The grant carries `max_images_per_day` and `max_per_call` caps.

If any pre-condition is missing, the host returns `IMAGE_NOT_NEGOTIATED (-32107)` or `IMAGE_NOT_GRANTED (-32101)` and the reverse-RPC never reaches a provider.

## Wire protocol

While processing an `invoke`, emit a reverse JSON-RPC request on stdout:

### `image/generate`

```json
{
  "jsonrpc": "2.0",
  "id": "img-1",
  "method": "image/generate",
  "params": {
    "prompt": "A bold art-deco poster of the planet Mars.",
    "n": 1,
    "size": "1024x1024",
    "reference_image_urls": [],
    "modelPreferences": { "hints": [{ "name": "dalle-3" }] },
    "metadata": { "executa_invoke_id": "<from-context>" }
  }
}
```

The host responds with the bare result (no wrapper):

```json
{
  "jsonrpc": "2.0",
  "id": "img-1",
  "result": {
    "images": [
      {
        "url": "https://r2.anna.partners/exec/.../poster.png",
        "mimeType": "image/png",
        "width": 1024,
        "height": 1024
      }
    ],
    "model": "dall-e-3",
    "quota_used": { "images_today": 3, "images_quota": 50 }
  }
}
```

### `image/edit`

```json
{
  "jsonrpc": "2.0",
  "id": "img-2",
  "method": "image/edit",
  "params": {
    "image_url": "https://r2.anna.partners/exec/.../poster.png",
    "prompt": "Restyle in a cyberpunk aesthetic. Preserve composition.",
    "n": 1,
    "mask_url": null
  }
}
```

`mask_url` is optional. Not every provider supports masks — if the user's preferred provider does not, the host returns `MASK_UNSUPPORTED (-32312)`.

## SDK examples

### Python

```python
from executa_sdk import ImageClient, ImageError

image = ImageClient(write_frame=_write_frame)

try:
    result = await image.generate(
        prompt="A bold art-deco poster of the planet Mars.",
        n=1,
        size="1024x1024",
        metadata={"executa_invoke_id": invoke_id},
        timeout=120.0,
    )
except ImageError as e:
    # e.code in {-32101, -32102, -32107, …}
    return _make_response(req_id, error={"code": e.code, "message": e.message})
```

### Node.js

```js
import { ImageClient } from "executa-sdk";

const image = new ImageClient({ writeFrame });
const result = await image.generate({
  prompt: "A bold art-deco poster of the planet Mars.",
  n: 1,
  size: "1024x1024",
  timeoutMs: 120000,
});
```

### Go

```go
import imageclient "github.com/openclaw/anna-executa-examples/sdk/go/image"

c := imageclient.New(writeFrame)
res, err := c.Generate(imageclient.GenerateRequest{
    Prompt: "A bold art-deco poster of the planet Mars.",
    N:      1,
    Size:   "1024x1024",
}, 120*time.Second)
```

## Error reference

| Code     | Constant                 | Meaning |
| -------- | ------------------------ | ------- |
| `-32101` | `IMAGE_NOT_GRANTED`      | User has not enabled `image_grant.generate` for this Executa. |
| `-32102` | `IMAGE_QUOTA_EXCEEDED`   | User exhausted `max_images_per_day`. |
| `-32103` | `IMAGE_PROVIDER_ERROR`   | Upstream provider 5xx / model error. |
| `-32104` | `IMAGE_INVALID_REQUEST`  | Bad `size`, empty `prompt`, etc. |
| `-32105` | `IMAGE_TIMEOUT`          | Provider exceeded host wall-clock. |
| `-32106` | `IMAGE_MAX_IMAGES_EXCEEDED` | `n` > `image_grant.max_per_call`. |
| `-32107` | `IMAGE_NOT_NEGOTIATED`   | Manifest did not list `llm.image`, or v2 not negotiated. |
| `-32108` | `IMAGE_USER_DENIED`      | User declined an in-the-moment confirm prompt. |
| `-32109` | `IMAGE_NO_MODEL_AVAILABLE` | User has no image provider configured. |
| `-32110` | `IMAGE_STORAGE_ERROR`    | Host failed to persist generated image to R2. |
| `-32311` | `EDIT_NOT_SUPPORTED`     | Selected provider does not support `image/edit`. |
| `-32312` | `MASK_UNSUPPORTED`       | Provider supports edit but not masks. |
| `-32313` | `N_UNSUPPORTED`          | Provider supports edit but not `n > 1`. |
| `-32314` | `REFERENCE_FETCH_FAILED` | `reference_image_urls[i]` was unreachable. |

## Pitfalls

> [!WARNING]
> **`n` is capped per-call AND per-day.** `image_grant.max_per_call` caps any single call; `max_images_per_day` is a rolling 24-hour counter shared across every Executa+app combo the user has granted image to. Surface the canonical error code and let the user adjust the grant — never silently retry with smaller `n`.

> [!IMPORTANT]
> **Returned URLs expire.** R2 presigned URLs default to 1 hour. If you store the URL in APS / app state, plan to refresh via `image/generate` regen, or persist via [`host/uploadFile`](/developers/tools/executa-host-upload) into a longer-lived key. Treat the URL as ephemeral artifact, not durable storage.

> [!TIP]
> **Reference images count against the `reference_image_urls[]` quota.** Each URL the host fetches is one inbound network hop billed against the user's monthly bandwidth. Keep the count small (≤ 3).

## See also

- App-side companion (anna-app bundle, Host API): [`image.*` reference](/developers/reference/host-api-image)
- Plugin sample: [`anna-executa-examples/examples/python/image-poster/`](https://github.com/openclaw/anna-executa-examples/tree/main/examples/python/image-poster)
- Persist generated bytes back to host: [Host Upload](/developers/tools/executa-host-upload)
- Lifecycle & v2 handshake: [Lifecycle](/developers/tools/executa-lifecycle)


---

---
title: Host Upload — Persist Files Without S3 Credentials
description: Hand a file (or its bytes) to Anna; the host stores it in shared R2 and returns a presigned download URL — your plugin never sees an S3 key.
section: tools
slug: executa-host-upload
updated: 2026-05-27
estimated_minutes: 7
---

`host/uploadFile` lets your plugin persist a file — text, image bytes, an LLM transcript, anything under the user's MIME allow-list — to Anna's shared R2 bucket **without holding S3 credentials**. The host writes the object under a stable per-user / per-tool / per-invoke key and returns a presigned download URL. The plugin never touches an AWS SDK and the file inherits the user's plan-level retention.

Available from Executa protocol **v2** onward; pairs naturally with [Image Generation](/developers/tools/executa-image) (persist a generated PNG outside its 30-minute window) and [Sampling](/developers/tools/executa-sampling) (persist an LLM summary).

> [!TIP]
> Use Host Upload for **ephemeral / shareable** artefacts (≤ 80 MiB total per invoke, short presigned URLs). For durable per-user data that survives across invokes — caches, notes, files in the user's drive — use [Persistent Storage (APS)](/developers/tools/executa-storage) instead.

## Three pre-conditions

End-to-end `host/uploadFile` access requires **all** of:

1. **v2 negotiation.** Reply to `initialize` with `protocolVersion: "2.0"` and a non-empty `capabilities.upload` claim (an empty object is fine).
2. **Manifest declaration.** Your published manifest declares the host capability:
   ```json
   { "host_capabilities": ["host.upload"] }
   ```
   The publish validator rejects unknown capability strings.
3. **User grant.** The end user enabled `upload_grant` for this Executa in Anna Admin. The grant carries:
   ```json
   {
     "enabled": true,
     "maxFiles": 16,
     "maxFileBytes": 26214400,
     "allowedMimeTypes": ["image/png", "application/pdf", "..."],
     "allowedPurposes": ["image_input", "image_reference", "user_artifact"]
   }
   ```
   `maxFiles` and `maxFileBytes` (single-file cap) feed the per-invoke counters. Empty `allowedMimeTypes` means **all non-blocked MIME types are accepted**; any explicit list is treated as an allow-list intersection.

Missing any pre-condition surfaces as `UPLOAD_NOT_GRANTED (-32201)` (capability / manifest / grant) or `UPLOAD_NOT_NEGOTIATED (-32210)` (no `upload_token` in the invoke context — usually means the host did not authorize this Executa at invoke time).

## Wire protocol

`host/uploadFile` is a single reverse-RPC method with three payload modes selected by `params.mode`:

```
inline      → base64 bytes (≤ 8 MiB)   ── 1 hop
negotiate   → presigned PUT URL        ── 2 hops (negotiate + plugin PUT)
confirm     → finalise presigned upload ── 1 hop (HEAD on R2 + GET url)
```

All three return a single envelope (see [Result shape](#result-shape)).

### `mode: "inline"` (recommended for ≤ 8 MiB)

```json
{
  "jsonrpc": "2.0",
  "id": "u-1",
  "method": "host/uploadFile",
  "params": {
    "mode": "inline",
    "filename": "summary.txt",
    "mime_type": "text/plain",
    "purpose": "user_artifact",
    "content_b64": "<base64 of bytes>"
  }
}
```

> [!IMPORTANT]
> **Hard 8 MiB cap on inline (decoded bytes).** This is a server constant (`INLINE_MAX_BYTES`), independent of `maxFileBytes`. Anything larger MUST use negotiate → PUT → confirm. The host returns `UPLOAD_TOO_LARGE (-32204)` after base64 decoding if exceeded.

### `mode: "negotiate"` (any size up to `maxFileBytes`)

```json
{
  "mode": "negotiate",
  "filename": "video.mp4",
  "mime_type": "video/mp4",
  "purpose": "user_artifact",
  "expected_bytes": 52428800
}
```

`expected_bytes` is optional but recommended — it lets the host reject oversized uploads before signing the URL.

The response carries a short-lived (default **5 min**) presigned PUT URL:

```json
{
  "r2_key": "exec-uploads/prod/<uuid>/<tool>/<invoke>/user_artifact/...",
  "put_url": "https://<bucket>.r2.cloudflarestorage.com/...?X-Amz-Signature=...",
  "headers": { "Content-Type": "video/mp4" },
  "expires_in": 300,
  "_meta": { "mode": "presigned-put" }
}
```

The plugin then `PUT`s the bytes directly to `put_url` with `Content-Type: <mime_type>` (no `Authorization` header — the URL is pre-signed) and finally:

### `mode: "confirm"`

```json
{
  "mode": "confirm",
  "r2_key": "<verbatim r2_key from negotiate response>"
}
```

`confirm` HEADs the R2 object, validates the upload landed, settles the byte counter against the per-invoke quota, and returns the canonical envelope (with `url`).

## Result shape

All three modes return the same envelope (only `_meta.mode` differs):

```json
{
  "r2_key":    "exec-uploads/<env>/<user>/<tool>/<invoke>/<purpose>/<ts>_<rand>_<name>",
  "url":       "https://r2.anna.partners/...?X-Amz-Signature=...",
  "mime_type": "image/png",
  "bytes":     204800,
  "expires_in": 1800,
  "_meta":     { "mode": "inline" }
}
```

| Field | Type | Notes |
|---|---|---|
| `r2_key` | string | Opaque storage key. Treat as a handle, not a navigable path. |
| `url` | string | Presigned **GET** URL. `expires_in` seconds from now. |
| `mime_type` | string | Echoes the request (lower-cased). |
| `bytes` | integer | Decoded / actual size after upload. |
| `expires_in` | integer | Seconds until `url` expires (default 30 min). Re-call `mode: "confirm"` with the same `r2_key` to mint a fresh URL at zero quota cost. |

> [!IMPORTANT]
> The returned `url` is **transient** — typically 30 minutes. If the artefact needs to survive longer, either persist the `r2_key` and re-sign on demand via `confirm`, or copy the bytes into [APS files](/executa-storage#object-uploads--two-step).

## SDK examples

### Python

```python
from executa_sdk import HostUploadClient

upload = HostUploadClient(write_frame=_write_frame)

result = await upload.upload_inline(
    filename="poster.png",
    mime_type="image/png",
    content=png_bytes,           # raw bytes; SDK base64-encodes
    purpose="user_artifact",
    timeout=60.0,
)
print(result["url"], result["bytes"], "expires_in", result["expires_in"], "s")
```

### Node.js

```js
import { HostUploadClient } from "executa-sdk";

const upload = new HostUploadClient({ writeFrame });
const out = await upload.uploadInline({
  filename: "poster.png",
  mimeType: "image/png",
  content: pngUint8,          // Uint8Array; SDK base64-encodes
  purpose: "user_artifact",
});
```

### Go

```go
import upload "github.com/openclaw/anna-executa-examples/sdk/go/host_upload"

c := upload.New(writeFrame)
res, err := c.UploadInline(upload.InlineRequest{
    Filename: "poster.png",
    MimeType: "image/png",
    Content:  pngBytes,
    Purpose:  "user_artifact",
}, 60*time.Second)
```

## Error reference

The plugin sees these JSON-RPC errors (wire codes & names from `matrix/src/executa/protocol.py`):

| Code     | Constant                    | Meaning |
| -------- | --------------------------- | ------- |
| `-32201` | `UPLOAD_NOT_GRANTED`        | Capability missing, manifest didn't declare `host.upload`, or `upload_grant.enabled = false`. |
| `-32202` | `QUOTA_EXCEEDED`            | Plan upload quota exhausted. |
| `-32203` | `INVALID_REQUEST`           | Bad `mode`, missing `filename` / `mime_type`, malformed `content_b64`, etc. |
| `-32204` | `TOO_LARGE`                 | Decoded bytes exceed `maxFileBytes` or the 8 MiB inline cap. |
| `-32205` | `MIME_REJECTED`             | `mime_type` not in `allowedMimeTypes` or on the host block-list (executables, `image/svg+xml`). |
| `-32206` | `PURPOSE_REJECTED`          | `purpose` not in the protocol whitelist (`image_input` / `image_reference` / `user_artifact`) or not in `allowedPurposes`. |
| `-32207` | `STORAGE_ERROR`             | R2 5xx / network. Also wraps subcall timeouts (`errorName: "subcall_timeout"`). |
| `-32208` | `TIMEOUT`                   | Provider call exceeded the host wall-clock. |
| `-32209` | `USER_DENIED`               | User declined an in-the-moment confirm prompt. |
| `-32210` | `UPLOAD_NOT_NEGOTIATED`     | v2 not negotiated, or reverse-RPC invoked outside an invoke context. |
| `-32211` | `MAX_FILES_EXCEEDED`        | Per-invoke `maxFiles` hit. |
| `-32212` | `NOT_FOUND`                 | `confirm` on an unknown `r2_key` (object not uploaded yet, or wrong tool / invoke). |
| `-32213` | `PRESIGN_FAILED`            | Host could not sign the PUT URL. |

## Quota & limits

| Limit | Default | Source |
|---|---|---|
| Inline payload (decoded) | **8 MiB** | `INLINE_MAX_BYTES` |
| Single-file size cap | **20 MiB** (token default); grants typically widen to **25 MiB** | `upload_token.max_file_bytes`, `upload_grant.maxFileBytes` |
| Per-invoke total bytes | **80 MiB** | `upload_token.max_total_bytes` |
| Per-invoke file count | **16** | `upload_token.max_files`, `upload_grant.maxFiles` |
| Presigned PUT URL TTL | **300 s** | `DEFAULT_PRESIGN_PUT_EXPIRY` |
| Returned GET URL TTL | **~30 min** | `R2_TRANSIENT_PRESIGN_EXPIRY` |
| `upload_token` TTL | **600 s** (10 min) | JWT `aud=executa-upload` |
| Default `allowedPurposes` | `image_input`, `image_reference`, `user_artifact` | `DEFAULT_UPLOAD_ALLOWED_PURPOSES` |

Treat `QUOTA_EXCEEDED`, `MAX_FILES_EXCEEDED`, and `TOO_LARGE` as **non-retryable** within the same invocation; treat `STORAGE_ERROR` / `TIMEOUT` as retryable with backoff (≤ 2 attempts).

## Pitfalls

> [!WARNING]
> **Inline payload is base64.** Wire size is ≈ 1.33 × the decoded bytes. A 7 MiB file becomes ~9.3 MiB on the wire — if your stdio frame writer caps at 8 MiB you'll truncate before the host even sees the request. SDKs encode for you, but if you hand-build frames, size-check the **encoded** length.

> [!IMPORTANT]
> **`r2_key` is opaque, not navigable.** Do not parse or construct it. The host owns the layout (`exec-uploads/<env>/<user>/<tool>/<invoke>/<purpose>/<ts>_<rand>_<name>`); future migrations may change it. Use `url` to share, `r2_key` only as an opaque handle for `confirm`.

> [!TIP]
> **`purpose` drives lifecycle policy.** Pick the most accurate value:
> - `image_input` — bytes the user uploaded into the plugin (model input).
> - `image_reference` — reference images passed to `image/generate`.
> - `user_artifact` — anything the plugin produced and wants to hand back to the user (default).
>
> Anything else returns `PURPOSE_REJECTED (-32206)`.

> [!CAUTION]
> **SVG is blocked.** `image/svg+xml` can carry executable JS → XSS risk. Use PNG / JPEG / WebP instead. Other blocked MIME types: `application/x-msdownload`, `application/x-msdos-program`, `application/x-executable`, `application/x-sharedlib`.

## See also

- App-side companion (anna-app bundle, Host API): [`upload.*` reference](/developers/reference/host-api-upload)
- Plugin sample: [`anna-executa-examples/examples/python/image-poster/`](https://github.com/openclaw/anna-executa-examples/tree/main/examples/python/image-poster) — uses `host/uploadFile` to persist a generated poster.
- Image generation: [Image (Tool)](/developers/tools/executa-image)
- Durable per-user storage: [Persistent Storage (APS)](/developers/tools/executa-storage)
- Lifecycle & v2 handshake: [Lifecycle](/developers/tools/executa-lifecycle)


---

---
title: Publishing a Tool
description: From local prototype to a discoverable, installable Executa tool.
section: tools
slug: executa-publish
updated: 2026-05-11
estimated_minutes: 6
---

The `/executa` page hosts the Tool / Skill lifecycle: create a draft, fill in the manifest, then choose how widely to publish it. Pro / Max users may publish their own tools.

## 1. Stabilise the manifest

Before publishing, do a self-review:

- [ ] Tool `name`s are stable. Renaming after publish breaks every saved conversation that referenced them.
- [ ] Each `description` reads well to an LLM — it's the prompt the model uses to decide whether to call your tool.
- [ ] Parameters are typed; arrays declare `items` so the LLM passes a real list, not a JSON-encoded string.
- [ ] Failure paths return `{ "success": false, "error": "…actionable message…" }` (or a JSON-RPC `error` for programmer errors).
- [ ] Credentials are declared with stable `name`s.
- [ ] `version` follows SemVer.
- [ ] Plugin process is **long-running** (loops on stdin until EOF). A one-shot process passes `describe` once and then shows up as **Stopped** in the UI forever — see [Common pitfalls](/developers/tools/executa-intro#common-pitfalls).

> [!IMPORTANT]
> **Identity is the server-minted `tool_id` — nothing else.** You **cannot** pick this string yourself; it is always `tool-{author_handle}-{slug}-{uniq}`, reserved by the **🪣 Mint** button, and the platform passes it to the Agent when the tool is installed.
>
> The Agent no longer reads a self-reported manifest `name` (neither the one your binary returns from `describe` nor the one in the archive `manifest.json`). You do **not** need to bake the `tool_id` into either of them. The Agent UI joins user-installed tools to running plugins via the minted `tool_id`.

## 2. Mint a stable `tool_id` first

Open the `/executa` page, switch to the **My Tools** tab, and click **Create Tool**. In the form:

1. Fill in **Name** and **Type** (`tool` / `skill`).
2. Click the **🪪 Mint** button next to the Tool ID field. **This step is mandatory** — the Tool ID input is read-only and the **Create** button is disabled until you mint.

Mint reserves a stable `tool_id` (`tool-{author_handle}-{slug}-{uniq}`) and locks it for your account. Copy this ID — you'll bake it into the binary in the next step. The button then shows **🔒 Minted**, and the ID is yours for the next 24 h even if you walk away (drafts expire after 24 h if never committed).

> [!IMPORTANT]
> **Mint-only policy.** Tool IDs are entirely server-controlled; clients cannot supply or override `tool_id` via the REST API or UI. Any `tool_id` field on a `POST /executas/my/tools` payload is silently dropped. The only way to obtain an ID is via the **🪪 Mint** flow (`POST /executas/my/drafts` → `POST /executas/my/drafts/{id}/commit`).

> [!IMPORTANT]
> Mint **before** building. The `tool_id` is the canonical identity the Agent uses to install, route, and pin versions of your tool. If you publish a binary first, you'll have to rebuild and re-upload everything to align them.

## 3. Build & host artifacts (binary distribution)

Now that you have the `tool_id`, build your tool and host the assets on GitHub Releases or any HTTPS CDN — follow [Binary Distribution](/developers/tools/executa-binary) for platform-key naming. You no longer need to embed the `tool_id` into the manifest your binary returns from `describe` or the `manifest.json` at the archive root; the platform tracks identity via the minted `tool_id` and passes it to the Agent at install time.

If you ship via `uv` / `npm` / `pipx` / `homebrew` instead, publish to that registry now; the Agent installs from there. (Local-only tools can skip this section.)

## 4. Fill in the rest of the form and publish

Back on the `/executa` Create Tool form (the draft you minted in step 2 is still open), fill in the remaining fields and click **Create**:

1. **Manifest** — paste the JSON your binary returns from `describe`. The form auto-extracts tools, credentials, and version.
2. **Distribution** — pick `distribution_type` (`uv` / `npm` / `homebrew` / `binary` / `pipx` / `local`), set `package_name`, `executable_name`, and:
   - For `binary`: the per-platform URLs you hosted in step 3.
   - For `local`: the absolute path to a local archive on the Agent machine (`.tar.gz` / `.tgz` / `.zip` / raw single executable). The Agent runs the **same install pipeline as `binary`** — extracts the archive into `tools/{tool_id}/v{version}/`, resolves the entrypoint, creates the `current` symlink, and registers the bin shim. This means Local **fully supports multi-file binaries** (PyInstaller `--onedir`, native `.so`, etc.); see [Local archive distribution](/developers/tools/executa-binary#local-archive-distribution-no-urls-no-upload).
3. **Capabilities & docs** — logo URL, README, sample prompts, capability tags.
4. **Visibility** — `private`, `app_bundled`, or `public` (see below).

Clicking **Create** promotes the draft into a real Executa under your account. The `tool_id` you minted in step 2 stays the same.

> [!NOTE]
> The whole flow is UI-driven on `/executa`; you don't need to call any HTTP endpoints by hand. The page handles draft reservation, manifest patching, and commit for you.

## 5. Choose a visibility

| Visibility | Where it appears | Who can install |
|---|---|---|
| `private` | Only your `/executa` workspace | Only you |
| `app_bundled` | Hidden from the Explore Hub, but installable as part of any Anna App that bundles it | Anyone who installs the host App |
| `public` | Listed in the Explore Hub | Anyone |

Use `app_bundled` when your tool is meant to ship alongside a specific Anna App rather than as a standalone offering. Switch between the three states using the visibility segmented control on each tool card in **My Tools** — no API call required.

## 5a. Iterate before publishing — the dev loop

You do **not** need to flip visibility to `public` (i.e. **Publish**) to test that your tool installs on an Agent. Doing so prematurely is the common cause of "every failed install leaves a useless tool behind". The intended dev loop is:

1. **Create** the Executa with `visibility=private`, and **Mint** a `tool_id` (sections 2 & 4 above). Don't click Publish yet.
2. From **/executa → My Tools**, click the install/enable toggle so a `UserExecuta` row is created for your account.
3. Go to **/agents → Install Essentials**. Your unpublished private Executa is picked up by the same batch installer the published ones use — `is_published` is **not** a filter on this path.
4. If the install fails, edit the Executa (description, `distribution_url`, `binary_urls`, manifest, …) and click Install Essentials again. **The same `tool_id` is reused on every retry — no new tool created, no cleanup needed.**
5. Only once the install succeeds end-to-end do you promote `visibility` to `app_bundled` (for a host Anna App) or `public` (Hub listing). The first promotion is the point at which an immutable `ExecutaVersion` snapshot is frozen.

> [!TIP]
> Editing an already-bundled tool is allowed and safe: the live row is mutable, but every published Anna App version pins to the **frozen `ExecutaVersion` snapshot** taken at its release, so existing users are not affected. The edit modal shows a banner reminding you of this.

## 6. Publish a new version

When you ship a manifest or binary update, click **New Version** on the tool card. Each publish freezes an immutable `ExecutaVersion` snapshot so apps that pin to a version see stable content. The version number auto-bumps SemVer patch unless you set a specific value in the manifest first.

If the manifest hasn't changed since the last published version, the action is rejected with "No content changes since the last published version" — update the manifest before re-publishing.

## 7. Promote inside an Anna App

The most common discovery path for a tool isn't the Hub — it's an Anna App that bundles it. Once your tool exists (any visibility), an Anna App can list its `tool_id` in the App manifest. See [What is an Anna App](/developers/apps/app-intro).

> [!TIP]
> Tools that don't appear in any App typically see a small fraction of the installs of those that do. Bundle your tool into a complementary App to maximise distribution.


---

---
title: Common Pitfalls
description: The bugs that show up most often when authors build Executa plugins, and how to spot them fast.
section: tools
slug: executa-pitfalls
updated: 2026-05-11
estimated_minutes: 8
---

If your plugin "installs" but the Anna UI shows it as **Stopped** (or it doesn't appear at all), this is the first page to read. Each pitfall lists the symptom you'll observe, the root cause, and the fix.

---

## 1 · Plugin process exits after one request

**Symptom**

- Manual test works: `echo '{"jsonrpc":"2.0","method":"describe","id":1}' | ./my-plugin` returns a manifest.
- The Agent UI shows the plugin card as **Stopped** immediately after install.
- Each tool call pays a noticeable cold-start delay.

**Cause**

Executa is a **long-running** protocol. The Agent spawns one process per plugin and reuses it for every `describe` / `invoke` / `health`. A plugin that returns from `main()` (or calls `sys.exit()` / `process.exit()` / `os.Exit()`) after handling a single request is broken — every subsequent request triggers a restart, and the UI never observes a live process.

**Fix**

Loop on stdin until EOF. The Agent closes stdin to request shutdown.

```python
# Python
import json, sys
for line in sys.stdin:                     # ← loop until EOF
    line = line.strip()
    if not line: continue
    req = json.loads(line)
    resp = handle(req)
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()                     # ← required
```

```javascript
// Node.js
const readline = require("readline");
const rl = readline.createInterface({ input: process.stdin });
rl.on("line", (line) => {
  const req = JSON.parse(line);
  process.stdout.write(JSON.stringify(handle(req)) + "\n");
});
// Don't call process.exit(); let the runtime exit naturally on stdin close.
```

```go
// Go
scanner := bufio.NewScanner(os.Stdin)
scanner.Buffer(make([]byte, 0, 1024*1024), 1024*1024)
for scanner.Scan() {                       // ← loop until EOF
    line := strings.TrimSpace(scanner.Text())
    if line == "" { continue }
    // ... handle and Fprintln(os.Stdout, ...) ...
}
```

**Quick local check**

```bash
./my-plugin <<< '{"jsonrpc":"2.0","method":"describe","id":1}' &
PID=$!
sleep 2
if kill -0 $PID 2>/dev/null; then
  echo "OK — still running"
  kill $PID
else
  echo "BUG — plugin exited after one request"
fi
```

---

## 2 · Three names don't match (`tool_id` vs `describe.name` vs archive `manifest.json` `name`)

**Symptom**

- The plugin appears under **Extra Agent Plugins** in the UI instead of next to the tool you installed.
- Or: the user-installed card shows **Stopped** while a duplicate appears as **Running** elsewhere.
- Or: `~/.anna/executa/bin/` contains a file with a generic name like `tool` instead of your tool ID.

**Cause**

Three identifiers must be **exactly** equal:

| Where | What |
|---|---|
| Anna `/executa` form (Tool ID field) | The `tool_id` minted with the 🪪 button, e.g. `tool-acme-my-tool-abcd1234` |
| Your binary | The `name` field in the manifest your plugin returns from `describe` |
| Archive root `manifest.json` | The `name` field in the JSON file you ship inside the `.tar.gz` / `.zip` |

The Agent UI joins user-installed tools to running plugins by string-matching these three; the archive `manifest.json` `name` also becomes the launcher symlink at `~/.anna/executa/bin/{name}`.

**Fix**

Pick the value once when you mint the `tool_id` and paste it everywhere. `display_name` is for the human-readable label — `display_name: "My Tool"` is fine; only `name` has to match.

---

## 3 · Banner / debug text on stdout

**Symptom**

- Agent log shows `Failed to parse JSON-RPC frame`.
- `describe` times out from the Agent's side even though `echo … | ./my-plugin` works.

**Cause**

You printed something to stdout before — or between — JSON-RPC responses. The Agent only treats lines that parse as JSON objects as protocol frames; banners and stray prints corrupt the stream.

**Fix**

All human-readable output goes to **stderr**:

```python
print("🔌 plugin started", file=sys.stderr)            # ✅
sys.stdout.write(json.dumps(response) + "\n")          # ✅ JSON-RPC only
```

```javascript
console.error("🔌 plugin started");                    // ✅
process.stdout.write(JSON.stringify(response) + "\n"); // ✅
```

---

## 4 · Manifest uses MCP-style `input_schema` instead of `parameters`

**Symptom**

- The plugin loads and the LLM calls the tool, but with **fabricated argument names** like `content`, `input`, or `query` that you never declared.
- Your tool's parameter dict shows up empty or partially filled — yet the tool returns success, so the failure is silent.

**Cause**

Matrix's `ToolDefinition.from_dict` reads the protocol-native `parameters` array. If you ship MCP-flavoured `input_schema` (a JSON Schema object), Matrix sees zero declared parameters; the LLM gets an undocumented tool and hallucinates argument names.

**Fix**

Use the canonical Executa shape:

```json
{
  "tools": [{
    "name": "send",
    "description": "Send a tweet",
    "parameters": [
      { "name": "text", "type": "string", "required": true,
        "description": "Tweet body, ≤ 280 chars" }
    ]
  }]
}
```

Not:

```jsonc
// ❌ Silently ignored by Matrix — produces empty parameter list
"input_schema": {
  "type": "object",
  "properties": { "text": { "type": "string" } },
  "required": ["text"]
}
```

See [Protocol Specification — Parameter schema](/developers/tools/executa-protocol#parameter-schema) for supported types.

---

## 5 · Wrong `result` shape for `describe` vs `invoke`

The two methods are asymmetric — easy to mix up.

**`describe`** returns the manifest **directly** as the `result`:

```json
{ "jsonrpc": "2.0", "id": 1, "result": { "name": "…", "tools": [...] } }    ✅

{ "jsonrpc": "2.0", "id": 1, "result": { "manifest": { … } } }              ❌
```

The wrong shape causes the Agent to log `❌ 无法获取 describe: …: 'name'` and drop the plugin at load time.

**`invoke`** returns a wrapped object inside `result`:

```json
{ "jsonrpc": "2.0", "id": 2,
  "result": { "success": true, "data": { … }, "duration_ms": 12 } }         ✅

{ "jsonrpc": "2.0", "id": 2, "result": { "etag": "…", "count": 5 } }        ❌
```

Without `success: true`, Matrix's `InvokeResult.from_dict` defaults `success = false` and the LLM thinks the call failed — even though your tool ran fine.

---

## 6 · Missing `manifest.json` in multi-file archives

**Symptom**

- After install, the Agent picks the wrong executable (e.g. a helper binary instead of the main one).
- Auxiliary scripts (`bin/post-install.sh`, sub-CLIs) get `Permission denied` at runtime.
- `~/.anna/executa/bin/` ends up with a generic name derived from the URL.

**Cause**

Without `manifest.json`, the Agent walks a five-level fallback (asset `entrypoint` → `bin/{name}` → only-or-first executable) and ZIP archives lose Unix permission bits. Both produce silent footguns when the archive contains more than one executable.

**Fix**

Always ship `manifest.json` at the archive root, even for single-file binaries:

```json
{
  "name": "tool-acme-my-tool-abcd1234",
  "version": "1.0.0",
  "runtime": {
    "binary": {
      "entrypoint": {
        "default":        "bin/my-tool",
        "windows-x86_64": "bin/my-tool.exe"
      },
      "permissions": {
        "bin/my-tool":         "0o755",
        "bin/post-install.sh": "0o755"
      }
    }
  }
}
```

See [Binary Distribution](/developers/tools/executa-binary).

---

## 7 · PyInstaller cold start exceeds the 5 s `describe` timeout

**Symptom**

- The first invocation after a fresh install fails with `describe timeout`. Subsequent calls work.

**Cause**

PyInstaller `--onefile` extracts the bundle to a temp directory on first launch; on a 200 MB+ binary this can take 10–30 s, especially on Apple Silicon under Rosetta or on slow filesystems.

**Fix**

The Agent already grants binary distributions a **60 s** describe timeout for the post-install scan, but the steady-state cap is back to 5 s. Three options, in order of preference:

1. Switch to `--onedir` and ship as a multi-file archive.
2. Reduce bundle size — `--exclude-module`, audit `--collect-all` flags.
3. Move heavy initialization into `invoke` rather than module-import / `describe` time.

---

## 8 · Sampling — `host_capabilities` not declared

**Symptom**

Your plugin issues `sampling/createMessage`, the host returns `error: { code: -32008, message: "not_negotiated" }`, and the Agent log says *"executa X did not declare host_capabilities['llm.sample']"*.

**Cause**

Even after v2 negotiation, Nexus refuses sampling unless the plugin's published manifest **also** declares the capability.

**Fix**

```json
{
  "name": "my-tool",
  "host_capabilities": ["llm.sample"],
  "tools": [ /* ... */ ]
}
```

Re-publish the Executa version and ask users to update. See [Sampling](/developers/tools/executa-sampling#three-pre-conditions).

---

## 9 · Sampling / Storage — plugin exits before reverse RPC completes

**Symptom**

First reverse RPC call works in dev, but in production the result never arrives — Agent logs *"unmatched response id=…"* and the host times out.

**Cause**

The plugin returned the `invoke` result and immediately did `process.exit()` / `sys.exit()`, killing the stdin reader before the reverse-RPC response could be dispatched.

**Fix**

Same as Pitfall #1 — the plugin process must be long-running. The official SDKs (`sdk/{python,nodejs,go}` in [anna-executa-examples](https://github.com/whtcjdtc2007/anna-executa-examples)) ship a single-reader-with-dispatch pattern that handles both Agent requests **and** host responses to your reverse RPCs. Use it.

---

## 10 · Sampling — `MAX_TOKENS_EXCEEDED` on a single small call

**Symptom**

A reasonable sampling request fails with `-32007 MAX_TOKENS_EXCEEDED` even though `maxTokens` is well under 8 192.

**Cause**

The cap is **cumulative across the same `invoke_id`**, not per call. Default total is 32 000 tokens.

**Fix**

Send fewer / smaller sampling calls per tool invocation, or ask the user to raise `sampling_grant.maxTokensTotal` in their Anna Admin panel (host caps it at 32 000 in v1).

---

## 11 · Storage — `cur["value"]` looks empty even on a successful read

**Symptom**

Your read-modify-write pattern silently overwrites previous data:

```python
cur = await rpc("storage/get", {"scope": "tool", "key": "log"})
log = cur["value"] if cur["value"] else []   # ← always [] even after writes!
```

**Cause**

Legitimate values include `0`, `""`, `false`, `[]`, `{}` — all falsy. Truthiness is the wrong check. The Agent guarantees an `exists` field on **both** hit and miss responses, exactly to avoid this trap.

**Fix**

Always branch on `exists`:

```python
log = cur["value"] if cur.get("exists") else []
```

See [Persistent Storage — Result shapes](/developers/tools/executa-storage#result-shapes).

---

## 12 · Storage — using the wrong scope or omitting it

**Symptom**

Data written by version 1 of your plugin is invisible to version 2; or two unrelated plugins clobber each other under the same key.

**Cause**

`scope` defaults to `"app"` when omitted. If you actually wanted plugin-private state, it ended up in the broader app namespace; if you wanted user-shared state, it ended up siloed by app.

**Fix**

Always pass `scope` explicitly:

| Want | Pass |
|---|---|
| Plugin-private state | `scope: "tool"` |
| Shared between views of the same Anna App | `scope: "app"` |
| Visible across the user's whole drive | `scope: "user"` on any `files/*` or `storage/*` call |

---

## See also

- [Lifecycle & Capability Negotiation](/developers/tools/executa-lifecycle)
- [Protocol Specification](/developers/tools/executa-protocol)
- [Sampling](/developers/tools/executa-sampling)
- [Persistent Storage](/developers/tools/executa-storage)
- [Binary Distribution](/developers/tools/executa-binary)


---



# === Build a Skill ===

---
title: What is a Skill
description: Skills are the declarative flavour of Executa: a folder of markdown that Anna loads on demand and turns into a LangChain tool.
section: skills
slug: skill-intro
updated: 2026-04-23
estimated_minutes: 4
---

A **Skill** is the *declarative* flavour of [Executa](/developers/overview/concepts). It's a folder containing a `SKILL.md` plus optional supporting files (examples, templates, scripts, datasets) that teaches Anna *how* to do something. At runtime the loader registers each skill as a LangChain `@tool`; when the LLM picks it, the tool returns the skill's markdown body — along with an execution-mode hint and any declared dependencies — and the agent then uses its built-in `exec` / `command` tools to run any bash or Python the body recommends.

> [!NOTE]
> Skills do **not** execute code by themselves. The skill body is delivered to the LLM as instructions; running anything is the agent's job, via its existing execution tools. That is why `execution_mode` is a *hint* ("this skill is best run via bash") and not an interpreter selection.

## When to ship a Skill (vs. a Tool Executa)

Both are Executas — same Hub, same draft → version → visibility lifecycle. The difference is the *shape* of the artifact.

| Ship a **Skill** when… | Ship a **Tool** when… |
|---|---|
| You want to teach Anna a process, style, or workflow | You need to maintain a long-running process with credentials |
| The work is mostly markdown + commands the agent can run via `exec` | You need bidirectional JSON-RPC, streaming, or complex SDK integrations |
| You want users to read / fork / customise the body | You want a black-box contract behind a stable manifest |

The two compose well: a `chart-generator` Skill teaches Anna *when and how* to render a chart, and may itself recommend calling a `pandas-tools` Tool Executa for heavier data wrangling.

## Anatomy

```
my-skill/
├── SKILL.md            # required — frontmatter + body
├── examples/
│   ├── input-1.md
│   └── output-1.md
├── templates/
│   └── report.md.tpl
└── README.md           # optional — for humans browsing the source
```

## A minimal SKILL.md

```markdown
---
name: meeting-summary
description: Turn raw meeting notes into a structured summary with decisions, action items, and open questions.
metadata: {"matrix":{"emoji":"📝","execution_mode":"prompt","category_name":"productivity"}}
---

# Meeting Summary Skill

When the user provides raw meeting notes, produce a summary with three sections:

## Decisions
- Bullet list of every decision the group made.

## Action Items
- `[ ] Owner — task — due date`

## Open Questions
- Bullet list of unresolved items.

If owner or due date is missing, write `?` and surface it as an open question.
```

The body is markdown that the LLM receives when it calls the skill. Frontmatter has two required keys (`name`, `description`) and one structured `metadata` blob — see [Skill format](/developers/skills/skill-format).

## Where to next

- **Format spec** — [Skill format](/developers/skills/skill-format).
- **Run locally** — [Local development](/developers/skills/skill-local).
- **Publish** — [Publishing](/developers/skills/skill-publish).


---

---
title: Skill Format
description: The frontmatter, metadata structure, and supporting files that make a Skill loadable.
section: skills
slug: skill-format
updated: 2026-04-23
estimated_minutes: 6
---

A Skill is the declarative flavour of an [Executa](/developers/overview/concepts). Every Skill is a folder; its entry point is **`SKILL.md`** — markdown with YAML frontmatter, where one frontmatter key (`metadata`) carries a JSON blob describing execution mode and dependencies.

## Top-level frontmatter

```yaml
---
name: short-kebab-name
description: One-sentence description used at skill-discovery time.
metadata: {"matrix":{ ... }}
---
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `name` | string | yes | Lowercase kebab-case; defaults to the parent directory name if omitted |
| `description` | string | yes | What the LLM uses to decide when to load the skill — write it as a search query the user might type |
| `metadata` | JSON | no | One-line JSON blob (see below) carrying executable metadata |

Top-level `version` / `author` are accepted but currently informational — versioning happens at publish time via the Executa version snapshot.

## The `metadata` blob

The loader (`src/skills/frontmatter.py`) parses `metadata` as JSON. If the JSON has a top-level `matrix`, `openclaw`, or `nexus` key (in that order), the value of that key is used as the actual structured metadata; otherwise the JSON is consumed directly. Real example from the bundled `chart-generator` skill:

```yaml
---
name: chart-generator
description: "Use matplotlib and seaborn to create publication-quality charts…"
metadata: {"matrix":{"emoji":"📈","execution_mode":"python","category_name":"data-analysis","requires":{"python_packages":["matplotlib","seaborn"]},"install":[{"id":"pip","kind":"pip","package":"matplotlib seaborn","label":"Install matplotlib & seaborn (pip)"}],"uninstall":[{"id":"pip","kind":"pip","command":"pip uninstall matplotlib seaborn","label":"Uninstall matplotlib & seaborn (pip)"}]}}
---
```

### Recognized fields under `matrix`

| Key | Type | Notes |
|---|---|---|
| `always` | boolean | Load this skill into every conversation (use sparingly — reserved for foundational tooling like `uv`) |
| `skill_key` | string | Override identifier (defaults to `name`) |
| `primary_env` | string | Required environment variable hint shown in onboarding |
| `emoji` | string | Display icon |
| `homepage` | string | Documentation link |
| `category_name` | string | Free-form group used by the Skill catalogue (`productivity`, `data-analysis`, `network`, `office`…) |
| `os` | array | Limit availability (`["macos", "linux", "windows"]`) |
| `execution_mode` | enum | `prompt` (default) / `bash` / `python` / `api` / `hybrid` |
| `parameters` | array | Optional input parameters declared like Executa tool parameters |
| `requires` | object | Dependency declarations (see below) |
| `install` | array | Install recipes (see below) |
| `uninstall` | array | Matching uninstall recipes |

### `requires`

Declare what the skill needs available at runtime. The agent surfaces missing requirements during onboarding:

```json
"requires": {
  "bins": ["jq"],                         // executables that MUST be on PATH
  "any_bins": ["uv", "curl"],             // satisfied by ANY one being present
  "env": ["GITHUB_TOKEN"],                // required environment variables
  "config": ["github.host"],              // required config keys
  "python_packages": ["matplotlib"]       // pip-installable packages
}
```

### `install` / `uninstall`

A list of recipes; the agent picks the first one matching the host OS and an available installer.

```json
"install": [
  {"id": "brew",  "kind": "brew",  "formula": "jq",  "bins": ["jq"], "os": ["macos"],  "label": "Install jq (brew)"},
  {"id": "apt",   "kind": "apt",   "package": "jq",                   "os": ["linux"],  "label": "Install jq (apt)"},
  {"id": "pip",   "kind": "pip",   "package": "matplotlib seaborn",                     "label": "Install via pip"}
]
```

| Field | Notes |
|---|---|
| `id` | Stable identifier within the recipe list |
| `kind` | One of `brew`, `pip`, `apt`, `npm`, `go`, `uv`, `download`; uninstall recipes also accept `shell` |
| `formula` / `package` / `command` | Provided depending on `kind`; `command` is a raw shell command for `shell` / `download` |
| `bins` | Executables this recipe makes available (used to verify success) |
| `os` | Restrict the recipe to specific OSes |
| `label` | UI string |

Uninstall recipes mirror the install side and may use a `command` to run a custom shell uninstall.

## Body conventions

When the LLM picks the skill, the runtime returns the body of `SKILL.md` to it (preceded by an execution-mode hint and any declared dependencies). It is not a script the runtime executes — it's instructions the LLM reads. Treat it as prompt engineering:

1. **Lead with intent.** First paragraph: what the skill does, plainly.
2. **Be explicit about output format** when in `prompt` mode.
3. **Provide one or two inline examples**; point to `examples/` for longer ones.
4. **For `bash` / `python` modes**, fence ready-to-run commands in code blocks. The LLM will copy those commands into a follow-up call to the agent's `exec` / `command` tool to run them in the workspace sandbox — the skill loader itself does not execute fenced blocks.
5. **Reference supporting files by relative path** — `templates/report.md.tpl`.

> [!TIP]
> Ambiguity in the body becomes ambiguity in the output. When in doubt, add a constraint.

## Supporting files

- `examples/` — input/output pairs the model can imitate.
- `templates/` — file scaffolds with placeholders.
- `data/` — small reference datasets (lookup tables, glossaries).
- `scripts/` — helper scripts the body references.

No manifest is needed for these — reference them by relative path from the body.

## Reference

Real in-tree examples live under [`skills/`](https://github.com/whtcjdtc2007/matrix-nexus/tree/main/skills) (chart-generator, csv-data-tools, jq, curl, pdf-tools, postgres-client, …). Copy one and adapt it.


---

---
title: Local Development
description: Build and iterate on a skill on your own machine before publishing.
section: skills
slug: skill-local
updated: 2026-04-23
estimated_minutes: 5
---

The fastest iteration loop is: **drop the folder into a discoverable skills directory → reload the agent → trigger the skill → revise.**

## 1. Where the loader looks

The Nexus skill loader (`src/skills/loader.py`) resolves the **bundled skills directory** by trying these paths in order and using the first one that exists:

| Order | Source | Path | Purpose |
|---|---|---|---|
| 1 | Env override | `$MATRIX_SKILLS_DIR` | Point at any folder of skills (recommended for development) |
| 2 | In-tree bundled | `<repo>/skills/` | Built-in skills shipped with Nexus (e.g. `chart-generator`, `jq`, `curl`) |
| 3 | Package bundled | `<repo>/src/skills/bundled/` | Internal fallback |

In addition, **workspace skills** under `<workspace>/skills/` are loaded separately by `load_workspace_skills(workspace_path)` and merged on top of the bundled set (workspace entries win on name collision via `merge_skills`).

Each immediate subdirectory containing a `SKILL.md` is a skill (the loader recursively walks the tree looking for `SKILL.md` files). On first access the registry builds an index of skill name → file path; the body is parsed lazily the first time a given skill is requested.

```bash
export MATRIX_SKILLS_DIR=~/dev/anna-skills
mkdir -p "$MATRIX_SKILLS_DIR/my-skill"
$EDITOR "$MATRIX_SKILLS_DIR/my-skill/SKILL.md"
```

Restart the agent (or hit the reload endpoint) and trigger the skill by asking Anna something matching its frontmatter `description`.

## 2. Pick the execution mode

The `metadata.matrix.execution_mode` field is a **hint** the runtime injects above the skill body so the LLM knows how the skill is intended to be run. The skill loader itself does not execute anything — the LLM uses the hint to decide which built-in agent tool (typically `exec` / `command`) to call next.

| Mode | Hint shown to the LLM |
|---|---|
| `prompt` (default) | "Follow the instructions in the body" — no execution implied |
| `bash` | "Run the example commands via `exec` (bash/shell)" |
| `python` | "Run the Python via `exec`, preferring `uv run --with <pkg> python script.py`" |
| `api` | "This skill describes an HTTP call — use `exec` to run `curl` or similar" |
| `hybrid` | "Mix bash and Python as the body suggests" |

For `bash` / `python` skills, declare any required `bins` / `python_packages` in `requires` plus matching `install` recipes so onboarding can ensure dependencies are present before the agent tries to run them. When any loaded skill is `python` mode, the runtime additionally injects a section into the system prompt instructing the agent to prefer `uv` over the system `pip` (see `src/skills/converter.py`).

## 3. Smoke-test checklist

- [ ] The frontmatter `description` is the kind of question a user would actually type. (If your skill never loads, this is almost always the cause.)
- [ ] Output matches your spec on three different inputs.
- [ ] Edge cases (empty input, malformed input) degrade gracefully.
- [ ] All `requires` items resolve on a clean machine, or the install recipes succeed.
- [ ] Supporting files referenced from the body actually exist at those paths.

## chart-generator walkthrough

A real bundled skill looks like this:

```
skills/chart-generator/
├── SKILL.md
└── examples/
```

Frontmatter (truncated):

```yaml
---
name: chart-generator
description: "Use matplotlib and seaborn to create publication-quality charts…"
metadata: {"matrix":{"emoji":"📈","execution_mode":"python","category_name":"data-analysis","requires":{"python_packages":["matplotlib","seaborn"]},"install":[{"id":"pip","kind":"pip","package":"matplotlib seaborn"}]}}
---
```

The body teaches Anna to:

1. Inspect the user's data.
2. Suggest the most appropriate chart type.
3. Emit a Python snippet that calls `matplotlib` / `seaborn` to render the chart.
4. Save the output as `chart.png` (or SVG/PDF) in the workspace.

When the LLM calls the skill, the runtime returns the body to it. The LLM then issues an `exec` call running `uv run --with matplotlib --with seaborn python script.py` (or installs the packages via the declared `install` recipe first). Browse the live source under [`skills/chart-generator`](https://github.com/whtcjdtc2007/matrix-nexus/tree/main/skills/chart-generator).

## Next

- **Publish your skill** — [Publishing](/developers/skills/skill-publish).


---

---
title: Publishing a Skill
description: Submit your skill so other users can discover and install it.
section: skills
slug: skill-publish
updated: 2026-04-23
estimated_minutes: 5
---

Once your skill is stable, publishing puts it in the Explore catalogue alongside the platform-bundled skills. Because **a Skill is just an Executa with `executa_type="skill"`**, it shares the *exact same* draft / version / visibility pipeline as a Tool Executa — same wizard, same REST surface, same Hub.

## 1. Prepare

- [ ] `SKILL.md` has the required frontmatter (`name`, `description`).
- [ ] `metadata.matrix` declares `execution_mode`, `category_name`, and (if applicable) `requires` / `install` / `uninstall`.
- [ ] Body is self-contained — no references to files outside the skill folder.
- [ ] You have a one-line and one-paragraph description ready for the listing.
- [ ] Optional: a screenshot/GIF showing the skill in action.

> [!WARNING]
> Don't include credentials, `.env` files, or anything you wouldn't paste into a public gist. The skill body ships verbatim to anyone who installs it.

## 2. Create the Skill via the wizard

The `/executa` page has a draft-first flow shared by both Executa flavours — you pick `Skill` at step 1 and the rest of the wizard adapts:

```
POST   /api/v1/executas/my/drafts                    → reserves tool_id (executa_type="skill")
PATCH  /api/v1/executas/my/drafts/{id}               → fill in skill_content + metadata
POST   /api/v1/executas/my/drafts/{id}/commit        → promote draft → Skill Executa
```

The UI walks through:

1. **Name & type** — pick `Skill`. The server returns a `tool_id` like `skill-{author_handle}-{slug}-{uniq}` you can copy into App manifests.
2. **Body & metadata** — paste the markdown of `SKILL.md`. The wizard parses your frontmatter (`metadata.matrix`) and surfaces `execution_mode`, `category_name`, and dependency declarations as form fields.
3. **Capabilities & docs** — logo, README, sample prompts.
4. **Visibility** — `private`, `app_bundled`, or `public`.
5. **Commit** — the draft becomes a real Skill Executa.

Drafts auto-expire after 24 h if you don't commit (see `DRAFT_TTL` in `src/services/executa_drafts.py`).

Direct REST mirrors are available for scripting:

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/api/v1/executas/my/skills` | List your Skill Executas |
| `POST` | `/api/v1/executas/my/skills/import` | Create a Skill from a JSON payload (server-side validates the frontmatter) |
| `GET`  | `/api/v1/executas/my/skills/{id}/detail` | Fetch full Skill detail |
| `PUT`  | `/api/v1/executas/my/skills/{id}` | Update body / metadata |
| `DELETE` | `/api/v1/executas/my/skills/{id}` | Delete the Skill |
| `GET`  | `/api/v1/executas/my/skills/{id}/export` | Round-trip the skill back to a payload you can re-import |
| `POST` | `/api/v1/executas/my/skills/{id}/publish` | Promote to `visibility=public` (Pro / Max) |
| `POST` | `/api/v1/executas/my/skills/{id}/unpublish` | Revert to `private` |
| `POST` | `/api/v1/executas/my/skills/{id}/visibility` | Set visibility explicitly (`private` / `app_bundled` / `public`) |
| `POST` | `/api/v1/executas/my/skills/{id}/versions` | Freeze a new immutable version snapshot |

## 3. Visibility model

| Visibility | Where it appears | Who can install |
|---|---|---|
| `private` | Only your `/executa` workspace | Only you |
| `app_bundled` | Hidden from Explore, installable as part of any Anna App that bundles it | Anyone who installs the host App |
| `public` | Listed in the Explore Hub | Anyone |

Use `app_bundled` when the skill only makes sense alongside a particular App.

## 4. Versioning

Every `POST /my/skills/{id}/versions` call freezes the current body + metadata into an immutable `ExecutaVersion`. If nothing changed since the last published version, the call returns `409 Conflict` so you don't ship empty updates.

Apps that pin a `min_version` see content frozen at that snapshot; users on auto-update get the latest snapshot at install time.

## 5. Bundle into an App

The highest-leverage distribution is being part of an Anna App. See [What is an Anna App](/developers/apps/app-intro) for how Apps bundle skills, tools, and prompts into a one-click install.

> [!NOTE]
> Self-hosted catalogues are on the roadmap. For now everything goes through the public Explore Hub review.


---



# === Build an Anna App ===

---
title: What is an Anna App
description: Apps bundle a curated set of Executas plus prompt instructions into a one-click install for end users.
section: apps
slug: app-intro
updated: 2026-04-29
estimated_minutes: 4
---

An **Anna App** is the highest-level packaging unit in the Anna App Store. It bundles:

- A curated set of **Executas** (Anna's tool/skill plugins) the app depends on.
- Prompt instructions (`system_prompt_addendum`, `user_message_prefix_template`) that steer the assistant when the user `#`mentions the app in a chat.
- **Listing metadata** (name, slug, category, tagline, description, logo, screenshots, homepage, pricing model) that powers the App Store entry.
- *(Optional, manifest `schema: 2`)* an **App UI bundle** — a static SPA (HTML/JS/CSS/wasm/fonts) that is uploaded to Anna and rendered inside a sandboxed `<iframe>` window on the dashboard. See [App UI Overview](/developers/apps/app-ui-overview).

When a user installs an app from the **Anna App Store**, every `required_executas` entry that the user does not yet have is auto-installed for them. From that point on, the user can `#`mention the app in any conversation to apply its bundled tools and prompt directives for that turn. If the app ships a UI, the assistant can also summon the app window via the built-in `open_app_view` tool.

<figure class="dh-figure">
<svg viewBox="0 0 720 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="An Anna App bundles Executas, prompt directives, listing metadata, and an optional UI bundle into a single install referenced from chat by hash-mention.">
<defs>
<linearGradient id="aiAppGrad" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#FF9E6C"/>
<stop offset="1" stop-color="#B388FF"/>
</linearGradient>
<linearGradient id="aiChip" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1B1D27"/>
<stop offset="1" stop-color="#12141C"/>
</linearGradient>
</defs>
<g font-family="Inter, sans-serif" font-size="12" fill="#E6E7EE">
<g transform="translate(34 46)">
<rect width="170" height="36" rx="18" fill="url(#aiChip)" stroke="#FF9E6C" stroke-opacity="0.55"/>
<circle cx="20" cy="18" r="4" fill="#FF9E6C"/>
<text x="34" y="22">Executas</text>
</g>
<g transform="translate(34 102)">
<rect width="170" height="36" rx="18" fill="url(#aiChip)" stroke="#B388FF" stroke-opacity="0.55"/>
<circle cx="20" cy="18" r="4" fill="#B388FF"/>
<text x="34" y="22">Prompt directives</text>
</g>
<g transform="translate(34 158)">
<rect width="170" height="36" rx="18" fill="url(#aiChip)" stroke="#82B1FF" stroke-opacity="0.55"/>
<circle cx="20" cy="18" r="4" fill="#82B1FF"/>
<text x="34" y="22">Listing metadata</text>
</g>
<g transform="translate(34 214)">
<rect width="170" height="36" rx="18" fill="url(#aiChip)" stroke="#FFC8A2" stroke-opacity="0.6" stroke-dasharray="3 3"/>
<circle cx="20" cy="18" r="4" fill="#FFC8A2"/>
<text x="34" y="22">UI bundle (optional)</text>
</g>
</g>
<g stroke="url(#aiAppGrad)" stroke-opacity="0.55" fill="none" stroke-width="1.2">
<path d="M204 64 C 270 64 270 145 330 145"/>
<path d="M204 120 C 270 120 270 145 330 145"/>
<path d="M204 176 C 270 176 270 145 330 145"/>
<path d="M204 232 C 270 232 270 145 330 145"/>
</g>
<g transform="translate(310 90)">
<rect x="4" y="6" width="110" height="110" rx="26" fill="#000" opacity="0.18" filter="blur(4px)"/>
<rect width="110" height="110" rx="26" fill="url(#aiAppGrad)"/>
<rect x="0.5" y="0.5" width="109" height="109" rx="25.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.28"/>
<rect x="3" y="3" width="104" height="40" rx="23" fill="#FFFFFF" opacity="0.10"/>
<g transform="translate(55 55)" fill="#FFFFFF">
<path d="M0 -30 Q 6 -6 30 0 Q 6 6 0 30 Q -6 6 -30 0 Q -6 -6 0 -30 Z" opacity="0.96"/>
<path d="M24 -22 Q 25 -14 32 -12 Q 25 -10 24 -2 Q 23 -10 16 -12 Q 23 -14 24 -22 Z" opacity="0.85"/>
<circle cx="-22" cy="22" r="2" opacity="0.7"/>
</g>
<text x="55" y="138" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="11" fill="#E6E7EE" letter-spacing="0.22em" font-weight="700">ANNA APP</text>
<text x="55" y="154" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#A6A8B5">single install · v1.0.0</text>
</g>
<g stroke="#FFC8A2" stroke-opacity="0.75" fill="none" stroke-width="1.5">
<path d="M440 145 L 540 145" stroke-dasharray="4 4"/>
<polyline points="534,139 544,145 534,151" stroke-linejoin="round" stroke-linecap="round"/>
</g>
<g transform="translate(540 95)">
<rect width="150" height="100" rx="14" fill="#12141C" stroke="#FFC8A2" stroke-opacity="0.35"/>
<text x="14" y="28" font-family="JetBrains Mono, monospace" font-size="11" fill="#82B1FF">#research-buddy</text>
<line x1="14" y1="40" x2="136" y2="40" stroke="#FFC8A2" stroke-opacity="0.18"/>
<text x="14" y="58" font-family="Inter, sans-serif" font-size="11" fill="#A6A8B5">summarise the</text>
<text x="14" y="74" font-family="Inter, sans-serif" font-size="11" fill="#A6A8B5">latest paper on...</text>
<circle cx="136" cy="86" r="3" fill="#FF9E6C"/>
</g>
</svg>
<figcaption>One install · one hash-mention · the assistant gains a curated capability set</figcaption>
</figure>

> [!TIP]
> In a hurry? Skip the theory and follow the [60-second quickstart](/developers/apps/app-quickstart) — `anna-app init` → `anna-app dev` → `anna-app validate`.

## Why ship an App instead of standalone Executas?

- **Discovery** — the App Store is where most non-technical users browse.
- **Composition** — a single Executa is rarely the full UX; an App glues a few of them together with a `system_prompt_addendum` that tells the assistant how to combine them.
- **Branding** — your app name, logo, and tagline appear on the user's App Store listings.
- **One-click install** — the user accepts a single install instead of authorising each Executa one by one.

<figure class="dh-figure">
<svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Four quadrants illustrate the four reasons to ship an App: Discovery, Composition, Branding, and One-click install.">
<defs>
<linearGradient id="wsBrand" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#FF9E6C"/>
<stop offset="1" stop-color="#B388FF"/>
</linearGradient>
<linearGradient id="wsTool" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1B1D27"/>
<stop offset="1" stop-color="#12141C"/>
</linearGradient>
<radialGradient id="wsCardBg" cx="0.5" cy="0" r="1">
<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.04"/>
<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
</radialGradient>
</defs>

<g fill="url(#wsCardBg)" stroke="#FFC8A2" stroke-opacity="0.18">
<rect x="20"  y="20"  width="335" height="155" rx="14"/>
<rect x="365" y="20"  width="335" height="155" rx="14"/>
<rect x="20"  y="185" width="335" height="155" rx="14"/>
<rect x="365" y="185" width="335" height="155" rx="14"/>
</g>

<g transform="translate(20 20)">
<text x="18" y="28" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.22em" fill="#FF9E6C">01 · DISCOVERY</text>
<text x="18" y="48" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="#E6E7EE">Found in the App Store</text>
<g transform="translate(18 64)">
<rect width="200" height="26" rx="13" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.22"/>
<g transform="translate(13 13)" stroke="#FFC8A2" stroke-opacity="0.7" stroke-width="1.3" fill="none" stroke-linecap="round">
<circle cx="0" cy="0" r="4"/><line x1="3" y1="3" x2="6" y2="6"/>
</g>
<text x="28" y="17" font-family="JetBrains Mono, monospace" font-size="10" fill="#A6A8B5">research</text>
<rect x="84" y="9" width="2" height="9" fill="#FF9E6C"/>
</g>
<g transform="translate(18 100)">
<rect width="44" height="44" rx="10" fill="url(#wsBrand)"/>
<rect x="0.5" y="0.5" width="43" height="43" rx="9.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.28"/>
<g transform="translate(22 22)" fill="#FFFFFF">
<path d="M0 -10 Q 2 -2 10 0 Q 2 2 0 10 Q -2 2 -10 0 Q -2 -2 0 -10 Z"/>
</g>
</g>
<g transform="translate(72 100)" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.22">
<rect width="44" height="44" rx="10"/>
</g>
<g transform="translate(126 100)" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.22">
<rect width="44" height="44" rx="10"/>
</g>
<g transform="translate(180 100)" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.22">
<rect width="44" height="44" rx="10"/>
</g>
<text x="244" y="120" font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">non-technical</text>
<text x="244" y="134" font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">users browse</text>
</g>


<g transform="translate(365 20)">
<text x="18" y="28" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.22em" fill="#B388FF">02 · COMPOSITION</text>
<text x="18" y="48" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="#E6E7EE">Executas + prompt = UX</text>
<g font-family="JetBrains Mono, monospace" font-size="9" fill="#A6A8B5">
<g transform="translate(18 70)"><rect width="80" height="22" rx="11" fill="url(#wsTool)" stroke="#FF9E6C" stroke-opacity="0.5"/><circle cx="11" cy="11" r="3" fill="#FF9E6C"/><text x="22" y="14">web_search</text></g>
<g transform="translate(18 96)"><rect width="80" height="22" rx="11" fill="url(#wsTool)" stroke="#B388FF" stroke-opacity="0.5"/><circle cx="11" cy="11" r="3" fill="#B388FF"/><text x="22" y="14">img_gen</text></g>
<g transform="translate(18 122)"><rect width="80" height="22" rx="11" fill="url(#wsTool)" stroke="#82B1FF" stroke-opacity="0.5"/><circle cx="11" cy="11" r="3" fill="#82B1FF"/><text x="22" y="14">pdf_reader</text></g>
<g transform="translate(106 96)">
<rect width="100" height="22" rx="11" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.45" stroke-dasharray="3 3"/>
<text x="50" y="14" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="8" letter-spacing="0.18em" fill="#FFC8A2">+ PROMPT</text>
</g>
</g>
<g fill="none" stroke="url(#wsBrand)" stroke-opacity="0.7" stroke-width="1.4" stroke-linecap="round">
<path d="M210 81 C 240 90 250 100 260 110"/>
<path d="M210 107 L 260 110"/>
<path d="M210 133 C 240 124 250 115 260 110"/>
</g>
<polyline points="254,103 264,110 254,117" fill="none" stroke="#B388FF" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
<g transform="translate(265 88)">
<rect width="50" height="44" rx="11" fill="url(#wsBrand)"/>
<rect x="0.5" y="0.5" width="49" height="43" rx="10.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.28"/>
<g transform="translate(25 22)" fill="#FFFFFF">
<path d="M0 -11 Q 2 -2 11 0 Q 2 2 0 11 Q -2 2 -11 0 Q -2 -2 0 -11 Z"/>
</g>
</g>
</g>
<g transform="translate(20 185)">
<text x="18" y="28" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.22em" fill="#82B1FF">03 · BRANDING</text>
<text x="18" y="48" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="#E6E7EE">Your name on the listing</text>
<g transform="translate(18 64)">
<rect width="300" height="80" rx="14" fill="url(#wsTool)" stroke="#FFC8A2" stroke-opacity="0.28"/>
<g transform="translate(14 14)">
<rect width="52" height="52" rx="13" fill="url(#wsBrand)"/>
<rect x="0.5" y="0.5" width="51" height="51" rx="12.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.28"/>
<rect x="2" y="2" width="48" height="20" rx="11" fill="#FFFFFF" opacity="0.12"/>
<g transform="translate(26 26)" fill="#FFFFFF">
<path d="M0 -14 Q 3 -3 14 0 Q 3 3 0 14 Q -3 3 -14 0 Q -3 -3 0 -14 Z"/>
</g>
</g>
<text x="80" y="30" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="#E6E7EE">Research Buddy</text>
<text x="80" y="48" font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">Cite-first research with PDFs &amp; web</text>
<g transform="translate(80 56)" font-family="JetBrains Mono, monospace" font-size="8" fill="#FFC8A2" fill-opacity="0.85">
<rect width="44" height="14" rx="7" fill="none" stroke="#FFC8A2" stroke-opacity="0.3"/>
<text x="22" y="10" text-anchor="middle" letter-spacing="0.14em">RESEARCH</text>
</g>
<g transform="translate(130 56)" font-family="JetBrains Mono, monospace" font-size="8" fill="#FFC8A2" fill-opacity="0.85">
<rect width="58" height="14" rx="7" fill="none" stroke="#FFC8A2" stroke-opacity="0.3"/>
<text x="29" y="10" text-anchor="middle" letter-spacing="0.14em">PRODUCTIVITY</text>
</g>
<text x="284" y="22" text-anchor="end" font-family="JetBrains Mono, monospace" font-size="9" fill="#A6A8B5">v1.0.0</text>
</g>
</g>
<g transform="translate(365 185)">
<text x="18" y="28" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.22em" fill="#FF9E6C">04 · ONE-CLICK INSTALL</text>
<text x="18" y="48" font-family="Inter, sans-serif" font-size="13" font-weight="700" fill="#E6E7EE">One consent · all Executas</text>
<g transform="translate(18 64)" font-family="JetBrains Mono, monospace" font-size="9">
<g><rect width="115" height="18" rx="9" fill="url(#wsTool)" stroke="#A6A8B5" stroke-opacity="0.25"/><text x="9" y="12" fill="#A6A8B5">authorise web_search</text></g>
<g transform="translate(0 22)"><rect width="115" height="18" rx="9" fill="url(#wsTool)" stroke="#A6A8B5" stroke-opacity="0.25"/><text x="9" y="12" fill="#A6A8B5">authorise img_gen</text></g>
<g transform="translate(0 44)"><rect width="115" height="18" rx="9" fill="url(#wsTool)" stroke="#A6A8B5" stroke-opacity="0.25"/><text x="9" y="12" fill="#A6A8B5">authorise pdf_reader</text></g>
<line x1="20" y1="68" x2="115" y2="-4" stroke="#FF6B6B" stroke-opacity="0.55" stroke-width="1.2"/>
<line x1="115" y1="68" x2="20" y2="-4" stroke="#FF6B6B" stroke-opacity="0.55" stroke-width="1.2"/>
</g>
<g fill="none" stroke="url(#wsBrand)" stroke-opacity="0.85" stroke-width="1.6" stroke-linecap="round">
<line x1="148" y1="100" x2="178" y2="100" stroke-dasharray="3 3"/>
<polyline points="172,94 182,100 172,106" stroke-linejoin="round"/>
</g>
<g transform="translate(184 78)">
<rect width="130" height="44" rx="22" fill="url(#wsBrand)"/>
<rect x="0.5" y="0.5" width="129" height="43" rx="21.5" fill="none" stroke="#FFFFFF" stroke-opacity="0.32"/>
<g transform="translate(28 22)" stroke="#FFFFFF" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="M0 -7 V 5"/><polyline points="-5,0 0,5 5,0"/>
<line x1="-7" y1="9" x2="7" y2="9"/>
</g>
<text x="78" y="27" text-anchor="middle" font-family="Space Grotesk, sans-serif" font-size="11" font-weight="700" fill="#0A0B11" letter-spacing="0.18em">INSTALL</text>
</g>
<text x="184" y="138" font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">single accept</text>
<text x="244" y="138" font-family="Inter, sans-serif" font-size="10" fill="#FF9E6C">·</text>
<text x="252" y="138" font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">all bundled</text>
</g>
</svg>
<figcaption>Discovery · Composition · Branding · One-click install</figcaption>
</figure>

## Anatomy

Most of an Anna App is filled in via the [Developer Console](/developer); there is no zip or tarball to assemble for the *manifest* part. UI apps additionally upload a static asset bundle alongside the manifest.

| Where | What you provide |
|---|---|
| **Listing tab** | `slug`, `name`, `category`, `tagline`, `description`, `logo` (uploaded; cropped to 256×256 WebP), optional `screenshots[]` (URLs), `homepage_url`, `repository_url`, `pricing_model` |
| **Versions tab** | A SemVer `version` string, a `changelog`, and a JSON **manifest** that declares `required_executas`, optional Executas, prompt directives, and (for `schema: 2`) the `ui` section |
| **Versions tab → Bundle** *(UI apps only)* | A static SPA bundle (HTML/JS/CSS/...) uploaded with `bundle/init` → per-file PUT → `bundle/finalize`. See [App UI Bundle Pipeline](/developers/apps/app-ui-bundle) |
| **Settings tab** | Submit for review; archive the app |

Each version is an immutable snapshot. To change the bundled Executas, the prompt, or the UI assets, you create a new version (with a strictly greater SemVer), upload its bundle if applicable, and publish it.

<figure class="dh-figure">
<svg viewBox="0 0 720 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="The Developer Console organises an app across four tabs — Listing, Versions, Bundle, Settings — each contributing different artefacts to an immutable version snapshot.">
<defs>
<linearGradient id="anFrame" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1B1D27"/>
<stop offset="1" stop-color="#12141C"/>
</linearGradient>
<linearGradient id="anActive" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#FF9E6C"/>
<stop offset="1" stop-color="#B388FF"/>
</linearGradient>
</defs>
<rect x="20" y="20" width="680" height="250" rx="14" fill="url(#anFrame)" stroke="#FFC8A2" stroke-opacity="0.22"/>
<g>
<circle cx="42" cy="42" r="5" fill="#FF6B6B" opacity="0.7"/>
<circle cx="60" cy="42" r="5" fill="#FFD166" opacity="0.7"/>
<circle cx="78" cy="42" r="5" fill="#7FD49C" opacity="0.7"/>
<text x="100" y="46" font-family="JetBrains Mono, monospace" font-size="11" fill="#A6A8B5">anna.partners / developers / apps / research-buddy</text>
</g>
<line x1="20" y1="64" x2="700" y2="64" stroke="#FFC8A2" stroke-opacity="0.18"/>
<g font-family="Space Grotesk, sans-serif" font-size="11" letter-spacing="0.16em">
<g transform="translate(40 84)">
<rect width="120" height="30" rx="8" fill="#0A0B11" stroke="url(#anActive)" stroke-width="1.4"/>
<text x="60" y="20" text-anchor="middle" fill="#FFC8A2">LISTING</text>
</g>
<g transform="translate(170 84)">
<rect width="120" height="30" rx="8" fill="transparent" stroke="#FFC8A2" stroke-opacity="0.18"/>
<text x="60" y="20" text-anchor="middle" fill="#A6A8B5">VERSIONS</text>
</g>
<g transform="translate(300 84)">
<rect width="120" height="30" rx="8" fill="transparent" stroke="#FFC8A2" stroke-opacity="0.18"/>
<text x="60" y="20" text-anchor="middle" fill="#A6A8B5">BUNDLE</text>
</g>
<g transform="translate(430 84)">
<rect width="120" height="30" rx="8" fill="transparent" stroke="#FFC8A2" stroke-opacity="0.18"/>
<text x="60" y="20" text-anchor="middle" fill="#A6A8B5">SETTINGS</text>
</g>
</g>
<g transform="translate(40 134)" font-family="Inter, sans-serif">
<rect width="200" height="120" rx="10" fill="#0A0B11" stroke="#FF9E6C" stroke-opacity="0.4"/>
<text x="14" y="22" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.2em" fill="#FF9E6C">LISTING</text>
<rect x="14" y="32" width="64" height="64" rx="8" fill="url(#anActive)" opacity="0.7"/>
<text x="86" y="46" font-size="11" fill="#E6E7EE">name · slug</text>
<text x="86" y="64" font-size="11" fill="#A6A8B5">tagline</text>
<text x="86" y="82" font-size="11" fill="#A6A8B5">screenshots</text>
</g>
<g transform="translate(255 134)" font-family="Inter, sans-serif">
<rect width="200" height="120" rx="10" fill="#0A0B11" stroke="#B388FF" stroke-opacity="0.4"/>
<text x="14" y="22" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.2em" fill="#B388FF">VERSIONS</text>
<text x="14" y="44" font-family="JetBrains Mono, monospace" font-size="10" fill="#E6E7EE">v1.0.0  ·  manifest.json</text>
<rect x="14" y="54" width="172" height="6" rx="3" fill="#FFC8A2" fill-opacity="0.18"/>
<rect x="14" y="54" width="64" height="6" rx="3" fill="#B388FF"/>
<text x="14" y="78" font-family="JetBrains Mono, monospace" font-size="10" fill="#A6A8B5">required_executas []</text>
<text x="14" y="92" font-family="JetBrains Mono, monospace" font-size="10" fill="#A6A8B5">system_prompt_addendum</text>
<text x="14" y="106" font-family="JetBrains Mono, monospace" font-size="10" fill="#A6A8B5">ui { schema: 2 }</text>
</g>
<g transform="translate(470 134)" font-family="Inter, sans-serif">
<rect width="100" height="120" rx="10" fill="#0A0B11" stroke="#82B1FF" stroke-opacity="0.4"/>
<text x="12" y="22" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.2em" fill="#82B1FF">BUNDLE</text>
<g font-family="JetBrains Mono, monospace" font-size="10" fill="#A6A8B5">
<text x="12" y="46">index.html</text>
<text x="12" y="62">app.js</text>
<text x="12" y="78">styles.css</text>
<text x="12" y="94">assets/</text>
</g>
</g>
<g transform="translate(585 134)" font-family="Inter, sans-serif">
<rect width="95" height="120" rx="10" fill="#0A0B11" stroke="#FFC8A2" stroke-opacity="0.4"/>
<text x="12" y="22" font-family="Space Grotesk, sans-serif" font-size="9" letter-spacing="0.2em" fill="#FFC8A2">SETTINGS</text>
<g font-family="Inter, sans-serif" font-size="10" fill="#A6A8B5">
<text x="12" y="50">Submit</text>
<text x="12" y="66">Archive</text>
<text x="12" y="82">Transfer</text>
</g>
</g>
</svg>
<figcaption>Four console tabs · one immutable version snapshot</figcaption>
</figure>

## Lifecycle

<figure class="dh-figure">
<svg viewBox="0 0 720 290" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="App lifecycle: DRAFT submits to PENDING_REVIEW, which is either rejected back to DRAFT or approved; APPROVED publishes a version into PUBLISHED, and PUBLISHED can be archived.">
<defs>
<linearGradient id="lcDraft" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#1B1D27"/>
<stop offset="1" stop-color="#12141C"/>
</linearGradient>
<linearGradient id="lcLive" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#FF9E6C"/>
<stop offset="1" stop-color="#B388FF"/>
</linearGradient>
<marker id="lcArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L 10 5 L 0 10 z" fill="#FFC8A2" fill-opacity="0.85"/>
</marker>
<marker id="lcArrowAccent" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L 10 5 L 0 10 z" fill="#FF9E6C"/>
</marker>
<marker id="lcArrowDim" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M0 0 L 10 5 L 0 10 z" fill="#A6A8B5" fill-opacity="0.7"/>
</marker>
</defs>
<g font-family="Space Grotesk, sans-serif" font-size="11" letter-spacing="0.16em">
<g transform="translate(20 80)">
<rect width="120" height="44" rx="22" fill="url(#lcDraft)" stroke="#FFC8A2" stroke-opacity="0.45"/>
<text x="60" y="27" text-anchor="middle" fill="#E6E7EE">DRAFT</text>
</g>
<g transform="translate(180 80)">
<rect width="160" height="44" rx="22" fill="url(#lcDraft)" stroke="#B388FF" stroke-opacity="0.6"/>
<text x="80" y="27" text-anchor="middle" fill="#B388FF">PENDING_REVIEW</text>
</g>
<g transform="translate(380 80)">
<rect width="130" height="44" rx="22" fill="url(#lcDraft)" stroke="#82B1FF" stroke-opacity="0.6"/>
<text x="65" y="27" text-anchor="middle" fill="#82B1FF">APPROVED</text>
</g>
<g transform="translate(550 80)">
<rect width="140" height="44" rx="22" fill="url(#lcLive)"/>
<text x="70" y="27" text-anchor="middle" fill="#0A0B11" font-weight="700">PUBLISHED</text>
</g>
<g transform="translate(180 200)">
<rect width="120" height="44" rx="22" fill="url(#lcDraft)" stroke="#FF6B6B" stroke-opacity="0.7" stroke-dasharray="4 3"/>
<text x="60" y="27" text-anchor="middle" fill="#FF6B6B">REJECTED</text>
</g>
<g transform="translate(560 200)">
<rect width="120" height="44" rx="22" fill="url(#lcDraft)" stroke="#A6A8B5" stroke-opacity="0.55" stroke-dasharray="4 3"/>
<text x="60" y="27" text-anchor="middle" fill="#A6A8B5">ARCHIVED</text>
</g>
</g>
<g fill="none" stroke-width="1.4">
<line x1="140" y1="102" x2="172" y2="102" stroke="#FFC8A2" stroke-opacity="0.85" marker-end="url(#lcArrow)"/>
<line x1="340" y1="102" x2="372" y2="102" stroke="#FFC8A2" stroke-opacity="0.85" marker-end="url(#lcArrow)"/>
<line x1="510" y1="102" x2="542" y2="102" stroke="#FF9E6C" marker-end="url(#lcArrowAccent)"/>
<path d="M260 124 L 260 200" stroke="#FF6B6B" stroke-opacity="0.7" marker-end="url(#lcArrow)"/>
<path d="M180 222 C 110 222 70 180 70 130" stroke="#A6A8B5" stroke-opacity="0.55" marker-end="url(#lcArrowDim)" stroke-dasharray="4 3"/>
<path d="M620 124 L 620 200" stroke="#A6A8B5" stroke-opacity="0.55" marker-end="url(#lcArrowDim)" stroke-dasharray="4 3"/>
</g>
<g font-family="JetBrains Mono, monospace" font-size="9" fill="#A6A8B5" letter-spacing="0.04em">
<text x="156" y="96" text-anchor="middle">submit</text>
<text x="356" y="96" text-anchor="middle">approve</text>
<text x="526" y="96" text-anchor="middle" fill="#FF9E6C">publish</text>
<text x="276" y="170">reject</text>
<text x="92" y="180" text-anchor="middle">revise</text>
<text x="636" y="170">archive</text>
</g>
</svg>
<figcaption>DRAFT · PENDING_REVIEW · APPROVED · PUBLISHED · REJECTED ↺ · ARCHIVED</figcaption>
</figure>

Only `PUBLISHED` apps are visible in the App Store and installable by new users. Existing installations remain usable after `ARCHIVED`.

## Where to next

- **Quickstart** — [Scaffold + run + validate](/developers/apps/app-quickstart) with the `anna-app` CLI.
- **Manifest** — [App manifest spec](/developers/apps/app-manifest).
- **Bundling** — [Bundling components](/developers/apps/app-bundling).
- **Listing** — [Listing assets](/developers/apps/app-listing).
- **Submitting** — [Publishing an app](/developers/apps/app-publish).
- **Updates** — [Versioning & updates](/developers/apps/app-versioning).
- **App UI** — [Overview](/developers/apps/app-ui-overview), [Manifest `ui` section](/developers/apps/app-ui-manifest), [Bundle pipeline](/developers/apps/app-ui-bundle), [Window lifecycle](/developers/apps/app-ui-windows), [SDK](/developers/apps/app-ui-sdk), [Host API](/developers/apps/app-ui-host-api), [LLM integration](/developers/apps/app-ui-llm).


---

---
title: Quickstart: anna-app CLI
description: From an empty directory to a running Anna App harness in under a minute — scaffold, dev, validate.
section: apps
slug: app-quickstart
updated: 2026-04-29
estimated_minutes: 4
---

This is the fastest path from "nothing" to a working Anna App on your laptop. Concepts come right after — see [App Manifest](/developers/apps/app-manifest), [Bundling](/developers/apps/app-bundling), and the rest of this section once you have something running.

> [!TIP]
> No platform source checkout is required. The CLI fetches the pinned Python runtime through `uvx` on first run and caches it.

## Prerequisites

- **Node 22+** — `node --version`
- **uv** (Astral) — one-time install:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **`anna-app` CLI** — global install:
  ```bash
  npm i -g @anna-ai/cli
  anna-app --help
  ```

Run `anna-app doctor` once to confirm `uv`, the `uvx` cache, and your dev signing key are in shape.

## 1. Scaffold

```bash
anna-app init my-focus-flow --slug focus-flow
cd my-focus-flow
```

The `minimal` template lays down a complete, valid project:

```
my-focus-flow/
├── manifest.json                      # schema 2 — UI + executa + dev block
├── app.json                           # store-listing metadata (name, tagline, category)
├── bundle/
│   ├── index.html                     # iframe entry; pulls the AnnaAppRuntime SDK
│   └── app.js                         # connects to the host, calls tools.invoke / storage
├── executas/
│   └── focus-flow/                    # local stdio executa (Python; auto-detected)
│       ├── focus_flow_plugin.py       # describe / health / invoke loop
│       └── pyproject.toml
└── README.md
```

The scaffold's `tool_id` is `tool-dev-focus-flow` — a synthetic dev id that lets you reference your local executa from the manifest before anything is published to the catalogue.

## 2. Run the harness

```bash
anna-app dev
```

The CLI prints `✓ dashboard http://localhost:5180/`. Open it. A mock-dashboard shell loads, and your bundle is mounted inside an iframe at `/anna-apps/<slug>/dev/index.html?wid=<window-uuid>&t=<dev-token>`. The harness runs the **same** dispatcher that ships in production, with an in-memory `WindowStore` (no Postgres, no NATS, no Executa Agent in the loop).

What's happening underneath:

- The CLI auto-discovers each `executas/<name>/` subdirectory and supervises it as a stdio process. Detection is language-agnostic: `executa.json` (explicit) > `pyproject.toml` (Python via `uv run`) > `package.json` (Node) > `go.mod` + `executa.json` (Go) > `bin/<name>` (pre-built binary). See [Multi-language executas](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/multi-language-anna-apps.md).
- A static-file server serves your `bundle/` at `/anna-apps/<slug>/dev/`.
- An SSE relay forwards server-pushed events (`auth.refresh`, `app/method`, `entry_payload`) into the iframe.
- The bundle's `tools.invoke`, `storage.set`, `storage.get`, `window.set_title`, `window.ready` calls land in the production RPC dispatcher and are ACL-checked against `manifest.ui.host_api`.

Hot reload is on by default — edit `bundle/app.js`, save, watch the iframe refresh.

## 3. Validate before publish

```bash
anna-app validate           # JSON Schema + ui static + tool_id linter
anna-app validate --strict  # also greps the bundle for host_api ACL coverage
```

The validator is fail-fast and layered:

1. JSON Schema (`@anna-ai/app-schema`) — same definition the server uses on `POST /api/v1/developer/apps/{id}/versions`.
2. UI static checks — bundle entry exists, view names unique, sizes well-formed.
3. Cross-file `tool_id` linter — every `host_api.tools[]` entry resolves to a `required_executas[]` entry, with Levenshtein-1 typo suggestions.
4. `--strict` — greps your bundle JS/TS for `anna.<ns>.<method>` usage and verifies each is allowlisted in `manifest.ui.host_api`.

If everything is green, you have a publishable artifact.

## 4. Drive it from a test

For CI, mount the bundle programmatically (no browser, no SSE):

```ts
import { mountBundle } from "@anna-ai/cli/test";

const h = await mountBundle({
  manifest: "./manifest.json",
  bundle:   "./bundle",
});

await h.call("storage", "set", { key: "ping", value: 1 });
const events = h.drainEvents();
await h.close();
```

For executa-side coverage, use the `anna-executa-test` pytest plugin (`executa_session` / `executa_invoke` fixtures). Both paths share the same dispatcher as `anna-app dev` and production.

## 5. Where to next

- **Manifest reference** — [App Manifest](/developers/apps/app-manifest) (every field, every validator)
- **Bundling components** — [Bundling](/developers/apps/app-bundling)
- **Listing assets** — [Listing](/developers/apps/app-listing)
- **App UI runtime** — [Overview](/developers/apps/app-ui-overview), [SDK](/developers/apps/app-ui-sdk), [Host API](/developers/apps/app-ui-host-api)
- **Local dev deep-dive** — [Local Development](/developers/apps/local-dev)
- **Recording & replay for CI** — [Recording / Replay](/developers/apps/recording-replay)
- **Submit for review** — [Publishing](/developers/apps/app-publish)

> [!NOTE]
> The CLI ships as [`@anna-ai/cli`](https://www.npmjs.com/package/@anna-ai/cli) on npm. Source, docs, and the rest of the developer hub live at [anna.partners](https://anna.partners). The pinned Python runtime version is exposed as `PINNED_RUNTIME_VERSION` in the harness bridge.


---

---
title: Build Beautiful: the Focus Flow Example
description: Clone the anna-app-focus-flow reference project and ship a polished Anna App — Tool plugin, Skill, and SPA bundle — in one sitting.
section: apps
slug: app-focus-flow
updated: 2026-05-06
estimated_minutes: 6
---

The [`anna-app-focus-flow`](https://github.com/whtcjdtc2007/anna-executa-examples/tree/main/examples/anna-app-focus-flow) example in the public [`anna-executa-examples`](https://github.com/whtcjdtc2007/anna-executa-examples) repo is the most complete reference Anna App we ship. It bundles **all three** building blocks an app can declare — a stdio Tool plugin, a Skill, and a polished UI bundle — wired together with the production RPC dispatcher. Treat it as a working blueprint: clone it, rename, and you have a beautiful Anna App.

> [!TIP]
> If you only want the bare CLI flow, start with [Quickstart: anna-app CLI](/developers/apps/app-quickstart). This page is for when you want a finished, opinionated example to learn from or fork.

## What you get out of the box

```
anna-app-focus-flow/
├── app.json                  # Listing metadata (slug, name, category)
├── manifest.json             # AppManifest schema:1 — UI + executas + host_api ACL
├── bundle/
│   ├── index.html            # SPA entry, loads the AnnaAppRuntime SDK
│   ├── app.js                # calls anna.tools.invoke / storage / chat / window
│   ├── style.css             # the "beautiful" part
│   └── icon.svg
├── executas/
│   ├── focus-session-python/ # stdio Tool plugin — Python / uv (default flavour)
│   │   ├── executa.json       #   {tool_id, type:"python", enabled:true}
│   │   ├── focus_session_plugin.py
│   │   ├── pyproject.toml
│   │   └── README.md
│   ├── focus-session-node/   # stdio Tool plugin — Node.js 18+ (alternate flavour)
│   │   ├── executa.json       #   {tool_id, type:"node", enabled:false}
│   │   ├── package.json
│   │   └── focus_session_plugin.js
│   ├── focus-session-go/     # stdio Tool plugin — Go 1.21+ (alternate flavour)
│   │   ├── executa.json       #   {tool_id, type:"go", enabled:false}
│   │   ├── go.mod
│   │   └── main.go
│   └── focus-coach/
│       └── SKILL.md          # declarative Skill loaded into the LLM prompt
├── fixtures/                 # recorded RPC sessions for replay-based tests
├── tests/                    # vitest (bundle) + pytest (plugin) suites
└── scripts/
    └── set-tool-id.py        # rewrite the placeholder tool_id across all 4 files
```

A single repo gives you everything an app submission needs:

- **Tool** — `focus-session` exposes one dispatcher method (`session`) with an `action` discriminator (`start`, `pause`, `resume`, `complete`, `get_state`). One Executa row per app, no per-method explosion. The plugin ships in **three language flavours** (Python, Node.js, Go) all conforming to the same JSON-RPC contract; pick one via the `enabled` field in each `executa.json` (default: Python). See [Multi-language executas](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/multi-language-anna-apps.md) for the full discovery rules.
- **Skill** — `focus-coach` is loaded into the assistant's system prompt whenever the app's window is focused, so the LLM knows when and how to call the tool.
- **UI bundle** — a static SPA that talks to the host through the [App UI SDK](/developers/apps/app-ui-sdk), exercising `tools.invoke`, `storage.get/set`, `chat.write_message`, and `window.set_title` against the real ACL.
- **Tests + fixtures** — vitest drives the bundle through `mountBundle`, pytest drives the plugin through `anna-executa-test`, and recorded JSONL fixtures replay through `anna-app fixture verify`.

## 1. Clone and install

```bash
git clone https://github.com/whtcjdtc2007/anna-executa-examples.git
cd anna-executa-examples
pnpm install                 # installs @anna-ai/cli for every example
uv --version                 # uv must be on PATH — used to spawn the Python bridge
anna-app doctor              # checks uv, runtime pin, signing key
```

Then jump into the example:

```bash
cd examples/anna-app-focus-flow
```

> [!NOTE]
> If `which anna-app` finds nothing on your PATH, use `pnpm --filter anna-app-focus-flow <script>` so the workspace-local CLI binary resolves correctly.

## 2. Run it locally

```bash
pnpm dev                     # → anna-app dev
# Harness UI: http://localhost:5180
```

The CLI starts the same harness you saw in the [Quickstart](/developers/apps/app-quickstart): it serves `bundle/` at `/anna-apps/focus-flow/dev/`, supervises the active `executas/focus-session-*/` flavour as a stdio process (Python via `uv run`, Node via `node`, Go via `go run`), and proxies every `anna.*` RPC to the real Python bridge — same dispatcher, same ACL gating, same SSE event shapes as production. Edits under `bundle/` hot-reload the iframe.

The first `tools.invoke` lazy-spawns the executa. If the process exits immediately, look for `tool_failed: executa process exited` in the right-hand RPC log panel; for the Python flavour, `cd executas/focus-session-python && uv sync` will surface the real dependency error.

To try a different language flavour for a single run without editing `executa.json`:

```bash
anna-app dev --executa dir=./executas/focus-session-node
anna-app dev --executa dir=./executas/focus-session-go,type=go
```

The `--executa` flag bypasses `enabled: false` on the directory you single out.

## 3. Mint your own Tool & Skill IDs

The example ships with `*-CHANGEME-*` placeholder IDs so it stays publishable as a template. Before installing on Anna for real, mint server-side IDs and rewrite all four files atomically:

```bash
# After minting at https://anna.partners/executa → My Tools → Mint:
scripts/set-tool-id.py apply --tool tool-yourhandle-focus-session-abcd1234
scripts/set-tool-id.py status   # confirm the three files agree
```

The helper updates (Python flavour only — see the per-flavour READMEs for Node / Go):

1. `executas/focus-session-python/pyproject.toml` (`[project].name` + `[project.scripts]` key)
2. `manifest.json` (`required_executas[].tool_id` + `ui.host_api.tools`)
3. `bundle/app.js` (`TOOL_ID` constant)

The runtime `MANIFEST` in `focus_session_plugin.py` no longer declares a `name` — the host identifies the Executa by its server-assigned `tool_id`, not by a self-reported manifest name.

Run `scripts/set-tool-id.py reset` to restore the placeholders before committing back to a fork.

> [!IMPORTANT]
> Tool IDs are **mint-only** — Anna assigns them server-side as `tool-{handle}-{slug}-{uniq}` and the dispatcher does literal string equality against `required_executas[].tool_id`. You cannot type a custom ID, and any client-supplied `tool_id` is dropped. See [App Manifest](/developers/apps/app-manifest) for the full ACL rules.

## 4. Validate

```bash
pnpm validate                # → anna-app validate --strict
```

This runs the same three layers `matrix-nexus` applies on submission:

1. **`AppManifest`** Pydantic model (`extra="forbid"`) — shape & types
2. **`validate_ui_section_static`** — CSP, view geometry, and the rule that every `host_api.tools` entry resolves to a declared `required_executas` / `optional_executas` ID
3. **Bundle linter** — entry exists, view names unique, sizes well-formed; `--strict` greps the bundle JS for `anna.<ns>.<method>` usage and asserts each is allow-listed

## 5. Test the contract

```bash
# Bundle (TypeScript / vitest):
pnpm test

# Plugin (Python / pytest via anna-executa-test):
cd executas/focus-session
uv sync --extra dev
uv run pytest ../../tests/plugin -q
```

Both suites use the production dispatcher path. See [Testing the Bundle](/developers/apps/testing-bundle) and [Testing the Plugin](/developers/apps/testing-plugin) for the underlying APIs.

## 6. Replay recorded fixtures

```bash
pnpm fixture:verify          # replays fixtures/*.jsonl through the harness
pnpm fixture:summarize       # human-readable transcript of the happy path
```

Recorded fixtures are how the example pins regressions — see [Recording and Replay](/developers/apps/recording-replay) for the JSONL format and how to capture new ones.

## 7. Submit it

When the example is yours (renamed, re-minted, restyled), follow the standard publish flow:

1. Mint a Skill ID for `focus-coach` and paste the SKILL.md body in the Anna console.
2. Create the App listing (`app.json` → **Listing** tab on the developer console).
3. Create a version, paste your `manifest.json`, upload every file under `bundle/` through the bundle uploader.
4. Submit for review → wait for approval → **Publish** → install from the app's detail page.

Detailed walk-throughs live at [Publishing an App](/developers/apps/app-publish), and the per-tab field reference at [Listing Fields](/developers/apps/app-listing).

## Where to look next

- **Manifest internals** — [App Manifest](/developers/apps/app-manifest)
- **Bundling executas** — [Bundling Executas](/developers/apps/app-bundling)
- **App UI surface** — [Overview](/developers/apps/app-ui-overview), [SDK](/developers/apps/app-ui-sdk), [Host API](/developers/apps/app-ui-host-api)
- **CI replay** — [Recording and Replay](/developers/apps/recording-replay)

> [!NOTE]
> The example tracks the latest stable [`@anna-ai/cli`](https://www.npmjs.com/package/@anna-ai/cli) and the pinned Python runtime declared in the harness bridge. If `anna-app doctor` flags a mismatch, run `pnpm install` at the repo root before `anna-app dev`.


---

---
title: App Manifest
description: The manifest JSON that declares which Executas an app bundles and how the assistant should behave when it is mentioned.
section: apps
slug: app-manifest
updated: 2026-04-22
estimated_minutes: 6
---

An Anna App is composed of two halves:

1. **Listing metadata** (name, slug, category, tagline, description, logo, screenshots, homepage, pricing model). This is edited in the **Listing** tab of the [Developer Console](/developer) and stored on the `AnnaApp` row. It is **not** part of the manifest.
2. **Manifest** — a JSON document attached to each immutable [version](/developers/apps/app-versioning). It declares the Executas the app bundles and the prompt instructions the assistant should follow when the user `#`mentions the app.

This page documents the manifest only.

## Minimal example

```json
{
  "schema": 1,
  "required_executas": [
    { "tool_id": "web_search" }
  ]
}
```

## Full example

```json
{
  "schema": 1,
  "required_executas": [
    { "tool_id": "web_search" },
    { "tool_id": "pdf_reader", "min_version": "1.0.0" }
  ],
  "optional_executas": [
    { "tool_id": "image_generation", "min_version": "1.0.0" }
  ],
  "permissions": [],
  "system_prompt_addendum": "You are Research Buddy, a meticulous research assistant. Always cite sources with markdown links. Prefer primary sources. When asked a question, search first, then synthesise.",
  "user_message_prefix_template": "[Research] {user_message}",
  "tags": ["research", "productivity"]
}
```

## Field reference

The manifest is parsed by the `AppManifest` Pydantic model with `extra="forbid"`. **Any field not listed below will be rejected.**

| Field | Type | Required | Constraints |
|---|---|---|---|
| `schema` | integer | yes | `1` (no UI) or `2` (UI runtime). `2` enables the [`ui`](#ui-section-schema-2) section |
| `required_executas` | array | yes | Length ≥ 1. Items: `{ "tool_id": string, "min_version"?: string, "version"?: string }` |
| `optional_executas` | array | no | Same item shape as `required_executas`. Defaults to `[]` |
| `permissions` | array of string | no | **Strict allow-list.** Unknown values are rejected. The Anna App UI Runtime enforces these scopes per RPC — see [Host API](/developers/apps/app-ui-host-api). For `schema: 1` apps with no UI the values are stored but currently have no runtime effect |
| `system_prompt_addendum` | string | no | Max 4000 characters. Appended to the assistant's system prompt when the user `#`mentions the app |
| `user_message_prefix_template` | string | no | Max 500 characters. Must contain **exactly one** `{user_message}` placeholder. See [Runtime behaviour](#runtime-behaviour) for current limitations |
| `tags` | array of string | no | Free-form tags. Stored but not surfaced in the App Store today |
| `ui` | object | no (yes when `schema: 2`) | UI bundle + views + host API ACL. Full reference: [App UI Manifest](/developers/apps/app-ui-manifest) |
| `dev` | object | no | **Local-harness-only.** Consumed by `anna-app dev`; production dispatcher ignores it at runtime, and `anna-app publish` strips it before upload. See [`dev` block](#dev-block-local-harness-only) |

Allowed `permissions` values (`_ALLOWED_PERMISSIONS`):

```
ui.svg
fs.read, fs.write
tools.invoke
chat.read, chat.write_message, chat.append_artifact
artifact.create, artifact.update, artifact.delete
llm.complete
storage.read, storage.write
prefs.read
```

### `required_executas[]` and `optional_executas[]`

```json
{ "tool_id": "web_search", "min_version": "1.0.0" }
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `tool_id` | string | yes | 1–200 chars. Must match the `tool_id` of an Executa already published in the platform's Executa catalogue (visibility must be `app_bundled` or `public`; `private` and `archived` Executas are rejected) |
| `min_version` | string | no | Up to 40 chars. Stored on the manifest; **not enforced** by the validator today (only `tool_id` existence is checked) |
| `version` | string | no | Pin a specific `ExecutaVersion` snapshot. Omit or use `"latest"` to auto-freeze the current Executa state at publish time |

Behavioural difference between the two arrays:

- **`required_executas`** — automatically installed for the user when the app is installed (a `UserExecuta` row is created if missing). Tool documentation is injected into the system prompt whenever the app is `#`mentioned.
- **`optional_executas`** — **not** auto-installed. Tool documentation is still injected when the app is `#`mentioned, but the user must have the Executa otherwise authorised for it to actually run.

A given `tool_id` may appear at most once across both arrays combined.

### `dev` block (local-harness-only)

The `dev` block is consumed by `anna-app dev` (the local harness shipped with the [`anna-app` CLI](/developers/apps/app-quickstart)). It is declared on the Pydantic model so `extra="forbid"` does not reject it, but the production dispatcher **ignores it at runtime**, and `anna-app publish` strips it before upload.

```json
{
  "schema": 2,
  "required_executas": [{ "tool_id": "tool-dev-focus-flow" }],
  "ui": { "...": "..." },
  "dev": {
    "fixtures": ["fixtures/*.jsonl"],
    "seed_storage": { "focus-flow:last": 0 },
    "user_id": 7,
    "mocks": {
      "tools.invoke": { "result": { "pong": true } }
    }
  }
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `fixtures` | array of string | no | Glob patterns, relative to the manifest dir, pointing at JSONL fixture files for replay |
| `mocks` | object | no | Per-`(ns, method)` static response mocks, keyed by `"ns.method"` (e.g. `"tools.invoke"`) |
| `seed_storage` | object | no | Initial `runtime_state` planted into the in-memory `WindowStore` for `anna-app dev` sessions |
| `user_id` | integer | no | Override the harness's default `user_id` (default: `1`) |

The `dev` block also accepts unknown extra keys (`extra="allow"`) so the harness can evolve independently from the on-the-wire schema.

## Validation

Validation runs in two places:

- `POST /api/v1/developer/apps/validate-manifest` — the **Validate** button in the Developer Console (read-only dry run).
- `POST /api/v1/developer/apps/{id}/versions` — when you create a new version. The same checks run again on `publish` to guard against an Executa being deleted in the meantime.

Checks performed (`anna_app_validator.validate_manifest`):

1. **Structure** — Pydantic `AppManifest` parsing (`extra="forbid"`, types, length limits).
2. **`schema`** must be `1` or `2`.
3. **`required_executas` non-empty** — **required for `schema: 1`** (chat-augmentation apps need at least one tool, otherwise the app is a runtime no-op). **Optional for `schema: 2`**: Bundle-only UI apps that rely solely on `ui.host_api` (e.g. `image.*`, `storage.*`, `llm.*`) may leave both `required_executas` and `optional_executas` empty.
4. **Placeholder rule** — if `user_message_prefix_template` is set, it must contain exactly one `{user_message}` substring. Zero or two+ occurrences fail.
5. **Executa existence + visibility** — every `tool_id` must resolve to a non-archived `executas` row whose `visibility` is `app_bundled` or `public`.
6. **Uniqueness** — no `tool_id` may appear twice across `required_executas + optional_executas`.
7. **Permissions allow-list** — unknown `permissions` entries are rejected.
8. **UI section** — when `schema: 2`, the `ui` section is statically validated (`validate_ui_section_static`). Bundle entry path existence is re-checked at `bundle/finalize`. See [App UI Manifest](/developers/apps/app-ui-manifest) for the full rules.

Common rejection reasons:

- Missing or wrong-typed required field.
- An unknown field (manifest uses `extra="forbid"`).
- `required_executas` empty **on a `schema: 1` app** (allowed on `schema: 2` Bundle-only apps).
- `tool_id` not found in the Executa catalogue.
- `user_message_prefix_template` missing `{user_message}` or containing it more than once.

Version-level checks (run alongside the manifest checks when creating a version):

- `version` must be valid SemVer (`X.Y.Z` with optional `-prerelease`).
- `version` must be **strictly greater** than the largest existing version of this app (pre-release sorts below the matching release).

## Runtime behaviour

The manifest only takes effect when the user explicitly `#`mentions the app in a chat **and** has it installed and enabled.

| Manifest field | What the runtime does with it |
|---|---|
| `required_executas` | On install, missing `UserExecuta` rows are auto-created. On `#`mention, all bundled Executas' tool documentation is injected into the system prompt |
| `optional_executas` | On `#`mention, tool documentation is injected. **Not** auto-installed |
| `system_prompt_addendum` | Wrapped in `<app><system_prompt_addendum>...</system_prompt_addendum></app>` and appended to the system prompt. Treated as authoritative for that turn |
| `user_message_prefix_template` | **Partial.** The template is surfaced to the model as a `<user_message_prefix_template>` block in the system prompt, so the assistant is aware of it. The placeholder is **not** yet substituted into the user's actual message — treat it as a hint, not a hard rewrite |
| `permissions` | Validated against the allow-list at submission. For `schema: 2` UI apps, the Anna App UI Runtime enforces these scopes on every host RPC call (see [Host API](/developers/apps/app-ui-host-api)). For non-UI apps, no further runtime gating is applied today |
| `tags` | Stored only |
| `schema` | `1` = no UI; `2` = UI runtime enabled. When `2`, the `<ui_views>` block is appended to the per-app prompt and the LLM gets the `open_app_view` / `update_app_view` / `close_app_view` tools |
| `ui` | See [App UI Overview](/developers/apps/app-ui-overview) and [App UI Manifest](/developers/apps/app-ui-manifest) |

If multiple apps are mentioned in the same turn, all `system_prompt_addendum` blocks are concatenated in mention order; `user_message_prefix_template` is taken from the first non-empty mentioned app (mention order).

> [!TIP]
> Validate locally before submission. The reviewer will tell you about a failed validation, but it adds days to the review cycle. Click **Validate** in the Developer Console version editor — it runs the exact same checks the version-create endpoint runs.


---

---
title: Bundling Executas
description: How an app declares the Executas it bundles, and what install/runtime semantics each kind has.
section: apps
slug: app-bundling
updated: 2026-04-22
estimated_minutes: 4
category: Distribution & Lifecycle
---

An Anna App's *Executa* bundling is **not a file package**. "Bundling" Executas means listing their `tool_id`s inside the version's manifest JSON — there is no zip or tarball for that part.

> [!NOTE]
> *UI* assets are different. Schema-2 apps additionally upload a static SPA (HTML/JS/CSS/wasm) via the bundle pipeline. That is a real file bundle and is documented in [App UI Bundle Pipeline](/developers/apps/app-ui-bundle).

If you haven't already, read [App Manifest](/developers/apps/app-manifest) first — this page only covers the `required_executas` / `optional_executas` arrays.

## The two arrays

```json
{
  "schema": 1,
  "required_executas": [
    { "tool_id": "web_search" },
    { "tool_id": "pdf_reader", "min_version": "1.0.0" }
  ],
  "optional_executas": [
    { "tool_id": "image_generation" }
  ]
}
```

| Array | Auto-installed for the user? | Tool docs injected on `#`mention? |
|---|---|---|
| `required_executas` | ✅ Yes — `install_app` creates a `UserExecuta` row for every entry the user does not yet have | ✅ |
| `optional_executas` | ❌ No — user must already have it (or install it separately) for it to actually run | ✅ |

A given `tool_id` may appear at most once across both arrays combined.

## Item shape

```json
{ "tool_id": "web_search", "min_version": "1.0.0" }
```

| Field | Required | Constraints |
|---|---|---|
| `tool_id` | yes | 1–200 chars. Must already exist as a row in the platform's `executas` table at submission time and again at publish time |
| `min_version` | no | ≤40 chars. Stored on the manifest but **not enforced** by the validator today; only `tool_id` existence is checked |

There is no syntax for `path://`, `catalogue://`, `hub://`, or any other reference scheme. Bundling Executa source code or binaries inside an app is not supported — Executas are platform-published units; the app simply declares which of them it depends on.

## Lifecycle of a bundle

1. **Create version** (`POST /api/v1/developer/apps/{id}/versions`) — manifest is parsed; every `tool_id` is checked for existence in the Executa catalogue. The version is stored with `is_latest=False`.
2. **Publish version** (`POST /api/v1/developer/apps/{id}/versions/{vid}/publish`) — the manifest is **re-validated** (in case an Executa was removed in the meantime). On success:
   - `anna_app_executas` snapshot table is rebuilt for this version: `required` first, then `optional`, in declared order, with `display_order` and `is_required` recorded.
   - The app's `latest_version` cache is updated.
   - If the app's `status` is `APPROVED` or `PENDING_REVIEW`, it is auto-promoted to `PUBLISHED`.
3. **User install** (`install_app`) — only allowed when `status ∈ {PUBLISHED, APPROVED}`. The latest published version is fetched; missing `UserExecuta` rows for `required_executas` are created. `optional_executas` are not auto-installed.
4. **User `#`mention** (`build_app_mention_prompt`) — only effective when the user has the app installed and `is_enabled=True`. All bundled Executas (required + optional) have their tool documentation injected into the system prompt for that turn.

## Validation checklist

Before clicking **Validate** in the Versions tab, make sure:

- [ ] `schema` is `1`.
- [ ] `required_executas` has at least one entry.
- [ ] Every `tool_id` exists in the Executa catalogue (the **Validate** button confirms this with a single round trip).
- [ ] No `tool_id` appears in both arrays.
- [ ] `system_prompt_addendum` is ≤4000 chars.
- [ ] `user_message_prefix_template`, if set, contains exactly one `{user_message}` and is ≤500 chars.

Next: [Listing assets](/developers/apps/app-listing).


---

---
title: Listing Fields
description: The store-facing metadata you fill in on the Listing tab of the Developer Console.
section: apps
slug: app-listing
updated: 2026-04-22
estimated_minutes: 4
category: Distribution & Lifecycle
---

The **Listing** tab of the [Developer Console](/developer) writes directly to the `AnnaApp` row. None of these fields live in the manifest — they are stored once and shared across every version of the app.

## Fields

| Field | Storage column | Required | Constraints |
|---|---|---|---|
| Name | `name` | yes | 1–120 chars |
| Slug | `slug` | yes (create only) | 3–80 chars; pattern `^[a-z0-9][a-z0-9-]{1,78}[a-z0-9]$` (no leading/trailing hyphen); globally unique; **immutable after creation** |
| Category | `category` | yes | One of: `productivity`, `developer-tools`, `creative`, `data`, `lifestyle`, `education`, `communication`, `entertainment`, `utilities` |
| Short description (tagline) | `tagline` | no | ≤160 chars |
| Long description | `description` | no | ≤20000 chars |
| Logo URL | `logo_url` | no | ≤500 chars. See [Logo upload](#logo-upload) for the recommended path |
| Cover URL | `cover_url` | no | ≤500 chars |
| Screenshots | `screenshots[]` | no | List of URLs, **max 6**. The Console accepts one URL per line |
| Homepage URL | `homepage_url` | no | ≤500 chars |
| Repository URL | `repository_url` | no | ≤500 chars |
| Support URL | `support_url` | no | ≤500 chars |
| Privacy URL | `privacy_url` | no | ≤500 chars |
| Pricing model | `pricing_model` | yes (defaults `free`) | One of `free`, `byo-key`, `paid` |

> [!WARNING]
> The Console's pricing dropdown currently exposes `free`, `paid`, `subscription`. The backend only accepts `free`, `byo-key`, `paid` — selecting `subscription` will fail validation. Until the dropdown is fixed, stick to `free` or `paid`.

## Logo upload

The recommended way to set a logo is the **Upload logo** button, which calls `POST /api/v1/developer/apps/{id}/logo`:

- Accepts `image/jpeg`, `image/png`, `image/webp`, `image/gif`.
- Max **2 MB** raw upload.
- Server-side: EXIF-rotated, centre-cropped to a square, resized to **256×256**, encoded as **WebP** (quality 88).
- Uploaded to the platform R2 CDN; the returned `logo_url` is written back to the app and the form field.
- Requires R2 to be configured server-side; otherwise the endpoint returns 503.

You can also paste an external URL directly into the `logo_url` field; the platform will not re-host it.

## What is **not** in the listing

- **Tags** — `tags` lives inside the manifest (free-form, stored only, not surfaced in the App Store today).
- **Starter prompts**, **persona**, **default model**, **temperature**, **greeting** — none of these exist anywhere in the schema.
- **What's new / changelog** — per-version, lives on `AnnaAppVersion.changelog`, not on the app listing.

## Locking and editability

- `slug` is sent on `POST /developer/apps` and can never be changed; the Console disables the field after creation, and the `PATCH /developer/apps/{id}` endpoint silently ignores it.
- All other listing fields can be updated at any time via `PATCH /developer/apps/{id}`. Updates do not require re-review.

Next: [Publishing your app](/developers/apps/app-publish).


---

---
title: Publishing an App
description: Walk an app through review and into the Anna App Store.
section: apps
slug: app-publish
updated: 2026-04-22
estimated_minutes: 5
category: Distribution & Lifecycle
---

Apps move through the review pipeline from the [Developer Console](/developer) **or** the `anna-app` CLI (`anna-app apps push` / `cut` / `release` / `publish` / `submit-review`, plus `archive` / `unpublish` / `status` / `versions` / `grants`). There is no raw zip upload — the CLI bundles and uploads for you, and admin review is the only step that happens exclusively server-side.

## Status machine

```
DRAFT ──submit──▶ PENDING_REVIEW ──admin approve──▶ APPROVED ──publish version──▶ PUBLISHED
  ▲                      │                              │                              │
  └──── REJECTED ◀───────┘                              └────── publish version ───────┘
                                                                                        │
                                                                                  ARCHIVED
```

Defined in `AnnaAppStatus`:

| Status | Meaning |
|---|---|
| `DRAFT` | Newly created. Not visible to anyone but you |
| `PENDING_REVIEW` | Submitted for admin review. You can no longer submit again until the admin acts |
| `APPROVED` | Admin approved but no version is `is_latest` yet — invisible in the App Store, but **installable** by direct lookup |
| `PUBLISHED` | Visible in the App Store and installable. Set automatically when you publish a version while in `APPROVED`/`PENDING_REVIEW`, or when an admin approves with `publish=True` |
| `REJECTED` | Admin rejected. You can edit and re-submit |
| `ARCHIVED` | Hidden from the App Store. Existing installations keep working |

## 1. Pre-flight (developer)

- [ ] Listing fields filled in ([Listing Fields](/developers/apps/app-listing)).
- [ ] At least one version exists ([App Manifest](/developers/apps/app-manifest)).
- [ ] **Validate** in the Versions tab returns `valid: true`.
- [ ] *(UI apps, `schema: 2`)* The version's UI bundle has been uploaded and `bundle/finalize` returned `status: bundle_ready`. The platform refuses to open windows for any version whose bundle is still `draft`. See [App UI Bundle Pipeline](/developers/apps/app-ui-bundle).
- [ ] You have installed and used the app yourself end-to-end.

## 2. Submit for review

In the Console: **Settings tab → Submit for review** (`POST /developer/apps/{id}/submit-review`).

Backend rules:

- The app must currently be `DRAFT` or `REJECTED`.
- The app must have at least one version (otherwise: `"提交审核前需至少创建一个版本"`).
- On success the status flips to `PENDING_REVIEW`.

There is no email notification today.

## 3. Admin review

An admin (or super-admin with the `APPS_MGMT` section) acts on the app via:

- `POST /api/v1/super-admin/apps/{id}/approve` with body `{ "publish": bool, "notes": string? }`
  - Status must be `PENDING_REVIEW`.
  - With `publish: false` → status becomes `APPROVED`.
  - With `publish: true` → the most-recently created version is published (becomes `is_latest`) and status becomes `PUBLISHED`.
  - `review_notes`, `reviewed_at`, `reviewed_by_id` are recorded.
- `POST /api/v1/super-admin/apps/{id}/reject` — status becomes `REJECTED`. You can revise and submit again.

Reviewers verify, at minimum:

- Manifest re-validates against the schema and against the live Executa catalogue.
- Listing copy and screenshots match observed behaviour.

There is no enforced SLA today; check **My Apps** in the Console for the current status.

## 4. Publish a version

Once the app reaches `APPROVED` (or `PUBLISHED`), the developer can publish individual versions via the **Versions** tab → **Publish** (`POST /developer/apps/{id}/versions/{vid}/publish`):

- Allowed only when `app.status ∈ {APPROVED, PUBLISHED}` (otherwise: `"App 必须先通过审核（APPROVED）后才能发布版本"`).
- The manifest is re-validated against the live Executa catalogue.
- Other versions of the same app have `is_latest` cleared; this one is set to `is_latest=True` with `published_at = now()`.
- The `anna_app_executas` snapshot is rebuilt.
- `app.latest_version` is updated; `status` auto-promotes from `APPROVED`/`PENDING_REVIEW` to `PUBLISHED`.

## 5. After publish

- The app appears in the public App Store list (`status == PUBLISHED`).
- New installs auto-install the app's `required_executas`.
- `install_count`, `rating_avg`, `rating_count`, and `is_featured` are tracked on `AnnaApp` (rating/featured are admin-driven).

## 6. Rejection

If the admin rejects, the app moves to `REJECTED`. Edit the listing or create a new version, then submit for review again. There is no penalty for multiple rounds.

## 7. Archive

Settings tab → **Archive** (`POST /developer/apps/{id}/archive`):

- Sets `status = ARCHIVED` from any state.
- Existing `UserAnnaApp` rows are untouched — installed users continue to use the app.
- New users cannot discover or install the app.

Next: [Versioning & updates](/developers/apps/app-versioning).


---

---
title: Versioning & Updates
description: How versions are created, ordered, and rolled out to installed users.
section: apps
slug: app-versioning
updated: 2026-04-22
estimated_minutes: 4
category: Distribution & Lifecycle
---

Each Anna App version is an immutable `AnnaAppVersion` row consisting of a SemVer string, a free-form `changelog`, and the manifest JSON. For `schema: 2` apps the version is also bound 1:1 to an immutable `AnnaAppUiBundle` (the uploaded static SPA) — a bundle that has been finalized cannot be edited; you must create a new version. To change anything bundled or any prompt directive, create a new version with a strictly greater SemVer and publish it.

## SemVer rules

The `version` field must match:

```
^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-.]+)?$
```

- `X.Y.Z` is required.
- An optional `-prerelease` suffix is allowed (e.g. `1.2.0-beta.1`).
- `+build` metadata is **not** supported by the validator.
- A new version must be **strictly greater** than the largest existing version of this app, comparing major/minor/patch numerically and treating any pre-release as smaller than the matching release (`1.2.0-beta.1 < 1.2.0`).

Examples:

| Existing latest | Allowed next | Rejected |
|---|---|---|
| `1.0.0` | `1.0.1`, `1.1.0`, `2.0.0` | `1.0.0`, `0.9.0` |
| `1.2.0-beta.1` | `1.2.0-beta.2`, `1.2.0`, `1.3.0` | `1.2.0-alpha.9`, `1.1.9` |

There is **no semantic distinction** between patch / minor / major bumps in the platform today. There is no separate "auto-install patch, prompt for major" tiering — see [Update behaviour](#update-behaviour) below.

## Creating a version

`POST /api/v1/developer/apps/{id}/versions`:

```json
{
  "version": "1.0.1",
  "changelog": "Fix typo in system_prompt_addendum.",
  "manifest": { "schema": 1, "required_executas": [{ "tool_id": "web_search" }] }
}
```

Server-side checks:

1. SemVer format.
2. No duplicate version on this app.
3. Strictly greater than current max.
4. Full manifest validation (see [App Manifest](/developers/apps/app-manifest#validation)).

The version is created with `is_latest=False`. It does not affect anyone until you publish it.

## Publishing

`POST /api/v1/developer/apps/{id}/versions/{vid}/publish` — see [Publishing an App](/developers/apps/app-publish#4-publish-a-version) for the full flow. In short:

- App must be `APPROVED` or `PUBLISHED`.
- Manifest is re-validated.
- This version becomes `is_latest`; the previous one's flag is cleared.
- The `anna_app_executas` snapshot is rebuilt for this version.

The previous "published" version row is **not** deleted — it remains in the table with `is_latest=False`. There is no public endpoint to install an arbitrary historical version.

## Update behaviour for installed users

`UserAnnaApp` carries `auto_update: bool` (defaults to `True` on first install). The platform behaviour today:

- Re-running `install_app` for an already-installed user upgrades `installed_version` to the current `is_latest` and re-runs `required_executas` auto-install for any newly added entries.
- There is **no scheduled job** that pushes updates automatically; "auto-update" is a stored preference, not an executed policy. New `is_latest` versions take effect for a user the next time install is invoked for them.
- There is **no in-product "What's new" prompt**, no per-segment (patch/minor/major) tiering, and no "user must accept major upgrade" gate.

## Rollback

There is no built-in rollback or "deprecate version" endpoint. To effectively roll back, publish a new version (with a higher SemVer) that restores the previous manifest content.

## Archiving the app

Archiving the **app** (`POST /developer/apps/{id}/archive`) sets `status=ARCHIVED`, removing it from the App Store. Existing `UserAnnaApp` rows continue to function. There is no per-version archive.

## Cadence and badges

The platform does **not** today implement:

- "Recently updated" badges based on shipping window.
- "Maintenance status: unknown" warnings for stale apps.
- Automatic delisting after N months of inactivity.

`AnnaApp.updated_at` is tracked and surfaced in the listing payload, but no policy is keyed off it.

That is the full versioning surface. Ship a new SemVer, publish it, and installed users converge on the next install call.


---

---
title: Anna App UI Overview
description: How Anna Apps render an interactive sandboxed window on the dashboard, and how the LLM, the iframe, and the host coordinate.
section: apps
slug: app-ui-overview
updated: 2026-04-28
estimated_minutes: 5
category: App UI
---

A `schema: 1` Anna App is just "a manifest + a set of Executas". When you bump the manifest to `schema: 2` and add a `ui` section, the app graduates to a **Talk-to-the-App, Run-in-a-Window** form factor: Anna can summon a sandboxed `<iframe>` window on the dashboard, the user can drag/resize/minimize it, and your iframe code can call back into the host through a typed RPC bridge.

This page is the framework-level orientation. Every concrete file/contract is linked to its detail page.

## What you ship

| Thing | Where it lives |
|---|---|
| `AnnaApp` row (listing, status, developer) | DB `anna_apps` |
| `AnnaAppVersion` row + manifest JSON (`schema: 2`, contains `ui`) | DB `anna_app_versions.manifest` |
| `AnnaAppUiBundle` + `AnnaAppUiFile[]` rows | DB; assets in R2 (`anna-app-bundles/<env>/<slug>/<version>/...`) |
| Static assets (your SPA: `index.html`, JS, CSS, wasm, fonts) | Uploaded by you via `bundle/init` → per-file PUT → `bundle/finalize` |
| `AnnaAppWindowSession` rows (one per opened window) | DB `anna_app_window_sessions` (created at runtime) |

## Runtime topology

```
┌──────────────────────────── Browser (/dashboard) ───────────────────────────┐
│                                                                              │
│  ┌─Chat Pane──┐  ┌─App Deck──┐  ┌──────── Window Layer ────────────┐         │
│  │ messages   │  │ installed │  │ floating <iframe sandbox> windows │         │
│  │ SSE stream │  │ apps      │  │ headers, resize, dock, z-index    │         │
│  └────────────┘  └───────────┘  └───────────────────────────────────┘         │
│       ▲              ▲                       ▲                                │
│       │              │                       │                                │
│  ┌────┴──────────────┴────────── Window Manager ───────────────────────┐      │
│  │  AnnaAppWM: open/focus/close/minimize/dock                          │      │
│  │  Hydrates from GET /runtime/windows on dashboard load               │      │
│  │  Applies SSE events (open_view, geometry_changed, …)                │      │
│  └────────────────────────────────────────────────────────────────────-┘      │
│                                  │                                            │
│                          ┌───────┴────────┐                                   │
│                          │ Host Bridge    │  postMessage  ◀── iframe SDK ──   │
│                          │ token mint +   │  /api/v1/anna-apps/runtime/rpc    │
│                          │ ACL forwarding │                                   │
│                          └───────┬────────┘                                   │
└──────────────────────────────────┼────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┴───────────────────────────┐
        │ Nexus FastAPI                                        │
        │ /anna-apps/{slug}/{version}/<path>          (assets) │
        │ /api/v1/anna-apps/runtime/windows[/{wid}]    (CRUD)  │
        │ /api/v1/anna-apps/runtime/rpc               (RPC)    │
        │ /api/v1/anna-apps/runtime/events/stream     (SSE)    │
        └──────────────────────────┬───────────────────────────┘
                                   │
        ┌──────────────────────────┼───────────────────────────┐
        │ AnnaAppWindowSession (Postgres) + Redis pub/sub      │
        └──────────────────────────┬───────────────────────────┘
                                   │  invokes
                                   ▼
                       ┌────────────────────────┐
                       │ Executa via NATS RPC   │
                       │ (user's Anna Agent)    │
                       └────────────────────────┘
```

There are four pieces:

1. **Window Manager** ([static/js/anna-app-window-manager.js](https://github.com/whtcjdtc2007/matrix-nexus/blob/main/static/js/anna-app-window-manager.js)) — a frontend singleton (`window.AnnaAppWM`) that owns the window DOM and the dock.
2. **Host Bridge** ([static/js/anna-app-host-bridge.js](https://github.com/whtcjdtc2007/matrix-nexus/blob/main/static/js/anna-app-host-bridge.js)) — routes `postMessage` between every iframe and the backend RPC endpoint, mints/refreshes per-window tokens.
3. **Backend Runtime** (`/api/v1/anna-apps/runtime/*` + `/anna-apps/...` for assets) — window CRUD, RPC dispatcher with manifest-driven ACL, SSE event stream, bundle serving with per-bundle CSP.
4. **LLM Tools** (`open_app_view` / `update_app_view` / `close_app_view`) — only injected when at least one mentioned app declares `ui.views`. The LLM uses them to summon, push state into, or close a window.

## Lifecycle of one user request

```
1.  User #mentions an app with `ui.views`.
2.  Backend builds <user_mentioned_apps>… <ui_views>…</ui_views> into the system prompt
    and injects open_app_view/update_app_view/close_app_view into the LLM tool list.
3.  LLM decides to call open_app_view(app_id, view, payload).
4.  Backend creates (or dedups) AnnaAppWindowSession, mints a 120s JWT, emits SSE
    `data_model/AnnaAppEvent { kind: "open_view", … }` on the user channel.
5.  Window Manager receives the SSE event, mounts an <iframe sandbox>
    pointing at /anna-apps/{slug}/{version}/{entry}?wid=…&t=…
6.  iframe imports /static/anna-apps/_sdk/latest/index.js as an ES module, calls
    AnnaAppRuntime.connect(); the SDK sends `window.hello` over postMessage.
7.  Host Bridge forwards hello to /runtime/rpc; backend returns capabilities,
    view_meta, entry_payload, runtime_state, geometry.
8.  iframe renders. It can now invoke whitelisted tools, push artifacts to chat,
    persist state via storage.set, etc.
9.  User drags/resizes the window → Window Manager debounces a PATCH /windows/{wid}
    {geometry: …} → backend persists + broadcasts SSE `geometry_changed` to other
    tabs/devices.
10. LLM may push updates by calling update_app_view (sends `entry_payload` patch
    over SSE → SDK exposes as `entry_payload` event).
11. User closes the window → Window Manager DELETEs /windows/{wid}; backend marks
    status=closed and emits SSE `close_view`. Other tabs cleanly tear down too.
```

## Persistence model (no `localStorage`)

All window state is server-authoritative so opening the same conversation in another tab or device shows the exact same windows in the exact same positions:

| Layer | Storage | Examples |
|---|---|---|
| Geometry, dock, monitor size | `anna_app_window_sessions.geometry` (JSON) | `{x, y, w, h, monitor_w, monitor_h, dock_pinned, dock_side, snapped}` |
| Window meta | `anna_app_window_sessions` columns | `window_uuid`, `status`, `view`, `entry_payload`, `conversation_session_uuid`, `last_focus_at` |
| App-internal state (≤256 KB) | `anna_app_window_sessions.runtime_state` (JSON) | written by your SDK call `storage.set(...)`; flushed via `navigator.sendBeacon` on tab close |
| Large objects | R2 / artifact; runtime_state holds only a handle | uploaded blobs |

Closing **≠** refreshing. Only an explicit user `×` or `close_app_view` flips `status` to `closed`. A page reload simply re-hydrates from `GET /runtime/windows` and re-attaches to the same `window_uuid`.

## Security baseline

- iframe runs in a `<iframe sandbox>` (no `allow-same-origin` in the spec; the SDK itself talks only via `postMessage`).
- Every request from iframe → backend carries a short-TTL (120s) JWT bound to `(window_uuid, user_id, app_id, version_id, scopes)`. The Host Bridge auto-refreshes it.
- Asset responses include a per-bundle `Content-Security-Policy` (default `default-src 'none'`, `frame-ancestors 'self'`, `script-src 'self'`, …) plus `X-Content-Type-Options: nosniff`, `Cross-Origin-Resource-Policy: same-origin`, `Permissions-Policy` locking off camera/mic/geolocation.
- Every host RPC re-validates the `(ns, method)` against `manifest.ui.host_api`. Unauthorised calls return `permission_denied` without ever reaching the handler.

## Where to next

Build it in this order:

1. [App UI Manifest](/developers/apps/app-ui-manifest) — declare `ui.bundle`, `ui.views`, `ui.host_api`.
2. [App UI Bundle Pipeline](/developers/apps/app-ui-bundle) — upload your static SPA via `bundle/init` → file PUT → `bundle/finalize`.
3. [App UI SDK](/developers/apps/app-ui-sdk) — wire `AnnaAppRuntime.connect()` inside your `index.html`.
4. [App UI Host API](/developers/apps/app-ui-host-api) — full RPC namespace reference + permissions matrix.
5. [App UI Windows](/developers/apps/app-ui-windows) — window lifecycle, persistence, multi-device sync, dock, sizing.
6. [App UI LLM Integration](/developers/apps/app-ui-llm) — `open_app_view` / `update_app_view` / `close_app_view`, SSE events, chat ↔ window patterns.


---

---
title: App UI Manifest
description: The `ui` section of a schema-2 manifest: bundle, views, host_api, csp_overrides.
section: apps
slug: app-ui-manifest
updated: 2026-04-28
estimated_minutes: 6
category: App UI
---

When `schema: 2`, an Anna App manifest gains a `ui` section that describes the static bundle, the named views the LLM can summon, the host API scopes the iframe is allowed to call, and any per-bundle CSP overrides. Everything else from [App Manifest](/developers/apps/app-manifest) still applies.

## Example

```jsonc
{
  "schema": 2,
  "permissions": [
    "tools.invoke",
    "chat.append_artifact",
    "storage.read", "storage.write"
  ],
  "required_executas": [
    { "tool_id": "tool-yourhandle-browser-abcd1234" }
  ],
  "system_prompt_addendum":
    "When the user asks to research, summon the workspace via open_app_view('research-suite'). Stream updates with update_app_view as findings arrive.",
  "ui": {
    "bundle": {
      "format": "static-spa",
      "entry": "index.html",
      "external_origins": ["https://api.example.com"]
    },
    "views": [
      {
        "name": "main",
        "title": "Research Workspace",
        "default": true,
        "min_size":  { "w": 480, "h": 360 },
        "default_size": { "w": 960, "h": 640 },
        "max_size":  { "w": 1920, "h": 1200 },
        "single_instance": true,
        "summary_template": "Research session: {topic}"
      },
      {
        "name": "chart_preview",
        "title": "Chart Preview",
        "entry": "index.html#/chart",
        "default_size": { "w": 640, "h": 480 }
      }
    ],
    "host_api": {
      "tools":  ["required:*"],
      "chat":   ["append_artifact"],
      "storage": ["get", "set", "delete", "list"],
      "window": ["set_title", "open_view", "close"]
    },
    "csp_overrides": {
      "connect-src": ["https://api.example.com"],
      "img-src":     ["https://images.example.com"]
    }
  }
}
```

## Field reference

`ui` is parsed by `UiManifestSection` (Pydantic, `extra="forbid"`).

| Field | Type | Required | Constraints |
|---|---|---|---|
| `bundle` | object | yes | See [`bundle`](#bundle) |
| `views` | array | yes | 1–16 entries; at most one `default: true`. See [`views[]`](#views) |
| `host_api` | object | no | RPC ACL. See [`host_api`](#host_api). Defaults to all empty (only the always-allowed `window` scope) |
| `csp_overrides` | object | no | Map of CSP directive → list of values. Only the directives below are accepted; `script-src` / `style-src` accept only `'self'`, `'sha256-...'`, `'nonce-...'` |
| `state_merge` | string | no | Reserved. Default `"last_writer_wins"` |

### `bundle`

```jsonc
{
  "format": "static-spa",
  "entry": "index.html",
  "external_origins": ["https://api.example.com"]
}
```

| Field | Type | Constraints |
|---|---|---|
| `format` | string | Currently only `"static-spa"` is accepted (validated server-side) |
| `entry` | string | Path to the entry HTML, relative to the bundle root. Must be present in the uploaded `file_map` at `bundle/finalize`. The path part (before `?`/`#`) must match `^[A-Za-z0-9_./\-]+$` and contain no `..`, `\`, or `//` |
| `external_origins` | array of string | Each must start with `https://` and must not contain `*`. Origins listed here are auto-added to `connect-src` and `img-src` of the bundle's CSP |

### `views[]`

A view is a named UI surface inside your bundle. The LLM passes `view: "<name>"` to `open_app_view`; if `view` is omitted the `default: true` view is used.

```jsonc
{
  "name": "main",                 // [a-z0-9_-]{1,40}
  "title": "Research Workspace",  // 1..120 chars
  "default": true,
  "entry": "index.html#/route",   // optional; otherwise bundle.entry
  "min_size":     { "w": 480, "h": 360 },
  "default_size": { "w": 960, "h": 640 },
  "max_size":     { "w": 1920, "h": 1200 },
  "resizable":       true,
  "movable":         true,
  "single_instance": true,        // dedup per (user, conversation, app, view)
  "summary_template": "Research session: {topic}",
  "icon": "icons/research.svg"
}
```

Sizes are integers in CSS pixels, `120 ≤ w,h ≤ 4096`. The validator rejects `default_size` outside `[min_size, max_size]`.

`single_instance: true` means: opening the same `view` again under the same `(user, conversation_session_uuid, app_id)` re-focuses the existing window and merges the new payload into `entry_payload` rather than spawning a second window.

### `host_api`

The ACL that gates host RPC calls from your iframe. Each namespace key is a list of methods the iframe is allowed to invoke. `window.*` is always granted; everything else requires explicit listing.

| Namespace | Allowed values | What it grants |
|---|---|---|
| `tools` | `required:*` &#124; `optional:*` &#124; `required:<tool_id>` &#124; `optional:<tool_id>` &#124; `<tool_id>` | Calls to [`tools.invoke`](/developers/apps/app-ui-host-api#tools) on the listed Executas. Bare `<tool_id>`s must appear in `required_executas` or `optional_executas` |
| `chat` | `read`, `write_message`, `append_artifact` | Read history, post messages, attach artifact cards |
| `artifact` | `create`, `update`, `delete` | Manipulate chat artifacts |
| `llm` | `complete` | Trigger a host-side LLM completion |
| `fs` | `read`, `write` | R2 / Anna Agent filesystem access |
| `storage` | `read`, `write` | Per-window `runtime_state` (≤256 KB) |
| `prefs` | `read` | Read user preferences |
| `window` | (always granted) | Geometry, title, focus, open/close — listing values here is harmless |

Full method-level reference: [App UI Host API](/developers/apps/app-ui-host-api).

### `csp_overrides`

Only these CSP directives may be added to / extended on the bundle response:

```
connect-src
img-src
media-src
font-src
style-src     ('self' | 'sha256-...' | 'nonce-...' only)
script-src    ('self' | 'sha256-...' | 'nonce-...' only)
```

Anything else is rejected. The base CSP is always:

```
default-src 'none'
base-uri 'self'
script-src 'self' <sdk-origin>
style-src 'self' 'unsafe-inline'
img-src 'self' data: blob:
font-src 'self' data:
media-src 'self' blob:
connect-src 'self'
worker-src 'self' blob:
frame-ancestors 'self'
form-action 'self'
```

`external_origins` from `ui.bundle` are automatically added to `connect-src` and `img-src` — you do **not** need to repeat them in `csp_overrides`.

### Top-level `permissions`

Although the field lives at the manifest root (not under `ui`), the Anna App UI Runtime enforces it on every host RPC call: a method whose namespace is gated by a permission (e.g. `chat.write_message` requires the `chat.write_message` permission) will return `permission_denied` when not declared. Allowed values are listed in the [Manifest reference](/developers/apps/app-manifest#field-reference).

## Validation

Two passes:

1. **Static** — runs on every `validate-manifest` and version-create call. Checks `format`, view counts/sizes, `host_api.tools` references, `csp_overrides` shape, `external_origins` schemes.
2. **With files** — runs at `bundle/finalize`. Confirms `bundle.entry` exists in the uploaded `file_map`.

Both raise `ManifestValidationError` with a Chinese-language reason string. Common rejections:

- `ui.bundle.format 当前仅支持 'static-spa'`
- `ui.views 数量必须在 1..16 之间`
- `ui.views 中只能有一个 default=true`
- `view '<name>' default_size 小于 min_size`
- `host_api.tools 引用未在 manifest 中声明的 tool_id: <ref>`
- `csp_overrides 含不允许的 directive: [...]`
- `csp_overrides[script-src] 仅允许 'self' / 'sha256-...' / 'nonce-...'`
- `ui.bundle.entry '<path>' 未在上传的 file_map 中` *(at finalize)*

Next: [App UI Bundle Pipeline](/developers/apps/app-ui-bundle).


---

---
title: App UI Bundle Pipeline
description: Upload your static SPA bundle for a schema-2 Anna App version: init, file PUTs, finalize.
section: apps
slug: app-ui-bundle
updated: 2026-04-28
estimated_minutes: 5
category: App UI
---

A `schema: 2` Anna App version is bound 1:1 to an immutable **bundle** — the static assets your iframe loads. This page covers the upload pipeline. The bundle is stored in R2 under `anna-app-bundles/<env>/<slug>/<version>/<relative_path>` and served at `GET /anna-apps/{slug}/{version}/{path}` with per-bundle CSP and `Cache-Control: public, max-age=31536000, immutable`.

## Quotas

Enforced at `bundle/init`:

| Limit | Value |
|---|---|
| Total bundle size | **50 MB** |
| File count | **2,000** |
| Per-file size | **10 MB** |
| Path safety | No `..`, no `\`, no `//`, no leading `/`, must match `^[A-Za-z0-9_./\-]+$` |

Allowed `content_type` values (`ALLOWED_BUNDLE_CONTENT_TYPES`):

```
text/html, text/css, text/plain
application/javascript, text/javascript, application/json
application/wasm
image/png, image/jpeg, image/gif, image/webp, image/svg+xml, image/avif
font/woff, font/woff2, application/font-woff, application/font-woff2,
font/ttf, font/otf, application/octet-stream (fonts only)
audio/mpeg, audio/wav, audio/ogg
video/mp4, video/webm
```

## Status machine

```
        bundle/init
draft ───────────────► draft
                         │
              all files PUT successfully + sha256/byte_size match
                         │
                         ▼
                    bundle/finalize
                         │
                         ▼
                   bundle_ready (immutable)
```

Once `bundle_ready`, the bundle cannot be edited. Ship a new version to change assets.

## Step 1 — `bundle/init`

```http
POST /api/v1/developer/apps/{app_id}/versions/{version_id}/bundle/init
Content-Type: application/json

{
  "file_map": {
    "index.html": {
      "byte_size": 8421,
      "sha256":    "ab12...",
      "content_type": "text/html"
    },
    "assets/app.js": {
      "byte_size": 92314,
      "sha256":    "cd34...",
      "content_type": "application/javascript"
    },
    "assets/app.css": {
      "byte_size": 1244,
      "sha256":    "ef56...",
      "content_type": "text/css"
    }
  }
}
```

Response:

```jsonc
{
  "bundle_id": "01J...",
  "status": "draft",
  "files": [
    {
      "relative_path": "index.html",
      "byte_size": 8421,
      "sha256": "ab12...",
      "content_type": "text/html",
      "presigned_put_url": "https://r2.example.com/...?X-Amz-Signature=...",  // 10-min TTL
      "proxy_upload_url":  "/api/v1/developer/apps/{app_id}/versions/{version_id}/bundle/file?path=index.html"
    },
    …
  ]
}
```

You have **two ways** to upload each file:

1. **Direct PUT** to `presigned_put_url` (recommended; bypasses Nexus). Set `Content-Type` to the value you declared in `file_map`.
2. **Proxy upload** — `multipart/form-data` POST to `proxy_upload_url` with field `file=<binary>`. Use this when your network blocks the R2 endpoint.

If you need to retry, just call `bundle/init` again on the same version with the same `file_map`; the existing draft is replaced.

## Step 2 — `bundle/finalize`

After every file is in R2, finalize:

```http
POST /api/v1/developer/apps/{app_id}/versions/{version_id}/bundle/finalize
```

The backend runs:

1. `HEAD` each R2 object — confirms it exists.
2. Re-checks `byte_size` and (if R2 returned `x-amz-checksum-sha256`) the `sha256`.
3. Confirms `manifest.ui.bundle.entry` is present in the uploaded set.
4. Marks `status = bundle_ready` and stamps `finalized_at`.

Failure modes:

| HTTP / payload | Meaning |
|---|---|
| `409 bundle_already_finalized` | Already `bundle_ready`; nothing to do |
| `412 file_missing` (`{path}`) | File not yet uploaded to R2 |
| `412 sha256_mismatch` (`{path}`) | The R2 object's checksum disagrees with the declared `sha256`; re-upload |
| `412 entry_not_in_bundle` | `manifest.ui.bundle.entry` references a path you didn't upload |

## Step 3 — Inspect

```http
GET /api/v1/developer/apps/{app_id}/versions/{version_id}/bundle
```

Returns the full `BundleDetail`:

```jsonc
{
  "bundle_id": "01J...",
  "status": "bundle_ready",
  "total_bytes": 102109,
  "file_count": 3,
  "finalized_at": "2026-04-28T08:14:29Z",
  "files": [
    { "relative_path": "index.html", "byte_size": 8421, "sha256": "ab12...", "content_type": "text/html" },
    …
  ]
}
```

## Step 4 — Publish the version

Only after `status == bundle_ready` may you publish. The `open_app_view` runtime call refuses to mount a window when the version's bundle is not ready (returns `bundle_not_ready`). Publishing flow itself is unchanged: see [Publishing an app](/developers/apps/app-publish).

## How assets are served at runtime

```
GET /anna-apps/{slug}/{version}/{relative_path}

Response headers:
  Content-Type: <declared>
  Content-Security-Policy: <built from manifest.ui.csp_overrides + external_origins>
  X-Content-Type-Options: nosniff
  Cross-Origin-Resource-Policy: same-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  ETag: "<sha256>"
  Cache-Control: public, max-age=31536000, immutable
```

Two extra rules apply to the entry HTML:

- The runtime requires `Sec-Fetch-Dest: iframe` on requests for the entry HTML when the header is sent (modern browsers always send it). Direct top-level navigations to the bundle URL are rejected with `403 must_be_iframed`.
- The bundle URL embeds **no authentication** — the iframe uses query params `?wid=<window_uuid>&t=<jwt>` to bootstrap, then upgrades to `postMessage` RPC.

## Local development tips

- Keep the file count low (`<200`) — every file is a separate R2 object.
- Pre-compute `sha256` with whatever your build system supports (`shasum -a 256 <file>`). The backend uses these to ETag responses.
- Reuse the same `entry` filename across versions to keep deep-links (`#/route`) stable; the version is part of the URL anyway.
- If you must skip Anna and serve directly during local dev, point the `<iframe>` at your localhost — but you lose the per-bundle CSP guarantees and the SDK will refuse `connect()` because the JWT is bound to the deployed `version_id`.

Next: [App UI SDK](/developers/apps/app-ui-sdk).


---

---
title: App UI Windows
description: Window lifecycle, geometry persistence, multi-tab/device sync, dock, single-instance dedup.
section: apps
slug: app-ui-windows
updated: 2026-04-28
estimated_minutes: 5
category: App UI
---

Each Anna App UI window is a row in `anna_app_window_sessions`. The frontend treats every window as ephemeral DOM; **all** durable state lives server-side.

## Lifecycle

```
                          ┌──── REST: POST /runtime/windows ────┐
LLM (open_app_view) ─────►│                                     │
User (deck click)  ─────► │  status = active                    │
SSE: open_view             │  geometry = view.default_size      │
                          │  entry_payload = caller-supplied    │
                          │  runtime_state = {} or persisted    │
                          └──────────────┬──────────────────────┘
                                         │  Window Manager mounts <iframe>
                                         ▼
                                    ┌──────────┐
                              ┌────►│ active   │── user click "—" ──► minimized
                              │     └────┬─────┘                          │
                              │          │ user closes ×                  │
                              │          ▼                                │
                              │     ┌──────────┐                          │
                              │     │ closed   │◄─── close_app_view ──────┘
                              │     └──────────┘
                              │ iframe crash / report_error
                              │          │
                              │          ▼
                              │     ┌──────────┐
                              └─────│ crashed  │
                                    └──────────┘
```

Status values (`AnnaAppWindowStatus`):

- `active` — currently mounted (or eligible to mount on hydrate).
- `minimized` — collapsed to dock; iframe unmounted, state preserved.
- `closed` — terminal; will not rehydrate.
- `crashed` — terminal; LLM is informed and may re-open.

## Endpoints

All under `/api/v1/anna-apps/runtime/`:

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/windows` | Open a window (LLM and deck both go through this) |
| `GET` | `/windows?conversation_session_uuid=…` | List active+minimized windows for the current conversation (used at hydrate) |
| `GET` | `/windows/{wid}` | Window detail incl. fresh JWT, sdk_url, bundle_url, runtime_state |
| `PATCH` | `/windows/{wid}` | Patch geometry / status / title / runtime_state (debounced 250 ms by frontend) |
| `DELETE` | `/windows/{wid}` | Close the window |
| `POST` | `/windows/{wid}/flush` | `navigator.sendBeacon`-friendly flush of `runtime_state` |
| `POST` | `/rpc` | Iframe → host RPC (see [Host API](/developers/apps/app-ui-host-api)) |
| `GET` | `/events/stream` | Server-Sent Events on the per-user channel |

Every PATCH and DELETE re-broadcasts a `data_model/AnnaAppEvent` over SSE so other tabs/devices stay in sync.

## Geometry & resize

```jsonc
"geometry": {
  "x": 240, "y": 120,
  "w": 960, "h": 640,
  "monitor_w": 1920, "monitor_h": 1080,
  "dock_pinned": false,
  "dock_side": null,    // "left" | "right" | "bottom" | null
  "snapped":   null     // "left" | "right" | "max" | null
}
```

- Drag/resize uses an in-memory transform for 60 fps; on `pointerup` the Window Manager `_schedulePatch`-es a `PATCH /windows/{wid} { geometry }` after a 250 ms debounce.
- The backend clamps `w`/`h` to the view's `min_size` and `max_size` (from the manifest).
- `monitor_w` / `monitor_h` are stored so a second device with a different screen can re-flow proportionally.

## Single-instance views

If a view declares `single_instance: true`, opening it again under the same `(user_id, conversation_session_uuid, app_id, view)` re-focuses the existing window and merges the new payload into `entry_payload`. Otherwise a fresh window is spawned.

## `runtime_state`

A 256 KB JSON blob, set via `storage.set` from inside the iframe. Use it for tiny UI state (current tab, open accordions, scroll position). For anything larger, store the blob in your own backend / artifact and put only a handle here.

```jsonc
"runtime_state": {
  "draft": { "title": "…", "body": "…" },
  "selectedTab": "preview"
}
```

`PATCH /windows/{wid} { runtime_state_patch }` is shallow-merged with the current `runtime_state` (last-writer-wins). To do a full replacement use `replace_runtime_state` (admin only) or `storage.delete` + re-set.

## Cross-tab / cross-device sync

Server-Sent Events on `GET /runtime/events/stream` carry envelopes of type `data_model/AnnaAppEvent`:

```jsonc
{
  "type": "data_model/AnnaAppEvent",
  "kind": "geometry_changed",     // see table below
  "window_uuid": "…",
  "app_id": "…",
  "version_id": "…",
  "conversation_session_uuid": "…",
  "by_client_id": "…",            // the client that originated the change; suppress local echo
  "ts": 1714291200,
  "payload": { … }                // kind-specific
}
```

Event kinds:

| `kind` | Payload |
|---|---|
| `artifact_appended` | `{ artifact_id, kind, summary?, payload?, payload_ref? }` *(app appended a chat artifact)* |
| `chat_message_from_app` | `{ role, content }` *(app posted into the conversation)* |
| `close_view` | `{ window_uuid, reason? }` |
| `geometry_changed` | `{ geometry }` |
| `open_view` | `{ window_uuid, app_id, version_id, view, entry_payload, geometry, runtime_state, source }` |
| `ping` | `{}` *(keepalive)* |
| `rpc.stream` | `{ … }` *(streaming RPC chunk — e.g. agent run frames)* |
| `runtime_state_synced` | `{ runtime_state }` *(only on full sync; patches are not broadcast to keep traffic small)* |
| `status_changed` | `{ status }` |
| `title_changed` | `{ title }` |
| `window_focus_changed` | `{ window_uuid, z_index }` |

These are the canonical wire `kind`s (see [`AnnaAppEvent.json`](https://github.com/whtcjdtc2007/matrix-nexus/blob/main/packages/anna-app-schema/events/AnnaAppEvent.json)); treat any unknown `kind` as a forward-compatible addition and ignore it. `entry_payload` is **not** a wire `kind` — the SDK re-surfaces entry-payload updates (carried by `open_view`) and `runtime_state_synced` to your `anna.on(...)` callbacks.

The Window Manager applies these via `applyEvent(event)`.

## Hydration on dashboard load

On page load `AnnaAppWM.init().hydrate(conversation_session_uuid)`:

1. `GET /runtime/windows?conversation_session_uuid=…` returns every `active` and `minimized` window for the current conversation.
2. For each, the Window Manager **reuses** the existing `window_uuid`, mints no new session, and mounts an iframe at `/anna-apps/{slug}/{version}/{entry}?wid=…&t=<freshly-issued-jwt>`.
3. Minimized windows render a dock chip but no iframe until restored.

Refreshing the page does **not** create new windows. Closing a tab without the user pressing × does **not** mark the window `closed` — only an explicit user action or `close_app_view` does.

## Idle reaper

Active windows with no heartbeat or RPC for **24 h** (default) are auto-marked `closed` and broadcast `close_view`. Tune via env `ANNA_APP_WINDOW_IDLE_HOURS`.

## sendBeacon flush

On `pagehide` the Host Bridge fires `navigator.sendBeacon('/runtime/windows/{wid}/flush', JSON.stringify({ runtime_state }))` so the latest state is durable even when the user just closes the tab. The endpoint is idempotent and requires no JWT (it's auth-checked by session cookie).

Next: [App UI LLM Integration](/developers/apps/app-ui-llm).


---

---
title: App UI SDK
description: Embed the Anna App SDK in your bundle and call host APIs from inside the iframe.
section: apps
slug: app-ui-sdk
updated: 2026-04-28
estimated_minutes: 5
category: App UI
---

The Anna App SDK is a single ESM file the host serves at:

```
/static/anna-apps/_sdk/latest/index.js
```

It runs **inside your iframe**, talks to the parent window over `postMessage`, and exposes a typed runtime object you use to call the host. It is a native ES module (it `export`s `AnnaAppRuntime`; there is no `window` global), so you load it with a single `<script type="module">` + `import` — the SDK origin is automatically allow-listed in your bundle's `script-src`.

## Minimum bundle

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>My App</title>
  <link rel="stylesheet" href="./assets/app.css" />
</head>
<body>
  <main id="root">Loading…</main>
  <script type="module">
    import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";

    const anna = await AnnaAppRuntime.connect();
    document.getElementById("root").textContent =
      anna.runtimeState?.notes ?? `Hello, ${anna.viewMeta.title}!`;

    // Persist on user input (debounce yourself)
    document.addEventListener("input", e => {
      anna.storage.set({ key: "notes", value: e.target.value });
    });
  </script>
</body>
</html>
```

That's it. No bundler is required; ESM imports work because the host serves the SDK with `Content-Type: application/javascript` and the bundle CSP already allows `script-src 'self' <sdk-origin>`.

## `AnnaAppRuntime.connect()`

```ts
const anna = await AnnaAppRuntime.connect();
```

Behind the scenes:

1. Reads `wid` and `t` from the iframe URL `?wid=…&t=…`.
2. Sends a `window.hello` RPC over `postMessage` to the parent.
3. Receives `capabilities`, `view_meta`, `entry_payload`, `runtime_state`, `geometry` and resolves.
4. Starts a 10s heartbeat (`window.ready` after first hello, then `window.heartbeat`).
5. Subscribes to host events (`auth.refresh`, `entry_payload`, `runtime_state_synced`, `geometry_changed`, `close`, …) — `auth.refresh` is handled internally by replacing the bound token.

The returned object:

```ts
interface AnnaAppRuntime {
  windowUuid: string;
  appId:      string;
  versionId:  string;
  viewMeta:   { name: string; title: string; default_size: {w,h}; … };
  capabilities: { tools: string[]; chat: string[]; storage: string[]; … };

  /** Initial payload supplied by `open_app_view(payload=…)` */
  entryPayload: any;
  /** Server-persisted runtime_state from `storage.set` calls */
  runtimeState: Record<string, any>;
  /** Last known window geometry */
  geometry: { x: number; y: number; w: number; h: number; … };

  // Namespaced proxies — every method returns a Promise<RpcResponse>
  tools:    { list(): Promise<…>; invoke(args): Promise<…> };
  chat:     { append_artifact(args): Promise<…> /* …stubs… */ };
  storage:  { get(args): Promise<…>; set(args): Promise<…>; delete(args): Promise<…> };
  artifact: { /* stubs, see Host API */ };
  llm:      { /* stubs, see Host API */ };
  fs:       { /* stubs, see Host API */ };
  prefs:    { /* stubs, see Host API */ };
  window: {
    set_title({ title }):    Promise<…>;
    resize({ w, h }):        Promise<…>;
    focus():                 Promise<…>;
    close({ reason? }):      Promise<…>;
    open_view({ view, payload? }): Promise<…>;
    report_error({ message, stack? }): Promise<…>;
  };

  // Event subscription
  on(event:
       | "entry_payload"
       | "runtime_state_synced"
       | "geometry_changed"
       | "title_changed"
       | "close",
     handler: (payload: any) => void
    ): () => void;  // returns unsubscribe
}
```

Every namespace proxy is generated dynamically from `capabilities` returned by `window.hello`. If your manifest does not list `chat.append_artifact`, calling `anna.chat.append_artifact(...)` from inside the iframe will throw `permission_denied` — you cannot escalate from the client.

## Resume vs first open

The host calls your iframe with two bundles of state:

| Field | Source | Purpose |
|---|---|---|
| `entry_payload` | `open_app_view(payload=…)` and `update_app_view(runtime_state_patch=…)` | Per-call instructions from the LLM (or the user via the deck) |
| `runtime_state` | `storage.set` calls from prior sessions | Your own persisted UI state (≤256 KB total) |

Recommended pattern:

```js
const anna = await AnnaAppRuntime.connect();

if (anna.runtimeState?.bootedOnce) {
  // Resume: rebuild UI from runtime_state, then merge any new entry_payload
  hydrateFrom(anna.runtimeState);
  if (anna.entryPayload) applyAdditionalInstruction(anna.entryPayload);
} else {
  // First open: drive UI from entry_payload alone
  bootstrapFrom(anna.entryPayload);
  await anna.storage.set({ key: "bootedOnce", value: true });
}

anna.on("entry_payload", payload => {
  // LLM pushed new instructions via update_app_view
  applyAdditionalInstruction(payload);
});

anna.on("runtime_state_synced", state => {
  // Another tab/device updated runtime_state
  hydrateFrom(state);
});
```

## Storing state

`storage.set` writes into `anna_app_window_sessions.runtime_state` (JSON, max 256 KB). Use it as a tiny key-value store. For larger objects, persist them to your own backend or to an artifact and store only a handle in `runtime_state`.

```js
await anna.storage.set({ key: "draft", value: { title, body } });
const { value } = await anna.storage.get({ key: "draft" });
await anna.storage.delete({ key: "draft" });

// Enumerate keys (paginated, returns the APS list shape):
const { items, next_cursor } = await anna.storage.list({
  prefix: "draft/",
  limit: 100,
});
```

The host debounces the underlying disk write; concurrent calls are coalesced. On tab close the host page emits a `navigator.sendBeacon` flush to `POST /runtime/windows/{wid}/flush` so the latest state is durable even when the user just closes the tab.

## Calling Executas

```js
const { result } = await anna.tools.invoke({
  tool_id: "tool-yourhandle-browser-abcd1234",
  method:  "page.fetch",   // required when tool_id is mint-only (no fixed plugin namespace)
  args:    { url: "https://example.com" }
});
```

The host resolves the `tool_id` against `(plugin_name, tool_name)` from the Executa registry, then invokes the Executa over NATS on the user's currently-online Anna Agent. If no agent is online you get `agent_unavailable`.

If you supplied a per-Executa allow-list in `host_api.tools` (e.g. `["required:tool-yourhandle-browser-abcd1234"]`), only those `tool_id`s can be invoked.

## Title, resize, close

```js
await anna.window.set_title({ title: "Editing report.md" });
await anna.window.resize({ w: 1024, h: 768 });
await anna.window.close({ reason: "user_done" });
```

`window.*` is always allowed — no permission required.

## Errors

Every RPC returns a Promise that resolves with a structured response:

```ts
{ ok: true,  result: any }
{ ok: false, error: { code: string; message: string; details?: any } }
```

Common codes:

| Code | Meaning |
|---|---|
| `invalid_token` | JWT expired or wrong window — the SDK auto-refreshes most cases |
| `permission_denied` | `(ns, method)` not in `host_api`, or referenced `tool_id` not in allow-list |
| `invalid_arg` | Schema mismatch on RPC args |
| `not_found` | Window already closed; storage key missing; etc. |
| `agent_unavailable` | `tools.invoke` could not reach the user's Anna Agent |
| `bundle_not_ready` | (At `open_app_view` time) the version's bundle is still `draft` |
| `rate_limited` | Too many RPCs in flight |

Full namespace × method matrix and current implementation status: [App UI Host API](/developers/apps/app-ui-host-api).


---

---
title: App UI Host API
description: RPC namespaces and methods your iframe can call on the host, with current implementation status.
section: apps
slug: app-ui-host-api
updated: 2026-04-28
estimated_minutes: 6
category: App UI
---

Every call from your iframe goes through `postMessage → Host Bridge → POST /api/v1/anna-apps/runtime/rpc → anna_app_rpc_dispatcher.dispatch`. The dispatcher does three things in order:

1. **Auth.** `decode_window_token(t)` against the JWT bound to `(window_uuid, user_id, app_id, version_id, scopes)` (TTL 120s, audience `anna-app-window`).
2. **ACL.** `host_api_allows(manifest, ns, method)` checks `manifest.ui.host_api[ns]` (with `*` and `<id>` wildcards). `window.*` is always allowed.
3. **Permissions.** Top-level `permissions` are checked for write/append actions (e.g. `chat.write_message` requires `chat.write_message`).

Then it dispatches to the namespace handler. Any failure returns `{ ok: false, error: { code, message, details? } }`.

## RPC envelope

```jsonc
// Request (sent via postMessage; Host Bridge forwards to backend)
{
  "id":          "<correlation>",
  "window_uuid": "<wid>",
  "ns":          "<namespace>",
  "method":      "<method>",
  "args":        { … }
}

// Response
{
  "id": "<correlation>",
  "ok": true,
  "result": { … }
}
// or
{
  "id": "<correlation>",
  "ok": false,
  "error": { "code": "permission_denied", "message": "…", "details": {…} }
}
```

The SDK wraps this for you — see [App UI SDK](/developers/apps/app-ui-sdk).

## Namespaces

Status legend:
- ✅ implemented
- ⏳ stub (defined; returns `not_implemented`)

### `window` *(always granted)*

| method | status | args | result |
|---|---|---|---|
| `hello` | ✅ | `{ client_info? }` | `{ window_uuid, app_id, version_id, view_meta, capabilities, entry_payload, runtime_state, geometry }` — sent automatically by SDK |
| `ready` | ✅ | `{}` | `{}` — emitted after first paint |
| `heartbeat` | ✅ | `{}` | `{}` — every 10 s |
| `set_title` | ✅ | `{ title: string (1..120) }` | `{}` — broadcasts SSE `title_changed` |
| `resize` | ✅ | `{ w, h }` (clamped to view min/max) | `{ w, h }` — persists geometry |
| `focus` | ✅ | `{}` | `{}` — bumps z-index, broadcasts SSE `window_focus_changed` |
| `close` | ✅ | `{ reason?: string }` | `{}` — sets `status=closed`, broadcasts SSE `close_view` |
| `open_view` | ✅ | `{ view: string, payload?: any }` | `{ window_uuid }` — opens (or focuses) another view of the same app |
| `report_error` | ✅ | `{ message, stack?, context? }` | `{}` — logged server-side as `crashed` if fatal |

### `tools`

| method | status | args | result |
|---|---|---|---|
| `list` | ✅ | `{}` | `{ tools: [{ tool_id, plugin_name, tool_name, description, input_schema }] }` filtered to your `host_api.tools` allow-list |
| `invoke` | ✅ | `{ tool_id, method?, args, timeoutMs? }` | `{ result }` — routes via NATS to the user's online Anna Agent |

`host_api.tools` is an **optional narrowing** allow-list. When omitted (or empty), the window may invoke **any** `tool_id` declared in `required_executas` / `optional_executas`. Provide explicit refs (e.g. `["required:bundled:foo"]`, `["required:*"]`) only when a window should reach a *subset* of the app's declared executas. Prefer `required:*` over pinning a concrete `tool_id`, since bundled handles are rewritten to concrete ids at publish/dev time and a pinned id will drift.

`method` is **required** when `tool_id` was minted ad-hoc (`tool-{handle}-{slug}-{uniq}` form). For Executas with a registered `(plugin_name, tool_name)`, the dispatcher resolves it from the catalogue and `method` is optional.

#### Per-call timeout (`timeoutMs`)

`tools.invoke` accepts an optional `timeoutMs` integer that bounds the host wait for a single call:

| Bound | Value | Source |
|---|---|---|
| Hard minimum | `1000` ms | `InvokeTimeoutPolicy.min_ms` |
| Hard maximum | `180000` ms | `InvokeTimeoutPolicy.max_ms` |
| Default (omitted or `null`) | `65000` ms | `InvokeTimeoutPolicy.default_ms` (fallback: manifest `tool.timeout`) |
| Host grace | `+2000` ms | added to the plugin-facing deadline so cancel/ack can land |

Values below `min_ms` are rejected with `invalid_arg`; values above `max_ms` are clamped silently. The clamped value is forwarded to the matrix Agent as `params.timeout`, and a wall-clock `params.deadline_ms` is propagated to the plugin so reverse-RPC subcalls (storage / image / upload) can size their own waits via the SDK's `ctx.remaining_s()` (Python) / `ctx.remainingS()` (Node) helpers.

When the host wait elapses the call rejects with:

| Code | Meaning |
|---|---|
| `tool_timeout` | The plugin did not return a response within the (clamped) `timeoutMs` window. The host also publishes a best-effort cancel signal on `matrix.cancel.{client_id}` so the Agent can stop the in-flight invocation. |
| `subcall_timeout` | A reverse-RPC subcall (storage/image/upload) timed out while the outer `tools.invoke` was still within its deadline. Same wire shape, but `error.details.subcall` identifies the channel. |

Example:

```ts
import { AnnaAppRuntime } from "/static/anna-apps/_sdk/latest/index.js";

const anna = await AnnaAppRuntime.connect();
try {
  const { result } = await anna.tools.invoke({
    tool_id: "tool-acme-summarize",
    args: { text },
    timeoutMs: 30_000,
  });
  render(result);
} catch (err) {
  if (err.code === "tool_timeout") {
    showRetryBanner("The tool took too long — try a shorter input.");
  } else {
    throw err;
  }
}
```

### `chat`

| method | status | args | result |
|---|---|---|---|
| `append_artifact` | ✅ | `{ kind: "app_event"\|"text"\|"image"\|…, summary?, payload?, payload_ref? }` | `{ artifact_id }` — attaches a card to the current conversation |
| `read_history` | ⏳ | `{ limit?, before? }` | future |
| `write_message` | ⏳ | `{ role, content }` | future |

### `storage` (per-window `runtime_state`, or APS in nexus)

In the local-dev harness (`anna-app dev`) these handlers operate on the
window's 256 KB `runtime_state` blob. In production matrix-nexus they are
overridden at startup to talk to **Anna Persistent Storage (APS)** —
`scope='app'`, `owner_id=window.app_id` — so values are durable across
window lifetimes.

| method | status | args | result |
|---|---|---|---|
| `get` | ✅ | `{ key }` | `{ value, etag?, generation?, exists? }` |
| `set` | ✅ | `{ key, value, if_match?, metadata?, tags?, ttl_seconds? }` | `{ ok: true }` (runtime_state) or `{ etag, generation, size_bytes }` (APS) |
| `delete` | ✅ | `{ key, if_match? }` | `{ ok: true }` / `{ deleted: true }` |
| `list` | ✅ | `{ prefix?, cursor?, limit?=100 }` | `{ items: [{ key, etag, size_bytes, metadata, tags, updated_at }], next_cursor }` |

`list` always returns the APS shape; the runtime_state backend fills
`metadata`/`tags`/`updated_at` with `null` and synthesises a weak
`W/"1-<digest>"` etag from the value. `if_match` lets `set` and `delete`
fail with `precondition_failed` instead of silently clobbering a
concurrent write.

### `agent`

Multi-turn, tool-using agent sessions bound to the user's quota. See
[LLM & Agent](/developers/apps/llm-and-agent) for the streaming frame shape.
The ACL is **structured** (`host_api.agent = { session: { auto, fixed }, tools: [...] }`),
not a flat method list — a session is granted when at least one submode
(`auto` / `fixed`) is enabled.

| method | status | args | result |
|---|---|---|---|
| `session.create` | ✅ | `{ submode: "auto"\|"fixed", fixed_client_id? }` | `{ app_session_uuid, … }` — mints an `app_session_token` (one per submode per window) |
| `session.run` | ✅ | `{ content, allowed_tools? }` | streaming frames (see [LLM & Agent](/developers/apps/llm-and-agent)) |
| `session.cancel` | ✅ | `{ run_id }` | `{}` |
| `session.history` | ✅ | `{ limit?, before? }` | `{ messages: […] }` |
| `session.list` | ✅ | `{ include_expired? }` | `{ sessions: […] }` |
| `session.delete` | ✅ | `{}` | `{ deleted: true }` |
| `session.refresh` | ✅ | `{}` | `{ … }` — re-mints the session token before expiry |

### `image`

Host-mediated image generation / editing — no provider key in the bundle.
Gated by `host_api.image` (method surface) **plus** the per-app
`image_grant` enforced inside the facade.

| method | status | args | result |
|---|---|---|---|
| `generate` | ✅ | `{ prompt, n?, size?, model_hint? }` | `{ images: [{ url, … }] }` |
| `edit` | ✅ | `{ prompt, image_ref, n?, size? }` | `{ images: [{ url, … }] }` |

### `upload`

Invoke-scoped, transient artifact upload to host R2. Gated by
`host_api.upload` (method surface) **plus** the per-app `upload_grant`.

| method | status | args | result |
|---|---|---|---|
| `inline` | ✅ | `{ bytes_b64, mime, purpose, filename? }` | `{ file_ref, url }` |
| `negotiate` | ✅ | `{ mime, purpose, size_bytes }` | `{ upload_url, file_ref }` |
| `confirm` | ✅ | `{ file_ref }` | `{ url, … }` |

### `artifact`, `llm`, `fs`, `prefs`

All declared in the dispatcher but stubbed today (`not_implemented`). Plan for Phase 3:

- `artifact.create` / `update` / `delete`
- `llm.complete` (host-side completion bound to the user's quota)
- `fs.read` / `fs.write` (R2-backed workspace, mirrors the Anna Agent FS)
- `prefs.get` (read user preference keys)

## Permissions matrix

`permissions` (top-level on the manifest) acts as a coarse capability gate; `ui.host_api` is the fine-grained ACL. Both are checked.

| Permission | Required for |
|---|---|
| `tools.invoke` | `tools.invoke` |
| `chat.read` | `chat.read_history` |
| `chat.write_message` | `chat.write_message` |
| `chat.append_artifact` | `chat.append_artifact` |
| `artifact.create` / `update` / `delete` | matching `artifact.*` calls |
| `llm.complete` | `llm.complete` |
| `fs.read` / `fs.write` | matching `fs.*` calls |
| `storage.read` | `storage.get`, `storage.list` |
| `storage.write` | `storage.set`, `storage.delete` |
| `prefs.read` | `prefs.get` |
| `ui.svg` | rendering inline SVG inside chat artifacts your app appends |

`agent.session.*`, `image.*`, and `upload.*` are gated by their
`ui.host_api.{agent,image,upload}` entries (the method-level surface) **plus**
the per-app grant enforced inside the facade (`image_grant` / `upload_grant`,
and for agent the user's session quota) — not by a coarse top-level
`permissions` verb.

Anything not declared is rejected with `permission_denied` before reaching the handler.

## Error codes

| Code | When |
|---|---|
| `invalid_token` | JWT expired, signature mismatch, or `wid` does not match `window_uuid` |
| `permission_denied` | `(ns, method)` not in `host_api`, missing top-level permission, or `tool_id` not in `host_api.tools` allow-list |
| `invalid_arg` | Pydantic validation failure on `args` |
| `not_found` | window closed; storage key missing |
| `agent_unavailable` | `tools.invoke` could not route to the user's Anna Agent (no NATS listener) |
| `executa_error` | Executa returned a non-zero error |
| `tool_timeout` | `tools.invoke` exceeded the per-call `timeoutMs` (clamped by `InvokeTimeoutPolicy`); host emitted a best-effort cancel on `matrix.cancel.{client_id}` |
| `subcall_timeout` | A reverse-RPC subcall (storage / image / upload) timed out while the outer `tools.invoke` was still alive; `details.subcall` names the channel |
| `bundle_not_ready` | Returned by `open_view` if the target version's bundle is still `draft` |
| `rate_limited` | Too many in-flight RPCs (per-window cap) |
| `state_too_large` | `storage.set` / runtime_state would exceed 256 KB |
| `not_implemented` | Method exists in the contract but is still a stub |
| `internal_error` | Unhandled server exception (logged) |

For the LLM-facing side of the same surface (`open_app_view` etc.), see [App UI LLM Integration](/developers/apps/app-ui-llm).


---

---
title: App UI LLM Integration
description: How the assistant summons, updates, and closes your app windows via LangChain tools and SSE events.
section: apps
slug: app-ui-llm
updated: 2026-04-28
estimated_minutes: 4
category: App UI
---

When the user `#`mentions a `schema: 2` app whose manifest contains `ui.views`, three LangChain tools are auto-injected into the assistant's tool list for that turn:

| Tool | Purpose |
|---|---|
| `open_app_view(app_id, view?, payload?)` | Summon (or focus) a window |
| `update_app_view(window_uuid, title?, geometry?, runtime_state_patch?)` | Push state into an existing window |
| `close_app_view(window_uuid, reason?)` | Close a window |

The tools are **only** injected when at least one mentioned app actually has UI views — schema-1 apps don't pollute the tool list.

## Prompt injection

When the user mentions an app with UI views, the system prompt grows a block:

```xml
<user_mentioned_apps>
  <app slug="research-suite" name="Research Suite" version="0.4.1">
    <tagline>Plan, capture, and summarise web research.</tagline>
    <system_prompt_addendum>
      When the user asks to research, summon the workspace via
      open_app_view('research-suite').
    </system_prompt_addendum>
    <bundled_executas>
      <executa tool_id="tool-yourhandle-browser-…" />
    </bundled_executas>
    <ui_views>
      <view name="main"          title="Research Workspace" default="true"
            summary_template="Research session: {topic}" />
      <view name="chart_preview" title="Chart Preview" />
    </ui_views>
  </app>
</user_mentioned_apps>
```

The `<ui_views>` block tells the model exactly which `view` names are valid arguments to `open_app_view`.

## Tools in detail

### `open_app_view(app_id, view?, payload?)`

```python
open_app_view(
    app_id="research-suite",
    view="main",                       # omitted → default view
    payload={"topic": "ECM-related immune evasion"}
)
```

- Resolves the user's installed version of the app.
- If the version's UI bundle is not `bundle_ready`, returns `bundle_not_ready`.
- If `single_instance: true` and a window already exists, focuses it and merges `payload` into `entry_payload`.
- Otherwise creates a new `AnnaAppWindowSession`, mints a JWT, and broadcasts SSE `open_view`.
- Returns `{ window_uuid, status: "active", entry_payload, geometry }`.

### `update_app_view(window_uuid, ...)`

```python
update_app_view(
    window_uuid="…",
    title="Research: ECM evasion",
    runtime_state_patch={"progress": 0.6}
)
```

- Patches geometry/title/runtime_state shallow-merged with current values.
- A `runtime_state_patch` triggers an SSE `runtime_state_synced` after the merge.
- Setting only `title` triggers `title_changed`.
- Use this to stream progress from a long-running tool call into the window.

### `close_app_view(window_uuid, reason?)`

```python
close_app_view(window_uuid="…", reason="task_done")
```

- Sets `status = closed`; broadcasts `close_view`.
- Idempotent.

## Recommended chat ↔ window pattern

```
User:    @research-suite please dig into ECM-related immune evasion.

LLM →    open_app_view(app_id="research-suite", payload={"topic": "ECM"})
         (Window appears.)

LLM →    chat.append_artifact (from inside the iframe, NOT a tool the LLM calls)
         {"kind": "app_event", "summary": "Started research on ECM",
          "payload_ref": "windows/<wid>/runtime_state"}

iframe → tools.invoke(tool_id=browser, args={"url": "…"})
iframe → storage.set({key: "findings", value: [...]})

LLM →    update_app_view(window_uuid="…",
                         runtime_state_patch={"progress": 1.0, "status": "ready"})

LLM:     "I summarised five papers in the workspace — open it to read."
```

The iframe should **always** post a chat artifact when it produces something the user might want to refer back to (a finding, a chart, a draft). The `chat.append_artifact` call goes through the host RPC; the artifact card appears in the chat scrollback even after the window is closed.

## Full SSE event stream

`GET /api/v1/anna-apps/runtime/events/stream` (cookie-authenticated). Events are framed as standard SSE:

```
event: data_model.AnnaAppEvent
data: {"type":"data_model/AnnaAppEvent","kind":"open_view", … }

```

Kinds and payloads are listed in [App UI Windows](/developers/apps/app-ui-windows#cross-tab--cross-device-sync). Both your iframe (via the SDK) and other dashboard tabs subscribe to the same stream — that is how multi-device coherence works without you doing anything.

## Failure modes the assistant should know about

When `open_app_view` fails, the tool returns a structured error the model can reason about:

| `error.code` | What to tell the user |
|---|---|
| `app_not_installed` | Suggest installing it from the App Store |
| `bundle_not_ready` | The developer hasn't finalised the bundle for this version — the model should not retry |
| `version_not_published` | Same as above |
| `agent_unavailable` | The user's Anna Agent is offline; the window opens but tool calls inside will fail |
| `quota_exceeded` | Too many active windows for the user (rare) |

For developer-side and iframe-side errors, see [App UI Host API → Error codes](/developers/apps/app-ui-host-api#error-codes).


---

---
title: App-Side LLM & Agent API
description: Call llm.complete and run a multi-turn agent session from inside your bundled app.
section: apps
slug: llm-and-agent
updated: 2026-06-07
estimated_minutes: 8
category: App UI
---

> **Audience:** app authors who want their bundled iframe / SPA to call
> the LLM (`anna.llm.complete`) or run a stateful tool-using agent
> (`anna.agent.session(...)`) from JavaScript.
>
> **Companion:** [Local dev with --llm](local-dev-llm.md) explains how to
> wire a developer PAT so these APIs work outside the desktop client.

This page covers what runs **inside the iframe**. For the auto-injected
UI orchestration tools (`open_app_view` / `update_app_view`), see
[App UI LLM Integration](app-ui-llm.md) — that's a separate, host-side
mechanism and does not require any host_api grant.

---

## 1. Manifest grants

The host enforces ACL by `manifest.ui.host_api`. Two independent grants:

```json
{
  "ui": {
    "bundle": { "entry": "index.html" },
    "views": [{ "name": "main", "default": true }],
    "host_api": {
      "llm": ["complete"],
      "agent": {
        "session": { "auto": true, "fixed": null },
        "tools":   ["tool-yourhandle-search-..."]
      }
    }
  }
}
```

| Field | Effect |
|---|---|
| `llm: ["complete"]` | Allows `anna.llm.complete(...)` from the iframe |
| `agent.session.auto: true` | Allows `anna.agent.session({ submode: "auto" })` |
| `agent.session.fixed: { client_ids: ["..."] }` | Allows `submode: "fixed"` with a pinned executa client_id |
| `agent.tools` | Subset of executa tool ids the agent may invoke |

If neither `auto` nor `fixed` is set, **all** `agent.session.*` calls
return `permission_denied` regardless of namespace.

---

## 2. `anna.llm.complete(req)` — single shot

Stateless completion. Counts against the user's quota; uses the user's
default model.

```js
const reply = await window.anna.llm.complete({
  messages: [
    { role: "user", content: { type: "text", text: "Say hi" } },
  ],
  maxTokens: 256,
});
console.log(reply.role, reply.content.text, reply.usage.totalTokens);
```

Response shape:

```ts
{
  role: "assistant",
  content: { type: "text", text: string },
  model: string,
  stopReason: "endTurn" | "stopSequence" | "maxTokens",
  usage: { inputTokens: number, outputTokens: number, totalTokens: number },
}
```

**Errors** are thrown as `HostRpcError`:

| `error.code` | When |
|---|---|
| `permission_denied` | Manifest doesn't include `llm: ["complete"]` |
| `not_implemented` | Host runtime didn't wire this method (e.g. local harness with `--no-llm`) |
| `quota_exceeded` | User has hit their daily/per-app cap |
| `invalid_arg` | Missing/empty `messages`, bad role, etc. |

---

## 3. `anna.agent.session(...)` — multi-turn tool-using agent

A **session** holds memory + access to a curated set of executa tools.
Ideal for chat-like UX or research workflows.

```js
// 1. Create (mints app_session_token; one per submode per window).
const sess = await window.anna.agent.session({
  submode: "auto",            // host picks the best tool list
  // submode: "fixed", fixed_client_id: "desktop-main"  // pin to one executa
});

// 2. Run a turn — returns a stream you can iterate.
const stream = sess.run({ content: "Find me 3 lunch options nearby" });
for await (const frame of stream) {
  // Status frames carry frame.event ∈ "queued" | "started" | "keepalive"
  //   | "run_meta" | "error" | "end". Token frames are tagged
  //   frame.event === "sse" and carry an OpenAI-style chunk.
  if (frame.event === "sse") {
    const delta = frame.choices?.[0]?.delta;
    if (delta?.content) render(delta.content);          // streamed token text
    // Final usage arrives at delta.task_complete.token_usage.
  }
  if (frame.event === "end") break;   // terminal { event: "end", run_id }, done=true
}

// 3. Optional: history, cancel, delete, list, refresh.
const past = await sess.history();
await sess.cancel(stream.runId);
await sess.delete();
```

The `session({...})` result also carries lifecycle metadata so you can
schedule work around the session's deadlines:

```js
const sess = await window.anna.agent.session({ submode: "auto" });
sess.expiresAt;        // ISO-8601 — the authoritative idle deadline
sess.maxLifetimeAt;    // ISO-8601 — the absolute cap (created_at + max lifetime)
sess.idleTtlSeconds;   // e.g. 1800 — how long the window slides on each activity
sess.appSessionUuid;   // persist THIS (not the token) to resume later
```

### 3.0 Session lifetime — sliding idle window

A session is alive while **both** hold:

1. **Idle window**: it has been active within the last `idleTtlSeconds`
   (agent: 30 min, complete: 15 min by default). Every `run()` slides the
   window forward.
2. **Hard cap**: it is younger than its absolute max lifetime (agent: 24 h,
   complete: 1 h by default). Activity cannot extend a session past this.

`expiresAt = min(now + idleTtl, createdAt + maxLifetime)`.

When a session crosses either deadline it is **expired**. Expired sessions
no longer count toward your concurrency/quota (the host reaps them
automatically — see §4), and any call referencing one fails with
`APP_SESSION_EXPIRED` (HTTP 410). Create a fresh session to continue.

### 3.05 Resume by uuid (survives reloads & restarts)

Persist `appSessionUuid` (NOT the token — tokens are short-lived and
re-minted on demand). On an iframe reload or a CLI restart, hand the uuid
back to any session operation and the host re-mints a fresh token straight
from the live session row — no stale token required:

```js
// after a reload, the app remembers only the uuid
await window.anna.agent.refresh({ app_session_uuid: saved.uuid });
// → { app_session_uuid, expires_in, expires_at, max_lifetime_at, ... }
// or just call run/cancel/delete with the uuid — they self-heal the token.
```

`refresh` both re-mints the token AND slides the idle window. Use it
proactively (e.g. on a timer at ~80% of `idleTtlSeconds`) to keep a session
warm during long idle periods, or reactively on resume. It fails with
`APP_SESSION_EXPIRED` / `APP_SESSION_REVOKED` only when the underlying
session is genuinely gone.

### 3.06 Enumerate & recover sessions

`anna.agent.list({ include_expired?, limit? })` returns the sessions this
app owns (scoped to your app — never another origin's), newest-first:

```js
const { sessions } = await window.anna.agent.list();
for (const s of sessions) {
  // s.app_session_uuid, s.kind, s.submode, s.expires_at, s.max_lifetime_at, ...
}
```

Use it to rebuild UI after losing in-memory handles (multi-tab, reload), or
to clean up leftovers via `refresh`/`delete`.


### 3.1 Each create is a distinct session

Calling `session({ submode, fixed_client_id })` returns a **new**
`app_session_uuid` every time — there is no idempotency collapsing. Two
concurrent `auto` sessions from the same window are two real sessions, which
is what multi-pane / parallel-research UIs need.

If you want to *reuse* a session across re-mounts or reloads, persist its
`appSessionUuid` and resume it via `refresh` (§3.05) — don't rely on
create-time dedupe. Keep your own handle and `delete()` (or let it idle out)
when finished so you don't accumulate sessions.

### 3.2 Stream framing

Each `stream.run()` allocates a `stream_id` (`strm_…`). The host emits
`rpc.stream` events with monotonically increasing `seq` numbers; the SDK
reorders out-of-order frames within a 256-frame buffer. You should **not**
need to deal with this directly — the `for await` loop yields frames in
order and ends after the `done: true` frame.

### 3.3 Concurrency

There is no fixed per-window session cap — create as many concurrent
sessions as your workflow needs. Usage is bounded by your account's quota
(`quota_caps` on each session) rather than a hard count. **Expired sessions
do not count** toward usage: the idle reaper (§4) revokes them, so a session
you forgot to `delete()` frees its slot once it crosses the idle deadline.


---

## 4. Cancellation & cleanup

| Action | Effect |
|---|---|
| `sess.cancel(runId)` | Aborts the in-flight turn; emits a final `complete` frame with `aborted: true` |
| `sess.delete()` | Revokes the `AnnaAppSession` row, frees the concurrency/quota slot. **Works even on an expired session** — release is identity-authed, not token-authed |
| `sess.refresh()` | Re-mints the token and slides the idle window (see §3.05) |
| Idle/hard expiry | A background reaper revokes expired sessions so they stop counting toward quota — you don't have to call `delete()` for *expired* ones |
| Window close | Host auto-revokes sessions belonging to that `window_uuid` after a short grace period |

`delete()` is **token-free**: you can always release a session by its
`app_session_uuid` even after its token expired. This fixes the previous
trap where an expired session could neither be used nor deleted and kept
occupying a quota slot.

After revocation, the row lingers briefly (default 24 h) so it stays
visible/auditable in `list({ include_expired: true })`, then the reaper
hard-deletes it and its conversation checkpoint.

Still, `delete()` sessions you're done with rather than waiting for the idle
timeout — it frees the slot immediately.

---

## 5. Token lifecycle (under the hood)

1. App calls `anna.agent.session(...)` → host mints an
   `app_session_token` (JWT, audience `aps-llm`, type
   `anna_app_session`, ~10 min TTL).
2. Token includes the `app_session_uuid` and the submode/fixed grant.
3. `sess.run()` posts to `/api/v1/copilot/app/agent` with that token.
4. The **token TTL is decoupled from the session lifetime** (§3.0). The
   token is a short-lived *capability*; the `AnnaAppSession` row is the
   durable *identity*. The runtime re-mints the token on demand — on each
   `run()`, on `refresh()`, or automatically when resuming by uuid — so the
   short token TTL never limits how long your session can live (only the
   idle window + hard cap do).

You normally don't see the token at all — it lives in the runtime, keyed by
`app_session_uuid`. Persist the **uuid**, never the token.
For local dev see [local-dev-llm.md](local-dev-llm.md).

### 5.1 Error codes

| `error.name` | code | HTTP | Meaning / what to do |
|---|---|---|---|
| `APP_SESSION_EXPIRED` | `-32017` | 410 | Session crossed its idle or hard deadline. Create a new session. |
| `APP_SESSION_TOKEN_EXPIRED` | `-32018` | 401 | The capability token lapsed but the session is alive. Call `refresh()` (or just retry — `run`/`cancel`/`delete` self-heal the token). |
| `APP_SESSION_REVOKED` | `-32011` | 410 | Session was deleted/revoked. Create a new one. |

Branch on `error.name` (the stable string), not the numeric code.

---

## 6. Quick reference

| Iframe call | Host endpoint | Manifest grant required |
|---|---|---|
| `anna.llm.complete(req)` | `POST /api/v1/copilot/app/complete` | `llm: ["complete"]` |
| `anna.agent.session({...})` | `POST /api/v1/copilot/app/sessions` | `agent.session.auto` or `.fixed` |
| `sess.run({content})` | `POST /api/v1/copilot/app/agent` (SSE) | (covered by session grant) |
| `sess.cancel(runId)` | `POST /api/v1/copilot/app/agent/cancel` | (covered) |
| `sess.refresh()` | `POST /api/v1/copilot/app/sessions/{uuid}/refresh` | (covered) |
| `sess.delete()` | `DELETE /api/v1/copilot/app/sessions/{uuid}` | (covered) |
| `anna.agent.list({...})` | `GET /api/v1/copilot/app/sessions` | (covered) |

> The iframe SDK reaches all of these over its `postMessage` → `/runtime/rpc`
> relay, so the browser never holds an `app_session_token`. The HTTP routes
> above are what the SDK / `matrix` agent / standalone executas call directly.


---

## 7. Testing locally

- Vitest harness: `mountBundle({ manifest })` with `mocks: { "llm.complete": ... }` — see
  [tests/llm-complete-mock.test.ts](https://github.com/talentai/anna-app-cli/blob/main/tests/llm-complete-mock.test.ts).
- CLI: `anna-app dev --llm real|mock|off` — see
  [local-dev-llm.md](local-dev-llm.md).

---

## 8. Plugin parity (stdio Executa plugins)

Stdio Executa plugins reach the **same** `/copilot/app/*` surface as iframe apps,
but never hold a bearer themselves. Use the `executa_sdk` Python SDK:

```python
from executa_sdk import AgentSessionClient, dispatch_message

agent = AgentSessionClient(write_frame=write_frame)

# Wire response routing — same loop you already use for SamplingClient/StorageClient
def on_msg(msg: dict) -> bool:
    return agent.dispatch_response(msg) or sampling.dispatch_response(msg)

# Inside an `invoke`:
session = await agent.create(kind="agent", agent_submode="auto", label="my plugin")
async for frame in session.run("hello world"):
    if frame["event"] == "delta":
        ...
    elif frame["event"] == "final":
        result_text = frame.get("text", "")
await session.delete()
```

Or for L1 stateless completion:

```python
res = await agent.complete(messages=[
    {"role": "user", "content": {"type": "text", "text": "Say hi."}},
], max_tokens=64)
print(res["content"]["text"])
```

**Auth model**: the matrix host injects a per-invoke `sampling_token` into the
plugin's reverse-RPC `ctx`. The host's `ExecutaAgentHandler` uses it to mint
an `app_session_token` against `POST /copilot/app/sessions/from_sampling`,
caches the token internally keyed by `(user_id, plugin_name, app_session_uuid)`,
and **never** returns it to the plugin. All subsequent `agent/session.run|cancel|delete`
calls look the cached token up by `app_session_uuid`.

**Wire format**: `agent/session.run` uses *buffered streaming* in v2 — the host
accumulates SSE frames and returns `{run_id, stream_id, frames: [...], final}`
once the run completes. The SDK iterates those frames so your code is identical
to anna-app's `agent.session().run()`. A future protocol bump will switch to
real-time push without changing the SDK API.

**Manifest**: declare `host_capabilities: ["llm.sample", "llm.agent.auto"]` in
your plugin manifest so users see exactly what they're authorizing. See the
[`executa-agent-demo` example](https://github.com/talentai/anna-executa-examples/tree/main/examples/executa-agent-demo)
for an end-to-end working plugin.

---

## 9. Related

- Design spec: `docs/design/app-llm-and-agent-access.md` (host-side details, security; plugin parity in §17).
- Auto-injected UI tools: [app-ui-llm.md](app-ui-llm.md).
- Manifest reference: [app-ui-manifest.md](app-ui-manifest.md).


---

---
title: Local Development
description: Run an Anna App locally with `anna-app dev` — in-process dispatcher, stdio executa, no nexus checkout required.
section: apps
slug: local-dev
updated: 2026-04-29
estimated_minutes: 5
category: Local Development & Testing
---

# Local Development with `anna-app dev`

`anna-app dev` boots a fully self-contained Anna App harness on your laptop:

- the **same** RPC dispatcher that ships in production (`anna-app-core`),
- an in-memory `WindowStore` (no Postgres, no NATS, no Executa Agent),
- a static-file server that loads your bundle in an iframe,
- an SSE relay so server-pushed events (`auth.refresh`, `app/method`,
  `entry_payload` updates) reach the iframe just like in production,
- a process supervisor for `executas/<name>/` that forwards `tools.invoke`
  RPCs over stdio to your plugin. Detection is language-agnostic
  (`executa.json` / `pyproject.toml` / `package.json` / `go.mod` /
  `bin/<name>`); see [Multi-language executas](https://github.com/whtcjdtc2007/anna-executa-examples/blob/main/docs/multi-language-anna-apps.md).

End users do **not** need a `matrix-nexus` checkout — the harness pulls
`anna-app-runtime-local` via `uvx` on demand (see [Runtime modes](#runtime-modes)).

## Prerequisites

- Node 22+
- `uv` (Astral) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- An app project created by `anna-app init <dir> --slug <slug>`

Run `anna-app doctor` to verify your environment before the first `dev`
session — it checks `uv`, the uvx cache, and (if you're contributing to
nexus) the in-tree runtime path.

## Quickstart

```bash
anna-app init my-focus-flow --slug focus-flow
cd my-focus-flow
anna-app dev
```

Open the URL it prints (`http://127.0.0.1:5180/dev/<wid>?t=<dev-token>` by
default). The bundle loads inside the harness iframe and can call every
host_api the manifest grants.

## CLI flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `--manifest <path>` | `manifest.json` | Manifest path (relative to `--cwd`). |
| `--bundle <dir>` | `./bundle` | Static-file root served at `/anna-apps/<slug>/dev/`. |
| `--slug <slug>` | from manifest `slug` (falls back to `name`) | Slug used in URLs and SSE topics. |
| `--view <name>` | manifest default | Open a non-default view at boot. |
| `--port <n>` | `5180` | HTTP port for the dev server. |
| `--user-id <id>` | `1` | Harness user_id (also overridable via `manifest.dev.user_id`). |
| `--no-watch` | (watcher on) | Disable bundle file watcher (LiveReload). |
| `--matrix-nexus-root <path>` | (auto) | Use an in-tree nexus checkout instead of `uvx`. |
| `--executa <spec>` *(repeatable)* | (auto-discovery) | Register an executa explicitly; spec is comma-separated `key=value` (`dir=<path>[,tool_id=<id>][,type=python\|node\|go\|binary][,command="<argv>"]`). When given, replaces auto-discovery for the run and bypasses `enabled: false` on the chosen dir. |

## Runtime modes

`anna-app dev` picks one of two modes automatically:

- **uvx (default for end users)** — runs
  `uvx anna-app-runtime-local@<PIN> anna-app-bridge`. The pin lives in
  [`anna-app-cli/src/harness/bridge.ts`](https://anna.partners/developers/apps/app-quickstart)
  (constant `PINNED_RUNTIME_VERSION`). The wheel is fetched once and
  cached under your platform's uv cache dir (see `uv tool dir`).
- **nexus-source (auto when contributing to matrix-nexus)** — runs
  `python -m anna_app_runtime_local.bridge` against the in-tree
  `packages/anna-app-runtime-local/` so contributor edits take effect
  without a publish round-trip. Triggered when:
  - `--matrix-nexus-root <path>` is passed, **or**
  - `$ANNA_NEXUS_ROOT` is set, **or**
  - the CLI auto-detects you're inside a nexus checkout.

The two modes are byte-equivalent at runtime — the dispatcher code is
the same wheel either way.

## `manifest.dev` block

The optional `dev` block lets you customise the harness without polluting
the production manifest. The production dispatcher ignores it; `anna-app
publish` strips it before upload.

```jsonc
{
  "dev": {
    "fixtures": ["fixtures/*.jsonl"],   // recordings to replay
    "seed_storage": { "theme": "dark" }, // initial runtime_state
    "user_id": 1,                       // override --user-id default
    "mocks": {                          // static responses, keyed "ns.method"
      "tools.invoke": { "success": true, "data": {} }
    }
  }
}
```

Field reference lives in
[`anna_app_core.manifest.AppDevConfig`](https://github.com/whtcjdtc2007/matrix-nexus/blob/main/packages/anna-app-core/src/anna_app_core/manifest.py).

## Live-reload

The watcher reloads the iframe whenever a file under `--bundle` changes.
Disable with `--no-watch` if your editor's autosave is too chatty.

## What's not in `dev`

- No `chat.read_history` / `chat.write_message` persistence — Phase 3 will
  proxy these through real conversation storage.
- `anna.llm.*` / `anna.agent.*` bridge to a real nexus by default (you must
  be logged in via `anna-app login`). Develop offline with `--no-llm` (calls
  return `llm_disabled`) or `--mock-llm <fixture>` (canned responses from a
  JSONL fixture).
- No real Executa NATS — `tools.invoke` calls go to the local stdio
  process spawned from `executas/<name>/`. To exercise the production
  NATS path, deploy to a staging nexus and use `anna-app dev --remote`
  (Phase 9).

## Related

- [Testing the bundle](/developers/apps/testing-bundle)
- [Testing the plugin](/developers/apps/testing-plugin)
- [Recording & replaying sessions](/developers/apps/recording-replay)


---

---
title: Local Dev with --llm (PAT setup)
description: Develop apps that call llm.complete or anna.agent.session against a real Nexus from your laptop.
section: apps
slug: local-dev-llm
updated: 2026-06-07
estimated_minutes: 6
category: App UI
---

> **Goal:** make `anna.llm.complete(...)` and `anna.agent.session(...)`
> work in `anna-app dev` without packaging the desktop app.
>
> **Non-goal:** running the host (matrix-nexus) itself locally — this
> doc assumes you connect to a remote Nexus (staging or prod) over HTTPS.

---

## 1. One-time: log in (mints a Developer PAT)

```bash
anna-app login --host https://nexus.example.com
```

What this does:

1. Starts a **device-flow login** at
   `POST /api/v1/anna-apps/dev/login/start`.
2. Opens your browser to the verification URL; you approve while
   signed in to Nexus normally.
3. Polls `/dev/login/poll` until approval; receives a long-lived JWT
   PAT (audience `aps-dev-pat`, type `anna_app_dev_pat`, default
   90-day TTL, `aps:dev` scope).
4. Atomically writes it to
   `~/.local/share/anna-app/credentials.json` (mode 600) keyed by host.

The PAT does **not** grant LLM access by itself — it only lets the CLI
mint short-lived `app_session_token`s for any app you own.

### List / revoke PATs

Web dashboard → **Developer Tokens** (`/dashboard/dev/tokens`):

- `GET /api/v1/anna-apps/dev/tokens?include_revoked=false` → list
- `POST /api/v1/anna-apps/dev/tokens/{token_id}/revoke` → 204

Revoked PATs are rejected on next mint with `401 token_revoked`. The
CLI surfaces this and asks you to re-login.

---

## 2. Run your app with `--llm real`

```bash
cd my-app
anna-app dev --llm real
```

The harness:

1. Loads the PAT for the matching host.
2. On every `anna.llm.complete` / `anna.agent.session.*` call inside
   the iframe, calls `POST /api/v1/anna-apps/dev/session/mint` with
   `{pat, kind, submode, fixed_client_id, app_id}`.
3. Caches the resulting `app_session_token` per `(window_uuid, kind)` and
   keeps it live: when a cached token is near expiry it transparently calls
   `POST /api/v1/anna-apps/dev/session/refresh` (which also slides the
   session's idle window) instead of minting a brand-new session.
4. Forwards the iframe RPC to the production endpoint
   (`/api/v1/copilot/app/...`) with the `Authorization: Bearer <token>`
   header.

Counts against your real quota and shows up in your usage dashboard.

### 2.1 Session lifecycle in dev

The harness mirrors the production session lifecycle (see
[llm-and-agent.md §3.0–§5](llm-and-agent.md)) using PAT-authed dev
endpoints, so an expired or restart-orphaned session never wedges your
loop:

| App call | Dev endpoint | Notes |
|---|---|---|
| `session.run` / `session.cancel` | (mint/refresh) → `/copilot/app/agent` | Token is auto-refreshed first; if the *session* is expired you get `APP_SESSION_EXPIRED`. |
| `session.refresh` | `POST /dev/session/refresh` | Re-mints + slides idle window. |
| `session.delete` | `POST /dev/session/revoke` | **Token-free** — releases by `app_session_uuid` even when the token is gone, so a dead session stops occupying quota. (When a live token exists the harness uses the token `DELETE` instead.) |
| `session.list` | `GET /dev/sessions?pat=…&app_slug=…` | Lists this app's sessions from the DB — lets your UI recover handles after a CLI restart. |

Because the harness re-derives tokens from the PAT + uuid, **restarting
`anna-app dev` does not strand existing sessions**: hand the saved
`app_session_uuid` back (resume/refresh) and the harness mints a fresh
token from the live row.

#### Dev session admin endpoints

All are PAT-authed (`{pat: ...}` in the body, or `?pat=` for the GET) and
scoped to apps you own:

| Endpoint | Body / query | Returns |
|---|---|---|
| `POST /api/v1/anna-apps/dev/session/refresh` | `{pat, app_session_uuid, ttl_seconds?}` | `{app_session_uuid, token, expires_in, expires_at, max_lifetime_at, …}` |
| `POST /api/v1/anna-apps/dev/session/revoke` | `{pat, app_session_uuid}` | `{revoked: true}` |
| `POST /api/v1/anna-apps/dev/session/revoke-all` | `{pat, app_slug?\|app_id?\|executa_id?, only_expired?}` | `{revoked: <count>}` |
| `GET /api/v1/anna-apps/dev/sessions` | `?pat=&app_slug=&include_expired=&limit=` | `{sessions: [{app_session_uuid, kind, submode, expires_at, max_lifetime_at, …}]}` |

`revoke-all` with `only_expired: true` is a handy "garbage-collect my dead
sessions" call during heavy local iteration.


---

## 3. `--llm mock` (deterministic, free, offline)

```bash
anna-app dev --llm mock --mock-llm fixtures/replies.jsonl
```

Each line of the JSONL fixture is a `MockEntry`:

```jsonl
{"ns":"llm","method":"complete","match":{"contentIncludes":"weather"},"result":{"role":"assistant","content":{"type":"text","text":"sunny"},"model":"mock","stopReason":"endTurn"}}
{"ns":"agent","method":"session.run","events":[{"payload":{"event":"token","text":"hello"}},{"payload":{"event":"token","text":" world"}}]}
```

- `match.contentIncludes` is a substring filter against the call
  payload (case-sensitive).
- For agent runs, `events: [...]` are emitted as `rpc.stream` frames
  in order; the harness adds a final `done: true` terminator.
- If no entry matches, the harness returns a generic echo so your app
  never crashes mid-demo.

This mode is what CI uses — see
[tests/llm-bridge.test.ts](https://github.com/talentai/anna-app-cli/blob/main/tests/llm-bridge.test.ts).

---

## 4. `--llm off` (or `--no-llm`)

Use this when you're iterating on UI that doesn't need LLM and want
zero network calls:

```bash
anna-app dev --no-llm
```

Every handled call returns:

```json
{ "ok": false, "error": { "code": "llm_disabled", "message": "harness started with --no-llm" } }
```

Your app code should handle this gracefully (e.g. show a "LLM disabled
in dev" placeholder).

---

## 5. Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `no PAT on disk` | Never logged in for this host | `anna-app login --host …` |
| `PAT expired` | Default 90-day TTL elapsed | Re-login |
| `session.mint failed: HTTP 403` | Manifest doesn't grant the requested kind/submode | Check `host_api.llm` / `host_api.agent.session` |
| `APP_SESSION_EXPIRED` on run/refresh | Session crossed its idle (30 min agent) or hard (24 h) deadline | Create a fresh session; expired ones auto-release quota |
| `APP_SESSION_TOKEN_EXPIRED` | Capability token lapsed but session is alive | Retry — the harness self-heals the token; or call `session.refresh` |
| Session can't be deleted after restart | Lost the in-memory token handle | Use token-free `session.delete` (PAT) or `POST /dev/session/revoke` with the uuid |
| `permission_denied` from the iframe | Manifest grant missing | Same as above |
| Tokens you didn't expect | Apps you forgot leaving sessions open | `revoke-all` (`only_expired:true`) or revoke the PAT |


---

## 6. Security notes

- The PAT is a bearer credential. Never commit `credentials.json` or
  paste its contents in screenshots.
- Mint calls hit a **dev-only** endpoint (`/api/v1/anna-apps/dev/...`).
  Production never accepts a PAT directly — only short-lived
  `app_session_token`s.
- Revoking a PAT in the dashboard is immediate; subsequent mint calls
  fail with `401 token_revoked`. Existing minted tokens still work
  until they naturally expire (~10 min).
- Quotas, rate limits, and per-app billing apply identically to
  `--llm real` and a packaged production app.

---

## 7. Related

- App-side API reference: [llm-and-agent.md](llm-and-agent.md).
- Design spec (host internals): `docs/design/app-llm-and-agent-access.md`.


---

---
title: Testing the Bundle
description: Drive the bundle from vitest with `mountBundle` — same ACL gating and call recording as the dev harness.
section: apps
slug: testing-bundle
updated: 2026-04-29
estimated_minutes: 4
category: Local Development & Testing
---

# Testing the App Bundle

Use `@anna-ai/cli/test` (the `mountBundle` helper) to drive your bundle
modules directly from `vitest` — no iframe, no harness server, no
`uvx`. The same ACL gating, mock-runtime, and call-recording layer that
backs `anna-app dev` runs in-process.

## Install

The helper ships inside `@anna-ai/cli` (re-exported as `@anna-ai/cli/test`).
Add it as a dev dep:

```bash
pnpm add -D @anna-ai/cli vitest
```

A standalone `@anna-ai/app-test` package will be carved out in a later
phase; until then `import { mountBundle } from "@anna-ai/cli/test"` is the
canonical entry.

## Minimal example

```ts
// tests/bundle/timer.spec.ts
import { describe, it, expect } from "vitest";
import { mountBundle } from "@anna-ai/cli/test";
import manifest from "../../manifest.json" assert { type: "json" };
import { startTimer } from "../../bundle/timer.js";

describe("timer", () => {
  it("invokes the executa tool", async () => {
    const harness = await mountBundle({
      manifest,
      mocks: {
        "tools.invoke": ({ tool_id, method, args }) => ({
          success: true,
          data: { state: "running", remaining_seconds: 1500 },
        }),
      },
    });

    await startTimer(harness.runtime, { duration_minutes: 25 });

    expect(harness.calls.byNs("tools.invoke")).toHaveLength(1);
    const call = harness.calls.lastOf("tools.invoke")!;
    expect(call.args).toMatchObject({ method: "start" });
  });
});
```

## What `mountBundle` gives you

| Property | Use |
| --- | --- |
| `harness.runtime` | Drop-in for the production SDK (`AnnaAppRuntime`). Same `tools.invoke` / `storage.set` / `chat.write_message` / event API. |
| `harness.calls` | `CallLog` with `all()`, `byNs(prefix)`, `last()`, `lastOf(prefix)`, `clear()`. |
| `harness.events` | `EventBus` with `emit(name, payload)` (simulate server events) and `on(name, fn)`. |
| `harness.acl` | Effective ACL derived from `manifest.ui.host_api`. |
| `harness.mock(key, handler)` | Replace / add a mock at any time. |
| `harness.wait(ms)` | Microtask helper. |

## ACL semantics

Calls outside `manifest.ui.host_api` resolve to `outcome: "denied"` and
the promise rejects with `HostApiError`. This mirrors the production
dispatcher's `permission_denied` path:

```ts
await expect(
  harness.runtime.fs.read({ path: "/etc/passwd" }),
).rejects.toThrow(HostApiError);
expect(harness.calls.last()?.outcome).toBe("denied");
```

## Pushing simulated events

```ts
harness.events.emit("entry_payload", { mode: "deep_focus" });
harness.events.emit("auth.refresh", { token: "xyz" });
```

Anything your bundle subscribes to via `runtime.on(name, ...)` will fire.

## Default mock behaviour

If you don't supply a mock for a method:

- `window.*` returns `{ ok: true }` (or the documented shape) and
  records the call.
- `storage.*` operates on an in-memory `Map` so set/get/delete behaves
  exactly like production (sans size limit).
- everything else returns a `denied` outcome and rejects.

## What this does **not** test

- The static manifest schema — use `anna-app validate`.
- The plugin side (`executas/`) — use
  [`anna-executa-test`](/developers/apps/testing-plugin).
- The full iframe + postMessage transport — use `anna-app dev` and the
  recordings it produces.

## Related

- [Local Development](/developers/apps/local-dev)
- [Recording & replaying](/developers/apps/recording-replay)
- [Host API reference](/developers/apps/app-ui-host-api)


---

---
title: Testing the Plugin
description: Test the executa plugin under `executas/` with `anna-executa-test` — pytest fixtures that spawn the plugin under uv run.
section: apps
slug: testing-plugin
updated: 2026-04-29
estimated_minutes: 4
category: Local Development & Testing
---

# Testing the Executa Plugin

`anna-executa-test` is a **pytest** plugin for the Python (or any
JSON-RPC over stdio) plugin that lives under `executas/<name>/` in your
app project. It spawns your plugin the same way Anna Agent will at
runtime, then drives it with one-shot calls and Hypothesis-generated
fuzz cases.

## Install

```bash
uv pip install anna-executa-test
# or
pip install anna-executa-test
```

The package's own README is the most up-to-date public-API reference;
this page is the integration guide for an Anna App project.

## Project layout

```
my-focus-flow/
├── manifest.json
├── bundle/
└── executas/
    └── timer/
        ├── pyproject.toml          # devDeps: anna-executa-test, pytest
        └── tests/
            └── test_smoke.py
```

## Minimal smoke test

```python
# executas/timer/tests/test_smoke.py
from pathlib import Path
import pytest
from anna_executa_test import executa, assert_jsonrpc_ok

PLUGIN_DIR = Path(__file__).parent.parent

@pytest.fixture(scope="module")
def plugin():
    with executa.spawn(PLUGIN_DIR) as p:
        yield p

def test_describe(plugin):
    info = plugin.call("describe")
    assert info["name"].startswith("tool-")
    assert info["tools"], "plugin should declare at least one tool"

def test_invoke_get_state(plugin):
    resp = plugin.call(
        "invoke",
        {"tool": "session", "arguments": {"action": "get_state"}},
    )
    assert_jsonrpc_ok(resp)
```

## Public surface (Phase 5 MVP)

| Symbol | Purpose |
| --- | --- |
| `executa.spawn(project_dir, *, command=None, env=None)` | Context manager spawning the plugin under `uv run`. Yields an `ExecutaClient`. |
| `ExecutaClient.call(method, params=None, *, timeout=10.0)` | One JSON-RPC round-trip. |
| `ExecutaClient.invoke(tool, arguments)` | Sugar for `("invoke", {"tool", "arguments"})`. |
| `ExecutaClient.describe()` / `.health()` | Standard control methods. |
| `assert_jsonrpc_ok(resp)` | Raises with a useful diff when `success != True`. |
| `assert_jsonrpc_error(resp, code=...)` | Verifies the structured error path. |
| `wire_format.validate_response(env)` | Strict envelope shape check, matches nexus's `executa_wire`. |
| `contract.contract_for(project_dir)` | Reads `pyproject.toml` + spawns briefly to capture `MANIFEST`; exposes `.parametrize_invoke(...)` for Hypothesis fuzzing. |
| `mock_state_dir(tmp_path)` (fixture) | Overrides `XDG_STATE_HOME` so plugins don't leak state. |

## Why "same invoker as Anna Agent"

The stdio client used by `anna-executa-test` is a near-line-for-line
extraction of the path Anna Agent runs in production. If your plugin
passes here, it will pass at runtime — modulo network credentials and
real-time NATS routing, which are by design out of scope.

## Wire-format compliance

Run `pytest -k contract` after writing your tests — `contract_for(...)`
will fuzz `invoke` against your declared `MANIFEST.tools[].parameters`
JSON Schema and assert the response envelope matches the nexus contract.

## Related

- [Local Development](/developers/apps/local-dev)
- [Testing the bundle](/developers/apps/testing-bundle)
- [App Manifest](/developers/apps/app-manifest)


---

---
title: Recording and Replay
description: Record `anna-app dev` sessions to JSONL and verify, summarize, or replay them against the current manifest.
section: apps
slug: recording-replay
updated: 2026-04-29
estimated_minutes: 4
category: Local Development & Testing
---

# Recording and Replaying Sessions

Every `anna-app dev` session records its RPC envelopes to a JSONL file.
You can verify recordings, summarise them, or dry-run a replay against a
manifest — useful for regression suites and bug reports.

## Where recordings live

By default the harness writes one JSONL per session under your project's
`./fixtures/` directory (or wherever `manifest.dev.fixtures` points the
harness to look). Each line is a single envelope:

```jsonl
{"t": 0,    "dir": "out", "ns": "window",  "method": "hello",  "args": {}, "result": {...}}
{"t": 12,   "dir": "out", "ns": "tools",   "method": "invoke", "args": {"tool_id": "..."}, "result": {...}}
{"t": 1500, "dir": "in",  "name": "auth.refresh", "payload": {...}}
```

`dir`:

- `out` — bundle → host (`call`)
- `in`  — host → bundle (server-pushed `event`)

## CLI

### `anna-app fixture verify <file>`

Schema + invariant checks. Confirms each line parses, every `out` call
maps to a known `(ns, method)`, and the timeline is monotonic.

```bash
anna-app fixture verify fixtures/happy-path.jsonl
# ✓ 84 envelopes, 0 issues
```

Pass `--json` for machine-readable output (CI integrations).

### `anna-app fixture summarize <file>`

Human-readable digest: per-namespace call counts, error breakdown, top
tools by invocation count, total duration.

```bash
anna-app fixture summarize fixtures/happy-path.jsonl
# Session: fixtures/happy-path.jsonl
# Duration: 4.2s   Calls: 84   Errors: 0
# By namespace:  window 12   storage 31   tools 18   chat 23
# Top tools: tool-dev-focus-flow.start (8), tool-dev-focus-flow.tick (10)
```

`--json` available.

### `anna-app fixture replay <file>`

Dry-run replay of a recording against the current manifest. Useful when
you've changed `host_api` ACL or renamed a tool — the replay surfaces
every call the new manifest would now reject.

```bash
anna-app fixture replay fixtures/happy-path.jsonl --manifest manifest.json
```

The MVP replay does **not** boot the bundle; it just walks the timeline
and reports each call's projected outcome under the supplied manifest.

## Wiring into vitest

You can hand a recording to `mountBundle` to exercise event delivery
deterministically:

```ts
import { mountBundle } from "@anna-ai/cli/test";
import { readFileSync } from "node:fs";
import manifest from "../manifest.json" assert { type: "json" };

const lines = readFileSync("fixtures/happy-path.jsonl", "utf8")
  .trim()
  .split("\n")
  .map((l) => JSON.parse(l));

const harness = await mountBundle({ manifest });

for (const env of lines) {
  if (env.dir === "in") {
    harness.events.emit(env.name, env.payload);
  }
  // `out` envelopes will be replayed by your test's normal call path
}
```

## CI usage

Drop one or two short, hand-curated recordings into `fixtures/` and
gate every PR with:

```yaml
- run: pnpm anna-app fixture verify fixtures/*.jsonl
- run: pnpm anna-app fixture replay fixtures/happy-path.jsonl
```

The replay step catches manifest regressions; the verify step catches
recording corruption.

## Related

- [Local Development](/developers/apps/local-dev)
- [Testing the bundle](/developers/apps/testing-bundle)
- Design doc:
  [`docs/design/anna-app-local-dev-and-test.md`](/developers/apps/app-ui-overview)
  §6 (recording format) and §10 (CI matrix)


---

---
title: Host API vs Executa Tool — When to Use Which
description: Anna apps can reach for the platform's host API or for a custom Executa tool to accomplish similar-looking tasks. They are not equivalent — this guide explains the real differences and gives a decision framework.
section: apps
slug: host-api-vs-executa
updated: 2026-05-27
estimated_minutes: 8
---

## The trap: they look like equivalent menus

At first glance the **Host API** (`anna.llm`, `anna.agent`, `anna.storage`, `anna.image`, `anna.upload`) and **Executa tools** (custom plugin processes invoked via `anna.tools.invoke`) appear to offer overlapping capabilities. Both can "call an LLM", both can "store data", both can "talk to external systems". So which one should an Anna App reach for?

**They are not actually peers.** Treating them as a free choice between two equivalent menus is the most common architectural mistake in Anna App design. They differ on identity, billing, lifecycle, trust boundary, and the platform contract — and picking the wrong one silently breaks quota accounting, cross-device sync, or maintainability.

## Side-by-side

| Dimension | Host API (`anna.llm`, `anna.storage`, …) | Executa Tool (`anna.tools.invoke`) |
|---|---|---|
| **Where the code lives** | Inside nexus / dispatcher (the platform) | A process the developer wrote (Python/Node/Go/binary) |
| **Identity** | Automatically scoped to the signed-in user via `app_session_token` / `storage_token` | The process has no user identity — it must reverse-RPC back to the host API to touch user-scoped resources |
| **Quota & billing** | Counts against the user's unified Anna quota (see *matrix pricing baseline*) | Developer-paid (your own API keys, your own infra) |
| **Audit / compliance** | Centralised in nexus logs | Black box on the developer side |
| **Cross-device** | Yes — server-backed | No — local to whichever machine / runner spawned the process |
| **Cold start** | ~0 ms (the dispatcher is already running in-process) | Tens to hundreds of milliseconds (process spawn + `describe` handshake) |
| **State** | Stateless — every call independent | Can hold long-lived state (a warm model client, a DB connection pool, an open file handle) |
| **Reach** | Whatever the platform has abstracted | Local filesystem, GPU, private SDKs, third-party systems |
| **Versioning** | Evolves with the dispatcher (schema pinned at `dispatcher_version=0.10.0`, tracking the `anna-app-schema` version) | Developer bumps it independently |
| **Permission model** | User grants per-namespace via `manifest.permissions` | Once installed, the executa is trusted wholesale |
| **Platform reach** | Web, Desktop, Mobile — all the same wire contract | Only where an Anna runtime is installed |

## The key clarification: Executa is not a substitute for the host API — it is an extension point for it

The most consequential misreading of the surface is "I can do LLM either way — let me pick one." The real design treats them as **nested**, not exclusive:

```
iframe (UI / orchestration)
   ├── anna.llm.complete(...)          ← Host API (direct)
   ├── anna.storage.set(...)            ← Host API (direct)
   └── anna.tools.invoke("rerank", ...) ← Executa
                  │
                  └── reverse-RPC from inside the executa:
                       anna.llm.complete(...)   ← still the Host API
                       anna.storage.get(...)    ← user identity inherited
```

So the right question is **not** "host API or executa?" — it's "does this piece of logic need to run in a separate process?" That is the real boundary between iframe code and an executa. Once you decide to move logic into an executa, the executa itself should still call back into the host API for any user-scoped work, rather than reimplementing those capabilities (and silently bypassing identity, quota, and audit).

## Decision framework

**Default to the Host API.** Only switch to an Executa when at least one of these hard constraints applies:

1. **Heavy CPU / memory work** — embeddings, vector search, local image processing, PDF parsing, numpy / PyTorch. The iframe main thread and per-call host RPC are both wrong places for these.
2. **Long-lived session state** — keep a model client, a database connection pool, a scraper session, or a cached index alive across many invocations. Host calls are stateless by contract.
3. **Capabilities the platform has not abstracted** — local filesystem, OS tooling (`git`, `ffmpeg`), intranet APIs, specific hardware. The host API simply does not expose these.
4. **Developer-owned secrets** — you are integrating a third-party SaaS using *your* API key (not the end user's). The key must not reach the iframe (browser context can be inspected); putting the integration in an executa keeps it server-side / process-side.
5. **Agent-orchestrable tools** — you want `anna.agent.session.run` to decide when to call this capability. That is exactly what executas are designed to be.

If none of the above applies, **use the host API**. You inherit maintenance, multi-platform reach, audit, and quota accounting for free.

## Anti-patterns (each one tempting, each one a trap)

| Anti-pattern | Why it bites |
|---|---|
| Executa `import openai` calling OpenAI directly | The end user's chosen model / quota / billing is bypassed. The bill lands on the developer. When the user switches models in their Anna settings, your app silently ignores it. |
| Executa writing "user data" to a local JSON file | Lost on device swap, reinstall, or uninstall. Will never sync between Web / Desktop / Mobile. |
| Wrapping `anna.upload.inline` in an executa that just forwards | One extra stdio hop plus a reverse-RPC for no gain. Pure overhead. |
| Making "translate this sentence" or "generate one image" into an executa | The cold-start cost exceeds the actual work. The user feels lag for no reason. |
| Running algorithms inside the iframe (when they belong in an executa) | Blocks the UI thread; the app appears frozen during work. |

## Practical guidance for Anna App authors

1. **The iframe is UI + orchestration.** It calls the host API for user-identity-bound operations (LLM, storage, image, upload), and it calls executas to trigger custom heavy logic.
2. **The host API is the default.** If a capability exists there, use it — you get platform maintenance, cross-platform behaviour, and audit / quota for free.
3. **Put only "must run locally" code in an executa.** And when an executa needs user-scoped capabilities, it should reverse-RPC back into the host API — never bring its own OpenAI key or roll its own storage layer.
4. **Always use APS for persistence** (see `local-dev` `--storage aps` to exercise the real backend in local development). Do not fake persistence by writing files inside an executa.
5. **Quick test:** identity / billing / sync / cross-device → host API; CPU / state / private keys / system access → executa.

## In one sentence

**The Host API is the default path; Executa is an escape hatch — and the escape hatch should still reverse-RPC back through the Host API, not bypass it.**


---



# === Reference ===

---
title: Verified Developer
description: What the Verified Developer flag unlocks, and how it is granted.
section: reference
slug: verified-developer
updated: 2026-04-23
estimated_minutes: 3
---

**Verified Developer** is the status that lets you create and manage **Anna Apps** in the App Store. It is a single boolean on your user record (`User.is_verified_developer`), independent of email verification (`is_verified`), and is granted manually by an Anna platform administrator.

> [!IMPORTANT]
> Verified Developer status is required **only for publishing Anna Apps**. You can ship Executas (Tools and Skills) into the Executa Hub without it — see [Publishing a Tool](/developers/tools/executa-publish) and [Publishing a Skill](/developers/skills/skill-publish). Promoting an Executa to `visibility=public` requires a paid subscription, but not the Verified Developer flag.

## What the flag unlocks

When `is_verified_developer = true`, the dependency `require_verified_developer` (`src/auth/deps.py`) lets you call every developer-side Anna App endpoint mounted under `/api/v1/developer/apps/*`:

- `GET    /api/v1/developer/apps` — list your apps
- `POST   /api/v1/developer/apps` — create a new app
- `PATCH  /api/v1/developer/apps/{app_id}` — edit metadata
- `POST   /api/v1/developer/apps/{app_id}/logo` — upload a square logo (≤2 MB, JPEG/PNG/WebP/GIF; auto-resized to 256×256 WebP)
- `GET    /api/v1/developer/apps/{app_id}/versions`, `POST .../versions`, `POST .../versions/{id}/publish`
- `POST   /api/v1/developer/apps/{app_id}/submit-review`
- `POST   /api/v1/developer/apps/{app_id}/archive`
- `POST   /api/v1/developer/apps/validate-manifest`

Without the flag, these endpoints return `403 Verified developer status required.`

## What the flag does **not** change

- It is **not** required to create or publish a Tool or Skill Executa.
- It does **not** affect ranking, trust scores, review SLAs, or quotas. There is no automatic ranking boost in the codebase.
- It does **not** unlock any private API or extra runtime capability beyond the `/api/v1/developer/apps/*` surface above.
- It is independent of email verification (`is_verified`), subscription tier, and superuser status.

## Two related fields

When the flag is granted, the admin can also set two public-profile fields on the same user record:

| Field | Type | Purpose |
|---|---|---|
| `developer_handle` | string, ≤80 chars, globally unique | Your public developer slug (e.g. `studio-acme`). Surfaces on App listings. |
| `developer_profile` | Markdown, ≤2000 chars | Your public developer bio. |

Both are nullable and only meaningful while `is_verified_developer = true`.

## How status is granted

There is no self-service application form in the codebase. Status is granted by an Anna platform administrator through `PATCH /api/v1/super-admin/users/{user_id}` (the admin user-management surface), which can set `is_verified_developer`, `developer_handle`, and `developer_profile` together.

In practice, if you want to ship an Anna App, contact platform staff (forum, support email, or your existing channel) with:

- The user account you want flagged.
- The `developer_handle` you want to claim (kebab-case, must be globally unique).
- A short description of what you intend to publish.

Once the admin updates your record, your next call to any `/api/v1/developer/apps/*` endpoint will succeed.

## Revocation

Because the flag is just a boolean on your user, the same admin endpoint can flip it back to `false` at any time. Revocation does not delete your existing apps; it only blocks further calls to the developer endpoints. Apps you have already published continue serving installed users until they are explicitly archived (`POST /api/v1/developer/apps/{app_id}/archive`) or rejected by an admin.

## Questions

If you have a status request or need clarification on what an admin will check before granting the flag, reach out via your usual platform support channel — there is no in-app application form yet.


---

---
title: FAQ
description: Answers to the questions developers most often ask.
section: reference
slug: faq
updated: 2026-04-23
estimated_minutes: 5
---

## Building

### Do I have to use Python / Node / Go for a Tool Executa?

No. The protocol is JSON-RPC over stdio — anything that can read a line and print a line works. Rust, Ruby, C#, Bash, even a compiled C binary. The three languages we document just have ready-made examples in [`anna-executa-examples`](https://github.com/whtcjdtc2007/anna-executa-examples).

### Are Tools and Skills the same thing?

They are the two flavours of one umbrella concept, **Executa** — same database table, same draft → version → visibility lifecycle, same Hub. A *Tool* is the executable flavour (a process speaking JSON-RPC); a *Skill* is the declarative flavour (a `SKILL.md` folder). See [Concepts](/developers/overview/concepts).

### Can my Tool Executa call other Tool Executas?

Not directly. Each Tool runs in its own process and only sees its own stdin/stdout/stderr and the env vars passed at spawn time. If you need composition, either:

- Bundle the Tools into an **Anna App** so the user installs them together; or
- Ship a **Skill** whose body teaches Anna *when* to call each Tool — the LLM does the orchestration.

### Is there an SDK?

No. The protocol is small enough that "the SDK" would be tens of lines. The example repos linked above stand in for thin wrappers.

### Does a Skill execute the bash / python in its body?

No. The skill loader (`src/skills/converter.py`) wraps every Skill — regardless of `execution_mode` — as a prompt-mode LangChain tool that returns the skill's markdown body to the LLM, decorated with an execution-mode hint and any declared dependencies. Running anything is the agent's job, via its built-in `exec` / `command` tools. `execution_mode` is purely a hint that helps the LLM pick the right execution path.

## Distribution

### Do I need Verified Developer status to publish?

Only for **Anna Apps**. Tool and Skill Executas can be created and made `public` by any user with a paid subscription (the `_require_paid_for_public` check in `src/api/executa.py`). Apps require the `is_verified_developer` flag — see [Verified Developer](/developers/reference/verified-developer).

### What is the App review flow?

`AnnaAppStatus` (`src/models/anna_app.py`) cycles through:

1. `draft` — created by the developer.
2. `pending_review` — set by `POST /api/v1/developer/apps/{id}/submit-review` (requires at least one version).
3. `approved` or `rejected` — decided by a platform admin via `POST /api/v1/super-admin/apps/{id}/approve` or `.../reject`. An admin can publish in the same call (`publish=true`).
4. `published` — visible in the public catalogue.
5. `archived` — set by the developer (`/archive`) or admin; existing installs keep working but new users can't discover it.

There is no documented review SLA in the codebase.

### Can I delete a published Executa?

`DELETE /api/v1/executas/my/{tools|skills}/{id}` calls `delete_executa` (`src/services/executa_crud.py`). It does a **hard delete** when nothing references the Executa, and a **soft archive** (sets `archived=True`) when a published `AnnaAppVersion` snapshot still references it — so other users' installed Apps don't break. Versions snapshotted into a published App are immutable; you can't selectively delete them.

### Can I delete a published Anna App?

There's no hard-delete endpoint for an App once it's published. Use `POST /api/v1/developer/apps/{id}/archive` to set status to `archived`: existing installs keep working, new users can't discover it. If you need a published version pulled for a security issue, contact platform support.

### Can I publish under a company name?

Yes — once an admin grants you Verified Developer status they can also set your `developer_handle` (e.g. `studio-acme`, ≤80 chars, globally unique) and `developer_profile` (Markdown bio). Both fields surface on App listings.

### Are there fees?

The platform doesn't charge submission or listing fees. Promoting an Executa to `visibility=public` does require a paid Anna subscription (Free accounts get `403 Publishing to the public Hub requires a paid plan.`). The `AnnaAppPricingModel` enum (`free`, `byo-key`, `paid`) is currently a metadata field on App records and is not enforced for billing.

## Versioning & rollouts

### What does versioning actually look like?

Two parallel mechanisms, depending on the artifact:

- **Executa (Tool / Skill)**: each `POST /my/{tools|skills}/{id}/versions` call freezes the current row into an immutable `ExecutaVersion`. Apps that bundle the Executa pin a `min_version`.
- **Anna App**: each app has its own `AnnaAppVersion` rows with their own version strings, changelogs, and `published_at`. Publishing a new version sets `is_latest=True` for that row.

There is no automatic semver-aware staged rollout, no per-version deprecation flag, and no in-app prompt asking users to "accept" a major bump — those behaviours don't exist in the current code.

### Can I do a staged rollout / canary?

Not today. All published versions are visible to every eligible user immediately.

## Credentials & data

### Where are user credentials stored?

In the platform-managed credential store; the Tool process receives them as **environment variables** declared in its manifest at spawn time. Your Tool doesn't see plaintext outside those env vars. See [Credentials & OAuth](/developers/tools/executa-credentials).

### Can my Tool store user data?

Yes — to its own scratch space under the user's data directory. Don't write outside it, don't write secrets, and don't assume the platform will sync the directory across devices. If you need durable cross-device state, point the user at an external service they authenticate against.

### Does Anna read my Tool's stderr?

Yes. The runtime captures stderr and surfaces it in tool execution traces visible to the user. Treat stderr as user-readable debug output — useful for diagnostics, but never log secrets there.

## Support

### Where do I report a platform bug?

Use your usual platform support channel (forum, support email). There is no dedicated in-app "Report a Bug" form documented in the codebase.

### Where do I propose a feature?

Same channel. Triage cadence isn't fixed.

## Anything else?

If your question isn't here, search the rest of the Developer Hub or open a support request through your usual channel. We'll add answers here as they come up.


---



# === Reference ===

## Executa — Anna's plugin extension system

*Executa · what & why*

An Executa is a standalone process Anna spawns and talks to over stdio. There is no SDK and no embedded runtime; any language that can read a line and print a line qualifies. Two declarative flavours ship today: Tool (executable JSON-RPC) and Skill (markdown recipe).

### Kinds

- **Tool** — A real process that runs and returns data. Long-running stdio JSON-RPC. Most common Executa shape.  `executa_type=tool`

- **Skill** — A folder of markdown loaded into the agent as a `@tool`. Skills do not execute code themselves — the agent does, via its built-in exec tools.  `executa_type=skill`

### Process model

- **Single long-running process** — Anna spawns one process per plugin and reuses it for every `describe` / `invoke` / `health`. Plugins must loop on stdin until EOF — exiting after one request is the #1 pitfall.  `lifecycle`

- **Per-user spawn** — Each (user, plugin) gets its own process. Credentials are injected per spawn, never shared across users.

- **Stdout = data, stderr = logs** — Stdout is the JSON-RPC channel; anything written there must be a frame. Use stderr for diagnostics — captured into user-visible traces.

### Protocol versions

- **v1.0** — Forward request / response only. `describe` + `invoke` + `health`.  `baseline`

- **v2** — Adds the `initialize` handshake + reverse RPC channel (host → plugin requests). Unlocks sampling and persistent storage.  `reverse-rpc`

- **v2.1** — Adds agent sessions (`agent/complete`, `agent/session.*`) — parity with iframe anna-apps for multi-turn tool-using runs.  `agent-parity`


---

## Tool Executa — wire protocol

*Executa · JSON-RPC over stdio*

**JSON-RPC 2.0 over stdio**, one message per line (LF-delimited UTF-8 JSON, no Content-Length headers). Agent owns transport, request IDs, error wrapping, restart, credential injection and reverse-RPC routing; the plugin only has to read stdin and write stdout.

**Three rules that cause 90% of `Stopped` plugins:**
1. `stdout` is **protocol-only** — a single `print()` outside the JSON-RPC envelope corrupts the framing. All logs go to `stderr`.
2. **Flush after every write.** Most languages block-buffer stdout by default; pipe back-pressure plus no flush = silent hang.
3. **Never `exit()` after a single response.** The main loop must keep reading stdin until EOF, otherwise sampling/storage reverse-RPC has nothing to read host replies on.

Source of truth: `matrix/src/executa/protocol.py` (method names, error codes, limits) and `runtime.py` (spawn / restart / timeout policy).

### Transport framing

- **stdin** — Agent writes one JSON-RPC request per line. Plugin must read line-by-line; handle empty lines as no-op.

- **stdout** — Protocol responses **only**. Any non-JSON-RPC byte breaks framing → host kills the plugin.

- **stderr** — Free-form logs. Captured and surfaced in execution traces. Never log credential values or `sampling_token`.

- **encoding** — UTF-8 everywhere. No BOM. No CRLF — LF only.

- **MAX_STDIO_MESSAGE_BYTES = 512 KiB** — Per-message soft cap. Larger responses MUST use file transport (see below) or risk pipe-buffer deadlock.

- **MAX_READLINE_BYTES = 2 MiB** — Hard line cap on the host's reader. A line longer than this is treated as a protocol violation.

### Forward methods (Agent → Plugin)

- **initialize** — **v2 handshake.** Host sends `{protocolVersion: "2.0", host_capabilities: {"llm.sample": true}}`. Plugin must echo `protocolVersion` and advertise `client_capabilities` (e.g. `{sampling: {}}`). Plugins that return `-32601 Method not found` silently fall back to v1 (no reverse RPC).  `5s` `v2 only`

- **describe** — Return the manifest (`name`, `version`, `tools[]`, `credentials[]`, `host_capabilities[]`, `runtime`). Called once per spawn and cached. **Result MUST be the manifest itself**, not wrapped — `from_dict` reads `data["name"]` directly.  `required` `5s · 60s binary cold-start`

- **invoke** — Execute one tool. Per-tool timeout defaults to **60s** and can be overridden via `ToolDefinition.timeout`. Streaming flag exists but invoke is request/response in v2 (streaming reserved for a future revision).  `required` `60s default`

- **health** — Optional liveness probe. Return `{status: "healthy", timestamp, version, tools_count}`. Host uses it to decide restart timing and surface red dots in Admin.  `optional` `3s`

- **shutdown** — Reserved graceful-shutdown method. In practice host closes stdin → SIGTERM → SIGKILL on a 5s grace window. Plugins should treat stdin EOF as the actual shutdown signal.

### Reverse methods (Plugin → Agent, v2 only)

- **sampling/createMessage** — Borrow the host's LLM for a single completion. Requires v2 negotiation + manifest `host_capabilities: ["llm.sample"]` + user grant. See `executa-sampling`.

- **agent/session.create · run · cancel · history · delete** — Drive multi-turn stateful agent sessions from a plugin. Requires `host_capabilities: ["llm.agent.auto"]`. See `executa-agent-sessions`.

- **agent/complete** — L1 stateless single-turn completion (convenience wrapper, same auth chain as `agent/session.*`).

- **storage/get · set · delete · list** — Anna Persistent Storage KV. Scope selected via `scope: "user"|"app"|"tool"`; server-side gated by the `storage_token`'s `allowed_scopes` claim. See `executa-persistent-storage`.

- **files/upload_begin · upload_complete · download_url · list · delete** — Anna Persistent Storage Files namespace (covers all three scopes). The legacy `user_files/*` alias was removed in favour of `files/*` + `scope="user"`.

- **Reverse-RPC dispatch contract** — Plugin uses the **same stdin reader** for incoming forward requests AND for host responses to its own reverse RPCs. Use the SDK's `dispatch_response` helper — naive `readline()` loops will hang the moment sampling is in flight.

### Manifest shape (describe result)

- **name** — Unique tool identifier. Lowercase kebab/snake-case. Maps to `tool_id` in Anna Admin.  `required`

- **display_name** — Human-readable name. Maps to `name` in Admin UI.  `required`

- **version** — Semantic version. Used for installed-vs-published diff and INSTALL.json bookkeeping.  `required`

- **description** — Plugin-level description shown in Anna Admin and the catalogue.

- **tools[]** — Array of `ToolDefinition`. Each item: `{name, description, parameters[], timeout?, streaming?}`. `description` is what the LLM sees — write for the model, not the developer.  `required`

- **credentials[]** — Array of `CredentialSchema`. Declares API keys / OAuth tokens the plugin needs; host renders config UI and injects via `context.credentials`. See `executa-credentials`.

- **host_capabilities[]** — Whitelist of reverse-RPC families this plugin intends to use: `"llm.sample"`, `"llm.agent.auto"`, `"storage"`, …. Missing entries → host rejects the corresponding reverse RPC with `not_negotiated` / `not_granted`.

- **runtime** — Optional `{type: "binary"|"uv"|"npm"|…, min_version?}` hint. Host uses it for compatibility checks; the actual runtime is decided by the distribution type (see `executa-distribution`).

- **author** — Optional. Displayed in catalogue. Not validated.

### Tool parameter schema (`parameters[]`)

- **name** — Argument name as the LLM will pass it.

- **type** — One of `string` · `integer` · `number` · `boolean` · `array` · `object`. **Use the protocol's `parameters[]` shape, NOT MCP `input_schema`** — `input_schema` is silently ignored by `ToolDefinition.from_dict`.

- **description** — Shown to the LLM. Critical for argument quality.

- **required** — Default `true`. Set `false` for optional args.

- **default** — Optional. Used by the host when LLM omits the arg.

- **enum** — Optional list of allowed values; surfaced as a constrained JSON Schema enum.

- **items / items_type (array only)** — **Required when `type="array"`** or the LLM will serialise the array as a quoted string (`"['/path']"`). Two equivalent forms: `items: {type: "string"}` (standard JSON Schema) or `items_type: "string"` (shorthand). Missing → host defaults to `string` and warns.

### Invoke envelope

- **params.tool** — Tool name (must match a `tools[].name` from describe).  `required`

- **params.arguments** — Object of validated args; populated by the LLM.  `required`

- **params.context.credentials** — Host-injected credentials keyed by `CredentialSchema.name`. Never visible to the LLM. Plugins should read these first and fall back to env vars only for local dev.

- **params.invoke_id (v2)** — Per-invoke correlation UUID. Plugin MUST echo it in every reverse-RPC `metadata` field — billing/audit attributes spend to this id.

- **params.sampling_token (v2)** — Short-lived JWT (TTL 600s). Only present when the user granted sampling for this Executa. Required to call `sampling/*` or `agent/*`.

- **result.success** — **Boolean, defaults to `false` in the parser** — you MUST set `true` explicitly on success or the host treats the call as failed.  `required`

- **result.data** — Tool-defined payload. Free-form JSON.

- **result.tool** — Echo of the tool name for log correlation. Recommended.

- **error envelope** — Use JSON-RPC `error: {code, message, data?}` for programmer/validation errors. Use `result: {success:false, error: "..."}` for user-facing tool failures the LLM should see and retry-or-route around.

### JSON-RPC error codes (standard)

- **-32700 Parse error** — Request body is not valid JSON. Host-emitted.

- **-32600 Invalid request** — Missing `jsonrpc` or `method`.

- **-32601 Method not found** — Unknown RPC method or unknown tool name. **Always return this for unknown methods** — the host's v1/v2 fallback depends on it.

- **-32602 Invalid params** — Missing required argument or type mismatch.

- **-32603 Internal error** — Plugin caught an exception during tool execution. Never crash the main loop — wrap exceptions and return this.

### Sampling error codes (-32001 … -32009)

- **-32001 SAMPLING_NOT_GRANTED** — User has not enabled sampling grant for this Executa.

- **-32002 SAMPLING_QUOTA_EXCEEDED** — User account quota exhausted.

- **-32003 SAMPLING_PROVIDER_ERROR** — Upstream LLM provider failed.

- **-32004 SAMPLING_INVALID_REQUEST** — Malformed sampling params (e.g. `maxTokens` missing or > 8192).

- **-32005 SAMPLING_TIMEOUT** — Sampling exceeded host wall-clock budget (default 90s).

- **-32006 SAMPLING_MAX_CALLS_EXCEEDED** — Per-invoke call cap reached (default 8).

- **-32007 SAMPLING_MAX_TOKENS_EXCEEDED** — Per-invoke cumulative token cap reached (default 32k).

- **-32008 SAMPLING_NOT_NEGOTIATED** — Host didn't negotiate v2 OR manifest is missing `host_capabilities: ["llm.sample"]`.

- **-32009 SAMPLING_USER_DENIED** — User explicitly rejected this sampling request.

### Storage reverse-RPC error codes (-32021 … -32029)

- **-32021 STORAGE_NOT_GRANTED** — Missing `storage_token` or requested scope not in `allowed_scopes`.

- **-32022 NOT_FOUND** — KV key or file does not exist.

- **-32023 PRECONDITION_FAILED** — `if_match` etag check failed or generation mismatch.

- **-32024 QUOTA_EXCEEDED** — User hit the 5 GB (or plan-specific) storage cap.

- **-32025 VALUE_TOO_LARGE** — Single value exceeds the KV per-entry limit.

- **-32026 RATE_LIMITED** — Throttled by Nexus.

- **-32027 INVALID_PATH** — Path violates the design §6.4 validation rules (traversal, reserved prefix, …).

- **-32028 INVALID_REQUEST** — Generic input validation failure.

- **-32029 UPSTREAM_ERROR** — Nexus 5xx or network failure.

### Agent reverse-RPC error codes (-32041 … -32048)

- **-32041 AGENT_NOT_GRANTED** — User has not granted plugin → agent access (no `llm.agent.auto`).

- **-32042 SESSION_NOT_FOUND** — `app_session_uuid` not in host cache (likely a fresh process).

- **-32043 INVALID_REQUEST** — Malformed `agent/*` payload.

- **-32044 SUBMODE_MISMATCH** — User authorisation doesn't match requested `submode` / `fixed_client`.

- **-32045 QUOTA_EXCEEDED** — Hit user quota OR per-run 4 096-frame cap.

- **-32046 PROVIDER_ERROR** — Nexus / upstream LLM failure during the agent run.

- **-32047 RATE_LIMITED** — Throttled.

- **-32048 TOOL_NOT_GRANTED** — Tool requested is outside the user's authorised whitelist.

### Timeouts & lifecycle limits

- **INITIALIZE_TIMEOUT = 5s** — v2 handshake. Plugin must answer (even with `Method not found`) within 5s.

- **DESCRIBE_TIMEOUT = 5s** — Normal manifest fetch.

- **DESCRIBE_TIMEOUT_BINARY_COLD_START = 60s** — First spawn of a `binary` distribution: PyInstaller-style onefile bundles need to unpack, mmap, possibly Rosetta-translate on Apple Silicon.

- **HEALTH_TIMEOUT = 3s** — Liveness probe.

- **DEFAULT_INVOKE_TIMEOUT = 60s** — Per-tool override via `ToolDefinition.timeout`.

- **DEFAULT_SAMPLING_TIMEOUT = 90s** — Extra 30s headroom over invoke to cover slow / thinking models.

- **MAX_RESTART_ATTEMPTS = 3** — Host restarts a crashed plugin up to 3 times with exponential backoff (`RESTART_BACKOFF_BASE = 1.0s`) before marking it Stopped.

### Large response — file transport

- **When to use** — Any single response > 512 KiB. Otherwise the pipe buffer can deadlock both sides.

- **Pointer envelope** — Plugin writes the full JSON-RPC response to a temp file (same user, same machine, readable by host) and sends `{jsonrpc:"2.0", id, __file_transport: "/tmp/executa-resp-xxxx.json"}` on stdout.

- **Host behaviour** — Reads the file, deletes it, processes the contents as a normal response.

- **Must still flush** — The pointer line itself must be flushed — file transport only saves the **body** from going through the pipe.

### Hard rules (causes of `Stopped` plugins)

- **stdout protocol only** — Any rogue `print()` / `console.log()` / `fmt.Println()` corrupts the JSON-RPC stream.

- **Flush after every write** — Python: `sys.stdout.reconfigure(line_buffering=True)` or `flush()` per write. Go: `bufio.Writer` + `Flush()`. Rust: `BufWriter::flush()`. Node: line-buffered by default.

- **describe result is bare** — Return the manifest dict directly. `_ok(id, {"manifest": …})` → `KeyError: 'name'`, plugin gets dropped.

- **invoke result is wrapped** — Return `{"success": true, "data": …, "tool": …}`. The parser defaults `success` to `false`, so omitting it silently fails.

- **parameters[] not input_schema** — MCP-style JSON-Schema is silently ignored — the LLM ends up hallucinating argument names.

- **Unknown method → -32601** — Never crash on unknown methods; the v1/v2 fallback relies on `Method not found`.

- **Never exit() after one response** — Main loop reads stdin until EOF. Exiting early breaks sampling/agent/storage reverse RPC.

- **Credentials never in tool schema** — Declare them via `credentials[]`; receive via `context.credentials`. They must be invisible to the LLM.


---

## Spawn → initialize → describe → invoke → shutdown

*Executa · lifecycle phases*

Five phases every Executa goes through. The `initialize` handshake is what negotiates v2 capabilities (sampling, storage); a plugin that returns `Method not found` silently downgrades to v1.

- **spawn** — Anna starts the process with the user's environment; stdin/stdout/stderr piped.

- **initialize** — v2 handshake. Plugin advertises capability set; host advertises reverse-RPC support. Skipping it = v1 mode.  `5s`

- **describe** — Manifest fetch. Cached for the process's life. 60s on first launch of a binary onefile, 5s thereafter.

- **invoke (loop)** — Hot path. Each request can also unlock reverse-RPC frames (sampling/agent/storage) if v2 negotiated.  `60s/call`

- **shutdown** — Host closes stdin → SIGTERM → SIGKILL. Plugin must keep reading stdin until EOF; never `exit()` after a single response.  `5s grace`


---

## Sampling — borrow the host's LLM

*Executa · reverse RPC (v2+) · Sampling*

Let a long-running Executa plugin ask its host (Anna) to perform an LLM completion **on the user's behalf** — no API key, no model selection, no quota tracking in the plugin. Modelled on MCP `sampling/createMessage`.

**Pre-requisites** (all three required):
1. **v2 protocol negotiation.** The host's `initialize` advertises `protocolVersion: 2.0`; the plugin must respond with the same version and `client_capabilities.sampling = {}`.
2. **Manifest declaration.** `host_capabilities: ["llm.sample"]`. Missing this → `-32008 SAMPLING_NOT_NEGOTIATED`.
3. **User grant.** The user enables sampling for this Executa in Anna Admin (`UserExecuta.custom_config.sampling_grant.enabled = true`, with `maxCalls` and `maxTokensTotal` caps). Missing this → `-32001 SAMPLING_NOT_GRANTED`.

**Per-invoke caps (v1 limits):** `maxTokens` per call defaults to **8,192** (`DEFAULT_SAMPLING_MAX_TOKENS_PER_CALL`); calls per `invoke_id` cap at **8** (`DEFAULT_SAMPLING_MAX_CALLS_PER_INVOKE`); cumulative tokens per invoke cap at **32,000**; `sampling_token` TTL **600s**; only `includeContext: "none"` is supported in v1.

**Model selection precedence:** `modelPreferences.hints[*].name` (case-insensitive substring; cheapest wins when `costPriority > 0`) → user's saved `preferred_model` → default provider's cheapest active model. Plugins should normally omit `modelPreferences` so user-level preferences apply.

**Common pitfalls:** the same stdin reader receives both agent-initiated requests AND host responses to reverse RPCs (use the SDK's `dispatch_response` helper); never `exit()` after a single invoke (sampling is async); always echo `invoke_id` in `metadata` so Nexus can attribute spend.

### Sampling (v2)

- **sampling/createMessage** — Single-shot LLM completion on the user's behalf. No API key, no model picking, no metering — host routes to the user's chosen provider and bills their plan. Equivalent to MCP sampling.  `reverse-rpc`

---

## Detailed reference

### sampling/createMessage

*Reverse RPC method*

Ask the host to run an LLM completion. Returns the host result dict.

**Signature**

```ts
create_message(*, messages: List[dict], max_tokens: int, system_prompt: Optional[str] = None, temperature: Optional[float] = None, stop_sequences: Optional[List[str]] = None, model_preferences: Optional[dict] = None, include_context: str = 'none', metadata: Optional[dict] = None, timeout: float = 90.0) -> dict
```

**Direction:** Plugin → Agent

**Parameters**

- `messages` (List[dict], required) — MCP-shaped messages, e.g. ``[{"role":"user","content":{"type":"text","text":"..."}}]``
- `max_tokens` (int, required) — Required; per-call cap (host enforces hard upper bound).
- `system_prompt` (Optional[str], optional) — Optional system message.
- `temperature` (Optional[float], optional) — Optional sampling temperature. Host substitutes ``0.7`` when ``None`` — it does **not** defer to the provider default.
- `stop_sequences` (Optional[List[str]], optional) — Optional stop strings.
- `model_preferences` (Optional[dict], optional) — MCP-style ``{"hints":[{"name":"..."}], "costPriority":0..1, "speedPriority":..., "intelligencePriority":...}``. Omit (None) to let the host fall back to the user's saved ``preferred_model``.
- `include_context` (str, optional) — Reserved. Phase 1 requires ``"none"``; any other value is rejected with ``SAMPLING_ERR_INVALID_REQUEST``.
- `metadata` (Optional[dict], optional) — **Reserved / not yet consumed by host.** Forwarded on the wire but currently dropped by the Nexus gate (no audit, no logging, no propagation to token-usage records). Do not rely on it for tracing until host support lands.
- `timeout` (float, optional) — Client-side wall-clock seconds before raising ``asyncio.TimeoutError``. Also propagated to the host on the wire as ``_clientTimeoutS`` so that matrix-agent (HTTP) and nexus-gate (ChatOpenAI ``timeout`` + ``asyncio.wait_for``) can cap their own deadlines inside this budget — preventing a "ghost success" where the host completes and bills after the client has already given up. Host clamps the derived model budget to ``[30s, 300s]``.


---

## Agent sessions — multi-turn tool-using runs

*Executa · reverse RPC (v2.1+) · Agent sessions*

Drive **stateful, tool-using Anna Agent sessions** from a stdio Executa plugin through reverse JSON-RPC — the same surface area an in-iframe `anna-app` gets, with the same auth boundaries, the same tool-grant model, and the same wire frames. Builds on top of sampling: sampling is single-turn; agent sessions are stateful, support tool calls the host runs, emit streaming frames (`delta`, `tool_call`, `tool_result`, `final`), and support cancellation.

**Pre-requisites.** Manifest must declare **both** grants:
- `host_capabilities: ["llm.sample"]` — unlocks `sampling/*` and `agent/complete` (L1 single-turn).
- `host_capabilities: ["llm.agent.auto"]` — unlocks `agent/session.*` (L2 multi-turn). Missing this → `-32041 AGENT_NOT_GRANTED`.

**Auth chain.** The plugin **never holds a bearer token**. Matrix host owns the secret: the plugin sends `agent/session.create` carrying the per-invoke `sampling_token`; the host mints an `app_session_token` via Nexus `POST /copilot/app/sessions/from_sampling`, caches it keyed by `(user_id, hash(plugin_name))`, and attaches it to outbound HTTP for every `run|cancel|delete`. The token is never returned to the plugin.

**Plugin/anna-app symmetry.** A Python plugin and a TypeScript anna-app should be **drop-in interchangeable** for the same agent workload. The only difference is transport: anna-app uses a postMessage channel, plugin uses stdio JSON-RPC.

**v2 limitations.** `agent/session.run` is **buffered** — host accumulates SSE frames and returns once `done=true`. SDK API (`async for frame`) matches the future real-time path. Hard cap: **4,096 frames per run** → `-32045 QUOTA_EXCEEDED`. `agent/session.history` returns `[]` until a public GET endpoint lands.

### Agent sessions (v2.1)

- **agent/complete** — L1 one-shot completion via Anna server's `POST /copilot/app/complete`. Sugar for plugins that don't need state.  `stateless`

- **agent/session.create** — Open a stateful, tool-using agent session bound to the calling user. Identity (`user_id`, `executa_id`) is derived from the sampling_token — the plugin cannot override it.  `stateful`

- **agent/session.run** — Submit a turn; receive buffered SSE frames (`delta`, `tool_call`, `tool_result`, `final`). 4,096-frame cap per run.  `buffered streaming`

- **agent/session.history** — Read prior turns of a session. Returns `[]` until the upstream GET endpoint lands.

- **agent/session.cancel** — Abort an in-flight `run_id` on the upstream session.

- **agent/session.delete** — Idempotent teardown; drops the cached `app_session_token` and tells Nexus to delete the session.

---

## Detailed reference

### agent/session.create

*Reverse RPC method · Agent*

Open a stateful, tool-using agent session bound to the calling user. Validates `agent_submode` ∈ {auto, fixed}; `fixed_client_id` is required when `agent_submode='fixed'`. For one-shot completion use `agent/complete` instead. Identity (`user_id`, `executa_id`) is derived from the sampling_token claims — the plugin cannot override it.

**Signature**

```ts
session_create(*, agent_submode: Literal['auto','fixed'] = 'auto', fixed_client_id: str | None = None, label: str | None = None, quota_caps: dict | None = None, ttl_seconds: int = 600) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `agent_submode` (Literal['auto','fixed'], optional) — Multi-turn agent mode. `auto` rotates `client_id` per turn; `fixed` pins one.
    - `auto` is the recommended default for most plugins.
    - `fixed` additionally requires `fixed_client_id` AND a matching entry in `llm_grant.agent.allowed_fixed_client_ids`, otherwise Anna server returns `AGENT_ERR_NOT_GRANTED` (-32041).
- `fixed_client_id` (str | None, optional) — Pin one `client_id` for the whole session.
    - Only meaningful when `agent_submode='fixed'`.
    - Under `submode='auto'` it is silently stored on the session row but has no runtime effect.
    - Must appear in `llm_grant.agent.allowed_fixed_client_ids` or the call is rejected.
- `label` (str | None, optional) — Human-readable label shown in the user's session console.
    - Max 120 chars; longer values are rejected at the Anna server pydantic boundary (HTTP 422).
    - When omitted, Anna agent substitutes the plugin display name from `ctx.plugin_name`.
- `quota_caps` (dict | None, optional) — Per-session quota / tool-scope override.
    - **Default when omitted**: Anna server injects `inherit_host_tools=True`, so the agent session inherits the host Copilot's full tool kit (`granted_tools` returns `['*']`).
    - To restrict tools, pass an explicit dict, e.g. `{"inherit_host_tools": False, "allowed_tools": ["tool_a", "tool_b"]}`.
    - Anna server intersects the result with the user's grant and may clamp further; the effective value is reflected back in `granted_tools` on the response.
- `ttl_seconds` (int, optional) — Session-token lifetime in seconds; Anna agent caches the bearer for this duration.
    - Bounded by `0 < ttl_seconds ≤ MAX_APP_SESSION_TTL_SECONDS` (7200).
    - Anna server pydantic rejects out-of-range with HTTP 422; bridge has no local validation, so the failure surfaces as `AGENT_ERR_PROVIDER_ERROR` (-32046) (the generic `Exception` arm in `_session_create`), **not** `AGENT_ERR_INVALID_REQUEST`.

### agent/session.run

*Reverse RPC method · Agent*

Submit one turn on an existing agent session. The Anna agent consumes the upstream SSE stream from Anna server `/copilot/app/agent`, tags every frame with `seq` + `stream_id`, and returns the full ordered `frames` array in a single JSON-RPC response — i.e. **buffered streaming**, not true streaming. Hard-capped at `_MAX_FRAMES_PER_RUN = 4096` frames per run; exceeding the cap aborts with `AGENT_ERR_PROVIDER_ERROR` (-32046).

**Signature**

```ts
session_run(*, app_session_uuid: str, content: str, attachments: list[dict] | None = None, recursion_limit: int = 8, run_id: str | None = None, allowed_tools: list[str] | None = None, modelPreferences: dict | None = None, system: str | None = None) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `app_session_uuid` (str, required) — The session handle returned by `agent/session.create`.
    - Must start with `aps_`.
    - The Anna agent looks up the cached `app_session_token` by `(uuid, owner)`; if missing or expired → `AGENT_ERR_SESSION_NOT_FOUND` (-32042).
- `content` (str, required) — Turn content (user / plugin input).
    - Validated as a non-empty string; whitespace-only is rejected with `AGENT_ERR_INVALID_REQUEST` (-32043).
- `attachments` (list[dict] | None, optional) — Optional attachments forwarded verbatim to Anna server.
    - The Anna agent does not parse or validate the payload — shape is whatever Anna server `/copilot/app/agent` currently accepts.
- `recursion_limit` (int, optional) — Max agent tool-call depth for this turn.
    - The Anna agent does not range-check the value; it is forwarded as-is.
    - Anna server pydantic enforces `1 ≤ recursion_limit ≤ 32` (`Field(ge=1, le=32)`). Out-of-range values → HTTP 422, surfaced as `AGENT_ERR_PROVIDER_ERROR` (-32046), **not** `AGENT_ERR_INVALID_REQUEST`.
- `run_id` (str | None, optional) — Idempotency / correlation id for `session.cancel`.
    - Auto-generated as `run_{16hex}` when omitted.
    - Echoed back in the response and required by `agent/session.cancel`.
- `allowed_tools` (list[str] | None, optional) — Per-turn tool whitelist; overrides the session-level `quota_caps.allowed_tools` for this run only.
    - Forwarded verbatim to Anna server as the `allowed_tools` field.
    - Anna server intersects this with the user's grant; tools outside the grant are silently dropped.
    - Pass `[]` to disable all tools for this turn (pure LLM reply).
- `modelPreferences` (dict | None, optional) — MCP-style model hint, e.g. `{"hints": [{"name": "gpt-4o"}], "costPriority": 0.2}`.
    - Camel-case to match the MCP wire spec and Anna server's `_AgentRunBody.modelPreferences` field.
    - Snake-case alias `model_preferences` is also accepted by the bridge and rewritten on the way out.
    - Anna server may ignore hints that fall outside the user's enabled model set.
- `system` (str | None, optional) — Per-turn system prompt override; prepended to the turn on Anna server.
    - Forwarded verbatim as the `system` field on the REST body.
    - Does not mutate session state — next turn falls back to the session default unless re-supplied.

### agent/session.cancel

*Reverse RPC method · Agent*

Cancel an in-flight `session.run`. Best-effort; the upstream may still emit a final frame.

**Signature**

```ts
session_cancel(*, app_session_uuid: str, run_id: str) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `app_session_uuid` (str, required)
- `run_id` (str, required) — The `run_id` returned by (or passed into) `session.run`.

### agent/session.history

*Reverse RPC method · Agent*

Read the persisted transcript of an agent session as MCP-shaped messages. Backed by the LangGraph checkpoint that `session.run` writes into; safe to poll, idempotent, and never mutates state. Use this to rehydrate UI after a plugin restart, sync across devices, or audit a completed conversation.

**Signature**

```ts
session_history(*, app_session_uuid: str, limit: int = 50, cursor: str | None = None) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `app_session_uuid` (str, required) — The session uuid to read; must match the cached token entry.
- `limit` (int, optional) — Page size; out-of-range values are rejected.
    - Bridge-side range check (`agent.py:_session_history`): values outside `[1, 200]` raise `AGENT_ERR_INVALID_REQUEST` (-32043) — the bridge does **not** clamp silently. Anna server applies the same `[1, 200]` clamp on its side as defense in depth.
    - Counts raw checkpoint messages, not turn pairs — a single user turn that triggered N tool calls contributes `1 + 2N` entries.
- `cursor` (str | None, optional) — Opaque pagination token returned by the previous page's `next_cursor`.
    - First call: pass `None` (or omit).
    - Round-trip the value verbatim; do not parse or mutate it — the format is intentionally opaque and may switch from offset-based to time-based without protocol churn.
    - Passing a malformed cursor raises `AGENT_ERR_INVALID_REQUEST`.

### agent/session.delete

*Reverse RPC method · Agent*

Drop the session and its history. **Idempotent** — calling on an unknown or already-deleted uuid still resolves successfully. The bridge always evicts the cached token before returning, so a follow-up `session.run` against the same uuid will fail with `AGENT_ERR_SESSION_NOT_FOUND`.

**Signature**

```ts
session_delete(*, app_session_uuid: str) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `app_session_uuid` (str, required) — The session uuid to drop; must start with `aps_`.

### agent/complete

*Reverse RPC method · Agent*

L1 one-shot completion via Anna server's `POST /copilot/app/complete`. The bridge transparently mints a throw-away app session under the `sampling_token` (ttl 120s), issues the request, then deletes the session in a `finally` block — plugins never see the underlying token. **Not** sugar over `sampling/createMessage` (that path runs through the host's own model); this hits the user's Anna server. **Note:** the backing session is minted with `kind='agent'` (not `kind='complete'`) and used purely as transport — Anna server's `/copilot/app/complete` endpoint accepts any agent-kind app-session token, and the same MCP completion shape is returned. Behaviour matches the `anna-app` SDK's `llm.complete`; callers wanting a strict `kind='complete'` session row must issue `session.create({kind: 'complete'})` + the HTTP `/copilot/app/complete` path manually. Use this when you only need a single model reply with no tools and no multi-turn history; for stateful tool-using runs use `session.create` + `session.run`.

**Signature**

```ts
complete(*, messages: list[dict], maxTokens: int | None = None, modelPreferences: dict | None = None, systemPrompt: str | None = None, temperature: float | None = None, stopSequences: list[str] | None = None, metadata: dict | None = None) -> dict
```

**Direction:** Plugin → Anna agent → Anna server /copilot/app/*

**Parameters**

- `messages` (list[dict], required) — Non-empty array of MCP-shaped messages (`{role, content}`).
    - Validated bridge-side: must be a list with at least one entry.
    - Anna server applies the same schema constraints as the `anna-app` SDK; multimodal content blocks are accepted verbatim.
- `maxTokens` (int | None, optional) — Hard cap on response tokens; must be `> 0` when supplied.
- `modelPreferences` (dict | None, optional) — MCP-style model hint, e.g. `{"hints": [{"name": "gpt-4o"}], "costPriority": 0.2}`.
    - Camel-case to match the MCP wire spec and Anna server's `_CompleteBody.modelPreferences` field.
    - Anna server may ignore hints that fall outside the user's enabled model set.
- `systemPrompt` (str | None, optional) — System prompt prepended on Anna server for this single call.
- `temperature` (float | None, optional) — Sampling temperature; passes through unchanged.
- `stopSequences` (list[str] | None, optional) — Stop strings forwarded to the upstream model.
- `metadata` (dict | None, optional) — Opaque metadata echoed in audit logs; not interpreted by the model.


---

## Anna Persistent Storage (APS) — per-user KV + objects

*Executa · reverse RPC (v2+) · Persistent storage*

Give an Executa plugin a small, durable, **per-user** key/value + object store hosted by Anna — no cloud account, no DB of its own. Quota and access control are enforced by the host. After `initialize` succeeds, the plugin issues reverse JSON-RPC calls; each call carries the per-invoke `storage_token` minted by Matrix Agent.

**Pre-requisites** (all three required):
1. **v2 protocol negotiation.** Plugin advertises `client_capabilities.storage = {}` on `initialize`.
2. **Manifest declaration.** `host_capabilities: ["storage.user"]` (or `storage.app` / `storage.tool` for narrower scopes). Missing this → `-32008 not_negotiated`.
3. **User grant.** End user enables persistent storage for this Executa in Anna Admin (`UserExecuta.custom_config.storage_grant.scopes = ["user", ...]` with `quotaBytes` and `objectMaxBytes` overrides). Missing this → `-32021 STORAGE_NOT_GRANTED`.

**Scopes.** `user` — owned by the end user, visible across every plugin they grant. `app` — owned by the Anna App bundle, shared across all installs of that app for one user. `tool` — strictly local to (user × executa). Default to `tool` for transient state; ask for `user` only when the user clearly benefits from cross-tool reuse (e.g. saving a generated PDF into "My Files"). The `files/*` namespace covers all three scopes via the `scope` parameter; the legacy `user_files/*` alias family was removed.

**Best practices.** Prefer `tool` scope unless the data is genuinely user-owned. Keep KV values small — anything bigger than a few KB belongs in `files/upload_begin`. Always pass `if_match` on overwrite to avoid lost updates. Set TTLs on cache-shaped data. Encode metadata in the key (`notes/{noteId}`), not the value — keys are listable, embedded JSON fields are not. Always read back the `etag` from `storage/set` / `files/upload_complete` — never assume your client already knows it.

**Built-in user-storage tools.** For LangChain agents, Nexus auto-registers six high-level wrappers under the `user_storage_*` namespace (`user_storage_get` / `_set` / `_delete` / `_list` / `_files_save_text` / `_files_get_url`). The agent never sees the raw RPC; the tool wraps each call in a soft 5-write / 20-read per-invocation budget. Users may disable the built-in tools per-account via `UserSettings.disable_user_storage_tools`.

### KV (v2)

- **storage/get** — Read a single JSON value by `(scope, key)`.

- **storage/set** — Write a JSON value (≤ 64 KB by default). Supports `if_match` (optimistic ETag) and `ttl_seconds`. Quotas enforced by Nexus.  `if_match`

- **storage/delete** — Soft-delete a key (recoverable for 7 days).

- **storage/list** — List keys by prefix; cursor paging.

### Files (v2)

- **files/upload_begin** — Start a two-step object upload; returns a presigned PUT URL.  `presigned-PUT`

- **files/upload_complete** — Commit the upload after the PUT succeeds. Returns object id + etag.

- **files/download_url** — Mint a time-limited GET URL for an object.

- **files/list** — List objects by path prefix.

- **files/delete** — Soft-delete an object.

---

## Detailed reference

### storage/get

*Reverse RPC method · APS*

Read one entry from the plugin's **APS** (Anna Persistent Storage) KV namespace — small JSON state keyed by `(scope, key)`. Missing keys resolve to `{value: None, exists: False}` instead of raising.

**Signature**

```ts
get(*, scope: str = 'tool', key: str) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (str, optional) — ACL scope. Defaults to `tool` (per-Executa namespace).
    - `tool` — visible only to invocations of this Executa for this user (recommended default).
    - `app` — shared across all Executas owned by the same anna-app for this user.
    - `user` — user-global; access requires the host to have minted a `storage_token` whose `allowed_scopes` claim contains `user`.
    - The Agent's minted `storage_token` is what actually gates access; this argument selects the row family.
- `key` (str, required) — Entry key within the active scope (≤ 1024 chars).
    - Namespaced by `(scope, owner, key)` in Postgres — no global collision with other plugins.
    - Choose stable, opaque keys (e.g. `prefs.v1`, `cursor.gmail.inbox`); the page caches by exact key.

### storage/set

*Reverse RPC method · APS*

Write one entry to the plugin's **APS** KV namespace — full-document replace, ETag-versioned, optionally CAS-guarded by `if_match` and auto-expiring via `ttl_seconds`.

**Signature**

```ts
set(*, scope: str = 'tool', key: str, value: Any, if_match: str | None = None, metadata: dict | None = None, tags: list[str] | None = None, ttl_seconds: int | None = None) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (str, optional) — ACL scope. Defaults to `tool` (per-Executa namespace).
    - `tool` / `app` / `user` — same semantics as `storage/get`.
    - Requires manifest `storage.write`. Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim (`user` / `app` / `tool`).
- `key` (str, required) — Entry key within the active scope (1–1024 chars).
    - Namespaced by `(scope, owner, key)`; no global collision with other plugins.
    - Validated by `validate_kv_key` server-side; rejected as `STORAGE_ERR_INVALID_REQUEST` on empty/oversize.
- `value` (Any, required) — JSON-serialisable payload. **Replaces** the previous value verbatim.
    - Serialised by `_serialize_value` to canonical UTF-8 JSON; the byte length must be ≤ 256 KB.
    - There is no server-side merge / JSON-patch — to update a sub-field, do read → mutate → set with `if_match`.
    - ETag is `sha256(payload)[:32]`, so writing the same value twice yields the same ETag but still bumps `generation`.
- `if_match` (str | None, optional) — Optimistic concurrency token. Pass the `etag` you previously read.
    - Mismatch → `STORAGE_ERR_PRECONDITION_FAILED` (HTTP 412); quota reservation is rolled back.
    - `None` (default) is unconditional write — last-writer-wins. Use only for keys you know are single-writer.
    - First-time create: pass `None`; there is no separate `if-none-match` mode.
- `metadata` (dict | None, optional) — Opaque per-entry metadata. **Overwrites** the stored dict; not a merge.
    - Stored on the row and echoed back by `storage/get` and `storage/list`; never used by the server for routing or filtering.
    - Passing `None` is treated as `{}` on write — i.e. it clears existing metadata.
- `tags` (list[str] | None, optional) — Up to 32 short labels for client-side filtering.
    - Surfaced in `storage/list` items so callers can sort/filter without re-reading values.
    - `None` keeps no tags; an empty list also clears.
- `ttl_seconds` (int | None, optional) — Auto-expire after N seconds (1 .. 31_536_000, i.e. 1 second to 1 year).
    - Stored as an absolute `expires_at` timestamp; expired entries are filtered out of `get`/`list` (lazy delete).
    - Omit (`None`) for permanent state. Updating an existing entry **replaces** `expires_at` — pass it on every write if you want a sliding TTL.

### storage/delete

*Reverse RPC method · APS*

Soft-delete one entry from the plugin's **APS** KV namespace. The row stays in Postgres (recoverable), but quota is released immediately and subsequent `storage/get`/`storage/list` treat the key as gone.

**Signature**

```ts
delete(*, scope: str = 'tool', key: str, if_match: str | None = None) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (str, optional) — ACL scope — same semantics as `storage/get` (`tool` / `app` / `user`).
    - Requires manifest `storage.write`. Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim (`user` / `app` / `tool`).
- `key` (str, required) — Exact key to delete within the active scope (1–1024 chars).
    - Exact match only — there is no glob / prefix delete. To bulk-remove, page through `storage/list(prefix=…)` and call `delete` per key.
    - Validated by `validate_kv_key`; empty or oversize → `STORAGE_ERR_INVALID_REQUEST`.
- `if_match` (str | None, optional) — Optional CAS guard. Pass the `etag` from your last read to avoid deleting a key that was updated in between.
    - Mismatch → `STORAGE_ERR_PRECONDITION_FAILED` (HTTP 412); the row is **not** touched.
    - `None` is an unconditional delete — only safe for keys you know are single-writer.

### storage/list

*Reverse RPC method · APS*

Enumerate the plugin's **APS** KV keys (alphabetical, cursor-paginated). Returns metadata heads only — `value` is **not** included; re-read with `storage/get` for any key you actually need.

**Signature**

```ts
list(*, scope: str = 'tool', prefix: str = '', cursor: str | None = None, limit: int = 100) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (str, optional) — ACL scope — same semantics as `storage/get` (`tool` / `app` / `user`).
    - Listing is per-scope; the same key in `tool` and `app` is reported separately if you list each scope.
    - Requires manifest `storage.read`. Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim (`user` / `app` / `tool`).
- `prefix` (str, optional) — Filter keys that start with this string. Empty = list everything in the scope.
    - Forward-match only — no glob or regex. Matching is byte-wise on the raw key.
    - Validated like a key path: ≤ 1024 chars, no leading `/`, no `.` / `..` segments, no forbidden characters.
    - Trailing `/` is allowed (e.g. `prefix='cursor/'`); empty trailing segments are tolerated.
- `cursor` (str | None, optional) — Opaque continuation token returned by a previous call as `next_cursor`.
    - Encodes the last-seen key; pages walk strict ascending order (`path > cursor`).
    - Treat as opaque — do not parse, persist long-term, or share across scopes/prefixes.
    - Pass `None` (or omit) for the first page.
- `limit` (int, optional) — Page size, 1 .. 1000 (default 100).
    - Out-of-range values are silently clamped by the server (`max(1, min(limit, 1000))`).
    - The server fetches `limit + 1` rows to decide whether `next_cursor` is set; cost is O(limit).

### files/upload_begin

*Reverse RPC method · APS*

Phase 1 of the two-phase Files (object) upload — reserves an APS object entry (marked `__pending=true`), soft-deducts the declared `size_bytes` from the user's APS quota, and returns a short-lived presigned PUT URL into APS object storage. The plugin then `PUT`s the bytes directly to that URL and calls `files/upload_complete` to flip the entry from pending to durable.

**Signature**

```ts
uploadbegin(*, scope: Literal['user','app','tool'] = 'app', path: str, size_bytes: int, content_type: str | None = None, metadata: dict[str, str] | None = None, timeout: float = 60.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (Literal['user','app','tool'], optional) — ACL scope. Files namespace defaults to `app` (shared across the anna-app's tools).
    - `tool` — visible only to invocations of this Executa for this user.
    - `app` — shared across all Executas owned by the same anna-app for this user (recommended for files the user-visible app surfaces, e.g. attachments).
    - `user` — user-global; intended for files the user uploaded via the Anna chat UI. Reading these requires the storage_token's `allowed_scopes` claim to contain `user`.
    - The Agent's minted `storage_token` is what actually gates access; this argument selects the row family. Unauthorised scope → `STORAGE_ERR_NOT_GRANTED` (`-32021`).
- `path` (str, required) — Logical file path within the chosen scope (e.g. `reports/2026/q1.pdf`).
    - Validated server-side by `validate_path`: 1..1024 chars, relative (no leading `/`), segments are non-empty and not `.` / `..`, no ASCII control chars / backslashes / zero-width / BiDi control characters; segments may not start/end with whitespace.
    - Invalid → `STORAGE_ERR_INVALID_PATH` (`-32027`). The returned path is canonicalised (redundant `/` collapsed) and used verbatim as the APS object key.
    - Namespaced by `(scope, owner, path)`; collisions with other plugins/users are impossible.
    - Re-using an existing path is allowed — the row is row-locked (`SELECT … FOR UPDATE`) and rewritten in place; pass `if_match` (server-side only — not exposed by the SDK) to guard against concurrent writers.
- `size_bytes` (int, required) — Declared byte length of the upload (0 .. 256 MB).
    - Hard cap is `OBJECT_MAX_BYTES = 256 * 1024 * 1024`. Exceed → `STORAGE_ERR_VALUE_TOO_LARGE` (`-32025`, HTTP 413). Zero-byte uploads are accepted.
    - Used to **soft-reserve** quota (`storage_quota_service.reserve(soft=True, ttl_seconds=600)`). Only the *delta* over an existing entry's `size_bytes` is reserved; pure overwrites of the same size cost nothing.
    - The reservation is auto-released by Redis after 10 min if `files/upload_complete` never lands; the row's `__pending` flag stays until a reaper cleans it.
    - Reservation failure → `STORAGE_ERR_QUOTA_EXCEEDED` (`-32024`); the call rolls back before any presign happens.
    - Honour the value you declare — APS object storage accepts any size and `files/upload_complete` writes the **actual** size, but quota accounting is based on this number until finalize reconciles.
- `content_type` (str | None, optional) — MIME type of the upload. **Effectively required** despite the optional Python type.
    - The Nexus body schema (`_FilesInitBody`) declares `content_type: str` as required (max 120 chars). Omitting it from the SDK call ⇒ FastAPI 422 surfaced as `STORAGE_ERR_INVALID_REQUEST` (`-32028`); empty/oversize ⇒ `STORAGE_ERR_INVALID_PATH` (`-32027`).
    - Echoed into the presigned URL's signed `Content-Type` query parameter — your subsequent `PUT` **must** send the same `Content-Type` header (the response's `headers` dict supplies it) or APS rejects the upload with 403 SignatureDoesNotMatch.
    - Stored on the row and surfaced by `files/list` / `files/download_url`. Pick something the consumer will use to choose a viewer (e.g. `application/pdf`, `image/png`); browsers also honour it on signed GETs unless `disposition` overrides.
- `metadata` (dict[str, str] | None, optional) — Opaque per-entry metadata. **Replaces** the stored dict (no merge).
    - Server adds `__pending=True` and, when a soft reservation is taken, `__reservation_token=<…>` to the dict before persisting; both are stripped by `files/upload_complete`. Do not use keys starting with `__`.
    - Echoed back by `files/list` and `storage/get` (for objects). Never used by the server for routing or filtering.
    - Passing `None` is treated as `{}` on write — it clears any metadata the previous version of the entry carried.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 60s).
    - Client-side only — the Agent → Nexus hop has its own 15s `request_timeout_s` (`DEFAULT_REQUEST_TIMEOUT_S` in `matrix/src/executa/storage.py`). Bumping the SDK timeout does not lift the upstream HTTP timeout.
    - On expiry the call raises the SDK's RPC timeout error, not a storage error.

### files/upload_complete

*Reverse RPC method · APS*

Phase 2 of the two-phase Files (object) upload — APS verifies that the bytes landed against the entry reserved by `files/upload_begin`, replaces the placeholder ETag with the canonical APS-computed object ETag, reconciles `size_bytes` against the actual uploaded size (positive delta is hard-deducted from quota, negative delta is refunded), strips the `__pending` flag, and returns the durable `ObjectEntry`.

**Signature**

```ts
uploadcomplete(*, scope: Literal['user','app','tool'] = 'app', path: str, etag: str | None = None, size_bytes: int | None = None, content_type: str | None = None, timeout: float = 60.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (Literal['user','app','tool'], optional) — ACL scope. **Must match** the scope you used at `upload_begin` (rows are scoped).
    - Mismatched scope → `STORAGE_ERR_NOT_FOUND` (row lookup fails); the pending row in the original scope still expires after 10 min and is reaped.
    - Per-scope authorisation is enforced by the `storage_token`'s `allowed_scopes` claim.
- `path` (str, required) — Same logical path you passed to `files/upload_begin` (re-validated server-side).
    - Looked up via `(scope, owner, path)` with a row lock (`SELECT … FOR UPDATE`).
    - If the row is missing or not in `mode='object'` → `STORAGE_ERR_NOT_FOUND` (`-32022`).
    - If the row exists but the `__pending` flag was already cleared (re-finalize after success, or a `path` that was never started via `upload_begin`) → `STORAGE_ERR_NOT_FOUND` ("object not pending finalize"). Finalize is **not** idempotent — call it exactly once per begin.
- `etag` (str | None, optional) — ETag you read from the presigned `PUT` response. **Stored but not verified** by APS.
    - Despite the field name, APS does **not** compare your `etag` to the stored object's ETag — it queries the object directly and uses the canonical APS-computed ETag (truncated to 64 chars). Pass it anyway for parity with the SDK signature and forward-compat.
    - If APS cannot verify the uploaded object (it never landed, wrong key, transient object-store outage) the call raises `pending_upload`, surfaced by the host as `STORAGE_ERR_UPSTREAM` (`-32029`).
    - ETag length is capped at 64 chars — APS truncates rather than rejecting.
- `size_bytes` (int | None, optional) — Actual uploaded size — **advisory**. APS uses its own measured size, not yours.
    - Quota reconciliation compares the APS-measured object size to the entry's stored `size_bytes` (the value you declared at `upload_begin`). Positive diff → hard-reserve from quota (may raise `STORAGE_ERR_QUOTA_EXCEEDED`); negative diff → refund.
    - Your `size_bytes` argument here is **not used** for reconciliation; only kept on the signature for SDK convenience. Tracking your local byte count is still useful for logs.
- `content_type` (str | None, optional) — Forwarded to Nexus but **silently dropped** by the current REST schema.
    - `_FilesFinalizeBody` only declares `path` / `etag` / `size_bytes` / `metadata`; FastAPI ignores extra fields. To change `content_type` after finalize there is no supported call — re-upload from scratch.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 60s).
    - Independent of the Agent → APS HTTP timeout (15s) and APS's own verification budget. Bumping this does not lift the upstream limits.

### files/download_url

*Reverse RPC method · APS*

Mint a short-lived presigned `GET` URL for a previously finalised object. The plugin (or the end user, if you hand the URL back) fetches the bytes **directly from APS object storage** — the agent host never proxies the body.

**Signature**

```ts
downloadurl(*, scope: Literal['user','app','tool'] = 'app', path: str, ttl_seconds: int = 300, expires_in: int | None = None, timeout: float = 60.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (Literal['user','app','tool'], optional) — ACL scope — must match the scope under which the object was uploaded.
    - Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim.
    - Cross-scope lookups are impossible: rows are namespaced by `(scope, owner, path)`.
- `path` (str, required) — Logical file path (re-validated server-side by `validate_path`).
    - Looked up via `(scope, owner, path)`; missing row → `STORAGE_ERR_NOT_FOUND` (`-32022`).
    - Row must be finalised — if it is still `__pending=true` (begin happened, complete didn't) the call raises `pending_upload` mapped to `STORAGE_ERR_UPSTREAM` (`-32029`).
    - Invalid path syntax → `STORAGE_ERR_INVALID_PATH` (`-32027`).
- `ttl_seconds` (int, optional)
- `expires_in` (int | None, optional) — **Currently a no-op via the SDK** — the REST endpoint reads `ttl`, not `expires_in`.
    - Nexus query parameter is `ttl: int = Query(300, ge=1, le=3600)`. The SDK forwards your value as `?expires_in=...`, which FastAPI silently ignores; the URL always lives **300 s** (5 min) until the SDK is updated.
    - Hard cap on the server is **3600 s** (1 h). Calling the REST endpoint directly with `?ttl=N` is the only way to override today.
    - If you need long-lived sharing, mint a fresh URL on demand rather than caching one.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 60s).
    - Independent of the 15s Agent→Nexus HTTP timeout; this only bounds the SDK wait.

### files/list

*Reverse RPC method · APS*

Enumerate finalised objects under a path prefix in the plugin's APS Files namespace (alphabetical by `path`, cursor-paginated). Returns metadata heads only — to download the bytes call `files/download_url` per entry.

**Signature**

```ts
list(*, scope: Literal['user','app','tool'] = 'app', prefix: str | None = None, cursor: str | None = None, limit: int | None = None, timeout: float = 60.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (Literal['user','app','tool'], optional) — ACL scope — same semantics as `files/upload_begin`. Files default to `app`.
    - Listing is per-scope; the same path under `tool` and `app` is reported separately if you list each scope.
    - Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim (`user` / `app` / `tool`).
- `prefix` (str | None, optional) — Forward-match filter on `path`. Empty (or `None`) lists everything in the scope.
    - Validated loosely (length ≤ 1024, must not start with `/`); unlike `validate_path` the segments **may** be empty, so trailing `/` like `prefix='reports/'` works.
    - Forward-match only — no glob/regex/suffix search. Matching is byte-wise on the raw path.
    - SQL `LIKE` with backslash-escaped wildcards — caller-supplied `%` / `_` characters are matched literally, not as wildcards.
- `cursor` (str | None, optional) — Opaque continuation token returned by a previous call as `next_cursor`.
    - Encodes the last-seen path; pages walk strict ascending order (`path > cursor`).
    - Treat as opaque — do not parse, persist long-term, or share across scopes/prefixes.
    - Pass `None` (or omit) for the first page.
- `limit` (int | None, optional) — Page size, **1 .. 1000** (default 100).
    - Out-of-range values raise `STORAGE_ERR_INVALID_PATH` (`-32027`) at the service layer; the REST endpoint also rejects with HTTP 422 via `Query(100, ge=1, le=1000)`.
    - The server fetches `limit + 1` rows to decide whether `next_cursor` is set; cost is O(limit).
    - When the SDK omits this, Nexus picks the server default of 100.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 60s).
    - Independent of the 15s Agent→Nexus HTTP timeout.

### files/delete

*Reverse RPC method · APS*

Soft-delete one finalised object from the plugin's APS Files namespace. The entry is tombstoned (`is_deleted=True`), the byte quota is **immediately** released, and the entry vanishes from `files/list` / `files/download_url`. The underlying APS object is kept for retention until a reaper job purges it.

**Signature**

```ts
delete(*, scope: Literal['user','app','tool'] = 'app', path: str, timeout: float = 60.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST

**Parameters**

- `scope` (Literal['user','app','tool'], optional) — ACL scope — must match the scope under which the object was uploaded.
    - Cross-scope deletes are impossible: rows are namespaced by `(scope, owner, path)`.
    - Requires manifest `storage.write`. Per-scope access is gated by the `storage_token`'s `allowed_scopes` claim.
- `path` (str, required) — Exact logical path to delete (re-validated server-side).
    - Exact match only — no glob / prefix delete. To bulk-remove, page through `files/list(prefix=…)` and call `files/delete` per path.
    - Missing or wrong-mode row → `STORAGE_ERR_NOT_FOUND` (`-32022`). Unlike `files/download_url`, **pending uploads can be deleted** — the row is dropped and the soft reservation is released by Redis after its TTL.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 60s).
    - Independent of the 15s Agent→Nexus HTTP timeout.


---

## Embeddings — borrow the host's embedding model

*Executa · reverse RPC (v2+) · Embeddings*

Let a long-running Executa plugin ask its host (Anna) to compute dense embedding vectors **on the user's behalf** — no provider API key, no model name leaked to the plugin, no per-plugin billing. Sibling of `sampling/createMessage` but on an **independent billing surface** (`LLMRequestType.EXECUTA_EMBED`), so exhausting your chat quota does not block RAG / semantic-search workloads and vice-versa.

**Pre-requisites** (all four required):
1. **v2 protocol negotiation.** Plugin advertises `client_capabilities.embed = {}` on `initialize` (the existing `client_capabilities.sampling = {}` also works — the same `sampling_token` is reused for both surfaces). Missing → `-32507 EMBED_NOT_NEGOTIATED`.
2. **Manifest declaration.** `host_capabilities: ["llm.embed"]`. Missing → `-32501 EMBED_NOT_GRANTED`.
3. **User install / grant.** `UserExecuta.is_enabled = true`. Optional explicit opt-out via `UserExecuta.custom_config.embed_grant = {enabled: false}` → `-32508 EMBED_USER_DENIED`. Default when omitted: enabled.
4. **Platform switch.** `EMBED_API_ENABLED = true` (default). Setting to `false` shuts down both the plugin reverse-RPC path AND the iframe `llm.embed` path with `-32507`.

**Stable alias contract.** The plugin only sees host-stable aliases (`anna-managed-v1` → 1536-dim today). Real provider model name surfaces in `_meta.backendModel` for audit. Dimensions are **immutable per alias** — upgrades go to a new alias (`anna-managed-v2`), never an in-place dimension change. Persist `_meta.alias` + `_meta.dimensions` next to every stored vector so cross-version reads can refuse-or-reindex.

**Reject-not-truncate.** Batch > 64 items or any item > 32 000 chars fails the *whole* request with `-32504 EMBED_INVALID_REQUEST` — chunk client-side and keep an index map. Provider errors are flattened to a single `-32503 EMBED_PROVIDER_ERROR` (upstream status not preserved).

**Local-dev gotcha.** Both the python harness bridge (`matrix-nexus/packages/anna-app-runtime-local/.../executa.py` `SERVER_REQUEST_METHODS`) AND the Node `LlmBridge` (`anna-app-cli/src/harness/server.ts` `HOST_OUTBOUND_ROUTES`) must list `embeddings/create` → `(llm, embed)`. Either missing → `-32601 Method not found`.

### Embeddings (v2)

- **embeddings/create** — Compute dense embedding vectors for one or many strings; returns OpenAI-shaped `{model, data:[{index,embedding}], usage, _meta}` where `model` is the host-stable alias and `_meta.dimensions` is the immutable per-alias dim.  `reverse-rpc` `OpenAI-shape`

### Manifest declaration (plugin side)

- **host_capabilities** — Array including `"llm.embed"`. The Agent uses this to decide whether to mint a `sampling_token` carrying embed authority for the invoke.  `required`

- **client_capabilities.embed** — Empty object `{}` advertised on `initialize` for v2 negotiation. `client_capabilities.sampling` also works — same token.

### Common errors (full list in detail page)

- **EMBED_NOT_GRANTED (-32501)** — Missing sampling_token, UserExecuta row missing / disabled, or manifest does not declare `llm.embed`.

- **EMBED_INVALID_REQUEST (-32504)** — Empty / oversize batch, item > 32 KB, non-string input, unknown alias, or `executa_tool_id` / `tool_invoke_id` body disagree with the JWT claims.

- **EMBED_PROVIDER_ERROR (-32503)** — Provider timeout / rate-limit / 5xx, or non-object body. Upstream error code is NOT preserved.

- **EMBED_NOT_NEGOTIATED (-32507)** — Plugin disabled the client (e.g. v1 negotiated) OR platform-wide `EMBED_API_ENABLED=false`.

- **EMBED_USER_DENIED (-32508)** — User explicitly set `embed_grant.enabled=false` for this Executa.

---

## Detailed reference

### embeddings/create

*Reverse RPC method · Embeddings*

Compute one or more dense embedding vectors **on the user's behalf** from a stdio Executa plugin — no provider API key, no model name leaked to the plugin, no per-plugin billing. The host owns the registry; the plugin only sees a stable alias (`anna-managed-v1` → 1536-dim) and gets back an OpenAI-compatible envelope. Independent from `sampling/createMessage` and `agent/*`: shares the same `sampling_token` mint flow but bills against an **independent embed surface** (`LLMRequestType.EXECUTA_EMBED`) — exhausting your LLM quota does not block embeddings and vice-versa.

**Pre-requisites** (all four required):
1. **v2 protocol negotiation.** Plugin advertises `client_capabilities.embed = {}` (or `client_capabilities.sampling = {}` — the same token is reused) on `initialize`. Without v2 the reverse-RPC returns `EMBED_NOT_NEGOTIATED` (-32507).
2. **Manifest declaration.** `host_capabilities: ["llm.embed"]`. Missing this → `EMBED_NOT_GRANTED` (-32501) at first call.
3. **User grant.** End user has the Executa enabled (`UserExecuta.is_enabled=true`). Optional explicit opt-out via `UserExecuta.custom_config.embed_grant = {enabled: false}` → `EMBED_USER_DENIED` (-32508). Default when omitted: enabled.
4. **Platform switch.** `EMBED_API_ENABLED = true` (default). Setting to `false` shuts down **both** the iframe `llm.embed` path and the plugin `embeddings/create` path with `EMBED_NOT_NEGOTIATED`.

**Auth chain.** Plugin only ever holds a `sampling_token` — the same token Matrix Agent injected for `sampling/createMessage`. The Agent forwards the reverse-RPC body to Nexus `POST /api/v1/copilot/embeddings` with `Authorization: Bearer <sampling_token>`; Nexus decodes the token claims (`user_id`, `executa_tool_id`, `tool_invoke_id`), enforces equality with the body fields, then dispatches into the embedding registry. The plugin never sees a bearer to a provider, never sees a real model name, and cannot impersonate another user.

**Signature**

```ts
EmbeddingsClient.create(*, input: str | Sequence[str], model: str | None = None, timeout: float = 30.0) -> dict
```

**Direction:** Plugin → Matrix Agent → Nexus `POST /api/v1/copilot/embeddings` → embedding registry → provider

**Parameters**

- `input` (str | list[str], required) — Text(s) to embed. A bare string is auto-wrapped to a single-element list before sending. Empty / whitespace-only strings are rejected.
    - Bridge-side hard caps (defence-in-depth before the HTTP boundary): `_HARD_MAX_INPUTS = 128`, `_HARD_MAX_INPUT_CHARS = 64_000` per item. Either limit overrun → `EMBED_INVALID_REQUEST` (-32504) **at the Agent**, never reaches Nexus.
    - Server-side caps from Nexus settings (`EMBED_MAX_INPUTS_PER_REQUEST = 64`, `EMBED_MAX_CHARS_PER_INPUT = 32_000`) are stricter and authoritative; the bridge values are just a wire safety net.
    - Per-spec cap from the embedding registry (`spec.max_inputs_per_request`) is intersected with the global ceiling — `anna-managed-v1` matches the global default.
    - Reject-not-truncate: a single 33 KB input fails the whole batch — chunk client-side.
- `model` (str | None, optional) — Host-stable **alias** — NOT a provider model name. Resolved server-side by `EmbeddingRegistry.resolve(alias)`. Unknown alias → `EMBED_INVALID_REQUEST` (-32504) with the available alias list in the error message.
    - Today's registered aliases (production): `anna-managed-v1` (= `openai/text-embedding-3-small`, 1536-dim). `anna-managed-v2` is **only registered when** `EMBEDDING_ENABLE_V2 = true` (rollout flag, default `false`).
    - **Dimensions are a contract.** Once an alias ships at N dims, it never changes — upgrades go to a new alias (e.g. `anna-managed-v2`). Persist `_meta.alias` + `_meta.dimensions` alongside any vector you store so cross-version reads can refuse-or-reindex gracefully.
    - Real provider model name is returned in `_meta.backendModel` for audit only — do not branch on it.
- `timeout` (float (seconds), optional) — Client-side wall-clock timeout. `asyncio.TimeoutError` raised locally as `EmbeddingsError(code=EMBED_TIMEOUT)` if no host response arrives in time.
    - Independent of `EMBED_REQUEST_TIMEOUT` (default 30 s) which gates the **upstream HTTP call** Nexus makes to the provider — leave headroom for that plus retries.
    - Local timeout drops the pending future; if the host eventually replies the response is discarded silently.


---

## LLM image generation & editing

*Executa · reverse RPC (v2+) · LLM image*

Let an Executa plugin **ask the host's LLM stack to generate or edit images** — no provider key, no R2 credentials, no per-plugin billing. Anna routes to the user's preferred image provider (DALL·E 3 / SDXL / FLUX / …), bills the user's plan, stores the bytes on host R2, and hands the plugin short-lived HTTPS URLs.

**Pre-requisites** (all four required):
1. **v2 protocol negotiation.** Plugin advertises `client_capabilities.image = {}` on `initialize`.
2. **Manifest declaration.** `host_capabilities: ["llm.image"]` for `generate`; add `"llm.image.edit"` for `edit`. Missing → `IMAGE_NOT_GRANTED` (`-32101`) at first call.
3. **User grant.** End user enables image in Anna Admin (`UserExecuta.custom_config.image_grant = {generate: true, edit?: true, max_images_per_day: N, max_per_call: M, model_hints?: [...]}`).
4. **Active image-capable plan.** User must have ≥ 1 enabled image provider; otherwise → `NO_MODEL_AVAILABLE` (`-32109`).

**Three layered quota gates** (you must handle each distinctly):
- **Host hard cap** — `_MAX_N = 8` per call (`matrix/src/executa/image.py`).
- **Per-call grant** — `max_per_call_generate` (default 4) / `max_per_call_edit` (default 1).
- **Per-invoke rolling cap** — `max_images` (default 4) tracked in Redis `img:invoke:{tool_invoke_id}` with 30-min TTL; shared across all `generate`+`edit` calls inside one `invoke_id`.

All three surface as `IMAGE_MAX_IMAGES_EXCEEDED` (`-32106`). Returned image URLs expire in ~30 min (`R2_TRANSIENT_PRESIGN_EXPIRY = 1800s`) — `GET` the bytes (or round-trip through `host/uploadFile`) for durable storage.

**Best practices.** Always inject `metadata.executa_invoke_id` so billing rows correlate. Set `timeout ≥ 60s` — cold-start providers (DALL·E 3, FLUX) often need 30–60s. Treat `IMAGE_ERR_PROVIDER_ERROR` with `data.subcall == "image"` as 'upstream timeout, do not retry immediately'. Prefer `image/edit` with a single `image_url` over `image/generate` with `reference_image_urls` when you have a source image — better fidelity, no inbound-fetch quota cost.

### Methods

- **image/generate** — Generate N images from a text prompt; optional `size`, `reference_image_urls` (≤ 4), `model_preferences`. Returns transient host-stored HTTPS URLs.  `n ≤ 8`

- **image/edit** — Mutate an existing `image_url` per a text prompt; optional `mask_url` (provider-dependent). Returns new transient URLs — source image is not modified.  `edit grant`

### Manifest declaration (plugin side)

- **host_capabilities** — Array including `"llm.image"` (for generate) and/or `"llm.image.edit"` (for edit). The Agent uses these to decide whether to mint an `image_token` for the invoke.  `required`

- **client_capabilities.image** — Empty object `{}` advertised on `initialize` for v2 negotiation.

### Common errors (full list in detail page)

- **IMAGE_NOT_GRANTED (-32101)** — Missing grant, disabled executa, or manifest doesn't declare the capability.

- **IMAGE_MAX_IMAGES_EXCEEDED (-32106)** — Host hard-cap (8), per-call grant, or per-invoke rolling counter exhausted.

- **IMAGE_PROVIDER_ERROR (-32103)** — Provider 5xx / safety refusal / **upstream timeout** (`data.subcall == "image"`).

---

## Detailed reference

### image/generate

*Reverse RPC method · Image*

Ask the host to generate **N images from a text prompt** on the user's behalf. The plugin ships no provider API key, holds no R2 credentials, and pays no quota of its own — Anna routes through the user's preferred image provider (DALL·E 3, Stable Diffusion XL, FLUX, …), bills the user's plan, persists the bytes to host storage, and returns short-lived HTTPS URLs.

**Signature**

```ts
generate(*, prompt: str, n: int = 1, size: str | None = None, reference_image_urls: list[str] | None = None, model_preferences: dict | None = None, metadata: dict | None = None, timeout: float = 120.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST → Image provider

**Parameters**

- `prompt` (str, required) — Non-empty natural-language description of the image you want.
    - Validated by `_validate_generate` in `matrix/src/executa/image.py`: empty or whitespace-only → `IMAGE_ERR_INVALID_REQUEST` (`-32104`).
    - Forwarded verbatim to the provider. Anna does **not** rewrite, translate, or moderate the prompt; provider-side safety filters apply (DALL·E 3 may refuse and surface as `IMAGE_ERR_PROVIDER_ERROR`).
- `n` (int, optional) — Number of images to generate in one call. Three independent caps apply — each surfaces a **different** error code.
    - **Host hard cap `_MAX_N = 8`** (`matrix/src/executa/image.py`). Enforced by the matrix Agent's `_validate_generate` BEFORE the request leaves the plugin host. `n > 8` → `MAX_IMAGES_EXCEEDED` (`-32106`) with `data.hostCap = 8`.
    - **Per-call grant cap** = `image_token.max_per_call_generate` (default **4**, `DEFAULT_IMAGE_MAX_PER_CALL_GEN`). Enforced by the Nexus gate AFTER token decode. `n > max_per_call_generate` → `IMAGE_PER_CALL_EXCEEDED` (`-32107`).
    - **Per-invoke rolling counter** `img:invoke:{tool_invoke_id}` (Redis HASH `images` field, **30-min TTL** = `_INVOKE_TTL_SECONDS`). Caps the cumulative total across all `image/generate` + `image/edit` calls in the same `tool_invoke_id` at `image_token.max_images` (default **4** = `DEFAULT_IMAGE_MAX_IMAGES`). Exceed → `MAX_IMAGES_EXCEEDED` (`-32106`) with `data.images` and `data.maxImages` set.
    - Not every provider supports `n > 1` (DALL·E 3 does not). The host attempts to batch and silently degrades to N serial single-image calls when the provider can't batch — billing is identical; latency is N×.
- `size` (str | None, optional) — Requested pixel dimensions as `"WxH"` (e.g. `"1024x1024"`, `"1792x1024"`).
    - REST schema default is `"1024x1024"` (see `_ImageGenerateBody.size` in `matrix-nexus/src/api/copilot_image.py`); omitting on the SDK lets Nexus apply that default.
    - Provider-specific. DALL·E 3 supports `1024x1024` / `1792x1024` / `1024x1792`; SDXL/FLUX accept arbitrary multiples of 8 up to provider limit. Invalid size → `IMAGE_ERR_INVALID_REQUEST`.
    - The actually-returned `width` / `height` may differ if the provider rounds; always read them from the response, not from `size`.
- `reference_image_urls` (list[str] | None, optional) — Up to 4 HTTPS URLs to feed as style / composition references (provider-dependent).
    - Hard cap **4** entries (`_MAX_REFERENCE_IMAGES`); exceed → `IMAGE_ERR_INVALID_REQUEST`. Non-string entries → same error.
    - Each URL passes `validate_image_url` server-side (HTTPS only, host allowlist, anti-SSRF); unreachable or rejected URLs surface as `IMAGE_ERR_REFERENCE_FETCH_FAILED` (`-32314`).
    - Each fetched reference counts against the user's monthly bandwidth quota; keep the count small.
    - Most providers ignore the field outright. Stable Diffusion XL with IP-Adapter respects it; DALL·E 3 does not. Use `image/edit` instead when you have a single source image to mutate.
- `model_preferences` (dict | None, optional) — MCP-style model hint, e.g. `{"hints": [{"name": "dall-e-3"}]}`. Sent on the wire as `modelPreferences` (camelCase).
    - Resolution order: `model_preferences.hints[*].name` (case-insensitive substring) → `image_token.model_hints` (set from the user's grant) → user's `preferred_image_model` → cheapest active image model on their plan.
    - Hints are advisory — if no enabled provider matches, the host falls back to the user's preferred model. No error is raised.
    - Omit unless you have a strong reason; user-level preferences are usually the right answer.
- `metadata` (dict | None, optional) — Opaque audit metadata. **Always inject `{"executa_invoke_id": invoke_id}`** so billing rows correlate.
    - Echoed into the LLM usage log; never affects routing or pricing.
    - Do NOT put PII or credentials here — usage rows are visible to the user in Anna Admin.
- `timeout` (float, optional) — SDK-side per-call deadline in seconds (default 120 s; `ImageClient.DEFAULT_TIMEOUT`).
    - The SDK does **not** forward `timeout` to the Agent automatically. To make the host honour the same deadline, the SDK passes `params._clientTimeoutS` (the matrix Agent reads it via `_resolve_image_timeout` and strips it before calling Nexus).
    - Agent default if `_clientTimeoutS` is absent: `IMAGE_DEFAULT_REQUEST_TIMEOUT_S = 180 s`. Channel-level hard cap: `IMAGE_MAX_REQUEST_TIMEOUT_S = 240 s` (`matrix/src/executa/image.py`) — any larger value is clamped down.
    - Local SDK timeout raises `ImageError(IMAGE_ERR_TIMEOUT, -32105)` from `asyncio.wait_for`. An upstream timeout (matrix Agent → Nexus → provider) surfaces as `ImageError(IMAGE_ERR_PROVIDER_ERROR, -32103)` with `data.subcall == "image"` and `data.timeout_s` set — match on `data.subcall` to differentiate provider 5xx from upstream timeout.
    - Cold-start providers (DALL·E 3, FLUX) routinely take 30–60 s. Do not set `timeout < 60 s`.

### image/edit

*Reverse RPC method · Image*

Mutate an existing image according to a text prompt — full-image restyle, or masked region inpainting if the provider supports it. Same auth/billing/storage envelope as `image/generate`; the only differences are an `image_url` input and optional `mask_url`.

**Signature**

```ts
edit(*, image_url: str, prompt: str, mask_url: str | None = None, n: int = 1, size: str | None = None, model_preferences: dict | None = None, metadata: dict | None = None, timeout: float = 120.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST → Image provider

**Parameters**

- `image_url` (str, required) — HTTPS URL of the source image to mutate.
    - Empty or non-string → `IMAGE_ERR_INVALID_REQUEST` (`-32104`).
    - Passes `validate_image_url` server-side (HTTPS only, host allowlist, anti-SSRF, max-size). Failure → `IMAGE_ERR_REFERENCE_FETCH_FAILED` (`-32314`).
    - Typical sources: a previous `image/generate` result url (refresh first if it's near its 30-min TTL), or a URL you obtained via `host/uploadFile`. Public CDN URLs work only if the host's allowlist covers them.
- `prompt` (str, required) — Edit instruction, e.g. `"Restyle in cyberpunk neon"` or `"Add a halo above the cat's head"`.
    - Validated like `image/generate.prompt` — empty rejected.
    - Provider-dependent: DALL·E 3 cannot do region edits without a mask; SDXL inpainting respects mask boundaries strictly; FLUX dev/Kontext takes natural-language transforms.
- `mask_url` (str | None, optional) — Optional 1-channel PNG mask URL (white = edit, black = preserve). Must match `image_url` dimensions exactly.
    - If the user's provider does not support masking, the host returns `MASK_UNSUPPORTED` (`-32312`, gate code) — do not retry with a different mask, retry without one.
    - Dimension/format mismatches surface as `IMAGE_ERR_INVALID_REQUEST` from the provider, mapped to `PROVIDER_ERROR` (`-32103`).
- `n` (int, optional) — Number of edited variants to return (1 .. 8).
    - Capped at `_MAX_N = 8` like `generate`; per-call cap is `image_token.max_per_call_edit` (**default 1**, lower than generate). Exceeding either → `IMAGE_ERR_MAX_IMAGES_EXCEEDED` (`-32106`).
    - Some providers reject `n > 1` for edits — surfaces as `N_UNSUPPORTED` (`-32313`).
- `size` (str | None, optional) — Output pixel dimensions; most providers ignore this for edit (output matches input).
    - Pass only when the provider documents it (rare). Otherwise omit.
- `model_preferences` (dict | None, optional) — Same MCP-style hint as `image/generate`; sent as `modelPreferences` on the wire.
    - Not all generate-capable models support edit. Mismatch → `EDIT_NOT_SUPPORTED` (`-32311`) — pick a different hint or omit.
- `metadata` (dict | None, optional) — Opaque audit metadata; always include `{"executa_invoke_id": invoke_id}`.
- `timeout` (float, optional) — SDK-side per-call deadline; injected as `_clientTimeoutS`. Same channel cap (240s) as `generate`.


---

## Host-managed file upload

*Executa · reverse RPC (v2+) · Host upload*

Persist a binary blob to host storage **in the lifetime of one `tool_invoke_id`** without holding R2 credentials. Three modes share one wire method: **`inline`** (base64 round-trip, ≤ 8 MiB), **`negotiate`** (presigned PUT URL for direct R2 upload), **`confirm`** (register the post-PUT object and get a download URL). All return short-lived HTTPS GET URLs (~30 min TTL).

**When to choose this over `files/upload_begin`** (in `executa-persistent-storage`): use `host/uploadFile` for **invoke-scoped, transient** artefacts — image inputs to chain to `image/edit`, screenshots to hand back to the user, intermediate PDFs the LLM should re-fetch within the same turn. The objects are not enumerable, not user-visible in 'My Files', and TTL out of presigned URLs quickly. For durable per-user state, use `files/upload_begin` + `files/upload_complete` instead.

**Pre-requisites** (all four required):
1. **v2 protocol negotiation.** Plugin advertises `client_capabilities.upload = {}` on `initialize`.
2. **Manifest declaration.** `host_capabilities: ["host.upload"]`. Missing → `UPLOAD_NOT_GRANTED` (`-32201`).
3. **User grant.** `UserExecuta.custom_config.upload_grant = {enabled: true, max_files?: N, max_file_bytes?: B, max_total_bytes?: T, allowed_mime_types?: [...], allowed_purposes?: [...]}`. Defaults: 16 files / 20 MiB per file / 80 MiB total per invoke (`matrix-nexus/src/auth/upload_token.py`).
4. **MIME + purpose allowlist.** `purpose` ∈ `{image_input, image_reference, user_artifact}` (`host_upload_service.ALLOWED_PURPOSES`); MIME must pass both the host denylist (SVG forced to attachment) and `upload_token.allowed_mime_types`.

**Per-invoke quotas are shared across all three modes.** Files counter increments on `inline` and `confirm` only (negotiate is free). Exceed → `UPLOAD_MAX_FILES_EXCEEDED` / `UPLOAD_MAX_BYTES_EXCEEDED`.

**Best practices.** Choose `inline` whenever payload is already in memory and ≤ 8 MiB — one round-trip vs three. Use `negotiate`+`confirm` for streaming or large payloads. Always store the returned `r2_key`, not the `download_url` — URLs expire, keys are forever (for the storage lifetime). Catch `UPLOAD_TOO_LARGE` in the SDK pre-check and gracefully fall back to `negotiate`. **Error code numbering diverges** between matrix-side SDK (`-3220x`) and matrix-nexus gate; always match on `error_name` strings.

### Modes (one wire method, three SDK entry points)

- **host/uploadFile · inline** — ≤ 8 MiB base64 round-trip; one network hop; SDK pre-checks size cap.  `≤ 8 MiB`

- **host/uploadFile · negotiate** — Get a presigned R2 PUT URL (5-min TTL); plugin uploads bytes directly to R2.  `presigned-PUT`

- **host/uploadFile · confirm** — Register the post-PUT object; HEADs R2 to verify; returns transient download URL.

### Manifest declaration (plugin side)

- **host_capabilities** — Array including `"host.upload"`. Without it the Agent refuses to mint an `upload_token`.  `required`

- **client_capabilities.upload** — Empty object `{}` advertised on `initialize` for v2 negotiation.

### Common errors (full list in detail page)

- **UPLOAD_NOT_GRANTED (-32201)** — Missing grant, disabled executa, or manifest doesn't declare `host.upload`.

- **UPLOAD_TOO_LARGE (-32204)** — Inline payload > 8 MiB, or `size_bytes` / actual PUT bytes > `max_file_bytes`.

- **UPLOAD_MIME_REJECTED (-32205)** — MIME not in `upload_token.allowed_mime_types` or in host denylist.

- **UPLOAD_MAX_FILES_EXCEEDED (-32211)** — Per-invoke files counter exhausted (charged on inline + confirm, NOT on negotiate).

- **UPLOAD_NOT_FOUND (-32212)** — `confirm` called for an `r2_key` that has no object — the PUT failed or was never made.

---

## Detailed reference

### host/uploadFile · inline

*Reverse RPC method · Host upload*

Persist a **≤ 8 MiB** payload to host storage in one round-trip by sending it inline as base64. The host decodes, writes to R2 under a per-(user, executa, invoke) key, and returns a short-lived HTTPS GET URL. The plugin holds no R2 credentials and pays no storage of its own. Use this when the payload is already in memory and small; for anything larger use the `negotiate` + `confirm` pair.

**Signature**

```ts
upload_inline(*, filename: str, mime_type: str, content: bytes, purpose: str | None = None, metadata: dict | None = None, timeout: float = 120.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST → R2

**Parameters**

- `filename` (str, required) — Logical filename, used for `Content-Disposition` and the storage key suffix.
    - Empty → `UPLOAD_INVALID_REQUEST` (`-32203` on the wire, `-32204` in matrix-nexus gate — see Errors).
    - The host runs `_safe_filename(filename)` before setting `Content-Disposition`; unsafe characters are stripped. The original name is **not** preserved in the storage key — keys are opaque (`exec-uploads/{env}/{user_uuid}/{tool_id}/{invoke_id}/{purpose}/{sha-suffix}`).
- `mime_type` (str, required) — Full MIME type, e.g. `"image/png"`, `"application/pdf"`, `"text/markdown"`.
    - Validated against the host's hard-coded denylist (`image/svg+xml` is force-attached, not inline) AND against `upload_token.allowed_mime_types` if the token set one. Reject → `UPLOAD_MIME_REJECTED` (`-32205` wire / `-32210` gate).
    - Drives `Content-Disposition`: `image/*` / `audio/*` / `video/*` (except SVG) → `inline`; everything else → `attachment`. Pick `text/plain` over `application/octet-stream` when you want the user's browser to preview the file.
- `content` (bytes, required) — Raw bytes; the SDK base64-encodes before sending (you do NOT pre-encode).
    - **Hard cap 8 MiB** raw (`INLINE_MAX_BYTES = 8 * 1024 * 1024`, `matrix-nexus/src/services/host_upload_service.py`); larger → `UPLOAD_TOO_LARGE` (`-32204` wire / `-32211` gate). The SDK pre-checks (`MAX_INLINE_BYTES`) and raises `UploadError` locally to avoid wasting a round-trip.
    - Empty bytes → `UPLOAD_INVALID_REQUEST`.
    - The wire payload is ~4/3× larger than `content` due to base64; budget your `_clientTimeoutS` for the upstream transfer.
- `purpose` (str | None, optional) — Storage purpose tag. One of `image_input` / `image_reference` / `user_artifact` (default).
    - Defaults to `"user_artifact"` server-side when omitted (see `executa_upload_gate.handle_upload_inline_request`).
    - Validated against `ALLOWED_PURPOSES = {"image_input", "image_reference", "user_artifact"}` AND against `upload_token.allowed_purposes` when set. Reject → `UPLOAD_PURPOSE_REJECTED` (`-32206` wire / `-32212` gate).
    - Used for billing categorisation and TTL policy (image purposes may have shorter retention).
- `metadata` (dict | None, optional) — Opaque metadata echoed into the storage row.
    - Do not store secrets — visible to user in account audit log.
- `timeout` (float, optional) — SDK-side per-call deadline; injected as `_clientTimeoutS`. Channel cap is `UPLOAD_MAX_REQUEST_TIMEOUT_S = 300s` (`matrix/src/executa/host_upload.py`).

### host/uploadFile · negotiate

*Reverse RPC method · Host upload*

Step 1 of the two-phase upload for payloads larger than `inline`'s 8 MiB cap (or whenever you want to stream from a file without buffering it all in memory): the host signs an R2 PUT URL bound to a specific key + content-type, the plugin uploads bytes directly to R2, then calls `confirm` to register the object. The PUT URL never expires until the TTL, but the plugin still holds no long-term R2 credentials.

**Signature**

```ts
negotiate(*, filename: str, mime_type: str, size_bytes: int, purpose: str | None = None, metadata: dict | None = None, timeout: float = 120.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST (presign) → returns PUT URL

**Parameters**

- `filename` (str, required) — Logical filename; same handling as `inline.filename`.
    - Empty → `UPLOAD_INVALID_REQUEST`. Not stored in the key path; opaque key only.
- `mime_type` (str, required) — MIME type; **must match exactly** what the plugin will send as `Content-Type` on the PUT (R2 enforces this).
    - Validated against `upload_token.allowed_mime_types`; reject → `MIME_REJECTED`.
    - Returned in `headers["Content-Type"]` so the plugin can copy it verbatim into the PUT request.
- `size_bytes` (int, required) — Expected byte count of the upload; used for quota pre-check only.
    - Wire field name on the REST body is `expected_bytes`; the SDK accepts the friendlier `size_bytes`.
    - Must be `> 0` → otherwise `UPLOAD_INVALID_REQUEST`.
    - If `size_bytes > upload_token.max_file_bytes` (default 20 MiB) → `UPLOAD_TOO_LARGE` (`-32204` wire) immediately, before any R2 round-trip — saves bandwidth.
    - R2 does **not** enforce the value on PUT; over-shipping bytes succeeds at the object store but the `confirm` step will rejet if `head_object.ContentLength > max_file_bytes`.
- `purpose` (str | None, optional) — Same purpose tag and validation as `inline.purpose`. Defaults to `user_artifact`.
- `metadata` (dict | None, optional) — Opaque metadata; echoed into storage row.
- `timeout` (float, optional) — SDK timeout for the *negotiate* round-trip only (typically <1s). The subsequent R2 PUT is plugin-managed and not bounded by this.

### host/uploadFile · confirm

*Reverse RPC method · Host upload*

Step 2 of the two-phase upload: after a successful R2 PUT, register the object with the host. The host HEADs R2 to verify the bytes landed, increments the per-invoke files+bytes counters, and returns a short-lived download URL — symmetric to the `inline` result. Must be called within the same `tool_invoke_id` that minted the upload_token.

**Signature**

```ts
confirm(*, r2_key: str, timeout: float = 120.0) -> dict
```

**Direction:** Plugin → Agent → Nexus REST → R2 HEAD

**Parameters**

- `r2_key` (str, required) — The exact `r2_key` returned by the preceding `negotiate` call.
    - Validated server-side: must start with `exec-uploads/{env}/{user_uuid}/` AND contain `/{executa_tool_id}/` AND `/{tool_invoke_id}/`. Cross-invoke or cross-tool reuse → `UPLOAD_INVALID_REQUEST` (`-32203`).
    - If R2 has no object at the key (PUT failed, never happened, or expired) → `UPLOAD_NOT_FOUND` (`-32212` wire / `-32213` gate). Treat as 'retry the negotiate+PUT pair'.
- `timeout` (float, optional) — SDK-side per-call deadline; this round-trip is just one R2 HEAD plus a presign — typically completes in <1s.


---

## Credentials & platform authorization

*Executa · secrets & auth*

Plugins declare the secrets they need in their manifest. Users connect a third-party service **once** in `/settings/authorizations`, and every Executa plugin that lists a matching credential name automatically receives the value at `invoke` time — no per-plugin OAuth flow.

Values live encrypted at rest (AES-256-GCM) and are injected via `params.context.credentials` on the JSON-RPC `invoke` call, so the LLM never sees them in tool arguments or transcripts. Resolution is **platform broker → plugin-stored fallback**; plugins may further fall back to environment variables during local dev.

First-class providers: **Google** and **X (Twitter)** via OAuth2 (auto-refresh); **GitHub**, **Notion**, **Slack** via API key. Adding a new provider is a single `_register(...)` entry in `src/services/credential_providers.py` — no schema changes.

### Manifest declaration (plugin side)

- **credentials[].name** — Stable identifier (e.g. `GMAIL_ACCESS_TOKEN`, `GITHUB_TOKEN`, `WEATHER_API_KEY`). Align with a provider's `credential_mapping` key to receive automatic platform injection; reuse the same `name` across plugins so the user enters it once.  `required`

- **credentials[].display_name** — Label shown in the per-plugin settings UI when no platform provider matches.

- **credentials[].description** — Help text — recommended to link to where the user obtains the value (e.g. `GitHub → Settings → Developer Settings → Tokens`).

- **credentials[].required** — Whether the user must supply this before `invoke` is callable.  `bool`

- **credentials[].sensitive** — Treat as secret — masked in the UI, never logged, stored AES-256-GCM encrypted.  `bool`

- **credentials[].default** — Optional pre-filled value shown in the per-plugin settings UI. Only meaningful for non-sensitive options (e.g. `"metric"` for a units selector); ignored for `sensitive: true` fields.  `string?`

### Receiving credentials at invoke time

- **params.context.credentials** — Plain-text `{name: value}` map injected on every `invoke` JSON-RPC call. **Never declare credentials as tool parameters** — that exposes them to the LLM in arguments and transcripts.  `context-only`

- **Local-dev fallback** — Plugins should read `credentials.get(NAME) or os.environ.get(NAME)` so they keep working when run outside Anna (CLI tests, CI).  `env-var`

- **Resolution priority** — 1. Platform broker (`user_platform_credentials` via `credential_mapping`)  →  2. Plugin-stored credentials (per-plugin settings, encrypted in `UserExecuta.custom_config`). Plugin-stored values only fill names the broker did not resolve. Users connect providers at `/settings/authorizations`; the backing REST endpoints (`/api/v1/platform-credentials/*`) are an internal surface for the Anna UI and **not** part of the plugin contract — plugins receive resolved values via `context.credentials` and must never call these endpoints directly.  `broker > plugin`

### First-class providers

- **Google** — OAuth2 with `access_type=offline` + `prompt=consent` for refresh tokens. 18 selectable scopes: Gmail (read / modify / compose / send), Calendar (read / events), Drive (read / file), Docs, Sheets, YouTube (read-only / monetary analytics). Aliases: `GOOGLE_ACCESS_TOKEN`, `GMAIL_ACCESS_TOKEN`, `GOOGLE_WORKSPACE_CLI_TOKEN`, `YOUTUBE_ACCESS_TOKEN`, `GOOGLE_DOCS_ACCESS_TOKEN`, `GOOGLE_SHEETS_ACCESS_TOKEN`.  `oauth2 + refresh`

- **X (Twitter)** — OAuth2 with PKCE, HTTP-Basic token auth, `offline.access` for refresh. 20 selectable scopes covering tweets, follows, likes, bookmarks, lists, blocks, mutes, DMs and Spaces. Aliases: `TWITTER_ACCESS_TOKEN`, `X_ACCESS_TOKEN`.  `oauth2 + pkce`

- **GitHub** — API-key (`github_api` provider) — Personal Access Token, fine-grained recommended. Aliases: `GITHUB_TOKEN`, `GITHUB_ACCESS_TOKEN`.  `api-key`

- **Notion** — API-key — Integration Token (Internal Integration Secret). Aliases: `NOTION_TOKEN`, `NOTION_API_KEY`.  `api-key`

- **Slack** — API-key — Bot User OAuth Token (`xoxb-…`). Aliases: `SLACK_BOT_TOKEN`, `SLACK_TOKEN`.  `api-key`

### Credential mapping (provider → manifest name)

- **$access_token** — Special value in `credential_mapping`. Resolves to the live OAuth2 access token; expired tokens are auto-refreshed using the stored refresh token before injection.  `oauth-only`

- **$refresh_token** — Reserved. **Never** exposed to plugins — the broker uses it internally to mint fresh access tokens.  `internal`

- **"FIELD_NAME"** — Literal field name from the provider's `api_key_fields`. Maps the plugin-requested credential to the value the user entered for that field.  `api-key`

### Storage & security

- **Encryption** — AES-256-GCM symmetric encryption. Key source order: `NEXUS_CREDENTIAL_KEY` env var → derived from `SECRET_KEY` → plaintext dev fallback (warns loudly).  `AES-256-GCM`

- **LLM isolation** — Credentials are injected via `context.credentials`, never as tool arguments. The LLM cannot see, log, or leak the values.

- **Least privilege** — OAuth scopes are user-selected at connect time — e.g. granting Gmail read-only without `gmail.send`.

- **Auto-refresh** — Expired OAuth access tokens are refreshed transparently using the stored refresh token. Plugins always see a valid token.

- **Revocation** — Disconnect calls the provider's revoke endpoint (Google, Twitter) where supported, then clears the encrypted row.

### Best practices

- **Align names with `credential_mapping`** — Use canonical names (`GITHUB_TOKEN`, `GOOGLE_ACCESS_TOKEN`, `TWITTER_ACCESS_TOKEN`, …) so the platform broker auto-injects. Custom names like `MY_GITHUB_KEY` defeat the broker.

- **Never put secrets in tool parameters** — Declare them in `credentials[]`; read from `context.credentials` at invoke time. Tool parameters end up in the LLM transcript.

- **Mark sensitive as `sensitive: true`** — Causes UI masking and ensures the value never appears in logs / audit trails.

- **Provide acquisition hints in `description`** — Link to the third-party settings page (`GitHub → Settings → Developer Settings → Tokens`) so users self-serve without leaving the consent dialog.


---

## Distribution, install pipeline & lifecycle

*Executa · ship it*

How Anna ships an Executa to an Agent host. Source-based runtimes (`uv` / `npm` / `pipx` / `homebrew`) defer to the package manager; **binary** distribution lets you ship a self-contained executable per `{os, arch}` with sha256 + size verification and atomic versioned installs.

The matrix Agent's `BinaryRuntime` (`src/executa/runtime.py`) is the source of truth for everything below — platform key format, archive formats, resolution order, install layout. The Hub admin UI just edits the data this code reads.

### Distribution types

- **`uv`** — Python tools installed via `uv tool install <package>` — default for the Python examples (`text-tools`, `storage-notebook`, …).  `python`

- **`npm`** — Node tools installed via `npm install -g <package>`.  `node`

- **`pipx`** — Alternative Python install path when `uv` isn't available on the host.  `python`

- **`homebrew`** — macOS / Linux brew formula install.  `macos / linux`

- **`binary`** — Direct download of a pre-built executable per `{os, arch}`. Plugin contains no source code; works on hosts with no runtime installed. This is what the rest of the section documents.  `no runtime needed`

- **`local`** — Development-mode install: consume an archive already staged on disk. Skips the download; reuses the same extract / layout pipeline as `binary`.  `dev only`

### Platform keys

- **Canonical format** — `{system}-{machine}`, all lowercase. `system` from `platform.system().lower()` (`darwin` / `linux` / `windows`); `machine` from `platform.machine().lower()` with aliases collapsed (`amd64` → `x86_64`, `x64` → `x86_64`).  `lowercase`

- **`darwin-arm64`** — macOS Apple Silicon (M1/M2/M3/M4).

- **`darwin-x86_64`** — macOS Intel.

- **`linux-x86_64`** — Linux x86_64 / AMD64.

- **`linux-aarch64`** — Linux ARM64 (Raspberry Pi 4/5, ARM servers).

- **`linux-armv7l`** — Linux ARMv7 (older Raspberry Pi).

- **`windows-x86_64`** — Windows x86_64.

- **`windows-arm64`** — Windows ARM64.

### Multi-platform asset map (`binary_urls`)

- **String value (shorthand)** — Map each platform key to a download URL: `{"darwin-arm64": "https://.../my-tool-darwin-arm64.tar.gz", "linux-x86_64": "..."}`. Sha256 and size are not verified in this form.

- **`BinaryAsset` object (full)** — Map each platform key to `{url, sha256?, size?, entrypoint?, format?}`. `sha256` and `size` are verified after download — any mismatch aborts the install. `entrypoint` overrides the in-archive `manifest.json` for this platform. `format` is one of `tar.gz` / `tgz` / `zip` / `raw`.  `verified`

- **Resolution order** — When the Agent installs, `resolve_binary_asset()` tries: 1. **exact** match on the current `platform_key` · 2. **OS-prefix** match (any arch with the same OS) · 3. **wildcard** key `*`, `any`, or `universal` · 4. if the map has **exactly one entry**, return it. No match → install fails with `No binary available for platform '<key>'. Available: <list>`.

- **Archive format detection** — If `format` is absent, `infer_archive_format(url)` reads the URL suffix: `.tar.gz` / `.tgz` → tar+gzip · `.zip` → zip · anything else → `raw` (downloaded verbatim and `chmod +x`).

### In-archive `manifest.json`

- **Canonical source of truth** — Bundle a `manifest.json` at the archive root. Its `name` field replaces the caller-supplied friendly name (so the `bin/` shim, `INSTALL.json`, and `list_plugins` agree with what `describe` returns at runtime). Path-traversal names (`/`, `\`, `.`, `..`) are rejected.

- **`runtime.binary.entrypoint` — string** — Single shared entry for every platform: `{"runtime":{"binary":{"entrypoint":"bin/my-tool"}}}`. Relative to the archive root.

- **`runtime.binary.entrypoint` — dict** — Per-platform entry: `{"default":"bin/x", "windows":"bin/x.exe", "darwin-arm64":"bin/x-arm64"}`. Lookup order: full `platform_key` → OS segment (`windows` / `darwin` / `linux`) → `default`.

- **Entrypoint precedence** — `BinaryAsset.entrypoint` (per-platform `binary_urls` override) → in-archive `manifest.runtime.binary.entrypoint` → heuristic search (single executable file under `bin/` or at the archive root).

### Install pipeline (binary)

- **1. Resolve asset** — Call `get_platform_key()`, look it up in `binary_urls`. Fall back to OS-prefix / wildcard / single-entry per the resolution order above.

- **2. Download with progress** — Stream to a temp file `/tmp/executa-{tool_id}-{rand}`. The streaming pipeline emits `progress` events (bytes_downloaded / bytes_total) on the NATS progress subject.

- **3. Verify size + sha256** — If the asset declared `size`, the byte count must match. If it declared `sha256`, the lower-hex digest must match. Mismatch → install aborts; no files are committed.

- **4. Extract to staging** — Unpack into `tools/{tool_id}/.staging-{rand}/`. Members with `..` or absolute paths are rejected by `_check_safe_member` (zip-slip defence).

- **5. Resolve entrypoint** — Apply the precedence rules above. Entry must live under staging (no `..` escape) and be a regular file.

- **6. Permissions + macOS unquarantine** — `_apply_permissions` walks the staged tree (entry + anything declared `executable` in the manifest gets `0o755`; rest stays as-is). On Darwin, `xattr -d com.apple.quarantine` is applied **recursively** to the staged tree — unsigned binaries Just Work for local dev.

- **7. Atomic version commit** — Rename staging → `tools/{tool_id}/v{version}/`. If the same version already exists, the old dir is moved aside (`.old-<rand>`) for rollback on failure.

- **8. Swap `current` symlink + bin shim** — Re-point `tools/{tool_id}/current` to the new version dir, then refresh `bin/{name}` shim. Existing scripts that ran `~/.anna/executa/bin/{name}` keep working without changes.

- **9. Write `INSTALL.json`** — Records `url`, `sha256`, `size`, `entrypoint`, install timestamp, source `binary_urls`. Used by `list_plugins` and for GC of stale versions (`EXECUTA_KEEP_VERSIONS`, default 1).

### Install layout (`~/.anna/executa/`)

- **`ANNA_EXECUTA_HOME`** — Override the install root (absolute path). Used by tests, sandboxed dev environments, and per-user installs on shared hosts.  `env`

- **`tools/{tool_id}/v{version}/`** — Isolated install root per version. `tool_id` and `version` are slugified to a flat `[A-Za-z0-9._-]+` segment (`sanitize_tool_id` / `sanitize_version`) — `@scope/pkg` → `_scope_pkg`, empty version → `unknown`.

- **`tools/{tool_id}/current`** — Symlink to the active version dir. Plugin loader resolves binaries via this link so swaps are atomic.

- **`bin/{name}`** — Back-compat shim (symlink or `.cmd` wrapper on Windows) → `tools/{tool_id}/current/{entrypoint}`. Lets old scripts that hard-code `~/.anna/executa/bin/{name}` keep working.

- **`EXECUTA_KEEP_VERSIONS`** — How many old versions to retain after an install (default `1`). GC runs at the end of the pipeline.  `env`

- **`EXECUTA_HOME` (runtime)** — Injected into every plugin subprocess as the absolute path of its own `tools/{tool_id}/current/`. Use it to locate side-by-side `lib/` / `data/` files without hard-coding the install root.

- **`EXECUTA_INSTALL_V2=0`** — Emergency fallback to the legacy single-file install path. Disables the multi-file pipeline, version dirs, and `current` symlink.  `env`

### `install_plugin` RPC params

- **Shape** — `{package_name, distribution_type, version?, executable_name?, binary_urls?, tool_id?, name?}` — see `install_essentials/streaming.py::install_plugins_batch_streaming`. Concurrency is bounded by 3 by default; per-plugin failures never abort the batch.

- **`tool_id`** — Stable identifier minted by nexus. Decides the install dir (`tools/{tool_id}/...`). When omitted, the Agent derives a slug from `package_name` (or, for binary, from the package/URL-derived friendly name).

- **`executable_name`** — Friendly name for the `bin/{name}` shim and operator UI. Optional for `binary` (derived from the package/URL when omitted); **required** for `local` to avoid a shim named after the archive filename.

### Publishing flow

- **Draft** — Owner-only. Edit manifest, swap `binary_urls`, iterate freely. Not visible to other users.  `private`

- **Version freeze** — `POST /executas/my/{tools|skills}/{id}/versions` snapshots the row into an immutable ExecutaVersion. Existing installs keep working at their pinned version.

- **Visibility** — Per version: `private` (default), `unlisted` (link-only), `public` (Hub-discoverable). Public requires a paid subscription.  `paid for public`

### macOS code signing

- **Local / internal distribution** — Agent runs `xattr -d com.apple.quarantine` recursively after extract, so ad-hoc signing (`codesign --force --sign - dist/my-tool`) or **no signing at all** is fine for local dev and trusted internal hosts.  `no signing required`

- **Public distribution** — For external users, sign with a Developer ID and notarize: `codesign --options runtime --sign 'Developer ID Application: ...'` then `xcrun notarytool submit ... --wait`. The notarized binary passes Gatekeeper without relying on the quarantine workaround.

### Hard rules

- **Stable tool names** — Renaming a tool after publish breaks every saved conversation that referenced it. The server-minted `tool_id` is the only runtime identity; the host no longer reads a self-reported manifest `name`.

- **LLM-readable descriptions** — The `description` field is the prompt the model uses to decide whether to call your tool. Write it for an LLM, not a human.

- **Typed parameters** — Arrays must declare `items`; otherwise the LLM passes JSON-encoded strings instead of real lists.

- **SemVer** — Versions must be SemVer. Old versions remain installable; new versions don't auto-upgrade existing installs.

- **No mutable archives** — An ExecutaVersion is supposed to be reproducible. Re-uploading a binary under the same `{tool_id, version, platform}` without bumping the version means a host that already installed it won't re-download — there is no auto-update path.


---

## Common pitfalls

*Executa · footguns*

If your plugin shows up as **Stopped** in the Anna UI or never appears at all, one of these is almost always the cause.

### Process lifecycle

- **Process exits after one request** — The protocol is long-running — the Agent spawns one process per plugin and reuses it for every `describe` / `invoke` / `health` call. Returning from `main()` (or calling `sys.exit` / `process.exit` / `os.Exit`) after one response triggers a restart on every call; the UI card stays **Stopped** and every invocation pays a cold-start delay. Always loop on stdin until EOF — the Agent closes stdin to signal shutdown.  `#1 cause`

- **Sampling: process exits before reverse RPC completes** — Same lifetime rule applies to `sampling/createMessage`. Exiting right after returning the `invoke` result kills the stdin reader before the reverse-RPC response arrives — plugin logs `unmatched response id=…`, host times out. Use the single-reader-with-dispatch pattern from `sdk/{python,nodejs,go}`.  `sampling`

- **Quick local liveness check** — `./my-plugin <<< '{...describe...}' &` then `kill -0 $PID` after 2 s — if the PID is gone, the process is exiting after one request. The `python/build_binary.sh --test` script runs this automatically.

### stdio framing

- **Banner / debug text on stdout** — Stdout is the JSON-RPC channel — only line-delimited JSON objects belong there. A startup `print("ready")` / `console.log` garbles framing; Agent logs `Failed to parse JSON-RPC frame` and `describe` times out. All human-readable output goes to **stderr** (`print(..., file=sys.stderr)`, `console.error`).

- **Blocking stdin reads with extra buffering** — Use line-buffered I/O (`-u` for Python, `setvbuf` for C, no `--harmony-readline` tricks for Node). Block-buffered stdin will deadlock the handshake.

- **Forgetting to flush stdout** — After writing each response also `sys.stdout.flush()` (Python) — the Agent reads line-by-line and won't see a buffered response.

### Identity matching

- **Three names must be exactly equal** — The Anna `tool_id` (minted with the 🪪 button), the `name` field your binary returns from `describe`, and the `name` in the archive's root `manifest.json` must be identical strings. The UI joins user-installed tools to running plugins by exact match; mismatch puts your plugin under **Extra Agent Plugins** or shows duplicate **Stopped** / **Running** cards. `manifest.json.name` also becomes the launcher symlink `~/.anna/executa/bin/{name}`.  `footgun`

- **Use `display_name` for the human label** — Only `name` has to match — `display_name` is the pretty UI label (e.g. `"My Tool"`) and is free-form.

### Distribution archives

- **Always ship `manifest.json` at the archive root** — Without it the Agent walks a five-level entrypoint fallback (asset `entrypoint` → `bin/{name}` → only-or-first executable) and ZIP archives lose Unix permission bits — auxiliary scripts get `Permission denied`, the wrong binary gets picked, the launcher symlink falls back to a URL-derived generic name.

- **Declare `permissions` for every executable file** — ZIPs drop the +x bit. Set `runtime.binary.permissions["bin/foo"] = "0o755"` for every helper script alongside the entrypoint.

- **PyInstaller `--onefile` exceeds the 5 s describe timeout** — First launch extracts the bundle to a temp dir; a 200 MB+ bundle can take 10–30 s, especially under Rosetta / slow disks. The Agent uses `DESCRIBE_TIMEOUT_BINARY_COLD_START = 60` only during the post-install scan (see `matrix/src/executa/rpc_handler.py`); normal calls hit `DESCRIBE_TIMEOUT = 5` and fail. Prefer `--onedir` shipped as a multi-file archive (no first-launch extract); otherwise shrink the bundle (`--exclude-module`, audit `--collect-all`).  `5s vs 60s`

### Sampling (reverse RPC)

- **Missing `host_capabilities: ["llm.sample"]` declaration** — Even after v2 capability negotiation, Nexus refuses `sampling/createMessage` unless the *published* manifest also lists `"llm.sample"` in `host_capabilities`. Host returns `{ code: -32008, message: "not_negotiated" }` (constant `SAMPLING_ERR_NOT_NEGOTIATED` in `src/services/executa_sampling_gate.py`); Agent log says `executa X did not declare host_capabilities['llm.sample']`. Add the field, republish, ask users to update.  `-32008`

- **`-32007 max_tokens_exceeded` on a single small call** — The cap is **cumulative across the same `invoke_id`**, not per-call (default 32 000 tokens; host max also 32 000 in v1, mirrored in the Sampling authorization UI's `maxTokensTotal` field). Send fewer / smaller sampling calls per tool invocation, or have the user raise `sampling_grant.maxTokensTotal` in Anna Admin.  `-32007` `per-invoke`

### Initialize & validation

- **Forgetting `initialize`** — If you want sampling / storage / agent sessions, you must respond to `initialize` with your v2 capability set. Missing handler = silent v1 downgrade and `sampling/*` calls return `not_negotiated`.

- **Manifest schema drift** — Run `anna-app validate` before publish. The upload path runs the same JSON Schema check and rejects ambiguous types — catching it locally avoids a publish-then-fail round trip.


---

## Skill — markdown that teaches the agent

*Skill · declarative recipe*

A Skill is a folder containing `SKILL.md` (markdown with YAML frontmatter) plus any supporting files. At runtime the loader registers each skill as a LangChain `@tool`; when the LLM picks it, the tool returns the skill body and the agent uses its built-in exec tools to act on it.

### SKILL.md frontmatter

- **title** — Short human label shown in the catalogue.  `required`

- **description** — One-sentence "when should I use this?" hint shown to the agent.  `required`

- **metadata.execution_mode** — Hint to the LLM about how to apply the recipe (e.g. prompt-only, shell, python). Advisory only.  `frontmatter`

- **metadata.dependencies** — Declared tools/binaries the recipe expects. Surfaced inside the loaded body.  `frontmatter`

- **body (markdown)** — The recipe itself. Loaded verbatim as the tool's return value when the agent invokes the skill.  `required`

- **supporting files** — Anything alongside `SKILL.md` is bundled with the version snapshot — templates, JSON examples, sub-prompts.  `optional`

### Local development

- **Discoverable skills directory** — The loader (`src/skills/loader.py`) walks a small ordered list of paths; drop your folder into the first one that exists, reload the agent, and the skill appears.  `local-only`

- **Reload loop** — Drop folder → reload → trigger → revise. No build step, no restart of the host.

### Publishing

- **Same pipeline as Tools** — A Skill is just an Executa with `executa_type="skill"`. Same wizard, same REST surface, same Hub draft/version/visibility flow as `executa-distribution`.


---

## Anna App manifest fields

*Manifest · top-level*

Top-level keys on the App manifest (stored in `anna_app_versions.manifest`). Unknown keys are rejected.

- **schema** — Manifest schema version. Integer in [1, 2]. Defaults to 1.  `int`

- **required_executas** — Executas the App needs. Each entry: `{ tool_id, version?, min_version? }`. `version="latest"` auto-freezes at publish time.  `ManifestExecutaRef[]`

- **optional_executas** — Executas the App can use if installed but does not require. Same shape as `required_executas`.  `ManifestExecutaRef[]`

- **host_capabilities** — String tokens declaring coarse host features the App expects (e.g. `agent-sessions`). Forward-compatible.  `string[]`

- **permissions** — Coarse permission tokens shown to the user at install time and enforced at the dispatcher.  `string[]`

- **tags** — Discovery hints; surfaced in App Store search & filters.  `string[]`

- **system_prompt_addendum** — Text injected into the system prompt when the App is active in a turn. Max 4000 chars.  `string`

- **user_message_prefix_template** — Optional template prepended to the user message when the App is #mentioned. Max 500 chars.  `string`

- **ui** — UI bundle section: declares bundle entry, views, host_api grants, CSP overrides. See "UI manifest".  `UiManifestSection`

- **dev** — Local-harness-only config (fixtures, mocks, seed_storage, user_id). Stripped by `anna-app publish`; ignored by production dispatcher.  `AppDevConfig` `dev-only`


---

## UI manifest — windows, views, grants

*Manifest · ui section*

The `ui` block describes the iframe bundle, the windows it can open, and which Host API namespaces the bundle is allowed to call.

### Bundle (UiBundleSection)

- **bundle.entry** — Bundle-relative path to the SPA entry HTML.  `required`

- **bundle.format** — Bundle layout. Defaults to `static-spa`.  `string`

- **bundle.external_origins** — Origins the iframe is allowed to load resources from (CSP-aware).  `string[]`

### Views (UiViewSpec[])

- **view.name** — Stable view identifier (1–40 chars, unique per App). Used by `window.open_view`.  `required`

- **view.title** — Window title shown in the chrome.  `required`

- **view.entry** — Optional sub-route within the bundle for this view. Defaults to the bundle entry.  `string`

- **view.icon** — Bundle-relative icon shown in the window chrome and dock.  `string`

- **view.default** — Whether the view opens automatically on App activation.  `bool`

- **view.default_size / min_size / max_size** — Window dimensions in CSS pixels (`UiSize: { w, h }`). Bounded [120, 4096].  `UiSize`

- **view.resizable / movable / single_instance** — Window UX flags. `single_instance` forbids opening a second instance.  `bool`

- **view.summary_template** — Template used to summarise the view state for the LLM (max 400 chars).  `string`

### Other

- **csp_overrides** — Per-directive CSP additions (object of directive → string[]).  `object`

- **state_merge** — Conflict policy for concurrent `runtime_state` writes. Default `last_writer_wins`.  `string`

- **host_api** — Whitelist of Host API methods the UI bundle may invoke, per namespace. See "Host API grants".  `UiHostApiSpec`


---

## UI Host API grants

*Manifest · ui.host_api*

Declare which Host API methods your iframe bundle may call, per namespace. Tokens are method names (e.g. `set`, `list`); the dispatcher refuses ungranted calls.

- **host_api.storage** — Per-method grants for storage namespace (`get`, `set`, `list`, `delete`).  `string[]`

- **host_api.chat** — Grants for chat operations: `write_message`, `read_history`, `append_artifact`.  `string[]`

- **host_api.window** — Window control surface: `open_view`, `close`, `focus`, `set_title`, `resize`.  `string[]`

- **host_api.tools** — Direct tool invocation from the UI: `list`, `invoke`.  `string[]`

- **host_api.llm** — LLM access from the UI bundle: typically `complete`.  `string[]`

- **host_api.agent** — Agent session control — see `AgentHostApiSpec` for session submode + `tools[]` shape.  `AgentHostApiSpec`

- **host_api.files** — Per-method grants for the implemented files object-storage namespace (`upload_init`, `upload_finalize`, `download_url`, `list`, `delete`).  `string[]`

- **host_api.fs / artifact / prefs** — Reserved namespaces; methods are stubs (see Host API methods table for current status).  `string[]`


---

## agent.* — agent sessions

*Host API · agent.**

Spin up, drive, and inspect **LangGraph-backed agent runs** from your bundle. `session.create` mints an `AnnaAppSession` (kind=`agent`) and caches the underlying `app_session_token` in `_aps_token_cache[uuid]` — the iframe never holds capability credentials; it threads the `app_session_uuid` (`aps_…`) through every subsequent call.

**Path:** Bundle (postMessage) → `POST /api/v1/anna-apps/runtime/rpc` → `_h_agent_session_*` (dispatcher) → `SqlAlchemyWindowStore.agent_session_*` (store) → `app_llm_facade.agent_session_*` → LangGraph runner via `src.services.app_runner._copilot_unified`.

**Two-layer ACL (the dispatcher checks ui.host_api, NOT permissions):**
1. The dispatcher gate `host_api_allows` for the `agent` namespace reads ONLY `manifest.ui.host_api.agent` — `manifest.permissions[]` is display/audit metadata and is NEVER consulted.
2. `manifest.ui.host_api.agent.session.{auto, fixed: {client_ids: []}}` is **submode-aware**: each submode is `false` until explicitly enabled. Fixed mode further validates `fixed_client_id` against the allow-list (empty list = any user-owned Executa).
3. `manifest.ui.host_api.agent.tools` advisory-restricts the tool surface for the session; the facade re-resolves at run time so newly-installed Executas appear without re-creating the session.

**Submodes**
• `auto` — LangGraph runner picks any tool the user's Executa exposes (intersected with `agent.tools`).
• `fixed` — pin the run to one Executa by `client_id`. Use this for deterministic flows or scoped access (e.g. read-only tools).

**Streaming model.** `agent.session.run` returns SYNCHRONOUSLY with `{stream_id, run_id}`; the dispatcher allocates `stream_id` and a background `_pump` task consumes the facade's SSE body, emitting frames over the `rpc.stream` event topic — `{stream_id, window_uuid, seq, payload, done}`. The SDK's `AgentRunStream` reassembles by `seq` (out-of-order frames are buffered until the missing seq arrives) into an `AsyncIterable`. The pump ALWAYS emits a terminal `{event:'end', run_id}` with `done:true`, even on cancellation or crash.

**Session lifecycle.** `create` → cached uuid for `expires_in` seconds (`_cache_aps_token` stores `ttl - 30s` to refresh slightly early) → many `run` calls → optional `cancel(run_id)` / `history(limit)` → `delete` revokes + pops cache. After `delete` or TTL eviction, subsequent calls fail `session_expired` / `APP_SESSION_NOT_FOUND`.

**Quotas + caps.** Per-call `quotaCaps` requested on `create` are intersected (`min`) with `UserAnnaApp.custom_config.llm_grant.quota_caps`; defaults to `max_tokens_per_call=4096` if neither side declares one. `APP_QUOTA_EXCEEDED` may be raised pre-stream (synchronously) OR mid-stream as an in-band `{event:'error'}` frame.

**SDK ergonomics.** Prefer the high-level helper `await anna.agent.session({submode, ...})` — it returns an `AgentSession` instance with `.run({content})` / `.cancel(runId)` / `.history({limit})` / `.delete()` methods bound to the new uuid, so apps never thread `app_session_uuid` manually. Per-namespace timeout default is **300 000 ms** (ack-only — long streams keep the iterator alive until `done`).

- **agent.session.create** — Mint a server-side `AnnaAppSession` (kind=`agent`). Validates `submode` against the manifest grant and `fixed_client_id` against the allow-list; optional `systemPrompt` overrides the agent's system prompt. Returns `{app_session_uuid, expires_in, submode, fixed_client_id, system_prompt, granted_tools, inherit_host_tools}` (`granted_tools` is runtime-resolved via `effective_granted_tool_names`, NOT a raw manifest echo).  `submode` `fixed_client_id` `systemPrompt` `quotaCaps∩grant`

- **agent.session.run** — Submit a user turn; returns SYNCHRONOUSLY with `{stream_id, run_id}`. LangGraph response frames arrive via `rpc.stream` events; the SDK's `AgentRunStream` reassembles by `seq` into an `AsyncIterable`. Terminal frame is always `{event:'end', run_id}` + `done:true`.  `streaming` `rpc.stream` `recursion_limit=8`

- **agent.session.cancel** — Best-effort cancellation. Writes a Redis signal that the runner polls *between* LangGraph nodes — an in-flight provider call still completes. Returns `{cancelled: bool}` — NOT a confirmation the run actually stopped (watch for the terminal `end` frame).  `run_id required` `best-effort`

- **agent.session.history** — Read the tail of the LangGraph `channel_values.messages` checkpoint. **Best-effort:** returns `{messages: []}` (NOT an error) when the checkpoint store is unavailable or the thread has no writes yet. `limit` clamped to `[1, 200]`, default 50.  `best-effort` `LangGraph checkpoint`

- **agent.session.delete** — Soft-revoke the session + pop its cached capability token. Idempotent. Does NOT cancel in-flight runs — call `cancel(run_id)` first if you need a clean shutdown.  `revoke` `idempotent`

- **agent.session.list** — Enumerate the caller's own agent sessions, scoped to this app (`window.app_id`). Returns `{sessions: [{app_session_uuid, kind, submode, fixed_client_id, label, created_at, last_active_at, expires_at, max_lifetime_at}]}` — metadata only, no token. `include_expired?` (default false); `limit` clamped `[1, 100]`, default 50. Use it to re-attach after an iframe reload instead of minting a duplicate.  `read-only` `since v0.8.0`

- **agent.session.refresh** — Re-mint a fresh capability token for an existing `app_session_uuid` and slide its idle window forward — WITHOUT re-creating the session (which would orphan the LangGraph `thread_id`). Can never push past `max_lifetime_at`. Returns `{app_session_uuid, expires_in, submode, fixed_client_id, expires_at, max_lifetime_at, idle_ttl_seconds, session_expires_in}`.  `extend TTL` `since v0.8.0`

---

## Detailed reference

### agent.session.create

*Host API method · iframe surface*

Mint a server-side `AnnaAppSession` (kind=`agent`) bound to the current `(user, app, window)` triple. Returns an `app_session_uuid` the bundle threads through every subsequent `run` / `cancel` / `history` / `delete` call. The underlying capability token is cached in `_aps_token_cache[uuid]` for its TTL — the iframe never sees it.

**Signature**

```ts
anna.agent.session.create(args: {submode: 'auto'|'fixed', fixed_client_id?: string, label?: string, systemPrompt?: string, quotaCaps?: {max_tokens_per_call?: number, max_runs_per_day?: number, max_concurrent_runs?: number}}, opts?: {timeoutMs?: number}) => Promise<{app_session_uuid: string, expires_in: number, submode: 'auto'|'fixed', fixed_client_id: string|null, system_prompt: string|null, granted_tools: string[], inherit_host_tools: boolean}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.agent_session_create → AnnaAppSession (kind=agent) + cached app_session_token

**Parameters**

- `submode` ('auto' | 'fixed', required) — Tool-resolution mode. `auto` lets the LangGraph runner pick any tool the user's Executa Agent exposes (constrained by `manifest.ui.host_api.agent.tools`). `fixed` pins the run to a single `client_id` (one specific Executa) and rejects any other tool.
    - `invalid_arg` if absent or not exactly `'auto'` / `'fixed'`.
    - `permission_denied` if the chosen submode is `false` in `manifest.ui.host_api.agent.session.{auto,fixed}` — the manifest must opt into each submode explicitly.
- `fixed_client_id` (string, required) — Executa `client_id` the run is pinned to. Required for `submode='fixed'`; ignored for `submode='auto'`. SDK also accepts the camelCase alias `fixedClientId`.
    - `invalid_arg` if missing when `submode='fixed'`.
    - `permission_denied` if not present in `manifest.ui.host_api.agent.session.fixed.client_ids` (when that list is non-empty — an empty list means "any user-owned Executa").
- `label` (string, optional) — Human-readable label stored on the `AnnaAppSession` row. Visible in admin / debug UIs; not surfaced to the model.
- `systemPrompt` (string, optional) — Optional session-level system prompt persisted on the `AnnaAppSession` row and applied to every `run`. Validated against the platform safety floor (≤ 4000 chars; forbidden role / fence tokens rejected with `APP_INVALID_REQUEST`). A per-run `systemPrompt` on `agent.session.run` overrides it for that turn. Legacy alias: `system_prompt`.
- `quotaCaps` ({max_tokens_per_call?, max_runs_per_day?, max_concurrent_runs?}, optional) — Caller-requested ceiling. Intersected (`min`) with the user's `llm_grant.quota_caps` via `_intersect_quota_caps`; the result is stored on `session.quota_caps` and consulted by every subsequent `run`.
    - Defaults fall back to grant value; if neither side declares a field, `max_tokens_per_call` defaults to **4096**.
    - Requesting *more* than the grant has no effect — silently clamped down.

### agent.session.run

*Host API method · iframe surface · streaming*

Submit a user turn to an existing agent session and stream the LangGraph response back to the iframe. The handler returns *immediately* with `{stream_id, run_id}`; a background pump consumes the facade's SSE body and emits successive `('rpc.stream', {stream_id, seq, payload, done})` events through `store.emit_event`, which the SDK's `AgentRunStream` reassembles into an `AsyncIterable`.

**Signature**

```ts
anna.agent.session.run(args: {app_session_uuid: string, content: string, run_id?: string, recursion_limit?: number, systemPrompt?: string, allowed_tools?: string[], modelPreferences?: object}, opts?: {timeoutMs?: number}) => Promise<{stream_id: string, run_id: string}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.agent_session_run → LangGraph runner → SSE → `rpc.stream` events

**Parameters**

- `app_session_uuid` (string (aps_…), required) — Session id from `agent.session.create`. `invalid_arg` if missing / non-string / does not start with `aps_`.
- `content` (string, required) — User turn text. `invalid_arg` if missing / non-string / whitespace-only.
- `run_id` (string (uuid), optional) — Caller-supplied run id (idempotency token). When omitted the store generates a fresh `uuid4`. Pass the same value to `agent.session.cancel` to abort.
- `recursion_limit` (number (int), optional) — LangGraph max recursion depth. Default **8** — increase for long tool-chain workflows; the facade caps server-side via LangGraph config.
- `systemPrompt` (string, optional) — Optional per-run system-prompt override. Takes precedence over the session-level `systemPrompt` from `create` for THIS turn only (not persisted). Validated against the platform safety floor. The server reads `systemPrompt` first, falling back to the legacy `system` field for older callers.
- `allowed_tools` (string[], optional) — Tighten the tool surface for this single run (subset of `granted_tools` returned by `create`). SDK accepts `allowedTools` alias. Useful for "safe mode" / read-only runs.
- `modelPreferences` (object, optional) — Same shape as `llm.complete` — `hints` / `costPriority` / `speedPriority` / `intelligencePriority`. Resolved at each LangGraph node, intersected with the user's grant.

### agent.session.cancel

*Host API method · iframe surface*

Best-effort cancellation of an in-flight `agent.session.run`. Writes a Redis cancel signal keyed by `(app_session_uuid, run_id)` that the LangGraph runner polls between nodes; an in-flight provider call still completes before the runner checks back in.

**Signature**

```ts
anna.agent.session.cancel(args: {app_session_uuid: string, run_id: string}, opts?: {timeoutMs?: number}) => Promise<{cancelled: boolean}>
```

**Direction:** Bundle (iframe) → Host RPC → src.services.app_runner.signal_cancel (Redis cancel signal)

**Parameters**

- `app_session_uuid` (string (aps_…), required) — Session id from `create`. Resolved through `_claims_for_aps` — `session_expired` if the cached token has been evicted.
- `run_id` (string, required) — Exact `run_id` returned (or supplied) by `agent.session.run`. `invalid_arg` if missing.

### agent.session.history

*Host API method · iframe surface*

Read recent agent messages by replaying the most recent LangGraph checkpoint for this session's `thread_id`. Best-effort: returns `{messages: []}` (NOT an error) if the checkpoint store is unavailable, the row hasn't been written yet, or the read fails — treat absence as "no history yet".

**Signature**

```ts
anna.agent.session.history(args: {app_session_uuid: string, limit?: number}, opts?: {timeoutMs?: number}) => Promise<{messages: Array<{role: 'user'|'assistant'|'system'|string, content: string | unknown[]}>}>
```

**Direction:** Bundle (iframe) → Host RPC → LangGraph AsyncCheckpointSaver.aget

**Parameters**

- `app_session_uuid` (string (aps_…), required) — Session id from `create`.
- `limit` (number (int), optional) — Max messages to return (clamped to `[1, 200]`). Always reads from the *tail* — the most recent `limit` messages.

### agent.session.delete

*Host API method · iframe surface*

Revoke an `AnnaAppSession` and drop its cached capability token. Idempotent — repeated calls succeed silently. Use this to free admin-view entries and force the next `create` call to mint a fresh session.

**Signature**

```ts
anna.agent.session.delete(args: {app_session_uuid: string}, opts?: {timeoutMs?: number}) => Promise<{deleted: true}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.revoke_session

**Parameters**

- `app_session_uuid` (string (aps_…), required) — Session id from `create`.

### agent.session.list

*Host API method · iframe surface*

Enumerate the caller's own agent sessions, scoped to THIS app (`window.app_id`) — an app can never see another origin's sessions. Use it to re-attach to or clean up sessions after losing in-memory handles (iframe reload, multi-tab, crash). Returns identity + lifecycle metadata only (no token, no `thread_id`, no `quota_caps`).

**Signature**

```ts
anna.agent.session.list(args?: {include_expired?: boolean, limit?: number}, opts?: {timeoutMs?: number}) => Promise<{sessions: Array<{app_session_uuid: string, kind: string, submode: 'auto'|'fixed'|null, fixed_client_id: string|null, label: string|null, created_at: string, last_active_at: string, expires_at: string, max_lifetime_at: string}>}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.list_sessions

**Parameters**

- `include_expired` (boolean, optional) — Include expired-but-not-revoked sessions. By default only active (non-revoked, non-expired) sessions are returned.
- `limit` (number (int), optional) — Max sessions to return, newest-first. Clamped to `[1, 100]`.

### agent.session.refresh

*Host API method · iframe surface*

Re-mint a fresh short-lived capability token for an existing session and slide its idle window forward — WITHOUT re-creating the session (which would orphan the LangGraph `thread_id`). The iframe only ever persists `app_session_uuid`; on resume, or proactively near expiry, it calls `refresh` to obtain a new deadline. Returns absolute lifecycle timestamps so the client can schedule its next refresh.

**Signature**

```ts
anna.agent.session.refresh(args: {app_session_uuid: string}, opts?: {timeoutMs?: number}) => Promise<{app_session_uuid: string, expires_in: number, submode: 'auto'|'fixed'|null, fixed_client_id: string|null, expires_at: string, max_lifetime_at: string, idle_ttl_seconds: number, session_expires_in: number}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.refresh_session_token (+ session_lifecycle_meta)

**Parameters**

- `app_session_uuid` (string (aps_…), required) — Session id from `create` (or from `agent.session.list`). SDK also accepts the camelCase alias `appSessionUuid`. `invalid_arg` if missing or not `aps_`-prefixed.


---

## chat.* — write back into the conversation

*Host API · chat.**

Post messages and artifacts back into the user-facing chat thread from your App. **ACL:** the dispatcher gate is `manifest.ui.host_api.chat` — a `string[]` that must list each called method (`write_message` / `read_history` / `append_artifact`), or `*`; `manifest.permissions[]` is display/audit only and is NEVER checked. **Status:** `append_artifact` is fully implemented; `write_message` is a Phase-3 functional stub (emits a `chat_message_from_app` event but does NOT persist); `read_history` is a Phase-3 stub that raises `not_implemented`.

- **chat.append_artifact** — Attach a generated artifact to the current turn. Reads `args.artifact` (object); fields `kind` (≤40 chars, default `app_event`), `app_slug`, `summary` (≤1000 chars), `payload_ref`, `data`. Emits an `artifact_appended` event and returns `{artifact_id}` (`app-<window_uuid[:8]>-<unix_ts>`). Fully implemented.

- **chat.write_message** — Append a message authored by the App. `role` (default `assistant`), `content` (string, truncated to ≤4000 chars). Emits a `chat_message_from_app` event and returns `{message_id}` (`msg-<unix_ms>`). **Phase-3 functional stub — does NOT persist.**  `stub`

- **chat.read_history** — Read prior turns of the chat thread. **Phase-3 stub — raises `not_implemented`.**  `stub`

---

## Detailed reference

### chat.append_artifact

*Host API method · iframe surface*

Attach a structured artifact to the conversation that hosts this App window. The handler normalises the caller's `artifact` object, stamps it with the server `ts` and `window_uuid`, and broadcasts an `artifact_appended` event over the window's event channel so the chat surface (and any other tab on the same session) can render it. This is the ONE fully-implemented chat method.

**Signature**

```ts
anna.chat.append_artifact(args: {artifact: {kind?: string, app_slug?: string, summary?: string, payload_ref?: string, data?: unknown}}, opts?: {timeoutMs?: number}) => Promise<{artifact_id: string}>
```

**Direction:** Bundle (iframe) → Host RPC → _h_chat_append_artifact (dispatcher) → store.emit_event

**Parameters**

- `artifact` (object, required) — The artifact payload. `invalid_arg` if not an object. Every field below is optional; unknown fields are dropped (the handler only copies the five named keys).
- `artifact.kind` (string, optional) — Free-form category tag. Coerced to string and **truncated to 40 chars**. Defaults to `app_event`.
- `artifact.app_slug` (string, optional) — Optional app slug for attribution. Passed through verbatim (no validation).
- `artifact.summary` (string, optional) — Human-readable one-liner. Coerced to string and **truncated to 1000 chars**.
- `artifact.payload_ref` (string, optional) — Optional reference (e.g. a `files.*` path or `storage` key) pointing at the full payload. Passed through verbatim.
- `artifact.data` (unknown, optional) — Optional inline structured data. Passed through as-is — keep it small; there is no server-side size clamp on this field, so prefer `payload_ref` for large blobs.

### chat.write_message

*Host API method · iframe surface*

PHASE-3 FUNCTIONAL STUB. Post a message authored by the App into the live conversation. Today the handler ONLY emits a `chat_message_from_app` event ({window_uuid, role, content}) for any subscribed UI to render — it does NOT persist the message to a conversation/message table. The method IS registered (not `_h_not_implemented`), so it returns a `message_id` and does not raise, but durable thread persistence is not yet wired.

**Signature**

```ts
anna.chat.write_message(args: {role?: string, content: string}, opts?: {timeoutMs?: number}) => Promise<{message_id: string}>
```

**Direction:** Bundle (iframe) → Host RPC → _h_chat_write_message (dispatcher) → store.emit_event

**Parameters**

- `role` (string, optional) — Author role for the emitted message. Passed through verbatim (no enum validation); defaults to `assistant`.
- `content` (string, optional) — Message text. Coerced to string and **truncated to 4000 chars**. An omitted/empty value emits an empty message rather than erroring.

### chat.read_history

*Host API method · iframe surface*

PHASE-3 STUB — NOT yet implemented. The method is registered in the dispatch table (so the namespace/method name is reserved and ACL-gated), but the handler unconditionally raises `not_implemented`. Do not call it in production flows; there is currently no way to read prior conversation turns from an App bundle.

**Signature**

```ts
anna.chat.read_history(args?: object, opts?: {timeoutMs?: number}) => Promise<never>  // always rejects with not_implemented
```

**Direction:** Bundle (iframe) → Host RPC → _h_chat_read_history (raises not_implemented)


---

## llm.* — host LLM access

*Host API · llm.**

Borrow the host's **user-configured** LLM provider for stateless single-shot completions. Your bundle never sees an API key, never hard-codes a model name, and the request is billed against the user's existing quota — `modelPreferences` only nudges the selector between providers the user *actually enabled*.

**Path:** Bundle (postMessage) → `POST /api/v1/anna-apps/runtime/rpc` → `_h_llm_complete` (dispatcher) → `SqlAlchemyWindowStore.llm_complete` → `_decode_or_mint_complete` lazy-mints an `AnnaAppSession` (kind=`complete`) cached by `complete:{window_uuid}` → `app_llm_facade.complete` → `LLMProviderService.select_model_by_preferences` → LangChain `ChatOpenAI`.

**ACL.** The only dispatcher gate is `host_api_allows` for the `llm` namespace: `manifest.ui.host_api.llm` (a `string[]`) must contain `complete` (or `*`). `manifest.permissions[]` is display/audit metadata and is NEVER checked.

**MCP-shaped.** Both request (`messages`, `maxTokens`, `temperature`, `modelPreferences`, `systemPrompt`, `stopSequences`) and response (`role`, `content:{type:'text', text}`, `model`, `stopReason`, `usage`, `_meta`) mirror MCP `sampling/createMessage` so the same payload works against MCP samplers too.

**Quota model.**
• Per-call cap `quota_caps.max_tokens_per_call` (default **4096**) — `maxTokens > cap` is **silently clamped down**; read back `usage.outputTokens` to detect.
• Pre-flight `check_quota_available` + post-call `check_and_consume_quota_with_redis` both raise `APP_QUOTA_EXCEEDED` (the latter raises *after* the model returns, dropping the response — never double-charges).
• `_meta.quotaConsumed` reports the actual debited amount (provider cost × `cost_multiplier`).

**Stateless.** No conversation state between calls. The lazy-minted `app_session_uuid` is reused server-side only for token caching, NOT for prompt history — callers MUST resend full `messages` every call. For multi-turn / tool-using workflows use `agent.*` instead.

**Non-streaming.** The response arrives in a single chunk after the provider finishes. For token-by-token UI use `agent.session.run` (LangGraph streaming over `rpc.stream`). SDK per-namespace timeout default is **180 000 ms**.

- **llm.complete** — MCP-shaped single-shot completion. `messages` required (array, non-empty). `maxTokens` silently clamped to `session.quota_caps.max_tokens_per_call` (default 4096). Provider + model resolved server-side from `modelPreferences ∩ user-grant`. Returns `{role, content:{type:'text', text}, model, stopReason:'endTurn', usage:{inputTokens, outputTokens, totalTokens}, _meta:{provider, latencyMs, quotaConsumed, appSessionUuid}}`. Errors: `APP_NOT_GRANTED`, `APP_INVALID_REQUEST`, `APP_QUOTA_EXCEEDED`, `APP_PROVIDER_ERROR`.  `MCP-shaped` `stateless` `non-streaming` `maxTokens clamped`

---

## Detailed reference

### llm.complete

*Host API method · iframe surface*

Stateless single-shot chat completion against the **user's chosen** LLM provider / model — your bundle never sees an API key, never hard-codes a model name, and the request is billed against the user's existing quota and provider routing. MCP-shaped: the request mirrors `sampling/createMessage` (`messages`, `maxTokens`, `temperature`, `modelPreferences`, `systemPrompt`, `stopSequences`) and the response mirrors the MCP result (`role`, `content: {type:'text', text}`, `model`, `stopReason`, `usage`).

**Signature**

```ts
anna.llm.complete(args: {messages: Array<{role:'user'|'assistant'|'system', content: string|object}>, maxTokens?: number, temperature?: number, modelPreferences?: {hints?: object, costPriority?: number, speedPriority?: number, intelligencePriority?: number}, systemPrompt?: string, stopSequences?: string[], metadata?: object}, opts?: {timeoutMs?: number}) => Promise<{role:'assistant', content:{type:'text', text:string}, model:string, stopReason:string, usage:{inputTokens:number, outputTokens:number, totalTokens:number}, _meta?:{provider:string|null, latencyMs:number, quotaConsumed:number, appSessionUuid:string}}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade.complete → LangChain ChatOpenAI → provider

**Parameters**

- `messages` (Array<{role, content}>, required) — Ordered chat transcript to complete. `role` is `user` / `assistant` / `system`. `content` is a string OR an MCP-shaped block (`{type:'text', text}` / `{type:'image', ...}`); blocks are flattened into a LangChain `HumanMessage` / `AIMessage` / `SystemMessage` by `_assemble_lc_messages`.
    - `APP_INVALID_REQUEST` if missing, non-array, or empty.
    - Order is preserved verbatim — caller is responsible for trimming context to the model's window.
    - Image content blocks require the selected model to be multimodal; otherwise the provider rejects upstream and the call surfaces as `APP_PROVIDER_ERROR`.
- `maxTokens` (number (int), optional) — Hard cap on output tokens. Silently clamped down to `session.quota_caps.max_tokens_per_call` — the grant's per-call ceiling intersected with what the user actually granted to *this* app.
    - `APP_INVALID_REQUEST` if `≤ 0`.
    - Clamping is silent — caller does not see the reduced value (read `usage.outputTokens` to confirm what landed).
    - Per-app cap is set at install time via `UserAnnaApp.custom_config.llm_grant.quota_caps.max_tokens_per_call`; defaults to 4096 if neither side declares one.
- `temperature` (number, optional) — Sampling temperature passed through to the provider. Default `0.7` when omitted.
- `modelPreferences` ({hints?, costPriority?, speedPriority?, intelligencePriority?}, optional) — Soft routing hints consumed by `LLMProviderService.select_model_by_preferences`. The user's grant ALWAYS overrides — preferences only break ties between providers the user actually enabled.
    - `hints` is an arbitrary dict (e.g. `{family: 'claude'}`); the selector pattern-matches against `LLMModel.metadata`.
    - Priorities are floats in `[0, 1]`; higher means "more important".
    - If no eligible model is available for the user, the call raises `APP_PROVIDER_ERROR` (`no eligible model available`).
- `systemPrompt` (string, optional) — Optional system prompt prepended as a `SystemMessage` before `messages`. Use this for app-specific persona / format instructions instead of injecting into `messages[0]`.
- `stopSequences` (string[], optional) — Forwarded as the provider's `stop` parameter. Caller must trim — the host does not validate length / count limits.
- `metadata` (object, optional) — Free-form caller-side tagging. NOT forwarded to the provider; reserved for future telemetry.


---

## image.* — host-managed image generation & editing

*Host API · image.**

Generate or edit images from the **anna-app bundle** without ever touching a provider key. The host owns the provider credentials, the user's image plan, R2 storage, and quota — your bundle just describes the picture.

**Auth chain.** Bundle calls `anna.image.{generate,edit}(...)` → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` → `_h_image_*` handler → `SqlAlchemyWindowStore.image_{generate,edit}` → `app_llm_facade.image_{generate,edit}` → user's preferred image provider (DALL·E 3 / SDXL / FLUX / …) → R2.

**ACL is two-layer.** (a) The dispatcher gate is `manifest.ui.host_api.image` — a `string[]` that must contain `generate` (and `edit` for `image.edit`), or `*`; `manifest.permissions[]` is display/audit only and is NEVER checked. (b) Anna Admin user-grant `UserExecuta.custom_config.image_grant = {enabled, allowGenerate, allowEdit, maxPerCallGenerate, maxPerCallEdit, …}`. Missing either side → `APP_NOT_GRANTED`. Edit grant defaults to **off** — `enabled = true` alone is not enough.

**Quota model.** Three layers: (1) per-call cap `maxPerCallGenerate` (default 4) / `maxPerCallEdit` (default 1) — exceed → `APP_INVALID_REQUEST`. (2) Plan-wide quota via `check_and_consume_quota_with_redis` — exceed → `APP_QUOTA_EXCEEDED` (HTTP 429). (3) Provider errors (safety refusals, 5xx, upstream timeout) → `APP_PROVIDER_ERROR` (HTTP 502 underneath). Per-invoke rolling cap used by Executa plugins is **not** applied to App-side calls.

**URL lifetime.** Returned `images[].url` are presigned R2 GETs with **~30 min TTL** (`R2_TRANSIENT_PRESIGN_EXPIRY = 1800s`). Never persist them — store nothing or round-trip through `upload.inline`/`upload.confirm` to get a durable `r2_key`. CSP must allow the R2 host (`csp_overrides.img-src: ["https:"]`); if you enable COEP `require-corp`, R2 must serve `Cross-Origin-Resource-Policy: cross-origin` or images break with a confusing `ERR_BLOCKED_BY_RESPONSE.NotSameOriginAfterDefaultedToSameOriginByCoep`.

- **image.generate** — Generate `n` images (default 1) from a text `prompt`, optional `size` (default `1024x1024`) and `reference_image_urls`. Returns `{images:[{url}], model, quota_used, latency_ms, …}` with ~30-min-TTL presigned R2 URLs.

- **image.edit** — Restyle / mask-edit an existing `image_url` per a text `prompt`. Optional `mask_url` for inpainting where the provider supports it. Source is not modified; results land in fresh R2 objects.  `edit grant`

---

## Detailed reference

### image.generate

*Host API method · iframe surface*

Generate `n` images from a text prompt using the host's configured image provider. The host enforces the per-(user, App) `image_grant`, checks plan quota, calls the provider, stores bytes on R2, and returns short-lived presigned URLs. The bundle never sees a provider key, never holds R2 credentials, and never bills directly.

**Signature**

```ts
anna.image.generate(args: {prompt: string, n?: number, size?: string, reference_image_urls?: string[]}, opts?: {timeoutMs?: number}) => Promise<{images, model, quota_used, ...}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade → image provider (DALL·E / SDXL / FLUX / …) → R2

**Parameters**

- `prompt` (string, required) — Natural-language description of the image to generate. Trimmed; an empty string after trim is rejected with `APP_INVALID_REQUEST`.
    - Forwarded verbatim to the provider — provider-side safety filters apply.
    - Provider safety refusals surface as `APP_PROVIDER_ERROR` (HTTP 502 underneath).
- `n` (integer, optional) — How many images to generate in this call. Must be a positive integer.
    - Clamped against `image_grant.maxPerCallGenerate` (default **4**) — exceeding → `APP_INVALID_REQUEST` with `n={n} exceeds per-call cap {max}`.
    - Independent host hard-cap of **8** lives in `matrix/src/executa/image.py` `_MAX_N` for the plugin-side path; the App-side facade enforces only the grant value.
    - Per-invoke rolling counter (`image_grant.max_images`) is **not** applied to App-side calls — those quotas are scoped to Executa plugin `tool_invoke_id` and not to App sessions.
- `size` (string, optional) — Output dimensions as `WxH`. Default `1024x1024`.
    - Provider-validated — unsupported aspect ratios surface as `APP_PROVIDER_ERROR` (HTTP 400 underneath, code `-32104` on the legacy HTTP route).
- `reference_image_urls` (string[] | null, optional) — Up to 4 reference image URLs the provider may condition on (style transfer / prompt-image blends). Validated by `validate_image_url` (no internal hostnames, no private IPs, no `file://`).
    - Any failing URL → `APP_INVALID_REQUEST` with `bad ref: <reason>`.
    - Prefer `image.edit` over `image.generate + reference_image_urls` when you have a single source image — better fidelity, simpler quota accounting.

### image.edit

*Host API method · iframe surface*

Mutate an existing image URL using a text prompt; the source image is not modified. Requires a stricter grant (`image_grant.allowEdit = true`) than `image.generate` because edits often imply higher provider cost. Optional `mask_url` enables inpainting where the provider supports it.

**Signature**

```ts
anna.image.edit(args: {image_url: string, prompt: string, n?: number, size?: string, mask_url?: string}, opts?: {timeoutMs?: number}) => Promise<{images, model, ...}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade → image provider → R2

**Parameters**

- `image_url` (string, required) — The source image to edit. Must pass `validate_image_url` (no internal hostnames, no private IPs, must be `http`/`https`).
    - Typically the presigned URL returned by a prior `image.generate` (live for ~30 min), or a presigned download URL from `upload.inline`/`upload.confirm`.
    - If the URL has expired by the time the provider fetches it, the result is `APP_PROVIDER_ERROR` — re-mint the URL via `image.generate` or by re-issuing the upload flow.
    - Validation failure → `APP_INVALID_REQUEST` with `bad image_url: <reason>`.
- `prompt` (string, required) — Edit instruction (e.g. 'restyle in cyberpunk aesthetic'). Trimmed; empty → `APP_INVALID_REQUEST`.
- `n` (integer, optional) — Number of edited variants. Must be positive.
    - Clamped against `image_grant.maxPerCallEdit` (default **1**) — usually stricter than the generate cap because edit variants are expensive.
    - Edit providers often return `n=1` regardless of request; check `out.images.length` rather than assuming.
- `size` (string | undefined, optional) — Output dimensions. When omitted the provider preserves the source `image_url` dimensions.
    - Some providers reject explicit resize on edit — surfaces as `APP_PROVIDER_ERROR`.
- `mask_url` (string | undefined, optional) — Optional PNG mask URL for inpainting. White pixels = edit, black pixels = preserve.
    - Validated by `validate_image_url` — failure → `APP_INVALID_REQUEST` with `bad mask_url: <reason>`.
    - Not all providers support masks. Unsupported provider returns `MASK_UNSUPPORTED` from the gate → `APP_PROVIDER_ERROR` (HTTP 400 underneath).
    - Mask dimensions should match `image_url` dimensions; providers vary on how strictly this is enforced.


---

## upload.* — persist files without S3 credentials

*Host API · upload.**

Put binary blobs into Anna's R2 bucket using only the iframe's session token. The host signs URLs, validates MIME / purpose against `upload_grant`, charges quota, and namespaces objects under a per-(user, App) prefix. Your bundle holds zero AWS keys.

**Auth chain.** Bundle calls `anna.upload.{inline,negotiate,confirm}(...)` → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` → `_h_upload_*` handler → `SqlAlchemyWindowStore.upload_*` → `app_llm_facade.upload_*` → `host_upload_service` → R2.

**ACL is two-layer.** (a) The dispatcher gate is `manifest.ui.host_api.upload` — a `string[]` that must contain the called method (`inline` / `negotiate` / `confirm`), or `*`; `manifest.permissions[]` is display/audit only and is NEVER checked. (b) Anna Admin user-grant `UserExecuta.custom_config.upload_grant = {enabled, maxFileBytes (default 20 MiB), allowedMimeTypes, allowedPurposes, maxUploadsPerDay}`. Missing either side → `APP_NOT_GRANTED`. Default per-purpose set is `{image_input, image_reference, user_artifact}`; the grant `allowedPurposes` (if set) narrows that further.

**Three modes, one budget.** Pick `inline` for ≤ 8 MiB payloads in memory (one round-trip); pick `negotiate` + `confirm` for large/streaming uploads (bytes flow direct browser→R2). Both flows charge the same per-day file counter on **success** (`inline` on completion, `negotiate`+`confirm` on `confirm`); a bare `negotiate` without `confirm` is free but leaves an orphan R2 object that lifecycle policy will reap.

**URL lifetime & key durability.** `download_url` is a presigned GET with TTL = `expires_in` seconds (~30 min). The **`r2_key` is durable** — persist it (`anna.storage.set`) and re-mint URLs by calling `upload.confirm({r2_key})` on each refresh. SVG payloads are forced to `application/octet-stream` (attachment download) to prevent active content; plan your renderer accordingly.

- **upload.inline** — ≤ 20 MiB inline base64 upload. One round-trip; SDK should pre-check `file.size` to fall back to `negotiate` rather than re-encoding on `TOO_LARGE`.  `≤ ~8 MiB raw`

- **upload.negotiate** — Mint a presigned R2 PUT URL (~5 min TTL) + the durable `r2_key`. Does NOT charge the file counter — `confirm` does. Caller MUST copy the returned `headers` (especially `Content-Type`) onto the PUT verbatim or R2 rejects with SignatureDoesNotMatch.  `presigned-PUT`

- **upload.confirm** — HEAD R2 to verify the PUT, charge the file counter, return a fresh `download_url`. Idempotent on success (same `r2_key` re-confirm just re-mints the URL — useful for refreshing expired downloads).

---

## Detailed reference

### upload.inline

*Host API method · iframe surface*

Single-shot upload — bundle base64-encodes the file and posts it inline in the RPC body. Best for payloads ≤ 8 MiB already in memory: one round-trip vs three for the negotiate/confirm flow. The host validates MIME + purpose against `upload_grant`, decodes, writes to R2 under a per-(user, App) prefix, and returns a short-lived download URL.

**Signature**

```ts
anna.upload.inline(args: {filename: string, mime_type: string, content_b64: string, purpose?: string}, opts?: {timeoutMs?: number}) => Promise<{r2_key, mime_type, bytes_size, download_url, expires_in}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade → host_upload_service → R2

**Parameters**

- `filename` (string, required) — Human-readable filename. Used in the R2 object path and exposed in the download `Content-Disposition` for the bytes when fetched.
- `mime_type` (string, required) — Wire MIME type of the payload. Must pass BOTH the host denylist (SVG is forced to attachment, executables/macros are rejected) AND the per-user `upload_grant.allowedMimeTypes` allowlist, if set.
    - Allowlist failure → `APP_PROVIDER_ERROR` (HTTP 400 underneath) with the `host_upload_service` reason verbatim — typically `MIME_REJECTED`.
    - Glob wildcards (`image/*`) in the grant are honoured.
- `content_b64` (string, required) — Base64-encoded bytes of the file. Inline payload after decode must be ≤ `upload_grant.maxFileBytes` (default **20 MiB**).
    - Wire size ≈ 1.33× raw bytes. A 15 MiB file becomes ~20 MiB on the wire — if you regularly approach the cap, use `upload.negotiate`+`confirm` instead to skip the encode overhead.
    - Too-large → `APP_PROVIDER_ERROR` with reason `TOO_LARGE` (HTTP 400 underneath).
    - Browsers: never use `btoa(String.fromCharCode(...))` on multi-MiB buffers — it allocates a UTF-16 intermediate. Prefer `FileReader.readAsDataURL` + slice off the prefix.
- `purpose` (string, optional) — Why the file is being uploaded — used for billing categorisation and to scope `upload_grant.allowedPurposes`. Allowed values: `image_input`, `image_reference`, `user_artifact`.
    - Outside the host's set → `APP_PROVIDER_ERROR` with reason `PURPOSE_REJECTED` (HTTP 403 underneath).
    - If `upload_grant.allowedPurposes` is configured, the value must additionally appear in that allowlist.
    - Choose `image_input` when you plan to feed the result to `image.edit`/`image.generate` so billing rows correlate.

### upload.negotiate

*Host API method · iframe surface*

Step 1/2 of the large-file flow. Validates MIME + purpose against `upload_grant`, mints a presigned R2 PUT URL (5-minute TTL), and returns the `r2_key` the bundle should remember. Does **not** count against the file quota — that's charged on `upload.confirm`.

**Signature**

```ts
anna.upload.negotiate(args: {filename: string, mime_type: string, purpose?: string}, opts?: {timeoutMs?: number}) => Promise<{r2_key, put_url, expires_in, headers}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade → host_upload_service (sign-only)

**Parameters**

- `filename` (string, required) — Human-readable filename. Used in the R2 object path.
- `mime_type` (string, required) — Final MIME of the PUT body. Validated against the host denylist + `upload_grant.allowedMimeTypes`.
    - **The browser MUST send the exact same `Content-Type` header on the PUT** — R2 rejects mismatches with HTTP 403 SignatureDoesNotMatch.
    - Failure → `APP_PROVIDER_ERROR` with `MIME_REJECTED`.
- `purpose` (string, optional) — One of `image_input`, `image_reference`, `user_artifact` — additionally constrained by `upload_grant.allowedPurposes` if set. Outside the set → `APP_PROVIDER_ERROR` `PURPOSE_REJECTED`.

### upload.confirm

*Host API method · iframe surface*

Step 2/2 of the large-file flow. The host HEADs the R2 object to verify the PUT actually landed, validates size against `upload_grant.maxFileBytes`, records the upload (charging the file quota), and returns the canonical `download_url`. Idempotent on success — repeated calls re-mint the URL without double-charging.

**Signature**

```ts
anna.upload.confirm(args: {r2_key: string}, opts?: {timeoutMs?: number}) => Promise<{r2_key, mime_type, bytes_size, download_url, expires_in}>
```

**Direction:** Bundle (iframe) → Host RPC → app_llm_facade → host_upload_service (HEAD R2)

**Parameters**

- `r2_key` (string, required) — Storage handle returned by `upload.negotiate` (or a prior `upload.inline`/`upload.confirm`).
    - Used both to locate the R2 object and to derive `expected_invoke_id` for cross-check: the host parses position 4 of the slash-split path and rejects mismatches with `APP_PROVIDER_ERROR` `NOT_FOUND`.
    - Missing/empty → `APP_INVALID_REQUEST` `r2_key required`.


---

## storage.* — per-App key-value state (APS)

*Host API · storage.**

Durable JSON key-value store backed by Anna Persistent Storage (APS) — Postgres rows under a per-(user, App) bucket with quotas, optimistic concurrency, TTLs, and metadata / tag annotations. Your bundle ships zero DB credentials and zero schema migrations.

**Auth chain.** Bundle calls `anna.storage.{get,set,delete,list}(...)` → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` → `_h_aps_storage_*` handler in `src/services/anna_app_rpc_handlers/storage.py` → `StorageService.kv_*` → Postgres (`aps_entries`, row-locked with `SELECT FOR UPDATE`) + Redis Lua quota reserve. At startup `main.py` calls `anna_app_rpc_handlers.install()` which monkey-patches `_DISPATCH` so the APS handlers shadow the legacy `runtime_state` ones for `storage.get` / `storage.set` / `storage.delete` / `storage.list`.

**Two backends, one surface.** (a) **APS-backed (production)** is the canonical path — per-row etag (`W/"<gen>-<digest>"`), per-user byte / entry quota, `if_match` optimistic concurrency, `ttl_seconds`, `metadata` / `tags`, and the rich `StorageErrorCode` enum (`not_found`, `precondition_failed`, `invalid_path`, `value_too_large`, `quota_exceeded`, `forbidden_scope`, `not_granted`, `pending_upload`, `rate_limited`, `internal_error`). (b) **Legacy `runtime_state` (fallback)** lives in `anna-app-core/dispatcher.py` and keeps the whole bucket in `AnnaAppWindowSession.runtime_state` (single JSON column, hard cap **256 KiB** = `MAX_RUNTIME_STATE_BYTES`); it emits a `runtime_state_synced` event on every `set` / `delete` for cross-tab sync but does NOT support `if_match`, `metadata`, `tags`, or `ttl_seconds`. Apps that only ran against the legacy backend will silently lose live cross-window sync on the APS path — fall back to polling `storage.get` on focus.

**ACL is two-layer.** (a) The PRIMARY dispatcher gate is `manifest.ui.host_api.storage` — a `string[]` that must contain the called method (`get` / `set` / `delete` / `list`), or `*`; `manifest.permissions[]` is display/audit only and is NEVER checked. (b) Capability strings in `host_capabilities` only gate NON-default scope/owner pairs (the default `scope=app, owner=self` bucket needs none) and decide *which* scope/owner pairs are reachable: `aps.kv` / `aps` (legacy: only `scope=app, owner=self`), `aps.scope.<user|app|tool>.<read|write>` (fine-grained), or `aps.scope.admin` (everything). The gate `_check_storage_scope` rejects with `permission_denied` *before* the handler runs; cross-owner `scope=app` and `scope=tool` raise `not_implemented` today regardless of capability.

**Key & value rules.** `key`: ≤ **1024 chars**, ≤ **128 chars per `/`-segment**, no leading `/`, no empty / `.` / `..` segments, no ASCII control / `\` / zero-width / bidi chars, no leading-or-trailing whitespace per segment — enforced by `validate_kv_key` in `storage_service.py`. `value`: any JSON-serialisable type (functions / BigInts / cycles rejected at `postMessage`); `null` is legal and round-trips — **always branch on `cur.exists`**, not `cur.value`, when distinguishing absent from stored-null. `etag` is opaque; treat as a black-box token.

- **storage.get** — Read a value by key. Returns `{value, etag, generation, exists: true}` on hit, `{value: null, exists: false}` on miss / expired / soft-deleted. `etag` feeds back into `set` / `delete` as `if_match` for optimistic concurrency.  `etag`

- **storage.set** — Upsert a JSON value. Supports `if_match` (optimistic concurrency), `metadata` / `tags` (round-trip on `list`), `ttl_seconds` (auto-expire 1 s..365 d). Returns `{etag, generation, size_bytes}`. Charges per-user byte / entry quota; legacy backend caps the whole bucket at 256 KiB and broadcasts `runtime_state_synced`.  `if_match` `ttl_seconds`

- **storage.list** — Page through keys under `prefix`. Returns metadata-only rows (`{key, etag, size_bytes, metadata, tags, updated_at}`) — no `value`. `limit` 1..1000 (default 100); `cursor` is opaque, not persistable across deploys.  `paginated`

- **storage.delete** — Soft-delete a key; quota bytes are reclaimed immediately. Accepts `if_match` (APS only). APS raises `not_found` on a missing key; the legacy backend silently no-ops.

---

## Detailed reference

### storage.get

*Host API method · iframe surface*

Read a per-(user, App, key) JSON value from Anna Persistent Storage (APS). Returns the stored value plus an `etag` / `generation` for optimistic-concurrency writes, or `{value: null, exists: false}` if the key is absent. Soft-deleted and TTL-expired rows look the same as missing.

**Signature**

```ts
anna.storage.get(args: {key: string, scope?: 'app'|'user'|'tool', owner?: string}, opts?: {timeoutMs?: number}) => Promise<{value: any, etag?: string, generation?: number, exists: boolean}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (Postgres + R2)

**Parameters**

- `key` (string, required) — Path-style key under the resolved `(scope, owner)` bucket. Must pass APS path validation (≤ 1024 chars total, ≤ 128 chars per `/`-separated segment, no leading `/`, no `.` / `..` segments, no control / bidi / zero-width chars).
    - `HostRpcError("invalid_arg", "key required")` if missing / empty / non-string.
    - APS-backed handler additionally raises `invalid_path` from `validate_kv_key` when the key shape is illegal.
    - Keys are case-sensitive and not normalised — `foo/bar` and `Foo/bar` are different rows.
    - Use a stable prefix scheme (`notes/<id>`, `settings/preferences`) so `storage.list({prefix})` can page over related rows.
- `scope` ('user' | 'app' | 'tool', optional) — Visibility scope. `app` (default) reads the calling App's per-user bucket; `user` reads the user's cross-App bucket; `tool` is reserved (not yet exposed to iframes).
    - `invalid_arg` if not one of `user` / `app` / `tool`.
    - PRIMARY gate: calling `storage.*` at all requires the method to be listed in `manifest.ui.host_api.storage` (e.g. `["get","set","delete","list"]`) — this is what `host_api_allows` checks. `manifest.permissions[]` is display/audit only and is NEVER consulted by the dispatcher.
    - The default `(scope=app, owner=self)` bucket needs NO further grant once `ui.host_api.storage` allows the method. Only NON-default scopes/owners require an extra `aps.scope.<scope>.<read|write>` (or `aps.scope.admin`) entry in `manifest.host_capabilities`.
    - Any non-default scope (e.g. `scope=user`) requires the manifest to declare `aps.scope.user.read` (or `aps.scope.admin`); the gate is enforced by `_check_storage_scope` *before* the handler runs.
    - `scope=tool` raises `not_implemented` today.
- `owner` (string | undefined, optional) — When `scope=app`, target a *different* App's bucket by slug. Defaults to `self` (calling App).
    - Cross-owner reads (`scope=app` + `owner != self`) require `aps.scope.app.read` *with* cross-owner support; the matrix-nexus implementation currently raises `not_implemented` for cross-app reads.
    - Ignored for `scope=user` (the user bucket is owner-less by design).

### storage.set

*Host API method · iframe surface*

Write a JSON value under the resolved `(scope, owner, key)`. Idempotent in shape — upserts an existing row or creates a new one — but charges per-user `bytes_used` and `entry_count` quota on every call. Supports If-Match optimistic concurrency, metadata / tag annotations, and TTL-based auto-expiry.

**Signature**

```ts
anna.storage.set(args: {key: string, value: any, scope?: 'app'|'user'|'tool', owner?: string, if_match?: string, metadata?: object, tags?: string[], ttl_seconds?: number}, opts?: {timeoutMs?: number}) => Promise<{etag: string, generation: number, size_bytes: number}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (Postgres) → quota reserve

**Parameters**

- `key` (string, required) — Same shape as `storage.get` — see the validation rules there.
    - `invalid_arg` if missing / empty.
    - `invalid_path` from APS validator if illegal.
- `value` (any (JSON-serialisable), required) — Arbitrary JSON. Serialised via `json.dumps(default=str)` server-side so `datetime` / `Decimal` stringify automatically.
    - There is no bundle-side size validator: the SDK does NOT pre-check `value`. Oversize payloads surface as `value_too_large` (APS per-row cap) or `state_too_large` (legacy backend 256 KiB) on the return path.
    - Functions, BigInts, and cyclic references are rejected at `postMessage` (V8 structured clone) — you never see them server-side.
    - Storing `null` is legal and round-trips correctly; consumers must branch on `cur.exists` to distinguish stored-null from absent.
- `if_match` (string | undefined, optional) — Optimistic-concurrency token from a prior `get` / `set` / `list` row. Pass to guarantee the row hasn't been touched by someone else since you observed it.
    - `precondition_failed` if the token does not match the live row's `etag`, *including* when the row no longer exists (mirrors GCS / S3 If-Match semantics).
    - Concurrent first-insert races are also surfaced as `precondition_failed` — retry the read-modify-write loop and the second pass will hit the update branch.
    - Opaque; treat it as a black-box string. Format is `W/"<gen>-<digest>"` for the legacy backend and a payload hash for APS.
- `metadata` (object | undefined, optional) — Free-form annotation map. Not used for indexing; round-trips on `list`.
    - Stored as JSON in `aps_entries.entry_metadata`.
    - Ignored by the legacy runtime_state backend.
- `tags` (string[] | undefined, optional) — Up to 32 free-form labels. Round-trips on `list` for client-side filtering; APS does not index by tag.
    - Validated server-side by `KVSetRequest` (Pydantic) when used over the HTTP APS API; the iframe path forwards them verbatim.
    - Ignored by the legacy runtime_state backend.
- `ttl_seconds` (int | undefined, optional) — Auto-expire the row after N seconds (range 1..365 days). Expired rows look like 404 to `get` but bytes are reclaimed lazily by the GC sweep.
    - Use for short-lived caches (session id, oauth state) rather than re-implementing TTL with timestamps in `value`.
    - Bound is server-side: `KVSetRequest.ttl_seconds` is `ge=1, le=60*60*24*365`.
    - Ignored by the legacy runtime_state backend.
- `scope` ('user' | 'app' | 'tool', optional) — Same as `storage.get`. Non-default scopes need `aps.scope.<scope>.write` in the manifest.
    - Write action gate; `_check_storage_scope(manifest, 'set', args)` maps to `aps.scope.<scope>.write`.
    - Cross-owner writes (`scope=app`, `owner != self`) raise `not_implemented` today.
- `owner` (string | undefined, optional) — App slug to target (cross-app writes only). Defaults to the calling App.

### storage.delete

*Host API method · iframe surface*

Remove a key from the resolved `(scope, owner)` bucket. The row is soft-deleted (kept for forensic / restore tooling) but immediately disappears from `get` / `list` and its bytes are returned to the per-user quota.

**Signature**

```ts
anna.storage.delete(args: {key: string, scope?: 'app'|'user'|'tool', owner?: string, if_match?: string}, opts?: {timeoutMs?: number}) => Promise<{deleted: true}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (soft-delete + quota release)

**Parameters**

- `key` (string, required) — Same validation as `storage.get`.
- `if_match` (string | undefined, optional) — Optimistic-concurrency token. Pass to guarantee you delete the exact row you observed (e.g. avoid clobbering a re-created entry under the same key).
    - `precondition_failed` if the etag does not match the live row.
    - Ignored by the legacy backend (which has no per-row etag).
- `scope` ('user' | 'app' | 'tool', optional) — Same gating as `storage.set` (`action='write'` → needs `aps.scope.<scope>.write`).
- `owner` (string | undefined, optional) — Cross-app delete target slug. Defaults to self.

### storage.list

*Host API method · iframe surface*

Enumerate keys in the resolved `(scope, owner)` bucket whose path starts with `prefix`. Returns metadata-only rows (no `value` — call `storage.get(key)` per item if you need the payload). Paginated by an opaque `cursor`.

**Signature**

```ts
anna.storage.list(args?: {prefix?: string, cursor?: string, limit?: number, scope?: 'app'|'user'|'tool', owner?: string}, opts?: {timeoutMs?: number}) => Promise<{items: Array<{key: string, etag: string, size_bytes: number, metadata: object|null, tags: string[]|null, updated_at: string|null}>, next_cursor: string|null}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (prefix scan)

**Parameters**

- `prefix` (string, optional) — Path-prefix filter. Empty string lists the whole bucket.
    - May end with `/` (matches a directory-style prefix) and may include empty trailing segments (`a/` is legal).
    - Otherwise follows the same validation as `key` — `..` segments, control chars, and absolute paths are rejected with `invalid_path`.
    - Match is plain `startswith` — there is no glob, no regex, no SQL `LIKE` wildcard escaping required from the caller (the service does it internally).
- `cursor` (string | undefined, optional) — Opaque pagination cursor returned by a prior `list` call as `next_cursor`.
    - Encodes the last seen key (base64-ish); not stable across schema changes. Always re-paginate from the start when retrying.
    - Passing a stale cursor returns rows that sort after it — may legitimately yield zero items if the bucket was drained.
    - Legacy backend uses the raw key as the cursor (no encoding); APS encodes it.
- `limit` (int, optional) — Page size, 1..1000. Default 100.
    - `invalid_arg` if non-int.
    - Values ≤ 0 or > 1000 raise `invalid_arg` on the legacy backend; the APS backend clamps silently via `max(1, min(limit, LIST_MAX_LIMIT))`.
- `scope` ('user' | 'app' | 'tool', optional) — Non-default scopes need `aps.scope.<scope>.read`.
- `owner` (string | undefined, optional) — Cross-app listing target. Defaults to self.


---

## llm.embed — host-managed embeddings (RAG / semantic search)

*Host API · llm.embed*

Compute dense embedding vectors from the **anna-app bundle (iframe)** with zero provider credentials, zero hard-coded model names, and **independent billing** from `llm.complete`. Your bundle gets an OpenAI-compatible `{model, data:[{index,embedding}], usage, _meta}` envelope so RAG / semantic-search / clustering code lifted straight from any OpenAI tutorial drops in.

**Auth chain.** Bundle calls `anna.llm.embed({input, model?, user?})` → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` → `_h_llm_embed` handler in `anna_app_core.dispatcher` → `SqlAlchemyWindowStore.llm_embed` (mints / reuses the `kind=complete` `app_session_token`, **same token as `llm.complete`** since the two are billed against distinct `LLMRequestType`s) → `app_embed_facade.embed` → `EmbeddingRegistry.client_for(spec).embed(inputs)` → provider.

**Two-surface billing isolation.** `llm.complete` debits `APP_LLM` quota; `llm.embed` debits `APP_EMBED` quota via `LLMTokenUsageService.record_usage(request_type=APP_EMBED, ...)`. Exhausting one does NOT block the other. The 2026-05-28 simplification removed the daily token pool and per-invoke token cap — embed is now purely pay-per-token through the standard usage table.

**ACL.** The dispatcher gate is `manifest.ui.host_api.llm` — it must include `embed` (or `*`); `manifest.permissions[]` is display/audit only and is NEVER checked. (c) `UserAnnaApp.custom_config.embed_grant` defaults to `{enabled: true}` when absent — **opt-out**, not opt-in (rationale: embed is near-universally needed for RAG; the real risk is token spend which the billing surface already governs). Users can disable per-app via `embed_grant: {enabled: false}` → `APP_NOT_GRANTED`.

**Stable alias contract.** Only host-stable aliases are exposed (`anna-managed-v1` = `openai/text-embedding-3-small`, 1536-dim). Real provider model name surfaces in `_meta.backendModel` for audit. **Dimensions are immutable per alias** — upgrades go to a new alias (`anna-managed-v2`); never an in-place dim change. Persist `_meta.alias` + `_meta.dimensions` next to every stored vector or you risk silent dim drift after a registry rotation.

**Limits & rejection policy.** Batch ≤ `min(spec.max_inputs_per_request, EMBED_MAX_INPUTS_PER_REQUEST=64)` items, each ≤ `EMBED_MAX_CHARS_PER_INPUT=32_000` chars. **Reject-not-truncate**: any single oversize item or one-too-many batch fails the whole request with `APP_INVALID_REQUEST` — chunk client-side and keep an index map. Provider errors are flattened to a single `APP_PROVIDER_ERROR`; the upstream code is NOT preserved.

- **llm.embed** — Compute dense embeddings for one string or a batch. Returns OpenAI-shaped `{object:'list', model, data:[{index,embedding}], usage, _meta}`. `model` is the stable alias (persist this), `_meta.dimensions` is immutable per alias, `_meta.backendModel` is audit-only. Independent billing surface from `llm.complete`.  `alias` `OpenAI-shape` `APP_EMBED billing`

---

## Detailed reference

### llm.embed

*Host API method · iframe surface*

Compute one or more dense embedding vectors **on the user's behalf** — your bundle never holds an embedding API key, never hard-codes a provider model, and the call is metered against the user's plan on an **independent embed billing surface** (`LLMRequestType.APP_EMBED`). Returns an OpenAI-compatible envelope so RAG / semantic-search / clustering code drops in straight from any OpenAI tutorial. Sibling of `llm.complete` — they share the lazy-minted `kind=complete` `app_session_token` but bill against separate `LLMRequestType`s, so a depleted chat quota does not break embeddings (and vice-versa).

**Signature**

```ts
anna.llm.embed(args: {input: string | string[], model?: string, user?: string}, opts?: {timeoutMs?: number}) => Promise<{object: 'list', model: string, data: Array<{object: 'embedding', index: number, embedding: number[]}>, usage: {prompt_tokens: number, total_tokens: number}, _meta: {alias: string, dimensions: number, backendModel: string, provider: string, latencyMs: number, quotaConsumed: number, costUsd: number}}>
```

**Direction:** Bundle (iframe) → Host RPC → app_embed_facade.embed → embedding registry → provider

**Parameters**

- `input` (string | string[], required) — Text(s) to embed. A bare string is auto-wrapped to a single-element list. Empty / whitespace-only items are rejected; the whole request fails if **any** item is invalid (no per-item soft-skip).
    - `APP_INVALID_REQUEST` if missing, wrong type, empty list, or any item is non-string / blank.
    - Per-request batch cap: `min(spec.max_inputs_per_request, settings.EMBED_MAX_INPUTS_PER_REQUEST = 64)`. Overrun → `APP_INVALID_REQUEST` with `too many inputs: N > max=64`.
    - Per-item char cap: `settings.EMBED_MAX_CHARS_PER_INPUT = 32_000` (≈ 8 K token). Overrun on **any** item → `APP_INVALID_REQUEST` — chunk client-side, no silent truncation.
    - Order is preserved verbatim — `data[i].index` mirrors input order, but always branch on `index` not array position for defence.
- `model` (string, optional) — Host-stable **alias** — never a real provider model name. Resolved by `EmbeddingRegistry.resolve(alias)`. Unknown alias → `APP_INVALID_REQUEST` with the full list of available aliases echoed back in the message.
    - Today's registered aliases: `anna-managed-v1` (= `openai/text-embedding-3-small`, 1536-dim). `anna-managed-v2` is only registered when `EMBEDDING_ENABLE_V2 = true` (rollout flag, default `false`).
    - **Dimensions are an immutable contract.** Once an alias ships at N dim, it never changes; new dim ⇒ new alias. Persist `_meta.alias` + `_meta.dimensions` alongside every stored vector so cross-version reads can refuse / reindex.
    - The real backend model name surfaces in `_meta.backendModel` for audit only — do not branch on it.
- `user` (string, optional) — Optional caller-side tag forwarded to the provider as the `user` label (OpenAI / OpenRouter use this for abuse mitigation). Defaults to `"u{user_id}"` when omitted.
    - Not validated, not rate-limited, not logged in `request_summary` — purely a provider passthrough.
    - Use a stable, anonymised value (e.g. hashed user-app pair) if you want providers to bucket your requests; do NOT leak real PII.


---

## files.* — per-App blob storage (APS objects + R2)

*Host API · files.**

Durable **object** storage backed by Anna Persistent Storage (APS): a `aps_entries` row in Postgres for metadata + a presigned-URL handle on Cloudflare R2 for the bytes. Your bundle never proxies bytes through nexus — browser PUTs directly to R2 on upload, browser GETs directly from R2 on read. Server-side stays cheap; large files don't pin a request worker.

**Auth chain.** Bundle calls `anna.files.{upload_init,upload_finalize,download_url,list,delete}(...)` → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` → `_h_files_*` handler in `src/services/anna_app_rpc_handlers/files.py` → `StorageService.object_*` → Postgres (`aps_entries`) + R2 presign (PUT/GET) + Redis Lua quota. At startup `main.py` calls `anna_app_rpc_handlers.install()` which monkey-patches `_DISPATCH` so these handlers shadow the legacy `_h_not_implemented` stubs declared in `anna-app-core/dispatcher.py` (necessary so the AST-generated `methods.json` knows the methods exist).

**Two-phase upload.** `files.upload_init` reserves the row (status `pending`), counts bytes against quota, and returns a single-use R2 presigned PUT URL. The browser streams the file directly to R2. Then `files.upload_finalize` calls R2 `HEAD` to verify bytes-and-etag, flips the row to `active`, and commits the quota reservation. Orphaned `pending` rows expire after `ttl_seconds` and free quota automatically — no manual cleanup. This is the *only* upload pattern; there is no synchronous `files.put(bytes)`.

**ACL.** The ONLY dispatcher gate is `manifest.ui.host_api.files` — a `string[]` that must list each called method (or `*`). `manifest.permissions[]` is display/audit only and is NEVER checked, and the `files.*` handlers always operate at `scope=app, owner=window.app_id`, so `host_capabilities` (`aps.*`) is NOT consulted for the iframe files surface. The dispatch ACL gate runs *before* the handler.

**Concurrency.** Every `active` row carries an opaque `etag` (`W/"<gen>-<digest>"`). `upload_init` and `delete` accept `if_match` for optimistic-concurrency writes against an existing entry — mismatch raises `precondition_failed`. `download_url` / `list` return the current `etag` so callers can carry it forward.

**Limits.** Per-object byte cap (`APS_OBJECT_MAX_BYTES`), per-user byte + entry quota, presigned URL TTL clamped to `APS_PRESIGN_{PUT,GET}_TTL_MAX_S`. Errors share the storage `StorageErrorCode` enum: `not_found`, `precondition_failed`, `invalid_path`, `value_too_large`, `quota_exceeded`, `forbidden_scope`, `not_granted`, `pending_upload`, `rate_limited`, `internal_error`.

- **files.upload_init** — Phase 1 of upload — reserve a `pending` row, count `size` against quota, return a single-use R2 presigned PUT URL the browser uses directly. Pair with `upload_finalize`.  `presign PUT` `quota` `if_match`

- **files.upload_finalize** — Phase 2 of upload — verify the PUT with R2 `HEAD`, flip the row to `active`, commit quota, return the canonical `etag` / `generation`.  `etag`

- **files.download_url** — Mint a short-lived R2 presigned GET URL. Embed in `<img>` / `<video>` / `<a href>`. Optional `disposition` forces a download dialog.  `presign GET` `ttl_seconds`

- **files.list** — Page metadata-only rows under an optional `prefix`. Returns `path`, `etag`, `size_bytes`, `content_type`, `metadata`, `tags`, `updated_at`. Cursor-based.  `paginated`

- **files.delete** — Soft-delete; quota reclaimed immediately, R2 object reaped async. Accepts `if_match`.  `if_match` `soft-delete`

---

## Detailed reference

### files.upload_init

*Host API method · iframe surface*

Phase 1 of a two-phase blob upload. Reserves a per-(user, App) `aps_entries` row (status `pending`), counts it against the user's byte quota, and returns a short-lived **R2 presigned PUT URL** the browser uses to stream the bytes directly to object storage — bypassing your server entirely. Pair every successful PUT with `files.upload_finalize`; orphaned `pending` rows expire after `ttl_seconds` and free the quota automatically.

**Signature**

```ts
anna.files.upload_init(args: {path: string, content_type: string, size: number, ttl_seconds?: number, metadata?: object, tags?: string[], if_match?: string}, opts?: {timeoutMs?: number}) => Promise<{upload_id: string, put_url: string, headers: Record<string,string>, expires_at: string, r2_key: string}>
```

**Direction:** Bundle (iframe) → Host RPC → APS → R2 presign

**Parameters**

- `path` (string, required) — Logical path under the calling App's bucket. Subject to the same `validate_kv_key` rules as `storage.*` keys (≤ 1024 chars total, ≤ 128 per `/`-segment, no leading `/`, no `.` / `..` segments, no control / bidi / zero-width chars).
    - `HostRpcError("invalid_arg", "path required (string)")` if missing / empty / non-string.
    - Re-uploading the same path produces a new row by default; pass `if_match` to enforce optimistic concurrency against an existing entry's `etag`.
- `content_type` (string, required) — MIME type the browser will set in the PUT `Content-Type` header. Stored alongside the entry and returned by `download_url` / `list` so consumers can render without sniffing.
    - Must match the PUT exactly — R2 rejects the presigned request if the header differs from the signed value.
- `size` (number (int), required) — Declared byte length. Reserved against the user's APS byte quota immediately; over-quota raises `quota_exceeded` *before* a presign URL is issued.
    - `invalid_arg` if missing or non-coercible to int.
    - The actual PUT body length is verified on `upload_finalize` via R2 `HEAD`; mismatch raises `precondition_failed` and the row stays `pending`.
- `ttl_seconds` (number (int), optional) — Presign URL lifetime AND the `pending` row's reclamation window. Orphaned rows (never finalized) are reaped after this many seconds and their quota reservation is released.
- `metadata` (object, optional) — Free-form JSON metadata stored on the row. Round-trips on `list`. No size limit beyond the row's total JSON budget.
- `tags` (string[], optional) — Sortable / filterable tags. Round-trips on `list`. Useful for cheap server-side categorisation without a separate index.
- `if_match` (string (etag), optional) — Optimistic-concurrency guard against an *existing* entry at the same path. Pass the prior `etag` you read via `download_url` / `list`; mismatch raises `precondition_failed`.

### files.upload_finalize

*Host API method · iframe surface*

Phase 2 of the upload. Verifies the PUT actually landed in R2 (`HEAD` for byte length / etag), flips the `pending` row to `active`, commits the quota reservation, and returns the canonical `etag` / `generation` you'll use for subsequent `if_match` writes.

**Signature**

```ts
anna.files.upload_finalize(args: {path: string, etag?: string, size?: number, size_bytes?: number, metadata?: object}, opts?: {timeoutMs?: number}) => Promise<{path: string, etag: string, generation: number, size_bytes: number}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (R2 HEAD verify + row flip)

**Parameters**

- `path` (string, required) — Same logical path passed to `upload_init`. The service looks up the matching `pending` row by `(user, app, path)`.
- `etag` (string, optional) — R2-returned ETag from the PUT response. When provided, the service verifies it matches R2's `HEAD` reply; mismatch raises `precondition_failed`.
- `size` (number (int), optional) — Alias for `size_bytes` (SDK accepts either). Cross-checked against the R2 `HEAD` content-length.
- `size_bytes` (number (int), optional) — Declared byte length. Cross-checked against R2 `HEAD`.
- `metadata` (object, optional) — Optional metadata replacement; merges over what was set in `upload_init`.

### files.download_url

*Host API method · iframe surface*

Mint a short-lived R2 presigned GET URL for an `active` entry. Use this in `<img src>` / `<video src>` / `fetch()` to stream the bytes directly from object storage without proxying through nexus. Optional `disposition` controls the `Content-Disposition` header baked into the signature (e.g. force a download dialog).

**Signature**

```ts
anna.files.download_url(args: {path: string, ttl_seconds?: number, ttl?: number, disposition?: string}, opts?: {timeoutMs?: number}) => Promise<{get_url: string, expires_at: string, etag: string, size_bytes: number, content_type: string}>
```

**Direction:** Bundle (iframe) → Host RPC → APS → R2 presign GET

**Parameters**

- `path` (string, required) — Logical path of the existing entry.
- `ttl_seconds` (number (int), optional) — URL lifetime in seconds. Clamped by `APS_PRESIGN_GET_TTL_MAX_S` server-side.
- `ttl` (number (int), optional) — Backward-compatible alias for `ttl_seconds`.
- `disposition` (string, optional) — `Content-Disposition` value to bake into the signature, e.g. `attachment; filename="report.pdf"` to force a download dialog instead of inline render.

### files.list

*Host API method · iframe surface*

Page through the calling App's file entries under an optional `prefix`. Returns metadata only — no bytes, no presigned URLs. Cursor-based; cursors are opaque and not stable across deploys.

**Signature**

```ts
anna.files.list(args: {prefix?: string, cursor?: string, limit?: number}, opts?: {timeoutMs?: number}) => Promise<{items: Array<{path: string, etag: string, size_bytes: number, content_type: string, metadata: object|null, tags: string[]|null, updated_at: string|null}>, next_cursor: string|null}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (Postgres)

**Parameters**

- `prefix` (string, optional) — Match entries whose `path` starts with this string. Empty / omitted lists the whole bucket.
- `cursor` (string, optional) — Opaque pagination cursor from a prior call's `next_cursor`.
- `limit` (number (int), optional) — Max rows per page. Service clamps to `APS_LIST_LIMIT_MAX` (typically 1000).

### files.delete

*Host API method · iframe surface*

Soft-delete an entry. The row is marked `deleted`, quota bytes are reclaimed immediately, and the underlying R2 object is hard-deleted asynchronously by the APS reaper. Supports `if_match` for safe concurrent-write scenarios.

**Signature**

```ts
anna.files.delete(args: {path: string, if_match?: string}, opts?: {timeoutMs?: number}) => Promise<{deleted: true}>
```

**Direction:** Bundle (iframe) → Host RPC → APS (Postgres soft-delete; R2 reaped async)

**Parameters**

- `path` (string, required) — Logical path of the entry to delete.
- `if_match` (string (etag), optional) — Optimistic-concurrency guard. Pass the etag you last observed; mismatch raises `precondition_failed` so a concurrent re-upload isn't silently clobbered.


---

## tools.* — call Executa tools from the UI

*Host API · tools.**

Drive any installed Executa tool directly from the **anna-app bundle** (iframe), bypassing the LLM. Useful for deterministic UI actions — "click this button → run this tool" — where you don't want the model in the loop.

**Auth chain.** Bundle calls `anna.tools.{list,invoke}(...)` from the SDK proxy → postMessage → `POST /api/v1/anna-apps/runtime/rpc` with `X-Anna-App-Token` (minted by `window.create`) + session cookie → `_h_tools_*` handler in `anna_app_core.dispatcher`. The token is never exposed to JS that didn't go through the SDK.

**ACL is two-layer.** A tool must be (a) declared in `manifest.required_executas` or `optional_executas`, AND (b) matched by an entry in `manifest.ui.host_api.tools` (`"required:*"`, `"optional:*"`, the bare `tool_id`, or any `<prefix>:<tool_id>`). `tools.list` returns exactly the intersection; `tools.invoke` re-checks per call and rejects with `permission_denied`.

**Timeout policy** (`tools.invoke` only). Caller-supplied `timeoutMs` is clamped to `[ANNA_APP_TOOLS_INVOKE_TIMEOUT_MIN_MS, _MAX_MS]` (defaults **1 s / 180 s**). When omitted, the Agent falls back to the plugin's manifest `tool_def.timeout`, or `_DEFAULT_MS` (**65 s**). Host wall-clock wait is `clamped + GRACE_MS` (default **2 s**) so an in-flight ack/cancel has room to land before `tool_timeout` fires. See RFC `docs/design/anna-app-tools-invoke-timeout.md`.

**Envelope stripping.** The raw NATS reply is `{success, data:{success, data:<payload>, error?}}`. The host unwraps both layers: outer-layer failure → `executa_unavailable`, inner-layer failure → `tool_failed`, otherwise the plugin payload (forced to `object`) lands on the iframe Promise.

- **tools.list** — Project the manifest's tool grants. Returns `{tools: [{tool_id}]}` filtered through the `host_api.tools` whitelist. Pure ACL — no Agent / NATS round-trip; safe to call at bundle boot to decide which buttons to render.

- **tools.invoke** — Call one tool by id with structured `args` and an optional clamped `timeoutMs`. Routes through the user's online Executa Agent over NATS, strips two envelope layers, and returns the plugin payload — or a stable error code (`tool_timeout`, `tool_failed`, `executa_unavailable`, `agent_unavailable`, `permission_denied`, `invalid_arg`).  `timeoutMs`

---

## Detailed reference

### tools.list

*Host API method · iframe surface*

Return every Executa `tool_id` this window is *currently allowed* to invoke. Pure ACL projection — no Agent round-trip, no NATS call. Useful at bundle boot to decide which UI buttons to render before the user clicks.

**Signature**

```ts
anna.tools.list(args?: {}, opts?: {timeoutMs?: number}) => Promise<{tools: Array<{tool_id: string}>}>
```

**Direction:** Bundle (iframe) → Host RPC → manifest ACL

### tools.invoke

*Host API method · iframe surface*

Invoke a single Executa tool *directly from the bundle*, bypassing the LLM. The host enforces the `host_api.tools` whitelist, mints credentials, negotiates a deadline, calls the user's online Executa Agent over NATS, and returns the plugin's payload — two envelope layers stripped — to the iframe.

**Signature**

```ts
anna.tools.invoke(args: {tool_id: string, method?: string, args?: object, timeoutMs?: number}, opts?: {timeoutMs?: number}) => Promise<object>
```

**Direction:** Bundle (iframe) → Host RPC → Executa Agent (NATS) → plugin

**Parameters**

- `tool_id` (string, required) — Server-minted Executa tool id; must be present in the `tools.list` projection.
    - Format is opaque. Mint-only ids look like `tool-{handle}-{slug}-{uniq}` (no separator); legacy ids use `plugin.tool` or `plugin__tool` — both still routed by `_split_tool_id`.
    - Must match an entry in `manifest.ui.host_api.tools`. The runtime gate `_is_tool_allowed` accepts `required:*`, `optional:*`, the bare id, or any ref ending in `:<tool_id>`; otherwise `permission_denied`. For authoring, the CLI `anna-app validate` only permits the canonical forms `required:*` / `optional:*` / `required:<id>` / `optional:<id>` / bare `<id>` / `bundled:<handle>`.
    - Reject reasons (HostRpcError `invalid_arg`): missing, empty, or non-string.
- `method` (string | undefined, optional) — Plugin-side method name. **Required** for mint-only `tool_id`s that contain no `.` or `__` separator.
    - When omitted, the host falls back to splitting `tool_id` on the first `__` or `.` separator — failing with `invalid_arg` if neither is present.
    - When provided, `tool_id` is used verbatim as `plugin_name` and `method` becomes `tool_name` on the NATS call.
    - Must be a string when set; non-string types raise `invalid_arg`.
- `args` (object, optional) — Structured tool arguments forwarded verbatim to the plugin as `arguments`.
    - JSON-serialised by the SDK; functions, BigInts, and cyclic refs are rejected at `postMessage` time.
    - Schema is plugin-defined — see the Executa's manifest `tools[].parameters`. The host does not validate field-level shape; an unknown field is silently passed through (or rejected by the plugin).
- `timeoutMs` (int | undefined, optional) — Caller-requested plugin-facing deadline in **milliseconds**. Clamped server-side to `[ANNA_APP_TOOLS_INVOKE_TIMEOUT_MIN_MS, _MAX_MS]` (defaults 1 000 / 180 000).
    - Booleans are rejected explicitly (`invalid_arg`) — `True`/`False` would otherwise clamp via the `bool ⊂ int` quirk.
    - When omitted, the Agent falls back to the per-tool `timeout` declared in the Executa manifest, or `ANNA_APP_TOOLS_INVOKE_TIMEOUT_DEFAULT_MS` (65 000) if neither side declares one.
    - Host wall-clock wait = clamped value + `ANNA_APP_TOOLS_INVOKE_TIMEOUT_GRACE_MS` (2 000) so an in-flight ack/cancel has room to land before `tool_timeout` fires.
    - SDK default per-call timeout is 70 000 ms (`DEFAULT_TIMEOUTS_BY_NS.tools`); pass a larger value here *and* in `opts.timeoutMs` if the plugin needs longer.


---

## window.* — window lifecycle & chrome

*Host API · window.**

Open additional views, react to focus, update titles. `window.hello` / `ready` / `report_error` bypass the host_api ACL because they are part of the bundle handshake.

- **window.hello** — Initial handshake from the bundle to the runtime.  `no auth`

- **window.ready** — Bundle signals it is ready to receive `runtime_state` and events.  `no auth`

- **window.report_error** — Forward a bundle-side exception to the host error log.  `no auth`

- **window.open_view** — Open one of the views declared in `ui.views`.

- **window.close** — Close the current (or named) view.

- **window.focus** — Pull a view to the foreground.

- **window.set_title** — Update the window chrome title at runtime.

- **window.resize** — Programmatically resize the current view (subject to min/max in the view spec).


---

## Reserved namespaces (stubs)

*Host API · reserved*

Declared in the dispatch table but not yet implemented. Calls return a structured "not implemented" error. Listed here so manifest authors know the namespace names are reserved.

- **artifact.create** — Artifact create — reserved.  `stub`

- **artifact.update** — Artifact update — reserved.  `stub`

- **artifact.delete** — Artifact delete — reserved.  `stub`

- **fs.read** — Sandboxed filesystem read — reserved.  `stub`

- **fs.write** — Sandboxed filesystem write — reserved.  `stub`

- **prefs.get** — User preference reads — reserved.  `stub`


---

## AnnaAppEvent — SSE event kinds

*Realtime · SSE*

The host streams events back to your bundle as `event: data_model/AnnaAppEvent` frames. Treat unknown kinds as forward-compatible — drop, don't throw.

- **ping** — Keep-alive heartbeat. Ignore unless you care about connection liveness.

- **open_view** — A new view instance was opened (typically by `window.open_view` or `default=true`).

- **close_view** — A view instance was closed by the user or the bundle.

- **window_focus_changed** — Focus moved between views.

- **geometry_changed** — The user resized or moved a window.

- **title_changed** — The window title was updated (via `window.set_title`).

- **status_changed** — High-level App status transition surfaced by the runtime.

- **runtime_state_synced** — Hydrated state delivered after `window.ready`, or after a remote storage write.

- **artifact_appended** — A `chat.append_artifact` call landed in the conversation.

- **chat_message_from_app** — A `chat.write_message` call from this App was committed to the thread.

- **rpc.stream** — Progressive frame from a streaming RPC (tool or LLM call).  `streaming`


---

## Runtime + schema packages

*SDK · npm / PyPI*

Published bundles you can pull into your App or test harness. Source lives under `packages/` in matrix-nexus. There is **no** Executa SDK — an Executa is any process that reads a JSON line on stdin and writes one on stdout, so Python / Node / Go plugins need nothing from this list beyond the optional test harness.

- **@anna-ai/app-runtime** — Browser runtime SDK loaded by every Anna App iframe — a typed proxy over the postMessage RPC bridge to the host (Anna dashboard / `anna-app dev` harness): Host API client, event subscription, runtime_state hooks. This is the package your App bundle imports.  `npm`

- **@anna-ai/app-schema** — Versioned schema bundle (AppManifest, UiManifestSection, host_api method table, AnnaAppEvent SSE union). Single source of truth; the same payload ships to npm and (as `anna-app-schema`) to PyPI.  `npm` `pypi`

- **anna-app-core** — Python platform core — manifest schemas, RPC dispatcher, protocols, error types. Shared by matrix-nexus and the local-dev runtime; you rarely import it directly.  `pypi`

- **anna-app-runtime-local** — Local-dev in-memory runtime used by `anna-app dev` so you can iterate without a hosted nexus. Wraps `anna-app-core`'s dispatcher with an in-memory window store + WebSocket bridge; the CLI pins a compatible version.  `pypi` `dev-only`

- **anna-executa-test** — Pytest plugin + helpers for Executa stdio JSON-RPC plugin authors — boots your binary, replays JSON-RPC fixtures, asserts responses.  `pypi`


---

## anna-app CLI commands

*CLI · anna-app*

The developer CLI — `anna-app`, published as `@anna-ai/cli`. It is the **supported, best-practice path** for everything a third-party developer does: scaffold projects, validate manifests, run an App or a single Executa **in isolation**, publish / version / release to any Anna Nexus host, and manage dev-mode auth. The CLI wraps the developer REST surface — drive your workflow through these commands, not the raw endpoints.

**Identity & namespacing.** Apps publish under your developer `@handle` as `@handle/slug` — set it once with `anna-app account set-handle`. The CLI caches server identity in `.anna/app.json` (apps) and `.anna/executa.json` (standalone executas) so re-publishes are idempotent.

**Working-draft vs version model.** `apps push` upserts a single mutable *working draft* (safe to run on every commit — no SemVer assigned, executa deps not frozen); `apps cut <version>` snapshots that draft into an immutable version; `apps release <version>` publishes a version live. `apps publish` is the one-shot 'mint a new immutable version' path. The bare `anna-app publish` auto-detects app vs executa from the cwd.

**Exit codes:** `0` success · `1` runtime error (e.g. an invoke returned an error envelope, or a missing PAT scope) · `2` launch / config problem (bad flags, no saved PAT). Most commands accept `--json` for machine-readable output and `--account <host>` to select a saved account.

### App workflow

- **anna-app init <dir>** — Scaffold a new Anna App project. `--slug` defaults to the dir basename; `--template minimal` (default) ships a working UI+manifest; `--force` overwrites a non-empty target.  `scaffold`

- **anna-app validate** — Run schema + ACL checks on `manifest.json` (and the matching `--bundle <dir>`). `--strict` adds a `host_api` ACL grep against the bundle. Same validators the upload path runs server-side.  `ci-safe`

- **anna-app dev** — Run the App against an in-process harness (dispatcher + iframe + SSE relay). Auto-discovers executas under `<manifest-dir>/executas/`. Common flags: `--port` (5180), `--user-id` (1), `--bundle`, `--view`, `--matrix-nexus-root` (or `$ANNA_NEXUS_ROOT`), `--no-watch`, `--no-llm`, `--mock-llm <fixture>`, `--llm-account <host>`, `--llm-app-slug`, `--storage legacy|aps` (default `legacy` = in-memory `runtime_state`; `aps` = real nexus APS via `/api/v1/storage/*`, needs `anna-app login`). Repeatable `--executa 'dir=...,type=...'` overrides discovery.  `local harness`

- **anna-app fixture verify <file>** — Schema + invariant checks on a harness JSONL recording. `--json` emits machine-readable output.

- **anna-app fixture summarize <file>** — Human-readable digest of a harness recording (event counts, durations, sampling/storage calls).

- **anna-app fixture replay <file>** — Dry-run replay against the current manifest (Phase 6 MVP). `--manifest <path>` overrides the default `manifest.json`.

### `anna-app dev` — `executas/` discovery & `executa.json`

- **Discovery order under `<manifest-dir>/executas/<name>/`** — First match wins, stop: 1. `executa.json` (explicit; `tool_id` required) → 2. `pyproject.toml` (`type=python`, tool_id = first key of `[project.scripts]`) → 3. `package.json` (`type=node`, tool_id = `executa.tool_id` → first key of `bin` → `name`) → 4. `go.mod` **alone** errors out — `go.mod` has no script-name field, you must add `executa.json` → 5. `bin/<dirname>` executable (`type=binary`, tool_id = the subdirectory name). No match = silently skipped (so `executas/<skill>/SKILL.md`-only folders coexist with launchable plugins).

- **`executa.json` schema** — Required: `tool_id` (must match every reference in `manifest.json`/`bundle/`), `type` (`python`|`node`|`go`|`binary`). Optional: `command` (argv array; fully overrides type default, cwd = this subdirectory), `enabled` (default `true`; set `false` to exclude from auto-discovery), `_comment` (free-form annotation, ignored by CLI).

- **Per-`type` default `command`** — `python` → `["uv","run","--project",<dir>,<tool_id>]` (needs `uv` 0.1+; `<tool_id>` must be a `[project.scripts]` key). `node` → `["node", <entry>]` where entry = `bin[tool_id]` → `bin` (string) → `main` → `module` (needs Node 18+; harness does NOT run `npm install`). `go` → `["go","run","."]` (needs Go 1.21+; first launch compiles + caches). `binary` → `[<dir>/bin/<tool_id>]` if present, otherwise you MUST set `command`.

- **Duplicate `tool_id` dedup** — When two subdirectories declare the same `tool_id`, only the first registration is kept; the rest are skipped with `⚠ skipping executa <name>: tool_id "..." already provided by <other>`. This is the mechanism behind shipping multiple language flavours of the same plugin and toggling the active one via the `enabled` field in each `executa.json`.

- **`--executa dir=…,…` (App harness flag)** — Repeatable. Mix-and-match registrations for executas living **outside** `executas/`, or override the auto-detected `command` for one run. Spec syntax: comma-separated `key=value` (all keys lowercase). Keys: `dir=` (always required). With **only** `dir=`, the launcher auto-discovers the executa exactly like the `executas/` rules above. The moment you pass `type=` **or** `command=`, you must **also** pass `tool_id=` — the parser otherwise fails with `--executa spec missing tool_id=`. `command=` accepts a shell-split string or a JSON array (use the JSON form when args contain spaces). When `--executa` is used **at all**, it fully replaces auto-discovery for the run. `--executa dir=…` **bypasses `enabled: false`** — the explicit flag wins over the auto-discovery dedup gate.

- **End-to-end wiring** — CLI walks `executas/`, sends `{tool_id, project_dir, command}` triples to the Python bridge via JSON-RPC `executas.register`. Bridge (`anna_app_runtime_local.executa.ExecutaPool`) records each spec in `_specs[tool_id]` but does NOT spawn yet. On the first `anna.tools.invoke({tool_id, …})` from the bundle, the bridge lazy-spawns the subprocess (cwd = `project_dir`), opens stdio JSON-RPC, and forwards the call. Subsequent invocations reuse the same process; pool cleans up on harness shutdown.

### Standalone Executa workflow

- **anna-app executa init <dir>** — Scaffold a standalone Executa plugin. `--template python|node|go` (default: `python`). `--slug` defaults to the dir basename; `--tool-id` overrides the default `tool-dev-<slug>`. `--force` overwrites a non-empty target.  `python/node/go`

- **anna-app executa register** — Register a **harness** AnnaApp (`kind=executa`) so `executa dev`'s real-mode reverse RPCs (storage / agent / sampling / image / upload) can mint tokens for a local executa subprocess. `--tool-id` is required; `--slug` defaults to `executa-<tool_id>`; `--name` defaults to `<tool_id>`. Idempotent. Usually optional — real-mode `executa dev` auto-registers on first mint. Does **not** publish the executa itself (use `executa publish`).  `idempotent`

- **anna-app executa install** — Install a local-dev shim for an Executa under its minted `tool_id` so the Agent can pick it up via 'Rediscover Local' (for `distribution_type: local`). Resolves the id from `.anna/executa.json` unless `--tool-id` is given. Flags: `--dir`, `--bin-dir` (default `~/.anna/executa/bin`), `--force`, `--json`.  `local shim`

- **anna-app executa dev** — Run **one** Executa plugin in isolation — REPL (default), or one-shot via `--describe` / `--health` / `--invoke <tool> [--args <json>]`. Performs the full `initialize` + `describe` handshake and proxies every reverse-RPC family the protocol defines (sampling / agent / storage / image / upload); no matrix-nexus, no dashboard, no app bundle required.  `no host required`

### `executa dev` — discovery

- **Auto-detection order** — When `--spec` is omitted, the runner inspects `--dir` (default: CWD) with the **same** parser `anna-app dev` uses for `<manifest-dir>/executas/`: 1. `executa.json` (explicit; `tool_id` + `type` required) → 2. `pyproject.toml` (Python; `uv run --project <dir> <tool_id>`, tool_id = first `[project.scripts]` key) → 3. `package.json` (Node; `node <entry>` where entry = `bin[tool_id]` → first `bin` → `main` → `module` — `npm run start` is **never** auto-run) → 4. `go.mod` **alone errors out** — a Go executa requires an explicit `executa.json` with `tool_id` and `type: "go"` (go.mod has no script-name field) → 5. `bin/<name>` (pre-built binary).

- **`--spec` override** — Force the launcher: `--spec 'tool_id=my-tool,type=node,command="node dist/server.js"'`. Keys: `dir=`, `tool_id=`, `type=python|node|go|binary`, `command=` (shell-split string or JSON array).

### `executa dev` — sampling (`sampling/createMessage`)

- **`--no-sampling` (forced off)** — Hard-disable — plugin sees `sampling_disabled` (`-32008`) on every reverse call. This is **not** the implicit default: with no sampling flag at all, the runner enters **real** mode whenever a saved account (PAT) is on disk (it auto-registers a dev AnnaApp for the slug), and only falls back to disabled when there is no `--mock-sampling`, no `--app-slug`, and no usable account.  `off`

- **`--mock-sampling <fixture.jsonl>` (mock)** — Serve canned `sampling/createMessage` replies from a JSONL fixture. Offline-safe — no network, no nexus.  `mock`

- **`--app-slug <slug>` (real)** — Forward sampling to nexus on behalf of a dev AnnaApp. Requires a prior `anna-app login`. Pair with `--sampling-account <host>` to pick a non-default saved account.  `real`

- **`--sampling-unsupported-format`** — Simulate a model without `json_schema` support — exercises the `responseFormat` `onUnsupported` branches (`-32010` / downgrade) so you can test both paths offline.  `test`

### `executa dev` — agent (`agent/session.*` + `agent/complete`)

- **`--no-agent` (forced off)** — Hard-disable — plugin sees `agent_not_granted` (`-32041`) on every reverse call. This is **not** the implicit default: with no agent flag at all, the runner enters **real** mode whenever a saved account (PAT) is on disk (it auto-registers a dev AnnaApp, same trigger as real sampling), and only falls back to disabled when there is no `--mock-agent`, no `--app-slug`, and no usable account.  `off`

- **`--mock-agent <fixture.jsonl>` (mock)** — Serve canned `agent/*` replies from a JSONL fixture. Offline-safe.  `mock`

- **`--app-slug <slug>` (real)** — Pass `--app-slug` **without** `--no-agent` / `--mock-agent` to enable real agent mode (same trigger as real sampling). The runner mints `kind=agent` / `kind=complete` tokens via `POST /api/v1/anna-apps/dev/session/mint` for that dev AnnaApp, then forwards to `/copilot/app/agent` (SSE) and `/copilot/app/complete`. `--agent-account <host>` picks the saved account (falls back to `--sampling-account`, then current).  `real`

- **Buffered SSE streaming** — Each `agent/*` SSE response is accumulated into the JSON-RPC `result` envelope. Production cap is 4 096 frames — exceeding it raises `-32047 agent_run_too_large`.

### `executa dev` — storage (`storage/*` + `files/*`)

- **`--storage off`** — Every storage and files call returns `storage_not_granted` (`-32021`).  `off`

- **`--storage memory` (default)** — In-process KV with full `if_match` + `ttl_seconds` semantics. `files/*` is unsupported and returns a 'use mock or real' error.  `memory`

- **`--storage mock --mock-storage <fixture.jsonl>`** — Serve canned `storage/*` and `files/*` replies from a JSONL fixture.  `mock`

- **`--storage real`** — Mint a `storage_token` via `POST /api/v1/anna-apps/dev/storage/mint` and forward to `/api/v1/storage/*`. Auto-registers the executa on the first call (override slug with `--app-slug`).  `real`

- **Real-mode auth flags** — `--storage-account <host>` picks a saved account (falls back to `--sampling-account`, then current). `--storage-scopes user,app,tool` (default all three) controls which scopes the minted token is allowed to write.

### `executa dev` — image (`image/generate` + `image/edit`)

- **`--no-image` (off)** — Default. Plugin sees `image_not_granted` (`-32101`) on every reverse call.  `off`

- **`--mock-image <fixture.jsonl>` (mock)** — Serve canned `image/generate` + `image/edit` replies from a JSONL fixture. Offline-safe.  `mock`

- **`--app-slug <slug>` (real)** — Pass `--app-slug` without `--no-image` / `--mock-image` to forward image calls to nexus on behalf of the dev AnnaApp. `--image-account <host>` picks the saved account (falls back to `--sampling-account`, then current).  `real`

### `executa dev` — upload (`host/uploadFile`)

- **`--no-upload` (off)** — Default. Plugin sees `upload_not_granted` (`-32201`) on every reverse call.  `off`

- **`--mock-upload <fixture.jsonl>` (mock)** — Serve canned `host/uploadFile` replies from a JSONL fixture. Offline-safe.  `mock`

- **`--app-slug <slug>` (real)** — Forward `host/uploadFile` to nexus on behalf of the dev AnnaApp. `--upload-account <host>` picks the saved account (falls back to `--sampling-account`, then current).  `real`

### `executa dev` — execution modes

- **Interactive REPL (default)** — Run with no one-shot flag → prompt with `describe` / `health` / `invoke <tool> <json-args?>` / `quit`. Each command prints the raw JSON-RPC `result`. Plugin stderr is interleaved without garbling the prompt.

- **One-shot — `--describe` / `--health`** — Print the MANIFEST or health probe and exit. Suitable for CI smoke tests.

- **One-shot — `--invoke <tool> --args <json>`** — Invoke a single tool, print the result envelope, exit. Add `--json` for compact, banner-free output (machine-readable).

### Auth & accounts

- **anna-app login** — Device-code flow against a nexus host. Saves a PAT to `~/.config/anna/credentials.json`. `--host <url>` is required; `--no-browser` skips the auto-open.

- **anna-app logout** — Remove a saved PAT entry. `--host <url>` for one account; `--all` removes every saved account.

- **anna-app whoami** — Show the current account (and any others). `--json` for machine-readable output.

- **anna-app account set-handle <handle>** — Set or rename your developer `@handle` — the namespace your apps publish under (`@handle/slug`). **Required before creating your first app.** `--host`, `--json`.  `namespace`

### App publish lifecycle

- **anna-app apps push** — Upsert the single mutable **working draft** (manifest + bundle). Safe on every commit — no SemVer, executa deps not frozen, idempotent on content hash. Flags: `--bump patch|minor|major`, `--no-write`, `--dry-run`, `--bundle-dir`, `--no-bundle`, `--executa-id <handle=id>` (repeatable), `--skip-executa-publish`, `--no-bundled-executas`, `--no-install-local`, `--if-match <revision>` (optimistic lock), `--account`, `--json`.  `working draft`

- **anna-app apps cut <version>** — Snapshot the working draft into an **immutable version** (freezes bundled-executa deps). `--changelog <text>`, `--slug`, `--cwd`, `--dry-run`, `--account`, `--json`.  `freeze`

- **anna-app apps release <version>** — Freeze & publish an existing remote version (go live). `--allow-create` runs `apps publish` first if the version isn't on the server yet. `--slug`, `--cwd`, `--dry-run`, `--account`, `--json`.  `go live`

- **anna-app apps publish** — One-shot: mint or update an immutable version directly from `manifest.json` in the cwd (recursively publishes bundled executas). `--bump`, `--no-write`, `--dry-run`, `--executa-id <handle=id>`, `--skip-executa-publish`, `--no-bundled-executas`, `--no-bundle`, `--bundle-dir`, `--account`, `--json`.  `mint version`

- **anna-app apps discard** — Drop the mutable working draft (leaves cut versions intact). `--slug`, `--cwd`, `--dry-run`, `--account`, `--json`.

- **anna-app apps submit-review [slug]** — Move an app into review (`DRAFT`/`REJECTED` → `PENDING_REVIEW`). Slug resolves from `.anna/app.json` when omitted. `--cwd`, `--account`, `--json`.

- **anna-app publish** — Auto-detect the cwd (`manifest.json` → app, `executa.json` → executa) and run the matching publish. `--bump`, `--dry-run`, `--publish` (executa: flip to PUBLIC), `--no-bundle`, `--bundle-dir`, `--account`, `--json`.  `auto-detect`

### App management & inspection

- **anna-app apps list** — List the Anna Apps you authored, with lifecycle status. `--account`, `--json`. (Replaces the old `apps:list`.)

- **anna-app apps status <slug>** — Show server-known state for one Anna App. `--account`, `--json`.

- **anna-app apps versions <slug>** — List all server versions of one Anna App. `--account`, `--json`.

- **anna-app apps grants <slug>** — Show currently granted scopes / quota for one Anna App. `--account`, `--json`.

- **anna-app apps sync-meta** — Push mutable store metadata (name / tagline / …) from the manifest. `--manifest`, `--cwd`, `--dry-run`, `--account`, `--json`.

- **anna-app apps rename-slug <new-slug>** — Rename an app's public slug — only allowed for `DRAFT`/`REJECTED`, never-published, zero-install apps. Updates local `app.json` + `.anna/app.json` on success. `--cwd`, `--manifest`, `--account`, `--json`.

### App destructive ops

- **anna-app apps unpublish <slug>** — Flip a `PUBLISHED` app back to `APPROVED` (private). Guarded by `--yes` + `--confirm <slug>`.  `destructive`

- **anna-app apps archive <slug>** — Archive an Anna App (hides it from end users; existing installs keep working). `--yes` + `--confirm <slug>`.  `destructive`

- **anna-app apps unarchive <slug>** — Restore an archived Anna App back to `APPROVED`. `--yes`.

- **anna-app apps delete <slug>** — Hard-delete an Anna App. Refused by the server if installs exist. `--yes` + `--confirm <slug>`.  `destructive`

### Executa publish lifecycle

- **anna-app executa publish** — Mint or update an Executa from `executa.json` in the cwd. `--bump`, `--no-write`, `--publish` (flip visibility to PUBLIC after freezing the version), `--dry-run`, `--account`, `--json`.  `mint version`

- **anna-app executa list** — List Executas owned by the current PAT. `--account`, `--json`.

- **anna-app executa status <ref>** — Show server-known state for one Executa (by slug or tool_id). `--account`, `--json`.

- **anna-app executa versions <ref>** — List immutable version snapshots for one Executa. `--account`, `--json`.

- **anna-app executa unpublish <slug>** — Flip an Executa's visibility back to private. `--yes` + `--confirm <slug>`.  `destructive`

- **anna-app executa yank <ref>** — Hard-delete one Executa version (`<slug>@<version>`). `--yes` + `--confirm <slug>`.  `destructive`

- **anna-app executa delete <slug>** — Hard-delete an Executa. `--yes` + `--confirm <slug>`.  `destructive`

- **anna-app executa cache-clear** — Delete the local `.anna/executa.json` identity cache — use after the server-side Executa was deleted/recreated or when switching host. Next `executa publish` re-mints via the idempotency key. `--cwd`.

### Token (PAT) management

- **anna-app token list** — List the caller's PATs (most-recent first). `--include-revoked`, `--account`, `--json`.

- **anna-app token revoke <id>** — Revoke one of the caller's PATs by integer id. `--account`, `--json`.

- **anna-app token scopes** — Print the available PAT scope catalogue. `--account`, `--json`.

### Diagnostics

- **anna-app doctor** — Check the environment `anna-app dev` needs — `uv`, matrix-nexus checkout (auto-detected or `--matrix-nexus-root <path>` / `$ANNA_NEXUS_ROOT`), dev key. Exit code is non-zero if any required dep is missing.


---

## Distribution lifecycle

*Lifecycle · status machine*

How Executas and Apps move from draft to published. Source: `src/models/anna_app.py` (`AnnaAppStatus`), `src/models/executa.py` (`ExecutaVisibility`) and `src/services/executa_crud.py`. The `status` values below are the server-side review state machine; the developer-facing working-draft → cut version → release flow (`apps push` / `apps cut` / `apps release`) is documented in the CLI section above.

### Anna App (AnnaAppStatus)

- **draft** — Initial state. Developer can edit freely; not visible to other users.

- **pending_review** — Set by `POST /developer/apps/{id}/submit-review`.

- **approved / rejected** — Admin decision. Approval can publish in the same call (`publish=true`).

- **published** — Visible in the public App Store.

- **archived** — Hidden from discovery; existing installs keep working.

### Executa visibility (ExecutaVisibility)

- **private** — Default. Only the owner can install. The enum is exactly `private | app_bundled | public` (`src/models/executa.py`) — there is no `unlisted` or `paid` visibility value.

- **app_bundled** — Not surfaced in the Explore Hub, but installable by (and bundled with) any published AnnaApp that references it. This is the tier `anna-app executa publish` upgrades to by default; the first `private → app_bundled` transition auto-freezes an immutable `ExecutaVersion` snapshot.  `default publish`

- **public** — Listed in the public Executa Hub for anyone to search / install. Only `anna-app executa publish --publish` (or a `visibility` POST) flips here, and it requires a paid plan (`_require_paid_for_public`).  `paid`

### Verified Developer

- **is_verified_developer** — Required to publish Anna Apps. Granted by platform admin.  `admin-granted`

- **developer_handle** — Globally unique slug (≤80 chars) shown on App listings.

- **developer_profile** — Markdown bio surfaced on App pages.


---
