# Job Scraper Executa

Anna Tool plugin for ResuMatch. Speaks JSON-RPC 2.0 over stdin/stdout.

## Run locally

```bash
cd executas/job-scraper
pip install -e .

# Describe manifest
echo '{"jsonrpc":"2.0","method":"describe","id":1}' | python job_scraper_plugin.py

# Scrape (real network)
echo '{"jsonrpc":"2.0","method":"invoke","id":2,"params":{"tool":"job_scraper","arguments":{"action":"scrape","mode":"free","search_term":"software engineer","location":"India","hours_old":24,"results_wanted":10}}}' | python job_scraper_plugin.py

# Last scrape summary (same plugin process session)
echo '{"jsonrpc":"2.0","method":"invoke","id":3,"params":{"tool":"job_scraper","arguments":{"action":"summary"}}}' | python job_scraper_plugin.py
```

From repo root, run `./scripts/smoke-test.sh` for a mocked protocol check (no network).

## Parameters (`action: scrape`)

| Parameter | Default | Notes |
|-----------|---------|-------|
| `mode` | `free` | `boost` adds LinkedIn |
| `search_term` | software engineer | |
| `location` | India | |
| `hours_old` | 24 | |
| `results_wanted` | 200 | |
| `country_indeed` | India | |
| `include_free_apis` | false | Remotive, RemoteOK, Arbeitnow |
| `proxies` | — | Optional list; overrides credential |
| `output_path` | — | Write full untruncated JSON to disk |
| `description_max_chars` | 400 | Truncate in LLM response |

## Credential

`SCRAPER_PROXY_LIST` — comma-separated proxies for boost mode, e.g. `user:pass@host:port,host:port`

## Anna install

1. Mint tool at https://anna.partners/executa
2. Point entry point to `job_scraper_plugin.py` (or `uv run` from this directory)
3. Set timeout ≥ 120s for scrape calls
