"""Safe link resolution.

The trap this module exists to close: Amazon answers an unknown /dp/ token
with a *shuffle fallback* page -- a real product page, for a product nobody
asked for. A resolver that only follows redirects will happily report that
"B04G1MEwY is a CHEFMAN air fryer". It is not.

is_fallback_redirect() is the guard. It keys off the parameters Amazon itself
adds on the fallback path (lv=shuf, plpRedirect=mhFallback, btn_ref=srctok-*),
and refuses to attribute the landing product to the requested token.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

FALLBACK_MARKERS = ("plpredirect", "lv=shuf", "btn_ref=srctok", "channelid=704")
REQUEST_ID_RE = re.compile(r"\b(?:\[?[A-Z0-9]{3}-[0-9]{7}-[0-9]{7})")


def classify(final_url: str, *, final_title: str = "", wanted_asin: str | None = None) -> dict:
    q = urlparse(final_url)
    qs = parse_qs(q.query)
    blob = (q.query or "").lower()
    markers = [m for m in FALLBACK_MARKERS if m in blob]
    path_asin = re.search(r"/dp/([A-Za-z0-9]{10})", q.path or "")
    landed = path_asin.group(1).upper() if path_asin else None
    is_fallback = bool(markers) or (wanted_asin is not None and landed != wanted_asin.upper())
    return {
        "final_url": final_url,
        "landed_asin": landed,
        "wanted_asin": (wanted_asin or "").upper() or None,
        "fallback_markers": markers,
        "is_fallback": is_fallback,
        "attributable": not is_fallback and landed is not None,
        "final_title": final_title,
        "verdict": (
            "REFUSED: Amazon served a shuffle/fallback page; the landing product is not the requested one"
            if is_fallback
            else "resolved"
        ),
    }


def attribution_allowed(cls: dict) -> bool:
    """Only a genuine resolution may populate the product table."""
    return bool(cls.get("attributable"))


def _unused(*_a, **_k) -> bool:  # pragma: no cover - kept for API symmetry
    return False
