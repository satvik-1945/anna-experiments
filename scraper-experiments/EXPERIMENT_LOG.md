# Scraper Experiment Log

Record results here as we test each tool from [SCRAPER_CATALOG.md](./SCRAPER_CATALOG.md).

---

## Template

```markdown
### [Tool Name] — YYYY-MM-DD

| Field | Value |
|-------|-------|
| Query | e.g. "software engineer", US, last 24h |
| Result count | |
| Unique in 24h | |
| Has apply URL | % |
| Has email/DM contact | % |
| Blocked / rate-limited | Y/N |
| Runtime | s |
| **Verdict** | PASS / FAIL / PARTIAL |
| Notes | |
```

---

## Experiments

### JobSpy (free mode + free APIs) — 2026-06-18

| Field | Value |
|-------|-------|
| Query | `software engineer`, location=`India`, `hours_old=24`, `results_wanted=120` |
| Result count | 120 |
| Unique in 24h | 120 |
| Has apply URL | 100% |
| Has email/DM contact | 0% (not extracted in this pass) |
| Blocked / rate-limited | No |
| Runtime | ~26.5s |
| **Verdict** | PASS (for initial baseline) |
| Notes | Output file: `scraper-experiments/output/jobs_latest.json`; source split in this run was mostly `indeed`, so next run should broaden keyword/location and test `boost` mode with proxies for LinkedIn coverage. |
