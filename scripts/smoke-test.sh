#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/executas/job-scraper/job_scraper_plugin.py"

if [[ -x "$ROOT/.venv314/bin/python" ]]; then
  PYTHON="$ROOT/.venv314/bin/python"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

send() {
  printf '%s\n' "$1" | "$PYTHON" "$PLUGIN"
}

echo "== describe =="
send '{"jsonrpc":"2.0","method":"describe","id":1}' | "$PYTHON" -c "
import json, sys
data = json.load(sys.stdin)
assert data['result']['name'] == 'job-scraper'
assert any(t['name'] == 'job_scraper' for t in data['result']['tools'])
print('ok')
"

echo "== health =="
send '{"jsonrpc":"2.0","method":"health","id":2}' | "$PYTHON" -c "
import json, sys
data = json.load(sys.stdin)
assert data['result']['status'] == 'ready'
print('ok')
"

echo "== summary (empty) =="
send '{"jsonrpc":"2.0","method":"invoke","id":3,"params":{"tool":"job_scraper","arguments":{"action":"summary"}}}' | "$PYTHON" -c "
import json, sys
data = json.load(sys.stdin)
assert data['result']['success'] is True
assert data['result']['data']['count'] == 0
print('ok')
"

echo "== scrape (mocked) =="
RESUMATCH_SMOKE_MOCK=1 send '{"jsonrpc":"2.0","method":"invoke","id":4,"params":{"tool":"job_scraper","arguments":{"action":"scrape","mode":"free","results_wanted":2,"hours_old":24}}}' | "$PYTHON" -c "
import json, sys
data = json.load(sys.stdin)
assert 'result' in data, data
assert data['result']['success'] is True
assert data['result']['data']['count'] == 1
print('ok')
"

echo "All smoke tests passed."
