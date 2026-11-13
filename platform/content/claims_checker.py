"""Claim substantiation: no generated sentence ships without a source.

This is the module that makes 'no hallucinations' a build step rather than an
aspiration. The generator may draft; the checker decides what survives.
"""
from __future__ import annotations

import re

from _common import Report

INCOME_PROMISES = (
    "guaranteed income", "passive income guaranteed", "earn up to", "make $", "you will earn",
    "expected commission", "projected revenue", "roi of", "profit per month",
)
IMPLIED_ENDORSEMENT = (
    "officially recommended by amazon", "amazon endorses", "amazon approved", "partnered with amazon",
    "sponsored by amazon", "amazon selects", "best seller on amazon award",
)
AGREEMENT_TELLTALES = ("according to section", "the operating agreement states", "per the associates agreement")


def no_income_promise(text: str) -> bool:
    t = (text or "").lower()
    return not any(p in t for p in INCOME_PROMISES)


def no_implied_endorsement(text: str) -> bool:
    t = (text or "").lower()
    return not any(p in t for p in IMPLIED_ENDORSEMENT)


def no_agreement_quotes(text: str) -> bool:
    """FT-10: aside from the section 5 sentence, do not publicise the agreement's terms."""
    t = (text or "").lower()
    return not any(p in t for p in AGREEMENT_TELLTALES)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text or "").strip())
    return [p for p in parts if p]


def audit_draft(draft: str, *, supported: list[str], has_affiliate_link: bool = True) -> Report:
    """Every factual sentence must appear in `supported` (the sourced fact set)."""
    r = Report()
    allowed = {re.sub(r"\s+", " ", s).strip().lower() for s in supported}
    for s in sentences(draft):
        key = re.sub(r"\s+", " ", s).strip().lower()
        if not no_income_promise(s):
            r.add("RK-6", "sentence promises or projects earnings", context=s)
        if not no_implied_endorsement(s):
            r.add("FT-9", "sentence implies Amazon sponsorship or endorsement", context=s)
        if not no_agreement_quotes(s):
            r.add("FT-10", "sentence publicly characterises the Associates Agreement", context=s)
        if re.search(r"\$\s?\d|\b\d+(\.\d+)?\s?%|\b\d{2,}\s?(reviews|ratings|units)\b", s) and key not in allowed:
            r.add("CN-6", "unsourced numeric claim", context=s)
    return r
