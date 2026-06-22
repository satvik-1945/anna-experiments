#!/usr/bin/env bash
# Package one Python executa as a darwin-arm64 binary archive for Anna Agent install.
# Usage: ./scripts/package-executa-binary.sh executas/profile
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXEC_DIR="${1:?usage: package-executa-binary.sh <executas/...>}"
ABS_EXEC="$(cd "$ROOT/$EXEC_DIR" && pwd)"
TOOL_ID="$(python3 -c "import json; print(json.load(open('$ABS_EXEC/executa.json'))['tool_id'])")"
SCRIPT_NAME="$(python3 -c "
import re, pathlib
text = pathlib.Path('$ABS_EXEC/pyproject.toml').read_text()
m = re.search(r'\\[project\\.scripts\\]\\s*\\n([^=]+)=', text)
print(m.group(1).strip() if m else '')
")"
if [[ -z "$SCRIPT_NAME" ]]; then
  echo "Could not read [project.scripts] from $ABS_EXEC/pyproject.toml" >&2
  exit 1
fi

PLATFORM="darwin-arm64"
OUT_DIR="$ROOT/dist/executas"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/bin" "$OUT_DIR"
rsync -a \
  --exclude '.anna' \
  --exclude '__pycache__' \
  --exclude '.pytest_cache' \
  --exclude '.venv' \
  --exclude '*.pyc' \
  "$ABS_EXEC/" "$STAGE/src/"

cat > "$STAGE/bin/$TOOL_ID" <<EOF
#!/bin/sh
# ResuMatch executa launcher. Must work when spawned by the Anna desktop
# Agent via ~/.anna/executa/bin/<tool_id> symlink (minimal PATH).
set -eu
# Follow symlinks: bin/<tool_id> -> tools/<tool_id>/current/bin/<tool_id>
script="\$0"
while [ -L "\$script" ]; do
  link="\$(readlink "\$script")"
  case "\$link" in
    /*) script="\$link" ;;
    *) script="\$(CDPATH= cd "\$(dirname "\$script")" && pwd)/\$link" ;;
  esac
done
ROOT="\$(CDPATH= cd "\$(dirname "\$script")/.." && pwd)"
cd "\$ROOT/src"

# Locate uv even with an empty/minimal PATH.
UV=""
if command -v uv >/dev/null 2>&1; then
  UV="\$(command -v uv)"
else
  for cand in "\$HOME/.local/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv "\$HOME/.cargo/bin/uv" /opt/local/bin/uv; do
    if [ -x "\$cand" ]; then UV="\$cand"; break; fi
  done
fi

if [ -n "\$UV" ]; then
  PATH="\$(dirname "\$UV"):\$PATH"; export PATH
  "\$UV" sync --quiet 2>/dev/null || true
  exec "\$UV" run "$SCRIPT_NAME" "\$@"
fi

# Fallback: run the plugin module directly (works for dependency-free executas).
PLUGIN_PY="\$(ls *_plugin.py 2>/dev/null | head -1 || true)"
for PY in python3 /usr/bin/python3 /opt/homebrew/bin/python3; do
  if command -v "\$PY" >/dev/null 2>&1 && [ -n "\$PLUGIN_PY" ]; then
    exec "\$PY" -u "\$PLUGIN_PY" "\$@"
  fi
done

echo "ResuMatch plugin needs uv (https://docs.astral.sh/uv/) or python3 available" >&2
exit 1
EOF
chmod +x "$STAGE/bin/$TOOL_ID"

cat > "$STAGE/manifest.json" <<EOF
{
  "name": "$TOOL_ID",
  "runtime": {
    "binary": {
      "entrypoint": "bin/$TOOL_ID"
    }
  }
}
EOF

ARCHIVE="$OUT_DIR/${TOOL_ID}-${PLATFORM}.tar.gz"
tar -czf "$ARCHIVE" -C "$STAGE" .
echo "Wrote $ARCHIVE ($(du -h "$ARCHIVE" | cut -f1))"
