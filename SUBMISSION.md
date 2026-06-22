# ResuMatch — Hackathon Submission

## Short project description (copy-paste for the form)

**What we built**  
ResuMatch is an Anna App that helps you job-hunt efficiently on your own machine. You save your profile and Overleaf resume once, fetch jobs from free APIs and Indeed/Google, get a tailored resume (Skills section only) for every listing, preview PDFs in-app, and track applications from Saved → Applied → Interview → Offer.

**Who it is for**  
Anyone who applies manually and wants speed without losing control — especially software engineers and students who already maintain a LaTeX resume.

**How AI is used**  
ResuMatch calls **Anna's LLM** (`anna.llm.complete`) to read each job description and extract the role's most important "Key Skills," which are written into a tailored copy of your LaTeX resume before you apply. Executas handle scraping, composition, and packing; the SPA orchestrates them via `tools.invoke`. If LLM access isn't granted, it falls back to deterministic skill matching so PDF building never breaks.

**How it connects to Anna**  
- **4 Tool Executas:** profile, job-scraper, resume-composer, application-pack  
- **Schema 2 UI bundle** with iframe sandbox + Host API (`tools`, `storage`, `window`)  
- **Published app:** `@tejasstvk8/resumatch` on [anna.partners](https://anna.partners)  
- **Manual apply by design** — user opens the job URL and clicks Submit; ResuMatch prepares the pack

---

## What to submit

| Item | Location |
|------|----------|
| Anna App (shareable) | `@tejasstvk8/resumatch` on Anna Hub — status: **pending review** |
| Runnable project | This repo — `./scripts/dev.sh` |
| Project description | This file (top section) |
| Demo video | Record using [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) |

---

## Current publish status

| Field | Value |
|-------|--------|
| App slug | `resumatch` |
| App ID | `136` |
| Developer handle | `@tejasstvk8` |
| Latest published version | `0.1.1` (`pending_review`) |
| Next version | `0.1.2` — UI fix + LLM Key Skills (ready to publish) |
| Old drafts removed | `anna-experiments`, `executa-job-scraper` deleted |

**Full step-by-step publishing instructions:** see [DEPLOYMENT.md](./DEPLOYMENT.md).

**To ship `0.1.2`:** `anna-app validate --strict` → `anna-app apps push` → `anna-app apps publish --bump patch` → `anna-app apps submit-review resumatch`. After approval: `anna-app apps release 0.1.2`.

Until approved, use the local harness: `./scripts/dev.sh` → open `http://localhost:5180`.

---

## Deploy / update (developer commands)

**Full guide (two apps explained, file map, delete stray apps, troubleshooting):** [DEPLOYMENT.md](./DEPLOYMENT.md)

Quick sequence to ship **v0.1.2** from repo root (`anna-app login` first):

```bash
# 1. Validate
anna-app validate --strict

# 2. Push working draft (manifest + bundle + executas)
anna-app apps push

# 3. Sync store listing from app.json
anna-app apps sync-meta

# 4. Publish immutable version
anna-app apps publish --bump patch

# 5. Submit for review (first time or after rejection)
anna-app apps submit-review resumatch

# 6. After APPROVED — go live
anna-app apps release 0.1.1
```

Check status anytime:

```bash
anna-app apps status resumatch --json
anna-app apps list --json
```

---

## Install ResuMatch in Anna (after approval)

1. Open [Developer Console](https://anna.partners/developer) or the **Anna App Store**.
2. Find **ResuMatch** (`@tejasstvk8/resumatch`).
3. **Install** — Anna auto-installs the four bundled Executas.
4. In chat, `#resumatch` or ask Anna to open the dashboard (`open_app_view('resumatch', 'main')`).
5. Complete profile → Settings → **Fetch jobs** → use Job Listings.

---

## Local data (for judges / users)

All job data lives under `~/.anna/resumatch/`. Each **Fetch** replaces the job cache and rebuilds listings. Application statuses (Applied, Interview, etc.) are stored in the browser and **persist across fetches** — the dashboard shows your real history.

To reset job data but keep profile: delete `application_packs.json`, `jobs_cache.json`, `jobs_latest.json`, and the `resumes/` + `pdfs/` folders under `~/.anna/resumatch/`.

---

## Architecture (one paragraph)

Profile saves `profile.json` and base LaTeX. Job-scraper fetches broadly (role + date window) into `jobs_cache.json`. Resume-composer tailors Skills per job into `resumes/`. Application-pack builds `application_packs.json` for the UI. The bundle SPA orchestrates fetch → compose → pack in one click and filters listings client-side without re-scraping.
