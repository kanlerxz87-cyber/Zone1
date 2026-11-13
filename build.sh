#!/usr/bin/env bash
# Build + verify the site. Exits non-zero on any broken link or unsourced row.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/build.py
python3 scripts/check.py
echo "Build OK — repo root is ready to publish via GitHub Pages."
