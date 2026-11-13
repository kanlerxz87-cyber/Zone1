"""Stage 1 — product research.

Input:  operator-supplied product URLs (or ASINs).
Output: a product record whose every field is either sourced or None.

Note what this module does *not* do: it never fills a field from the model,
from a search snippet, or from a neighbouring product. An empty field is the
correct representation of "unknown" and is what the site renders.
"""
from __future__ import annotations

from _common import Fact, Status
from catalog.asin import parse_url, validate_asin
from resolver.link import attribution_allowed, classify


def intake(supplied: list[str]) -> list[dict]:
    records = []
    for url in supplied:
        parsed = parse_url(url)
        candidate = parsed.get("candidate")
        fmt = validate_asin(candidate)
        records.append(
            {
                "supplied_url": url,
                "extracted_token": candidate,
                "token_length": len(candidate) if candidate else 0,
                "asin_format_valid": fmt.status is Status.VERIFIED,
                "asin_note": fmt.note,
                "catalog_lookup": parsed.get("lookup"),
                "fields": {},
                "record_status": Status.UNVERIFIED,
            }
        )
    return records


def observe_redirect(record: dict, final_url: str, final_title: str = "") -> dict:
    """Attach what Amazon actually served, then decide if it may be attributed."""
    cls = classify(final_url, final_title=final_title, wanted_asin=record.get("extracted_token"))
    record["redirect"] = cls
    record["attributable"] = attribution_allowed(cls)
    if not record["attributable"]:
        record["fields"] = {}
        record["record_status"] = Status.UNVERIFIED
        record["blocker_reason"] = cls["verdict"]
    return record


def adopt(record: dict, field: str, value, source_url: str, *, official: bool) -> Fact:
    """Only a sourced value from an official host becomes a usable Fact."""
    if not official or not source_url:
        return Fact(field, None, Status.UNVERIFIED, note="rejected: no official source")
    return Fact(field, value, Status.VERIFIED, url=source_url)
