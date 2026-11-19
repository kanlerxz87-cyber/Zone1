#!/usr/bin/env bash
# Canonical + independent-build regression gates. No remote/account data is fabricated.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "· canonical output must be current BEFORE regeneration"
python3 scripts/check_canonical.py
echo "· canonical Python tests (disabled/enabled fixtures; no production counts)"
python3 -m unittest discover -s tests -v
echo "· generated browser-client contract tests"
node --test tests/test_analytics_client.cjs
echo "· canonical/all-tree link and source structure"
python3 verify.py
echo "· engine tests"
python3 -m unittest discover -s platform/tests -t platform -p 'test_*.py'
echo "· data audit"
python3 -c "
import sys; sys.path.insert(0,'platform')
from audit.report import audit_data
r=audit_data()
print(r.to_dict()['findings'] or 'clean')
sys.exit(0 if r.ok else 1)"
echo "· independent annex output is current"
# Check-only: writing first and comparing the write to itself cannot detect stale output.
python3 scripts/build_s2_site.py --check
echo "· inherited link gate"
python3 scripts/check_links.py
echo "· public artifact, including deployment-only archives"
stage_root="$(mktemp -d)"
trap 'rm -rf "$stage_root"' EXIT
python3 scripts/stage_pages.py --output "$stage_root/public"
python3 scripts/verify_staged.py "$stage_root/public"
echo "OK — structural/code checks, not legal, account, traffic or sales certification"
