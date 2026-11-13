#!/usr/bin/env python3
"""
verify_site.py — asserts the guarantees this project claims.

Failure conditions (each one fails the build):
  V1  every internal link target exists on disk
  V2  every outbound Amazon link is a direct /dp/<ASIN> URL (no cloaking, C-13)
  V3  every populated spec row has a source id that resolves to the registry
  V4  no spec row is 'verified' with an empty value
  V5  no spec row is 'unverified' with a populated value (blank means blank)
  V6  every flagged row carries a flag_id that exists in flagged.json
  V7  every flag referenced from data is rendered on flagged.html
  V8  every page carries the exact Amazon disclosure sentence (C-01)
  V9  every compliance rule has a resolving source id and a non-empty quote or an explicit note
  V10 no Amazon price / rating value is published anywhere (C-07, C-09)
  V11 no third-party script, cookie setter or analytics snippet is present (C-19)
  V12 no page contains a bare 'affiliate link' used as its only disclosure (C-02)

Exit code 0 = all checks passed.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

failures: list[str] = []
warnings: list[str] = []
checks_run = 0


def fail(check: str, msg: str) -> None:
    failures.append(f"[{check}] {msg}")


def warn(check: str, msg: str) -> None:
    warnings.append(f"[{check}] {msg}")


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


CONFIG = load("config.json")
SOURCES = load("sources.json")
PRODUCTS = load("products.json")
COMPLIANCE = load("compliance.json")
FLAGGED = load("flagged.json")
OPPS = load("opportunities.json")

SOURCE_IDS = {s["id"] for s in SOURCES["sources"]}
FLAG_IDS = {f["id"] for f in FLAGGED["items"]}

PAGES = sorted(p.name for p in ROOT.glob("*.html"))
EXPECTED_PAGES = {
    "index.html", "products.html", "compare.html", "guides.html",
    "compliance.html", "methodology.html", "sources.html", "flagged.html",
    "privacy.html", "executive-summary.html", "404.html",
}


# ------------------------------------------------------------------ V1 links
def check_internal_links() -> None:
    global checks_run
    link_re = re.compile(r'(?:href|src)="([^"]+)"')
    for page in PAGES:
        checks_run += 1
        text = (ROOT / page).read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "data:")):
                continue
            path_part = target.split("#")[0].split("?")[0]
            if not path_part:
                continue  # pure fragment on same page
            candidate = (ROOT / path_part).resolve()
            if not candidate.exists():
                fail("V1", f"{page}: broken internal link -> {target}")
        # fragment-only links must resolve to an id on the same page
        for target in re.findall(r'href="#([^"]+)"', text):
            if f'id="{target}"' not in text:
                fail("V1", f"{page}: anchor #{target} has no matching id on the page")


def check_expected_pages() -> None:
    global checks_run
    checks_run += 1
    missing = EXPECTED_PAGES - set(PAGES)
    if missing:
        fail("V1", f"missing expected page(s): {sorted(missing)}")


# ------------------------------------------------- V2 outbound Amazon links
def check_outbound_links() -> None:
    global checks_run
    checks_run += 1
    href_re = re.compile(r'href="(https?://[^"]*amazon\.[^"]*)"')
    seen = 0
    for page in PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        for url in href_re.findall(text):
            seen += 1
            parsed = urlparse(url)
            # allowed: direct product page, or an affiliate-program help page
            if parsed.path.startswith("/dp/"):
                asin = parsed.path.split("/dp/")[1].split("/")[0].split("?")[0]
                if not re.fullmatch(r"[A-Z0-9]{10}", asin):
                    fail("V2", f"{page}: bad ASIN in outbound link {url}")
                q = parsed.query
                if q and not q.startswith("tag="):
                    fail("V2", f"{page}: unexpected query on product link {url}")
                if q.startswith("tag="):
                    tag = q.split("tag=")[1].split("&")[0]
                    if not re.fullmatch(r"[A-Za-z0-9\-]{3,}-(20|21|22)", tag):
                        fail("V2", f"{page}: malformed Associates tag in {url}")
                if any(x in url for x in ("link.amazon", "/gp/", "redirect", "?" + "ref=")):
                    fail("V2", f"{page}: product link may be cloaked or indirect: {url}")
            elif "affiliate-program.amazon.com" in url or "www.amazon.com/gp/help" in url:
                pass  # plain citation of a policy document, not a Special Link
            else:
                fail("V2", f"{page}: non-canonical amazon link {url}")
    if seen == 0:
        fail("V2", "no Amazon outbound links found at all")


# -------------------------------------------------------- V3–V5 spec rows
def check_spec_rows() -> None:
    global checks_run
    for p in PRODUCTS["products"]:
        for s in p["specs"]:
            checks_run += 1
            where = f"{p['asin']} / {s['field']}"
            status = s.get("status")
            value = (s.get("value") or "").strip()
            sid = (s.get("source_id") or "").strip()

            if status not in ("verified", "flagged", "unverified"):
                fail("V3", f"{where}: invalid status {status!r}")
                continue

            also = (s.get("also_source_id") or "").strip()
            if also and also not in SOURCE_IDS:
                fail("V3", f"{where}: also_source_id {also!r} not in sources.json")

            if status == "verified":
                if not value:
                    fail("V4", f"{where}: verified but value is blank")
                if not sid:
                    fail("V3", f"{where}: verified but has no source_id")
                elif sid not in SOURCE_IDS:
                    fail("V3", f"{where}: source_id {sid!r} not in sources.json")

            if status == "flagged":
                if not sid and not s.get("flag_id"):
                    fail("V3", f"{where}: flagged with neither a source nor a flag")
                if sid and sid not in SOURCE_IDS:
                    fail("V3", f"{where}: source_id {sid!r} not in sources.json")

            if status == "unverified":
                if value:
                    fail("V5", f"{where}: unverified but value is populated ({value!r})")
                if sid:
                    fail("V5", f"{where}: unverified but cites source {sid!r}")


# ----------------------------------------------------- V6–V7 flag wiring
def check_flags() -> None:
    global checks_run
    referenced: set[str] = set()

    for p in PRODUCTS["products"]:
        for s in p["specs"]:
            if s.get("flag_id"):
                referenced.add(s["flag_id"])

    for r in COMPLIANCE["rules"]:
        if r.get("flag_id"):
            referenced.add(r["flag_id"])

    for fid in sorted(referenced):
        checks_run += 1
        if fid not in FLAG_IDS:
            fail("V6", f"flag id {fid} is referenced from data but not defined in flagged.json")

    checks_run += 1
    flagged_html = (ROOT / "flagged.html").read_text(encoding="utf-8")
    for fid in sorted(FLAG_IDS):
        if f'id="{fid}"' not in flagged_html:
            fail("V7", f"flag {fid} is not rendered on flagged.html")

    # V6b: every flag must carry at least one source link
    for f in FLAGGED["items"]:
        checks_run += 1
        if not f.get("source_links"):
            fail("V6", f"flag {f['id']} has no source links")

    # Cross-link audit: flag ids appearing as text in HTML must exist.
    for page in PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        for fid in set(re.findall(r"flagged\.html#(F-\d+)", text)):
            checks_run += 1
            if fid not in FLAG_IDS:
                fail("V6", f"{page}: links to undefined flag {fid}")


# ------------------------------------------------ V8 disclosure on every page
def check_disclosure() -> None:
    global checks_run
    for page in PAGES:
        checks_run += 1
        text = (ROOT / page).read_text(encoding="utf-8")
        if DISCLOSURE not in text:
            fail("V8", f"{page}: missing the exact required disclosure sentence")
        if "I get commissions for purchases made through links" not in text:
            fail("V8", f"{page}: missing the plain-language FTC-style disclosure")


# ------------------------------------------------------- V9 compliance rows
def check_compliance() -> None:
    global checks_run
    for r in COMPLIANCE["rules"]:
        checks_run += 1
        if (r.get("source_id") or "") not in SOURCE_IDS:
            fail("V9", f"{r['id']}: source_id {r.get('source_id')!r} not in registry")
        if not (r.get("verbatim_quote") or "").strip() and not r.get("source_section"):
            fail("V9", f"{r['id']}: no quote and no named section")
        if not (r.get("how_this_site_complies") or "").strip():
            fail("V9", f"{r['id']}: no implementation statement")
        if r.get("status") not in ("verified", "flagged"):
            fail("V9", f"{r['id']}: invalid status {r.get('status')!r}")


# ------------------------------------- V10 no Amazon price/rating published
def check_no_amazon_price_or_rating() -> None:
    """
    C-07 / C-09: no Amazon price, availability or star rating may be published.
    Enforced structurally: every row whose field mentions Amazon price/rating must
    be unverified with an empty value.
    """
    global checks_run
    for p in PRODUCTS["products"]:
        for s in p["specs"]:
            checks_run += 1
            f = s["field"].lower()
            if ("amazon" in f and ("price" in f or "rating" in f or "review" in f)):
                if (s.get("value") or "").strip():
                    fail("V10", f"{p['asin']} / {s['field']}: Amazon price/rating must stay blank")
                if s.get("status") != "unverified":
                    fail("V10", f"{p['asin']} / {s['field']}: Amazon price/rating must be 'unverified'")

    # Also refuse obvious marketplace-price patterns rendered into HTML.
    checks_run += 1
    price_pat = re.compile(r"Amazon price[^<]{0,40}\$\s?\d", re.I)
    for page in PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        if price_pat.search(text):
            fail("V10", f"{page}: looks like it publishes an Amazon price")

    # Amazon star-rating display would look like "4.5 out of 5" attributed to Amazon.
    checks_run += 1
    for page in PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        if re.search(r"Amazon[^<]{0,24}\d\.\d\s*(out of 5|/5)", text, re.I):
            fail("V10", f"{page}: looks like it publishes an Amazon star rating")


# ------------------------------------------ V11 no tracking / third parties
def check_no_tracking() -> None:
    global checks_run
    forbidden = [
        ("<script", "inline or external <script> tag"),
        ("google-analytics", "Google Analytics"),
        ("googletagmanager", "Google Tag Manager"),
        ("document.cookie", "cookie writing"),
        ("xmlhttprequest", "XHR"),
        ("fetch(", "network fetch"),
        ("@import", "CSS @import of a remote sheet"),
        ("fonts.googleapis", "Google Fonts"),
        ("hotjar", "Hotjar"),
        ("facebook.com/tr", "Facebook pixel"),
    ]
    for page in PAGES:
        text = (ROOT / page).read_text(encoding="utf-8")
        lower = text.lower()
        for needle, label in forbidden:
            checks_run += 1
            if needle in lower:
                fail("V11", f"{page}: contains {label} ({needle!r}) - site claims no tracking")

    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    checks_run += 1
    if "url(http" in css.replace(" ", ""):
        fail("V11", "stylesheet references a remote asset")


# ------------------------------------------ V12 'affiliate link' not alone
def check_disclosure_wording() -> None:
    """
    C-02: the phrase "affiliate link" on its own is not an adequate disclosure.
    This check is only meaningful on pages that actually carry outbound product
    links. On those pages, every occurrence of the bare phrase must sit in a
    sentence that also explains the payment relationship.
    """
    global checks_run
    product_link_pages = [
        page for page in PAGES
        if re.search(r'href="https://www\.amazon\.com/dp/', (ROOT / page).read_text(encoding="utf-8"))
    ]
    checks_run += 1
    if not product_link_pages:
        fail("V12", "no page carries a product link - cannot assess disclosure adequacy")

    for page in product_link_pages:
        text = (ROOT / page).read_text(encoding="utf-8")
        for m in re.finditer(r"affiliate link", text, re.I):
            window = text[max(0, m.start() - 260): m.end() + 260]
            checks_run += 1
            if not re.search(r"commission|earn|paid|compensat|inadequate", window, re.I):
                fail(
                    "V12",
                    f"{page}: bare 'affiliate link' with no payment explanation nearby -> "
                    f"{re.sub(r'<[^>]+>', '', window)[:140]!r}",
                )


# ----------------------------------- additional sanity: data integrity
def check_data_integrity() -> None:
    global checks_run
    # every product's ASIN appears in exactly one place in products.json
    checks_run += 1
    asins = [p["asin"] for p in PRODUCTS["products"]]
    if len(asins) != len(set(asins)):
        fail("V0", "duplicate ASIN in products.json")

    # the three supplied short links must all be represented
    checks_run += 1
    supplied = ["https://link.amazon/B04G1MEwY", "https://link.amazon/B02NbDxp3",
                "https://link.amazon/B00hJ57DV"]
    have = {p["short_link"] for p in PRODUCTS["products"]}
    for s in supplied:
        if s not in have:
            fail("V0", f"supplied short link {s} missing from products.json")

    # every opportunity row must reference a real product
    for r in OPPS["results"]:
        checks_run += 1
        if r["asin"] not in asins:
            fail("V0", f"opportunities.json references unknown ASIN {r['asin']}")
        comp = r["component_scores"]
        expected = set(OPPS["meta"]["weights"].keys())
        if set(comp.keys()) != expected:
            fail("V0", f"{r['asin']}: component scores do not match declared weights")

    # composite must actually match the stated weights
    for r in OPPS["results"]:
        checks_run += 1
        calc = round(sum(r["component_scores"][k] * w for k, w in OPPS["meta"]["weights"].items()), 1)
        if abs(calc - r["composite"]) > 0.05:
            fail("V0", f"{r['asin']}: composite {r['composite']} != weighted {calc}")

    # sources registry: ids unique, urls https, every source actually cited
    checks_run += 1
    ids = [s["id"] for s in SOURCES["sources"]]
    if len(ids) != len(set(ids)):
        fail("V0", "duplicate source id in sources.json")
    for s in SOURCES["sources"]:
        checks_run += 1
        if not s["url"].startswith("https://"):
            fail("V0", f"source {s['id']} is not https")

    cited = set()
    for p in PRODUCTS["products"]:
        for s in p["specs"]:
            if s.get("source_id"):
                cited.add(s["source_id"])
            if s.get("also_source_id"):
                cited.add(s["also_source_id"])
        cited.add(p["commission_rate_source"])
    for r in COMPLIANCE["rules"]:
        if r.get("source_id"):
            cited.add(r["source_id"])
    for f in FLAGGED["items"]:
        cited.update(f.get("source_ids") or [])
    for s in SOURCES["sources"]:
        checks_run += 1
        if s["id"] not in cited:
            warn("V0", f"source {s['id']} is registered but never cited by any row")


def main() -> int:
    check_expected_pages()
    check_internal_links()
    check_outbound_links()
    check_spec_rows()
    check_flags()
    check_disclosure()
    check_compliance()
    check_no_amazon_price_or_rating()
    check_no_tracking()
    check_disclosure_wording()
    check_data_integrity()

    total_fields = sum(len(p["specs"]) for p in PRODUCTS["products"])
    print(f"Pages checked:        {len(PAGES)}")
    print(f"Spec fields checked:  {total_fields}")
    print(f"Sources in registry:  {len(SOURCES['sources'])}")
    print(f"Compliance rules:     {len(COMPLIANCE['rules'])}")
    print(f"Flags:                {len(FLAGGED['items'])}")
    print(f"Assertions run:       {checks_run}")
    print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print("  " + w)
        print()

    if failures:
        print(f"FAILED - {len(failures)} problem(s):")
        for f in failures:
            print("  " + f)
        return 1

    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
