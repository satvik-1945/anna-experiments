# ResuMatch — Deployment & Publishing Guide

Complete reference for shipping **ResuMatch** (`@tejasstvk8/resumatch`) to Anna Hub.
Use this when cutting **v0.1.2** (or any later patch) from this repo.

---

## 1. Which app is which? (read this first)

Your **git repo folder** is named `anna-experiments`, but the **real Anna App** is **ResuMatch**.

| What you see | Slug | App ID | Meaning |
|--------------|------|--------|---------|
| **ResuMatch** | `resumatch` | **136** | The app you publish, submit, and install. **This is the only one you care about.** |
| ~~anna-experiments~~ | ~~anna-experiments~~ | ~~141~~ | **Deleted.** Accidental draft created when `anna-app dev` used the **folder name** as slug because `manifest.json` has no top-level `slug`. Never published a version. |

### Why two apps appeared

1. You ran `anna-app apps push` / `publish` from this repo → correctly bound to **`.anna/app.json`** → **resumatch** (136).
2. You ran `./scripts/dev.sh` (`anna-app dev`) → the CLI registered a **separate dev app** using the directory name **`anna-experiments`** → stored in **`.anna/dev-app.json`** → showed up in Developer Console as a second draft app.

**Fix applied in this repo:** `scripts/dev.sh` now passes `--slug resumatch --llm-app-slug resumatch` so local dev always ties to ResuMatch, not the folder name.

**Cleanup already done:** `anna-experiments` (id 141) was hard-deleted from Anna Hub; local `.anna/dev-app.json` was removed.

Verify only one app remains:

```bash
anna-app apps list --json
# Expected: single entry — slug "resumatch", id 136
```

---

## 2. Config files — what each one does

All paths relative to repo root `/Users/satviktejas/f/anna-experiments`.

| File | Purpose | Edit by hand? |
|------|---------|---------------|
| **[`.anna/app.json`](.anna/app.json)** | **Published app identity** — `app_id`, `slug`, `handle`, host. `anna-app apps push/publish` uses this. | **No** — CLI writes on first publish |
| **[`app.json`](app.json)** | **Store listing metadata** — name, tagline, description, category. Synced with `apps sync-meta`. | Yes (marketing copy) |
| **[`manifest.json`](manifest.json)** | **Runtime manifest** — executas, UI bundle, permissions, `host_api`, views. | Yes (features) |
| **[`bundle/tools.js`](bundle/tools.js)** | Maps logical tool names → published `tool_id`s. | **No** — rewritten by `apps push` |
| ~~`.anna/dev-app.json`~~ | Old dev-harness side registration. **Removed.** Should not come back if you use `./scripts/dev.sh`. | N/A |
| **`~/.anna/resumatch/`** | **End-user runtime data** on disk (profile, jobs, resumes). Not part of publish. | Users manage locally |

### Important distinction

- **`anna-app apps push`** → updates the **working draft** for **resumatch** (uses `.anna/app.json`).
- **`anna-app dev`** → local harness only; does **not** replace a publish. With the fixed `dev.sh`, it should **not** create a second hub app.

---

## 3. Current server state (ResuMatch)

Check anytime:

```bash
anna-app apps status resumatch --json
anna-app apps versions resumatch --json
```

As of your last successful `cut`:

| Field | Value |
|-------|-------|
| Slug | `resumatch` |
| App ID | `136` |
| **Live version** (users / Console badge) | **0.1.3** (`is_latest: true`) |
| App status | `published` (already went through review once) |

### First publish vs update (important)

| Situation | Flow |
|-----------|------|
| **First time** (app was `draft` / never live) | `push` → `cut` → **`submit-review`** → admin approves → `release` |
| **Update** (app already `published`, like ResuMatch now) | `push` → `cut X.Y.Z` → **`release X.Y.Z`** — **skip `submit-review`** |

`submit-review` only works when status is `DRAFT` or `REJECTED`. Yours is already **published**, so you got:

`App 状态不允许提交审核: published` — **expected; not a failure of your cut.**

Lifecycle for **updates**:

```
push (draft) → cut 0.1.2 (snapshot on server) → release 0.1.2 (go live, Console shows v0.1.2)
```

---

## 4. Ship v0.1.2 — exact command sequence

Run from **repo root**. Requires `anna-app login` first.

### Semver explained simply (why `publish --bump patch` failed)

Think of versions as **edition numbers** on a book:

| Edition | Where |
|---------|--------|
| **0.1.1** | Already printed and on the shelf (Anna Hub — **live today**) |
| **0.1.0** | What your laptop *thought* was the current edition (no `"version"` in `manifest.json` → CLI default) |

`publish --bump patch` means: *“take local edition number, add one patch, print that.”*

- Local `0.1.0` + patch → tries to print **0.1.1**
- **0.1.1 already exists** → error `版本号已存在: 0.1.1`

`cut 0.1.2` means: *“print edition **0.1.2** directly”* — no guessing from local file. That is why it worked.

**Option B** (`publish --bump patch`) only works if local manifest says `"version": "0.1.1"` (same as live), then bump → **0.1.2**. You do **not** need Option B if `cut 0.1.2` already succeeded.

### Three layers (working draft vs cut vs live)

| Layer | What it is | Console shows |
|-------|------------|---------------|
| **Working draft** | Mutable code from `apps push` | Orange **WORKING** badge |
| **Cut version** | Frozen snapshot (`apps cut X.Y.Z`) | Listed under Versions, not live until released |
| **Live / released** | What users install (`apps release` or Console **Publish**) | Badge shows that version (currently **v0.1.2**) |

Check all versions:

```bash
anna-app apps versions resumatch --json
# Live row has is_latest: true
```

---

### Update flow (ResuMatch — already published)

```bash
cd /Users/satviktejas/f/anna-experiments

anna-app validate --strict
anna-app apps push
anna-app apps sync-meta
anna-app apps cut 0.1.3          # next patch (example)

# SKIP submit-review — not allowed for published apps

anna-app apps release 0.1.3      # make that version live
```

If `release` fails with `app status is published; release not permitted — app must be APPROVED or PUBLISHED to release`, that is a **CLI bug** (v0.1.30): the API returns lowercase `published`/`approved` but the CLI checks uppercase. Workarounds:

1. **Developer Console** (easiest): [Developer Console](https://anna.partners/developer) → **ResuMatch** → **Versions** → **Publish** on the cut version.
2. **Direct API** (same as `release`): `POST /api/v1/developer/apps/136/versions/<version_id>/publish` with your PAT from `anna-app login`.

---

### First-time publish flow (for reference only)

```bash
anna-app apps push
anna-app apps cut 0.1.0
anna-app apps submit-review resumatch   # only when status is draft/rejected
# wait for admin approval
anna-app apps release 0.1.0
```

---

### Why `publish --bump patch` failed (detail)

| Location | Version |
|----------|---------|
| Anna Hub (already live) | **0.1.1** |
| Your local `manifest.json` | missing → CLI defaults to **0.1.0** |
| What `--bump patch` tried to mint | **0.1.1** again → **400 rejected** |

You need **0.1.2**, not another 0.1.1 — use `cut 0.1.2` (already done) or Option B below only if starting fresh.

### Option B — one-shot publish (alternative to cut)

Only if you have **not** cut yet and local `manifest.json` matches the live version:

```bash
anna-app apps versions resumatch --json   # → live 0.1.1
# Add to manifest.json:  "version": "0.1.1"
anna-app apps publish --bump patch        # → mints 0.1.2
anna-app apps release 0.1.2
```

If local is `0.1.0` (or no `version` field), **do not** use `publish --bump patch`.

### What each step does (detail)

| Step | Command | Effect |
|------|---------|--------|
| `push` | Upload mutable draft | Safe every commit; orange WORKING in Console |
| `cut 0.1.2` | Freeze snapshot | Creates immutable **0.1.2** on server (not live yet) |
| `submit-review` | First publish only | **Skip** if app already `published` |
| `release 0.1.2` | Go live | Sets **0.1.2** as `is_latest`; Console shows v0.1.2 |

### Dry-run (optional)

```bash
anna-app apps push --dry-run
anna-app apps publish --bump patch --dry-run
```

---

## 5. v0.1.2 changelog (for review / release notes)

- Full-width UI + collapsible sidebar; larger default window
- Fetch jobs panel redesign
- LLM **Key Skills** from job descriptions (`anna.llm.complete`); capped to one line in PDF
- Starter resume template + profile guard before PDF preview
- First-run guided tour
- New scraper action: `get_job` (single JD for LLM)
- New manifest permission: `llm.complete`

---

## 6. Local development (no publish)

```bash
./scripts/dev.sh
# → http://localhost:5180/
# Uses slug resumatch (not anna-experiments)
```

Useful flags (append to `./scripts/dev.sh`):

```bash
./scripts/dev.sh --port 5181          # if 5180 busy
./scripts/dev.sh --no-llm               # offline UI testing
./scripts/dev.sh --mock-llm fixture.jsonl
```

**Port already in use:**

```bash
lsof -nP -iTCP:5180 -sTCP:LISTEN
kill <PID>
./scripts/dev.sh
```

---

## 7. Remove a stray / junk Anna App

If a second app appears again (draft, zero installs, no versions):

```bash
anna-app apps list --json
anna-app apps status <bad-slug> --json   # confirm version_count: 0

anna-app apps delete <bad-slug> --yes --confirm <bad-slug>
```

Remove local sidecar if present:

```bash
rm -f .anna/dev-app.json
```

**Refused if installs exist:** archive instead:

```bash
anna-app apps archive <slug> --yes --confirm <slug>
```

Other destructive ops (rare):

```bash
anna-app apps unpublish resumatch --yes --confirm resumatch   # published → approved (private)
anna-app apps unarchive resumatch                             # restore archived app
```

---

## 8. Rollback to an older version

Versions are immutable. To revert live users to **0.1.1**:

```bash
anna-app apps release 0.1.1
```

---

## 9. Executas (four tools)

Published via `apps push` / `apps publish` — not separately for this app flow.

| Logical name | Role |
|--------------|------|
| `resumatch-profile` | Profile + base LaTeX |
| `job-scraper` | Scrape + cache + `get_job` |
| `resume-composer` | Tailor Skills + PDF |
| `application-pack` | Job listings for UI |

Inspect:

```bash
anna-app executa list --json
```

Local data paths (user machine): `~/.anna/resumatch/` — see Settings → Local data in the app.

---

## 10. Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Two apps in Developer Console | `anna-app dev` without `--slug resumatch` | Use `./scripts/dev.sh`; delete stray app (§7) |
| `validate --strict` fails on `llm.complete` | Bundle uses LLM but manifest missing ACL | Ensure `manifest.json` has `"llm": ["complete"]` and permission `llm.complete` |
| `push` targets wrong app | Wrong cwd or missing `.anna/app.json` | Run from repo root; `cat .anna/app.json` → slug `resumatch`, id `136` |
| Dev shows `app_slug=anna-experiments` | Old dev.sh / stale dev-app.json | Pull latest `scripts/dev.sh`; delete `.anna/dev-app.json` |
| `submit-review` rejected | Prior version still pending | Check `apps status`; wait or fix review_message |
| `publish --bump patch` → `版本号已存在: 0.1.1` | Local manifest is `0.1.0` (or missing); server already has `0.1.1` | Use `apps push` then `apps cut 0.1.2` (§4 Option A), or set `"version": "0.1.1"` in manifest then `publish --bump patch` |
| `release` → `must be APPROVED or PUBLISHED` while status is already `published` | CLI case-sensitivity bug in `anna-app` v0.1.30 | Publish via Developer Console **Versions → Publish**, or POST `.../versions/<id>/publish` (§4) |
| **`Plugin not found: tool-tejasstvk8-…`** after installing from the App Store | Executas had no `distribution` block — Anna Agent could not install the backend plugins (`anna-app dev` worked because it runs local subprocesses) | **v0.1.3+** ships binary distribution. On your Mac: **Agents → Install Essentials**, then reinstall `@tejasstvk8/resumatch`. Ensure `dist/executas/*.tar.gz` is pushed to GitHub `main` (see §12). Dev shortcut: `anna-app executa install --dir executas/profile --force` (repeat for each executa) → Agent **Rediscover Local**. |

---

## 12. Executa binaries (required for store install)

Store-installed ResuMatch invokes four Python plugins via your Anna Agent. Each `executa.json` must declare `distribution` (we use `binary` archives). Build and host them:

```bash
./scripts/package-all-executas.sh          # writes dist/executas/*-darwin-arm64.tar.gz
# Commit + push dist/executas/ to GitHub main (raw URLs in executa.json depend on this)
cd executas/profile && anna-app executa publish   # repeat per executa after source changes
anna-app apps push && anna-app apps cut X.Y.Z && anna-app apps release X.Y.Z
```

Currently packaged for **darwin-arm64** (Apple Silicon Mac). Add more `binary_urls` keys (`darwin-x86_64`, `linux-x86_64`, …) before shipping to other platforms.


## 11. Quick reference

```bash
anna-app login
anna-app apps list --json
anna-app apps status resumatch --json
anna-app validate --strict
anna-app apps push
anna-app apps sync-meta
anna-app apps cut 0.1.3
anna-app apps release 0.1.3   # or Console Publish if CLI fails
```

**Hub:** [anna.partners/developer](https://anna.partners/developer)  
**Install (after release):** App Store → `@tejasstvk8/resumatch`  
**Hackathon copy:** [SUBMISSION.md](./SUBMISSION.md)
