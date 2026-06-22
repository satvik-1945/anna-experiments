#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for d in executas/profile executas/job-scraper executas/resume-composer executas/application-pack; do
  ./scripts/package-executa-binary.sh "$d"
done
echo "Done. Archives are in dist/executas/"
