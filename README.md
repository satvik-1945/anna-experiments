# ResuMatch

Anna hackathon project — scrape fresh jobs for **manual** apply, with profile-driven search, resume tailoring, and a dashboard UI.

## Pipeline

```
Profile (search query + Overleaf resume)
        ↓
Job scraper → jobs_latest.json (free APIs + Indeed/Google; optional boost + LinkedIn)
        ↓
Resume composer (tailor Skills in .tex per job)
        ↓
Application pack → apply_url + tailored .tex + PDF export (manual apply)
```

## Repo layout

```
resumatch/
├── app.json                   # Anna App listing (dashboard)
├── manifest.json              # schema 2 — UI bundle + 4 executas
├── bundle/                    # Dashboard SPA (onboarding + job list)
├── executas/job-scraper/      # Scrape Indeed / free APIs / optional LinkedIn boost
├── executas/profile/          # Save job-search profile (local JSON)
├── executas/resume-composer/  # Tailor LaTeX Skills section per job + PDF export
├── executas/application-pack/ # Job link + resume path for manual apply
├── skills/resumatch-profile/  # Teaches Anna when to set profile
├── scripts/smoke-test.sh
└── tests/
```

## Quick start — job scraper

```bash
deactivate 2>/dev/null || true   # avoid uv venv mismatch warning
cd executas/job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","mode":"free","search_term":"software engineer","location":"India","hours_old":24,"results_wanted":50,"include_free_apis":true}' \
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
  "search_term":"Python developer",
  "resume_latex":"\\documentclass{article}...\\section{Skills}..."
}' --json

# Scrape using saved profile
cd ../job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","use_profile":true,"include_free_apis":true,"results_wanted":500,"hours_old":24}' \
  --json
```

Profile file: `~/.anna/resumatch/profile.json`

## Quick start — full pipeline

```bash
# 1. Save profile — paste Overleaf LaTeX
cd executas/profile
anna-app executa dev --invoke user_profile --args '{
  "action":"save","domain":"software_engineering","seniority":"mid",
  "years_experience":2,"location":"India","search_term":"Python developer",
  "resume_latex":"\\documentclass{article}...\\section{Skills}..."
}' --json

# 2. Scrape (auto-saves ~/.anna/resumatch/jobs_latest.json)
cd ../job-scraper
anna-app executa dev --invoke job_scraper \
  --args '{"action":"scrape","use_profile":true,"include_free_apis":true,"results_wanted":500,"hours_old":24}' --json

# 3. Compose tailored resumes (Skills section only)
cd ../resume-composer && uv sync
anna-app executa dev --invoke resume_composer --args '{"action":"compose_all"}' --json

# 4. Application packs (link + resume + checklist)
cd ../application-pack && uv sync
anna-app executa dev --invoke application_pack --args '{"action":"prepare_all"}' --json
anna-app executa dev --invoke application_pack --args '{"action":"list"}' --json
```

## Dashboard (Anna App UI)

1. **Profile** — name, search query, skills, Overleaf LaTeX
2. **Sync jobs** — free scrape (Remotive, RemoteOK, Arbeitnow + Indeed/Google)
3. **Boost mode** — proxy form for LinkedIn-inclusive scrape
4. **Job listings** — apply link, Resume to PDF, mark applied

```bash
./scripts/dev.sh
# Open http://localhost:5180
```

## Tool APIs

**job_scraper** — `scrape`, `refilter`, `cache_status`, `summary`, `get_job` (single JD by index, for LLM key-skill extraction); `use_profile`, `include_free_apis` (default true), `mode: free|boost`

**user_profile** — `save` with **`resume_latex`**, `get`, `domains`, `scraper_defaults`

**resume_composer** — `compose`, `compose_all`, `compile_pdf` (accepts `key_skills` for LLM-tailored "Key Skills"), `list`

**application_pack** — `prepare_all`, `prepare`, `list`

## Links

- [Anna Developer Hub](https://anna.partners/developers)
