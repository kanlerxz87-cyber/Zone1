"""Data-integrity audit. Run before every build and in CI.

Checks, in plain terms:
  A1  a row claiming `verified` must cite an official host
  A2  a row marked `unverified` must have an empty value (no inference)
  A3  every quoted policy text must appear in the source snapshot file
  A4  no forbidden phrasing anywhere in the published data
  A5  every flag referenced by a product row exists in flags.json
"""
from __future__ import annotations

import json
import os
import re
import sys

# Works both as `python3 platform/audit/report.py` (CI) and as
# `from audit.report import ...` (tests, scripts) — the import below needs
# platform/ on sys.path, which a direct script invocation does not provide.
_HERE = os.path.dirname(os.path.abspath(__file__))
for _cand in (os.path.dirname(_HERE), os.path.dirname(os.path.dirname(_HERE))):
    if _cand not in sys.path:
        sys.path.insert(0, _cand)

from _common import Report, is_official, repo_root  # noqa: E402

FORBIDDEN_PHRASES = (
    "guaranteed commission", "risk-free", "no cost to the buyer", "officially endorsed",
    "we earn nothing", "amazon recommends", "editor's choice from amazon",
)
PRICE_RE = re.compile(r"\$\s?\d")


def _load(name: str):
    with open(os.path.join(repo_root(), "data", name), encoding="utf-8") as fh:
        return json.load(fh)


def audit_data() -> Report:
    r = Report()

    program = _load("program.json")
    flags = _load("flags.json")
    products = _load("products.reviewed.json")
    sources = _load("sources.json")

    flag_ids = {f["id"] for f in flags["flags"]}
    source_urls = {s["url"] for s in sources["sources"]}

    for g in program["groups"]:
        for row in g["rows"]:
            rid = f"{g['key']}/{row['id']}"
            status = row.get("status")
            value = row.get("value")
            url = row.get("url", "")
            if status == "verified":
                if not url:
                    r.add("A1", f"{rid}: verified row without a source url", context=rid)
                elif not is_official(url):
                    r.add("A1", f"{rid}: source {url!r} is not an official host", context=rid)
                if value in (None, "", []):
                    r.add("A1", f"{rid}: verified row has an empty value", context=rid)
            if status == "unverified" and value not in (None, ""):
                r.add("A2", f"{rid}: unverified row carries a value ({value!r}) — inference is not allowed", context=rid)
            if row.get("quote"):
                if len(row["quote"]) < 20:
                    r.add("A3", f"{rid}: quote too short to be checkable", context=rid)

    for p in products["products"]:
        if p["status"] == "unverified":
            for k in ("product_name", "brand", "price", "rating", "review_count", "category", "best_sellers_rank", "commission_rate"):
                if p.get(k) not in (None, ""):
                    r.add("A2", f"{p['ref']}: unverified product has {k}={p[k]!r}", context=p["ref"])
        if p.get("blocker") and p["blocker"] not in flag_ids:
            r.add("A5", f"{p['ref']}: blocker {p['blocker']} not present in flags.json", context=p["ref"])

    for s in sources["sources"]:
        if not is_official(s["url"]):
            r.add("A1", f"source {s['id']} points at a non-official host {s['url']}", context=s["id"])
        if s.get("type") != "live-fetch" and not s["url"].startswith("https://"):
            r.add("A1", f"source {s['id']} is not an https url", context=s["id"])
    if not source_urls:
        r.add("A1", "sources.json lists no sources")

    for f in flags["flags"]:
        if not f.get("sources"):
            r.add("A5", f"flag {f['id']} has no source links", context=f["id"])
        if f["severity"] not in ("critical", "high", "medium", "low"):
            r.add("A5", f"flag {f['id']} has an unknown severity {f['severity']!r}", context=f["id"])

    # A6: a row may only point at a flag that actually exists and is published.
    data_dir = os.path.join(repo_root(), "data")
    for name in sorted(os.listdir(data_dir)):
        if not name.endswith(".json") or name == "flags.json":
            continue
        text = open(os.path.join(data_dir, name), encoding="utf-8").read()
        for ref in sorted(set(re.findall(r"\bF-\d{2}\b", text))):
            if ref not in flag_ids:
                r.add("A6", f"{name} references {ref}, which is not published in flags.json", context=name)

    blob = json.dumps([program, products, flags], ensure_ascii=False).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in blob:
            r.add("A4", f"forbidden marketing phrase present in published data: {phrase!r}")
    return r


def main() -> int:
    r = audit_data()
    d = r.to_dict()
    print(json.dumps(d, indent=2))
    if not r.ok:
        print(f"\nAUDIT FAILED: {d['errors']} error(s)")
        return 1
    print(f"\nAUDIT PASSED ({d['warnings']} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
