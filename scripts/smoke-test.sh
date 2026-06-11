#!/usr/bin/env bash
# Smoke tests for the calc Executa plugin.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/executas/calc/calc_plugin.py"
PYTHON="${PYTHON:-python3}"

echo "== describe =="
OUT=$(echo '{"jsonrpc":"2.0","method":"describe","id":1}' | "$PYTHON" "$PLUGIN")
echo "$OUT" | grep -q '"name": "calc"' || { echo "FAIL: describe"; exit 1; }
echo "OK"

echo "== evaluate 2+2 =="
OUT=$(echo '{"jsonrpc":"2.0","method":"invoke","id":2,"params":{"tool":"calc","arguments":{"action":"evaluate","expression":"2+2"}}}' | "$PYTHON" "$PLUGIN")
echo "$OUT" | grep -q '"result": 4' || { echo "FAIL: evaluate"; echo "$OUT"; exit 1; }
echo "OK"

echo "== evaluate with precedence =="
OUT=$(echo '{"jsonrpc":"2.0","method":"invoke","id":3,"params":{"tool":"calc","arguments":{"action":"evaluate","expression":"2+3*4"}}}' | "$PYTHON" "$PLUGIN")
echo "$OUT" | grep -q '"result": 14' || { echo "FAIL: precedence"; echo "$OUT"; exit 1; }
echo "OK"

echo "== health =="
OUT=$(echo '{"jsonrpc":"2.0","method":"health","id":4}' | "$PYTHON" "$PLUGIN")
echo "$OUT" | grep -q '"status": "ready"' || { echo "FAIL: health"; exit 1; }
echo "OK"

echo "== long-running loop (must not exit while stdin is open) =="
FIFO=$(mktemp -u "${TMPDIR:-/tmp}/calc-smoke.XXXXXX")
mkfifo "$FIFO"
"$PYTHON" "$PLUGIN" < "$FIFO" &
PID=$!
exec 3>"$FIFO"
echo '{"jsonrpc":"2.0","id":1,"method":"describe"}' >&3
sleep 2
if kill -0 "$PID" 2>/dev/null; then
  echo "OK (process still alive with open stdin)"
  exec 3>&-
  kill "$PID" 2>/dev/null || true
  wait "$PID" 2>/dev/null || true
else
  echo "BUG: process exited while stdin was still open"
  exec 3>&- 2>/dev/null || true
  rm -f "$FIFO"
  exit 1
fi
rm -f "$FIFO"

echo ""
echo "All smoke tests passed."
