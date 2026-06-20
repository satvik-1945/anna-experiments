---
name: resumatch-profile
description: Manage the user's job-search profile (domain, seniority, experience, resume) before scraping or matching jobs.
---

# ResuMatch Profile

Use when the user wants to set up or view their job-search profile.

## Required user inputs (ask once)

1. **Resume** — paste text or provide a local `.txt` path
2. **Domain** — e.g. `software_engineering`, `accounting`, `banking`, `teaching`
3. **Seniority** — intern, junior, mid, senior, lead, manager, director
4. **Years of experience** — integer
5. **Location** — e.g. India, Remote, Berlin

Call `user_profile` with `action: save` and all fields. Skills/name/email are extracted from the resume.

## Other actions

- `action: get` — read saved profile
- `action: domains` — list valid domain keys
- `action: scraper_defaults` — show what job_scraper will use

## Then scrape

After profile is saved, call `job_scraper` with `action: scrape` and `use_profile: true` (or omit search_term/location to auto-load profile).

No login needed — profile is stored locally on the user's machine at `~/.anna/resumatch/profile.json`.
