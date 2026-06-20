---
name: resumatch-pipeline
description: End-to-end ResuMatch flow — profile, scrape, match jobs for manual apply.
---

# ResuMatch Pipeline

Run in order when user asks to find matching jobs:

1. **user_profile** `action: save` — ask for **Overleaf LaTeX paste** (`resume_latex`), not plain text. Also: domain, seniority, years, location.
2. **job_scraper** `action: scrape`, `use_profile: true`, `persist: true`
3. **job_matcher** `action: score`, `threshold: 80`
4. **resume_composer** `action: compose_all`
5. **application_pack** `action: prepare_all` → job link + tailored .tex path
6. User opens apply_url, compiles .tex in Overleaf, applies manually

No email draft. Free-tier scrape only (Indeed etc.) — apply_url from job boards.
