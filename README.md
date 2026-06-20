# ResuMatch

Anna hackathon project — scrape fresh jobs for **manual** apply, with profile-driven search, matching, resume tailoring, and a dashboard UI.

## Pipeline

```
Profile (domain + seniority + resume)
        ↓
Job scraper → jobs_latest.json
        ↓
Job matcher (≥80% pass)
        ↓
Resume composer (tailor Skills in .tex)
        ↓
Application pack → apply_url + tailored .tex (manual apply)
```

## Repo layout

```
resumatch/
├── app.json                   # Anna App listing (dashboard)
├── manifest.json              # schema 2 — UI bundle + 5 executas
├── bundle/                    # Dashboard SPA (onboarding + job list)
├── executas/job-scraper/      # Scrape Indeed / optional LinkedIn boost
├── executas/profile/          # Save job-search profile (local JSON)
├── executas/job-matcher/      # Score jobs vs profile (80% pass)
├── executas/resume-composer/  # Tailor LaTeX Skills section per job
├── executas/application-pack/ # Job link + resume path for manual apply
├── skills/resumatch-profile/  # Teaches Anna when to set profile
├── scraper-experiments/       # CLI research + catalog
├── scripts/smoke-test.sh
└── tests/
```

## Quick start — job scraper

```bash
deactivate 2>/dev/null || true   # avoid uv venv mismatch warning
cd executas/job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","mode":"free","search_term":"software engineer","location":"India","hours_old":24,"results_wanted":5}' \
  --json
```

## Quick start — profile

```bash
cd executas/profile
uv sync
anna-app executa dev --invoke user_profile --args '{
  "action":"save",
  "domain":"software_engineering",
  "seniority":"mid",
  "years_experience":3,
  "location":"India",
  "resume_text":"Satvik Tejas\nPython, FastAPI, Docker, 3 years software engineering."
}' --json

# Scrape using saved profile
cd ../job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","use_profile":true,"results_wanted":5,"hours_old":24}' \
  --json
```

Profile file: `~/.anna/resumatch/profile.json`

## Quick start — full pipeline

```bash
# 1. Save profile — paste Overleaf LaTeX
cd executas/profile
anna-app executa dev --invoke user_profile --args '{
  "action":"save","domain":"software_engineering","seniority":"mid",
  "years_experience":2,"location":"India",
  "resume_latex":"\\documentclass{article}...\\section{Skills}..."
}' --json

# Or save from file: tests/fixtures/resume_base.tex

# 2. Scrape (auto-saves ~/.anna/resumatch/jobs_latest.json)
cd ../job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","use_profile":true,"results_wanted":20,"hours_old":24}' --json

# 3. Match (≥80% pass)
cd ../job-matcher && uv sync
anna-app executa dev --invoke job_matcher \
  --args '{"action":"score","threshold":80}' --json
anna-app executa dev --invoke job_matcher --args '{"action":"passed"}' --json

# 4. Compose tailored resumes (Skills section only)
cd ../resume-composer && uv sync
anna-app executa dev --invoke resume_composer --args '{"action":"compose_all"}' --json
# Output: ~/.anna/resumatch/resumes/resume_*.tex → upload to Overleaf

# 5. Application packs (no email — just link + resume + checklist)
cd ../application-pack && uv sync
anna-app executa dev --invoke application_pack --args '{"action":"prepare_all"}' --json
anna-app executa dev --invoke application_pack --args '{"action":"list"}' --json
```

## Dashboard (Anna App UI)

The repo includes a **schema-2 Anna App** with a bundled dashboard:

1. **Onboarding** — name + Overleaf LaTeX paste → saves profile
2. **Empty dashboard** until you click **Refresh jobs**
3. **Refresh** runs scrape → match (≥80%) → compose → pack
4. **Mark applied** — tracked in the browser (manual apply workflow)

```bash
cd /path/to/anna-experiments
anna-app validate --strict
anna-app dev
# Open http://localhost:5180
```

Publish to Anna:

```bash
anna-app apps push
anna-app apps cut 0.1.0
anna-app apps release 0.1.0
```

Then `#resumatch` in Anna chat to open the dashboard window.

## Storage (APS)

**Anna Persistent Storage (APS) is not integrated** in the Executas yet. The profile manifest declares `host_capabilities: ["storage.tool"]` as forward-looking, but all pipeline data still lives in local files under `~/.anna/resumatch/`. The dashboard “Mark applied” state uses browser `localStorage` for now.

## Publish all Executas to Anna Agent

```bash
cd executas/job-matcher   # repeat for profile, job-scraper
anna-app executa publish && anna-app executa install --force
# Restart Anna.app → Rediscover Local
```

Profile file: `~/.anna/resumatch/profile.json` (single-user, no auth).

## Anna vs Rasa (mental model)

| Rasa | Anna |
|------|------|
| Hard-coded intents + stories | LLM picks tools from natural language |
| Python actions | Executa plugins (JSON-RPC over stdin) |
| No built-in LLM | Cloud LLM + local agent execution |
| You wire every path | Tool router + optional Skills |

## Tool APIs

**job_scraper** — `scrape`, `summary`, `use_profile`, `persist`

**user_profile** — `save` with **`resume_latex`**, `get`, `domains`, `scraper_defaults`

**job_matcher** — `score`, `passed`, `summary`

**resume_composer** — `compose`, `compose_all`, `list`

**application_pack** — `prepare_all`, `prepare`, `list` (no email draft)

## Links

- [Anna Developer Hub](https://anna.partners/developers)
- [Forum: First Anna App guide](https://forum.anna.partners/t/from-zero-to-your-first-anna-app-a-hands-on-beginners-guide/117)
