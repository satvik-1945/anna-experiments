#!/usr/bin/env bash
# Run Anna App harness without the repo .venv314 confusing uv in each executa.
set -euo pipefail
cd "$(dirname "$0")/.."
deactivate 2>/dev/null || true
unset VIRTUAL_ENV
# Always bind dev to the published ResuMatch app — never register a stray
# "anna-experiments" app from the repo folder name.
exec anna-app dev --slug resumatch --llm-app-slug resumatch "$@"
