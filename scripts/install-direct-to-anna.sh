#!/usr/bin/env bash
# Install the calculator plugin into ~/.anna/executa.
# This is the correct local-dev install path for Anna.app.
#
# Usage:
#   ./scripts/install-direct-to-anna.sh                  # reads tool_id from anna.local.json
#   ./scripts/install-direct-to-anna.sh tool-YOUR-ID     # pass tool_id directly
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CALC="$ROOT/executas/calc/calc_plugin.py"
ANNA_HOME="${ANNA_EXECUTA_HOME:-$HOME/.anna/executa}"
CONFIG="$ROOT/anna.local.json"

TOOL_ID="${1:-}"
if [[ -z "$TOOL_ID" && -f "$CONFIG" ]]; then
  TOOL_ID="$(python3 -c "import json; print(json.load(open('$CONFIG'))['tool_id'])" 2>/dev/null || true)"
fi

if [[ -z "$TOOL_ID" ]]; then
  echo "ERROR: tool_id required."
  echo ""
  echo "  1. Mint at anna.partners/executa → copy your Tool ID"
  echo "  2. Save it:"
  echo "     echo '{\"tool_id\": \"tool-yourhandle-calci-abc123\"}' > anna.local.json"
  echo "  3. Re-run:"
  echo "     ./scripts/install-direct-to-anna.sh"
  exit 1
fi

VERSION="dev"
TOOL_HOME="$ANNA_HOME/tools/$TOOL_ID"
VERSION_DIR="$TOOL_HOME/$VERSION"
BIN_SHIM="$ANNA_HOME/bin/calc-plugin"

mkdir -p "$VERSION_DIR/bin" "$ANNA_HOME/bin"

cp "$CALC" "$VERSION_DIR/calc_plugin.py"

python3 - <<PY > "$VERSION_DIR/manifest.json"
import json
print(json.dumps({
    "name": "calc",
    "display_name": "Calculator",
    "version": "1.0.0",
    "description": "Evaluate arithmetic expressions and track calculation history.",
    "tools": [{
        "name": "calc",
        "description": "Evaluate math expressions or return recent calculation history.",
        "parameters": [
            {"name": "action", "type": "string", "required": True},
            {"name": "expression", "type": "string", "required": False},
            {"name": "limit", "type": "integer", "required": False},
        ],
    }],
}, indent=2))
PY

cat > "$VERSION_DIR/bin/calc-plugin" <<'WRAP'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$0")"
DIR="$(cd "$(dirname "$SCRIPT")/.." && pwd)"
exec python3 "$DIR/calc_plugin.py"
WRAP
chmod +x "$VERSION_DIR/bin/calc-plugin"

ln -sfn "$VERSION" "$TOOL_HOME/current"
ln -sfn "$VERSION_DIR/bin/calc-plugin" "$BIN_SHIM"

python3 - <<PY > "$VERSION_DIR/INSTALL.json"
import json, time
print(json.dumps({
    "tool_id": "$TOOL_ID",
    "version": "$VERSION",
    "distribution_type": "local",
    "executable_name": "calc-plugin",
    "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
}, indent=2))
PY

echo "Installed calc plugin for Anna"
echo "  tool_id:    $TOOL_ID"
echo "  tool home:  $VERSION_DIR"
echo "  bin shim:   $BIN_SHIM"
echo ""
echo "Verify:"
echo "  echo '{\"jsonrpc\":\"2.0\",\"method\":\"describe\",\"id\":1}' | $BIN_SHIM"
echo ""
echo "NEXT: Quit Anna.app completely (Cmd+Q) and reopen it."
echo "      Then check Agents → Executa should show 1/1 running."
