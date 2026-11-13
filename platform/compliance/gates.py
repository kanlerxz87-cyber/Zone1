"""Hard compliance gates. Each function maps to a rule id in data/program.json.

These are called by the site builder and by the CI audit. A page that fails a
gate is not written -- the build fails instead, which is the only behaviour
that keeps "compliance with Amazon Associates policies" from being a slogan.
"""
from __future__ import annotations

import re

from _common import Report

# The sentence section 5 of the Operating Agreement requires, verbatim.
AMAZON_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AMAZON_MARKS = ("amazon", "kindle", "alexa", "echo", "prime", "audible", "imdb", "eero", "ring")


def disclosure_present(html: str) -> bool:
    return AMAZON_DISCLOSURE.lower() in re.sub(r"\s+", " ", (html or "")).lower()


def per_page_disclosure(html: str, *, has_affiliate_link: bool) -> bool:
    """FT-5: a home-page-only disclosure does not cover individual review pages."""
    return (not has_affiliate_link) or disclosure_present(html)


def no_buried_disclosure(html: str) -> bool:
    """FT-6: the disclosure must be visible text, not a 'DISCLOSURE' hyperlink."""
    if re.search(r">\s*(disclosure|legal|disclaimer)\s*</a>", html or "", re.I):
        return disclosure_present(html)
    return True


LINK_HREF_RE = re.compile(r'<a\b[^>]*href="([^"]+)"', re.I)


def is_special_link(href: str) -> bool:
    """A Special Link is one that carries the publisher's tag -- i.e. one that earns.

    Citations pointing at amazon.com policy or /dp/ pages earn nothing and are not
    Program Content placement, so they do not trigger the adjacency rule. Being
    stricter than the letter of the text here would push people to hide citations;
    being looser would let a monetized link ship undisclosed, so the tag parameter
    is the line.
    """
    h = (href or "").lower()
    if "tag=" in h:
        return True
    return any(s in h for s in ("//amzn.to/", "//amzn.asia/", "//amzn.com/", "amazon-adsystem.com"))


def special_links(html: str) -> list[str]:
    return [m for m in LINK_HREF_RE.findall(html or "") if is_special_link(m)]


def disclosure_adjacent_to_link(html: str, *, window: int = 1200) -> bool:
    """FT-4: the closer to the recommendation, the better -- require adjacency."""
    body = re.sub(r"\s+", " ", html or "")
    for href in special_links(body):
        pos = body.find(href)
        if pos < 0:
            continue
        seg = body[max(0, pos - window) : pos + len(href) + window]
        if AMAZON_DISCLOSURE.lower() not in seg.lower():
            return False
    return True


def amazon_disclosure_exact(html: str) -> bool:
    """FT-8: exact required sentence, not a paraphrase."""
    return disclosure_present(html)


def site_has_original_content(text: str, *, min_words: int = 300) -> bool:
    words = len(re.findall(r"[A-Za-z0-9']+", text or ""))
    return words >= min_words


def no_amazon_mark_in_identity(identity: str) -> bool:
    """ID-5: no Amazon mark (or misspelling) in domain, tag, or username."""
    s = (identity or "").lower()
    return not any(mark in s for mark in AMAZON_MARKS)


def not_child_directed(meta: dict) -> bool:
    """ID-6: sites directed at children under 13 are unsuitable."""
    return not bool(meta.get("child_directed") or meta.get("under_13_audience"))


def not_on_amazon(url: str) -> bool:
    """LK-8: never place a Special Link on an Amazon property."""
    return "amazon." not in (url or "").lower() or "affiliate-program" in (url or "").lower()


def no_amazon_mark_bidding(keywords: list[str]) -> list[str]:
    """DQ-1: returns the offending keywords that must be excluded or negatived."""
    out = []
    for k in keywords or []:
        kl = (k or "").lower().strip()
        if any(mark in kl for mark in AMAZON_MARKS):
            out.append(k)
    return out


def mobile_approved_only(approved: bool) -> bool:
    return bool(approved)


def no_price_tracking(features: list[str]) -> bool:
    return not any("price" in (f or "").lower() and ("track" in f.lower() or "alert" in f.lower()) for f in features)


def no_webview(platform_features: list[str]) -> bool:
    return not any("webview" in (f or "").lower() for f in platform_features)


def paapi_surface_ok(*, mobile_first: bool, written_approval: bool = False) -> bool:
    """MB-5: Product Advertising Content on a mobile-first site needs written approval."""
    return (not mobile_first) or bool(written_approval)


def no_client_side_injection(surface: str) -> bool:
    return (surface or "").lower() not in ("browser_extension", "toolbar", "plug-in", "plugin", "helper_object")


def no_tv_surface(surface: str) -> bool:
    return (surface or "").lower() in ("web", "mobile_web") or "tv" not in (surface or "").lower()


def audit_page(html: str, *, has_affiliate_link: bool | None = None, rules: list[str] | None = None) -> Report:
    """has_affiliate_link defaults to "the page contains a monetized Special Link"."""
    if has_affiliate_link is None:
        has_affiliate_link = bool(special_links(html))
    r = Report()
    checks = [
        ("FT-8/RK-2", amazon_disclosure_exact(html) if has_affiliate_link else True, "required disclosure sentence missing"),
        ("FT-4", disclosure_adjacent_to_link(html), "disclosure is not adjacent to a Special Link"),
        ("FT-5", per_page_disclosure(html, has_affiliate_link=has_affiliate_link), "disclosure only present site-wide"),
        ("FT-6", no_buried_disclosure(html), "disclosure is only reachable behind a 'DISCLOSURE' link"),
    ]
    for rule, ok, msg in checks:
        if not ok:
            r.add(rule, msg)
    return r
