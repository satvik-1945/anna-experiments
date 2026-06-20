#!/usr/bin/env bash
# Run Anna App harness without the repo .venv314 confusing uv in each executa.
set -euo pipefail
cd "$(dirname "$0")/.."
deactivate 2>/dev/null || true
unset VIRTUAL_ENV
exec anna-app dev "$@"
