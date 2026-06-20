# Scraper Experiments Runner

Local CLI and research for Step 1. The **Anna Executa plugin** lives in `executas/job-scraper/`.

## Script

- `scripts/smoke_jobspy.py`
  - `free` mode: JobSpy without LinkedIn + optional free APIs
  - `boost` mode: JobSpy with LinkedIn (proxies recommended)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U python-jobspy requests
```

## Run (free mode, safer)

```bash
python scraper-experiments/scripts/smoke_jobspy.py \
  --mode free \
  --search-term "software engineer" \
  --location "India" \
  --hours-old 24 \
  --results-wanted 200 \
  --include-free-apis
```

## Run (boost mode, LinkedIn + proxy)

```bash
python scraper-experiments/scripts/smoke_jobspy.py \
  --mode boost \
  --search-term "software engineer" \
  --location "India" \
  --hours-old 24 \
  --results-wanted 200 \
  --proxy "user:pass@host:port" \
  --proxy "user:pass@host2:port2" \
  --include-free-apis
```

## Output

- Default output: `scraper-experiments/output/jobs_latest.json`
- The script prints source-wise counts to terminal for quick validation.

## Notes

- In `boost` mode without proxies, LinkedIn usually rate-limits quickly.
- Keep hackathon default to `free` mode and add LinkedIn only when needed.
