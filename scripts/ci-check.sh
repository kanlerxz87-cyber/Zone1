#!/usr/bin/env bash
# Gate for every commit: engine tests, data audit, site build, stale-build check, link check.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "· unit tests"
python3 -m unittest discover -s platform/tests -t platform -p 'test_*.py' 2>&1 | tail -3
echo "· data audit"
python3 -c "
import sys; sys.path.insert(0,'platform')
from audit.report import audit_data
r=audit_data()
print(r.to_dict()['findings'] or 'clean')
sys.exit(0 if r.ok else 1)"
echo "· build + compliance gate"
python3 scripts/build_s2_site.py >/dev/null
python3 scripts/build_s2_site.py --check
echo "· link check"
python3 scripts/check_links.py
echo "OK"
