"""Promotion expiry (LK-7): references to a finished sale must come down."""
from __future__ import annotations

from datetime import date


def prune(promos: list[dict], *, today: date | None = None) -> dict:
    today = today or date.today()
    keep, remove = [], []
    for p in promos:
        ends = p.get("ends")
        try:
            expired = ends is not None and date.fromisoformat(str(ends)[:10]) < today
        except ValueError:
            expired = True  # an undated promo claim cannot be verified, so it goes
        (remove if expired else keep).append(p)
    return {"keep": keep, "remove": remove, "reason": "LK-7 remove references once the promotion ends"}
