"""Staleness expiry (CN-5, F-14): nothing older than its window may render."""
from __future__ import annotations

from datetime import date


def is_stale(retrieved: str | None, *, max_age_days: int, today: date | None = None) -> bool:
    if not retrieved:
        return True
    today = today or date.today()
    try:
        then = date.fromisoformat(str(retrieved)[:10])
    except ValueError:
        return True
    return (today - then).days > max_age_days


def sweep(records: list[dict], *, max_age_days: int, today: date | None = None) -> dict:
    fresh, stale = [], []
    for rec in records:
        (stale if is_stale(rec.get("retrieved"), max_age_days=max_age_days, today=today) else fresh).append(rec)
    return {"fresh": fresh, "stale": stale, "max_age_days": max_age_days}
