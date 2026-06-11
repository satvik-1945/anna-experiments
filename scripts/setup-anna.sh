#!/usr/bin/env bash
# Verify calculator plugin — local tests + Anna install status.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Anna Calculator — status check"
echo "=============================="
echo ""

echo "1. Protocol smoke test"
"$ROOT/scripts/smoke-test.sh"
echo ""

echo "2. Anna install (~/.anna/executa/)"
if [[ -x "$HOME/.anna/executa/bin/calc-plugin" ]]; then
  echo "   ✓ ~/.anna/executa/bin/calc-plugin exists"
  if echo '{"jsonrpc":"2.0","method":"describe","id":1}' | "$HOME/.anna/executa/bin/calc-plugin" | grep -q '"name": "calc"'; then
    echo "   ✓ describe handshake OK"
  else
    echo "   ✗ describe failed — re-run: ./scripts/install-direct-to-anna.sh"
  fi
else
  echo "   ✗ not installed — run:"
  echo "     cp anna.local.json.example anna.local.json"
  echo "     ./scripts/install-direct-to-anna.sh"
fi
echo ""

echo "3. Next: quit Anna.app (Cmd+Q), reopen, test in chat"
echo "   Docs: docs/ANNA_TOOLS.md"
