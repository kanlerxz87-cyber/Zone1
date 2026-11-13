"""Stage 2 — niche and product scoring, with the weights stated in the open.

The scores on the public site are all blank, because scoring needs inputs it
does not have. This module is what will run when they exist: a transparent,
reproducible weighted model -- no hidden coefficients, no learned numbers, and
an explicit refusal to score a record with missing required inputs.
"""
from __future__ import annotations

from dataclasses import dataclass

WEIGHTS = {
    "demand": 0.30,
    "competition": 0.20,
    "price_band": 0.15,
    "review_quality": 0.15,
    "commission": 0.20,
}
REQUIRED = tuple(WEIGHTS)


@dataclass
class ScoreResult:
    score: float | None
    missing: list[str]
    usable_inputs: dict


def inputs_from(record: dict) -> dict:
    out = {}
    for key in REQUIRED:
        val = record.get(key)
        if isinstance(val, dict):
            val = val.get("value")
        if val is None:
            continue
        out[key] = float(val)
    return out


def score(record: dict) -> ScoreResult:
    usable = inputs_from(record)
    missing = [k for k in REQUIRED if k not in usable]
    if missing:
        # Refusing to score is the honest output; a partial score would be a
        # number that looks comparable to a complete one but is not.
        return ScoreResult(None, missing, usable)
    total = sum(usable[k] * WEIGHTS[k] for k in REQUIRED)
    return ScoreResult(round(total, 4), [], usable)


def rank(records: list[dict]) -> list[dict]:
    scored = [(score(r), r) for r in records]
    usable = [(s, r) for s, r in scored if s.score is not None]
    usable.sort(key=lambda t: t[0].score, reverse=True)
    return [
        {"ref": r.get("ref"), "score": s.score, "weights": WEIGHTS} for s, r in usable
    ]
