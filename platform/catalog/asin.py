"""Identifier validation -- the gate that everything else depends on.

Implements CT-1..CT-5 in data/program.json.
"""
from __future__ import annotations

import re

from _common import Fact, Status

ASIN_RE = re.compile(r"^[A-Z0-9]{10}$")
ISBN10_RE = re.compile(r"^(?=[0-9X]{10}$)[0-9]{9}[0-9X]$")
# /dp/<id>, /product/<id>, /gp/product/<id> -- the ASIN follows /dp/ per CT-5.
DP_RE = re.compile(r"(?:/dp/|/product/|/gp/product/)([A-Za-z0-9]{6,20})")
# Amazon's own link-shortener style: https://link.amazon/<token> or /s/<token>.
BARE_TOKEN_RE = re.compile(r"^/(?:[A-Za-z0-9_-]{1,3}/)?([A-Za-z0-9]{6,20})/?$")
BARE_TOKEN_HOSTS = ("link.amazon", "amzn.to", "amzn.com", "amzn.asia")


def validate_asin(value: str | None) -> Fact:
    """An ASIN is a unique combination of 10 letters and numbers (S5, S6)."""
    if value is None or str(value).strip() == "":
        return Fact("asin", None, Status.UNVERIFIED, note="no identifier supplied")
    raw = str(value).strip()
    norm = raw.upper()
    if not re.fullmatch(r"[A-Z0-9]+", norm):
        return Fact("asin", None, Status.UNVERIFIED, note=f"{raw!r} contains non-alphanumeric characters")
    if len(norm) != 10:
        return Fact(
            "asin",
            None,
            Status.UNVERIFIED,
            url="https://advertising.amazon.com/library/guides/asins-introduction",
            note=f"{raw!r} is {len(norm)} characters; an ASIN is exactly 10",
        )
    return Fact(
        "asin",
        norm,
        Status.VERIFIED,
        url="https://advertising.amazon.com/library/guides/asins-introduction",
        note="format-only check; existence in the catalog still requires a live lookup",
    )


def allow_isbn(value: str) -> Fact:
    """Books are identified by their 10-digit ISBN instead of an ASIN (S6)."""
    norm = str(value).strip().upper()
    if ISBN10_RE.match(norm):
        return Fact("isbn", norm, Status.VERIFIED, url="https://sell.amazon.com/blog/how-to-create-a-new-asin-amazon")
    return Fact("isbn", None, Status.UNVERIFIED, note="not a 10-digit ISBN")


def expand_variations(asins: list[str]) -> dict:
    """Variations each carry their own ASIN (S6) -- never collapse a family to one id."""
    seen, out = set(), []
    for a in asins:
        v = validate_asin(a)
        if v.usable and v.value not in seen:
            seen.add(v.value)
            out.append(v.value)
    return {"variation_asins": out, "rejected": [a for a in asins if a.upper() not in seen]}


def parse_url(url: str) -> dict:
    """Extract the catalog identifier from an Amazon product or short link."""
    from urllib.parse import urlparse

    m = DP_RE.search(url or "")
    candidate = m.group(1).upper() if m else None
    host = (urlparse(url or "").hostname or "").lower()
    if candidate is None and host in BARE_TOKEN_HOSTS:
        bare = BARE_TOKEN_RE.match(urlparse(url).path or "")
        if bare:
            candidate = bare.group(1).upper()
    if candidate is None:
        return {"asin": None, "candidate": None, "source_url": url, "lookup": None, "length": 0,
                "format_valid": False, "note": "no product identifier in this URL"}
    # Preserve the operator's original casing for the live lookup: an ASIN is
    # uppercase in Amazon's systems, but a mistyped mixed-case token must be
    # fetched exactly as supplied before we declare anything about it.
    v = validate_asin(candidate)
    lookup_token = raw_token if (raw_token := _raw_token(url, candidate)) else candidate
    return {
        "asin": v.value,
        "candidate": candidate,
        "length": len(candidate),
        "format_valid": v.status is Status.VERIFIED,
        "note": v.note,
        "lookup": f"https://www.amazon.com/dp/{lookup_token}",
        "source_url": url,
    }


def _raw_token(url: str, normalized: str) -> str | None:
    """Return the token exactly as the operator typed it."""
    from urllib.parse import urlparse

    for m in (DP_RE.search(url or ""), BARE_TOKEN_RE.match(urlparse(url or "").path or "")):
        if m and m.group(1).upper() == normalized:
            return m.group(1)
    return None
