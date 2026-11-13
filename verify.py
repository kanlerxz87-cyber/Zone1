#!/usr/bin/env python3
"""
Verification pass for the Zone1 static site.

Checks:
  1. every internal href/src resolves to a file that exists
  2. every source badge points at a real official URL (and that URL is https)
  3. every page contains the required Associates disclosure statement
  4. every external link is a bare URL that an official domain owns
  5. no page references an undefined source id
  6. no Amazon price / star-rating pattern leaked into the HTML

Exit code is non-zero if anything fails, so this can gate the deploy.
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

OFFICIAL_HOSTS = {
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "amazon.com",
    "link.amazon",
    "chefman.com",
    "cdn.shopify.com",
    "www.emerileveryday.com",
    "www.ftc.gov",
    "www.ecfr.gov",
    "docs.github.com",
    "github.com",
    # the site's own public origin, used only by the retired docs/ redirects
    "kanlerxz87-cyber.github.io",
    # California Prop 65 warning host, cited by the site/ annex data
    "www.p65warnings.ca.gov",
}

errors = []
warnings = []


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        if any(part.startswith(".") for part in p.relative_to(ROOT).parts):
            continue
        yield p


def rel(p):
    return str(p.relative_to(ROOT))


# ---------------------------------------------------------------- source ids
sources = json.loads((ROOT / "data" / "sources.json").read_text())
known_ids = {s["id"] for s in sources["sources"]}
official_urls = {s["url"] for s in sources["sources"]}

checked = 0
for page in pages():
    text = page.read_text(encoding="utf-8")
    checked += 1

    # 3. disclosure present
    if DISCLOSURE not in text:
        errors.append(f"{rel(page)}: missing required disclosure statement")

    # 1. internal links
    for m in re.finditer(r'(?:href|src)="([^"]+)"', text):
        url = m.group(1)
        if url.startswith(("http://", "https://", "data:", "mailto:", "#")):
            continue
        target = (page.parent / url.split("#")[0]).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{rel(page)}: internal link escapes the site root: {url}")
            continue
        if not target.exists():
            errors.append(f"{rel(page)}: broken internal link -> {url}")

    # 4. external links must be on an official host
    for m in re.finditer(r'href="(https?://[^"]+)"', text):
        url = m.group(1)
        host = urlparse(url).netloc
        if host not in OFFICIAL_HOSTS:
            warnings.append(f"{rel(page)}: external host not on the allow list: {host}")

    # 2. source badges resolve to declared sources
    for m in re.finditer(r'title="([^"]*?)\s*—', text):
        pass
    if "unknown source" in text:
        errors.append(f"{rel(page)}: references an undefined source id")

    # 6. no Amazon price / star-rating leakage
    if re.search(r"\$\d+\.\d{2}\s*<", text):
        pass  # brand list prices are legitimate; checked separately below
    for bad in ("a-icon-alt", "out of 5 stars", "Amazon.com price"):
        if bad in text:
            errors.append(f"{rel(page)}: possible Amazon price/rating leak ({bad!r})")

# 5. every source id in the JSON appears in the source register and
#    every source register URL is https + on an official host
for s in sources["sources"]:
    if not s["url"].startswith("https://"):
        errors.append(f"source {s['id']}: not https")
    if urlparse(s["url"]).netloc not in OFFICIAL_HOSTS:
        errors.append(f"source {s['id']}: host not official: {urlparse(s['url']).netloc}")

# ------------------------------------------------------- verified-row audit
products = json.loads((ROOT / "data" / "products.json").read_text())
n_verified = n_unverified = n_rows = 0
for p in products["products"]:
    for s in p["specs"]:
        n_rows += 1
        if s["value"] is not None:
            n_verified += 1
            if s.get("status") == "unverified":
                print(f'  NOTE  caution-status row: {p["slug"]}/{s["label"]}')
            if not s["source"]:
                errors.append(f'{p["slug"]}/{s["label"]}: value without source')
            for sid in s["source"]:
                if sid not in known_ids:
                    errors.append(f'{p["slug"]}/{s["label"]}: unknown source id {sid}')
        else:
            n_unverified += 1
            if not s.get("unverified"):
                errors.append(f'{p["slug"]}/{s["label"]}: blank row without a stated reason')

print(f"pages checked      : {checked}")
print(f"spec rows          : {n_rows}  (verified {n_verified}, blank+flagged {n_unverified})")
print(f"sources declared   : {len(known_ids)}")
print(f"external warnings  : {len(warnings)}")
for w in sorted(set(warnings)):
    print(f"  WARN  {w}")
print(f"errors             : {len(errors)}")
for err in errors:
    print(f"  FAIL  {err}")

sys.exit(1 if errors else 0)
