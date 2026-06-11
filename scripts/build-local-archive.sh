#!/usr/bin/env bash
# Build a local .tar.gz Anna can install with distribution_type: local
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CALC="$ROOT/executas/calc"
DIST="$ROOT/dist"
STAGING="$DIST/staging-calc"
ARCHIVE="$DIST/calc-executa-dev.tar.gz"

rm -rf "$STAGING"
mkdir -p "$STAGING/bin" "$DIST"

cp "$CALC/calc_plugin.py" "$STAGING/"
python3 - <<'PY' > "$STAGING/manifest.json"
import json
manifest = {
    "name": "calc",
    "display_name": "Calculator",
    "version": "1.0.0",
    "description": "Evaluate arithmetic expressions and track calculation history.",
    "runtime": {"binary": {"entrypoint": "bin/calc-plugin"}},
    "tools": [{
        "name": "calc",
        "description": "Evaluate math expressions or return recent calculation history.",
        "parameters": [
            {"name": "action", "type": "string", "description": "evaluate or history", "required": True},
            {"name": "expression", "type": "string", "description": "Arithmetic expression", "required": False},
            {"name": "limit", "type": "integer", "description": "History limit", "required": False},
        ],
    }],
}
print(json.dumps(manifest, indent=2))
PY

cat > "$STAGING/bin/calc-plugin" <<'WRAP'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$0")"
DIR="$(cd "$(dirname "$SCRIPT")/.." && pwd)"
exec python3 "$DIR/calc_plugin.py"
WRAP
chmod +x "$STAGING/bin/calc-plugin"

tar -czf "$ARCHIVE" -C "$STAGING" .
rm -rf "$STAGING"

echo "Built: $ARCHIVE"
echo "Use this path in Anna Hub → Distribution Type: local → Local Archive Path"
