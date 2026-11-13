#!/usr/bin/env python3
"""Verification gate for the Zone1 site.

Fails (exit 1) if any of the following is true:
  1. A data field marked verified=true has no source URL.
  2. A data field has a source id that does not exist in data/sources.json.
  3. An irregularity references a source URL that is not in the source register.
  4. A compliance row marked verified=true has no source_url and no quote.
  5. Any internal link or asset reference in docs/ resolves to a missing file.
  6. Any page that contains an outbound Amazon affiliate link is missing the
     required Amazon disclosure sentence (operating agreement §5).
  7. Any page is missing the required trademark attribution statement.
  8. A product table row renders without a source link and is not explicitly
     marked unverified.

This script checks structure and traceability. It does not re-fetch the web —
source URLs are recorded in data/sources.json with an access date.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
TRADEMARK = "Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates."

errors = []
warnings = []
checks = 0


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    global checks
    sources_doc = load("sources.json")
    products_doc = load("products.json")
    compliance_doc = load("compliance.json")
    irr_doc = load("irregularities.json")
    analysis_doc = load("analysis.json")

    source_ids = {s["id"] for s in sources_doc["sources"]}
    source_urls = {s["url"] for s in sources_doc["sources"]}

    # ---- 1/2. field traceability -----------------------------------------
    verified_fields = 0
    unverified_fields = 0
    for p in products_doc["products"]:
        for key, val in p.items():
            if not isinstance(val, dict) or "verified" not in val:
                continue
            checks += 1
            if val.get("verified"):
                verified_fields += 1
                if not val.get("source"):
                    err(f"{p['id']}.{key}: verified but no source id")
                elif val["source"] not in source_ids:
                    err(f"{p['id']}.{key}: unknown source id {val['source']}")
            else:
                unverified_fields += 1
                if val.get("value") not in (None, ""):
                    err(f"{p['id']}.{key}: unverified but carries value {val.get('value')!r} "
                        f"(unverified values must be blank)")

    # ---- 3. irregularity sources are registered --------------------------
    for it in irr_doc["items"]:
        checks += 1
        if not it.get("source_urls"):
            err(f"{it['id']}: no source_urls")
        for url in it.get("source_urls", []):
            if url not in source_urls:
                err(f"{it['id']}: source url not in register: {url}")
        if it.get("severity") not in {"high", "medium", "low"}:
            err(f"{it['id']}: invalid severity {it.get('severity')!r}")

    # ---- 4. compliance rows ---------------------------------------------
    for r in compliance_doc["rows"]:
        checks += 1
        if not r.get("source_url") or r["source_url"] not in source_urls:
            err(f"{r['id']}: compliance source_url missing from register")
        if r.get("verified") and not r.get("quote"):
            err(f"{r['id']}: marked verified but has no verbatim quote")
        if not r.get("verified") and r.get("quote"):
            warn(f"{r['id']}: unverified but has a quote — check this row")

    # ---- analysis honesty checks ----------------------------------------
    for s in analysis_doc["scoring_model"]["products"]:
        checks += 1
        if s["price_point_clarity"]["score"] != 0:
            err(f"scoring {s['id']}: price clarity must be 0 while no price is verifiable")

    # ---- 5. internal links and assets ------------------------------------
    pages = []
    for dirpath, _dirs, files in os.walk(DOCS):
        for f in files:
            if f.endswith(".html"):
                pages.append(os.path.join(dirpath, f))

    if not pages:
        err("no HTML pages found in docs/")

    link_re = re.compile(r'(?:href|src)="([^"]+)"')
    for path in pages:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        rel = os.path.relpath(path, DOCS)
        for target in link_re.findall(text):
            checks += 1
            if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            clean = target.split("#")[0].split("?")[0]
            if not clean:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), clean))
            if not os.path.exists(resolved):
                err(f"{rel}: broken internal link -> {target}")

    # ---- 6/7. disclosure + trademark on pages with affiliate links -------
    affiliate_link_re = re.compile(r'href="https://link\.amazon/')
    for path in pages:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        rel = os.path.relpath(path, DOCS)
        checks += 1
        if DISCLOSURE not in text:
            err(f"{rel}: missing required Amazon disclosure sentence")
        checks += 1
        if TRADEMARK not in text:
            err(f"{rel}: missing required trademark attribution statement")
        if affiliate_link_re.search(text):
            checks += 1
            # every affiliate CTA (class="btn") must be marked sponsored; plain
            # reference citations in the flag register do not need it.
            for cta in re.findall(r'<a class="btn[^"]*" href="https://link\.amazon/[^"]*"[^>]*>', text):
                if 'rel="sponsored' not in cta:
                    err(f"{rel}: affiliate CTA without rel=\"sponsored\": {cta[:80]}")
            if text.count(DISCLOSURE) < 2:
                warn(f"{rel}: affiliate links present but disclosure appears only once")

    # ---- 8. rendered product rows carry sources or unverified ------------
    prod_html = os.path.join(DOCS, "products.html")
    if os.path.exists(prod_html):
        with open(prod_html, encoding="utf-8") as fh:
            html_text = fh.read()
        rows = re.findall(r"<tr><th>(.*?)</th>(<td>.*?</td>)</tr>", html_text, re.S)
        checks += 1
        if len(rows) < 60:
            err(f"products.html: expected >=60 sourced rows, found {len(rows)}")
        for label, cell in rows:
            checks += 1
            has_source = 'class="srclink"' in cell
            marked_unverified = 'class="unv"' in cell
            if not (has_source or marked_unverified):
                err(f"products.html row {label!r}: neither a source link nor an unverified marker")

    # ---- 9. published counts must equal rendered rows ---------------------
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from importlib import import_module
    build_mod = import_module("build")
    product_fields = build_mod.PRODUCT_FIELDS
    expected_total = len(products_doc["products"]) * len(product_fields)
    if os.path.exists(prod_html):
        with open(prod_html, encoding="utf-8") as fh:
            t = fh.read()
        m = re.search(r"(\d+) fields across 3 products", t)
        checks += 1
        if not m or int(m.group(1)) != expected_total:
            err(f"products.html headline says {m.group(1) if m else '?'} fields, "
                f"expected {expected_total}")
        m2 = re.search(r"(\d+) verified &middot; (\d+) blank", t)
        checks += 1
        if m2:
            v, b = int(m2.group(1)), int(m2.group(2))
            if v + b != expected_total:
                err(f"products.html verified+blank ({v}+{b}) != {expected_total}")
        else:
            err("products.html: could not read the verified/blank counters")

    # ---- summary ---------------------------------------------------------
    print(f"checks run: {checks}")
    print(f"verified product fields: {verified_fields}")
    print(f"blank/flagged product fields: {unverified_fields}")
    print(f"pages: {len(pages)}")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print("  WARN " + w)
    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for e in errors:
            print("  FAIL " + e)
        return 1
    print("\nOK — no broken links, no unsourced rows, disclosures present on every page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
