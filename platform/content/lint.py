"""Program-Content and CTA lint (CN-3, CN-4, LK-4, LK-6)."""
from __future__ import annotations

import re

from _common import Report


def no_bookmark_cta(text: str) -> bool:
    return not re.search(r"\b(bookmark|save this link|pin this link)\b", text or "", re.I)


def no_altered_program_content(provided: str, published: str) -> bool:
    """Only proportional resize or non-meaning-altering truncation is allowed."""
    p = re.sub(r"\s+", " ", provided or "").strip().lower()
    q = re.sub(r"\s+", " ", published or "").strip().lower()
    if q == p:
        return True
    # A truncation is only "..." removed from the tail: strip the ellipsis, then
    # the published text must be a true prefix of what Amazon supplied.
    stem = re.sub(r"(\.\.\.|…)$", "", q).strip()
    return bool(stem) and p.startswith(stem)


def list_link_needs_context(list_link: str, surrounding_words: int) -> bool:
    return surrounding_words >= 300


def audit_page(html: str, *, words_around_list_links: int = 10**9, program_content: tuple[str, str] | None = None) -> Report:
    r = Report()
    if not no_bookmark_cta(html):
        r.add("LK-4", "page invites readers to bookmark a Special Link")
    if program_content and not no_altered_program_content(*program_content):
        r.add("CN-3", "Amazon Program Content was altered beyond allowed truncation")
    if words_around_list_links < 300:
        r.add("LK-6", "product-list link without sufficient original surrounding content")
    return r
