"""Transformative-use ratio for ID-4 (originality must be significant)."""
from __future__ import annotations

import re


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", (s or "").lower())


def overlap_ratio(source: str, draft: str) -> float:
    a, b = set(_tokens(source)), set(_tokens(draft))
    if not b:
        return 1.0
    return len(a & b) / len(b)


def transformative_use_ok(source: str, draft: str, *, max_overlap: float = 0.35) -> bool:
    """More than `max_overlap` of the draft's vocabulary taken from Amazon's copy
    is re-publication, not commentary, analysis, or transformation."""
    return overlap_ratio(source, draft) <= max_overlap
