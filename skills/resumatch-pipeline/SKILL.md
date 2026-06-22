---
name: resumatch-pipeline
description: End-to-end ResuMatch flow — profile, scrape, tailor resumes for manual apply.
---

# ResuMatch Pipeline

Run in order when user asks to find jobs:

1. **user_profile** `action: save` — Overleaf LaTeX (`resume_latex`), search_term, skills, location
2. **job_scraper** `action: scrape`, `use_profile: true`, `include_free_apis: true`, `persist: true`
3. **resume_composer** `action: compose_all`
4. **application_pack** `action: prepare_all` → job link + tailored .tex path
5. User opens apply_url, downloads PDF or compiles .tex, applies manually

Optional: **job_scraper** `mode: boost` with `proxies` for LinkedIn.

No email draft. Manual apply only.
