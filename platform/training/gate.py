"""No Program Content in model training without Amazon's written approval (CN-7)."""
from __future__ import annotations

from _common import Report


def may_train(has_written_approval: bool) -> bool:
    return bool(has_written_approval)


def audit_dataset(records: list[dict], *, has_written_approval: bool = False) -> Report:
    r = Report()
    if may_train(has_written_approval):
        return r
    for i, rec in enumerate(records):
        if rec.get("origin") in ("program_content", "pa_api_payload", "special_link", "amazon_listing"):
            r.add(
                "CN-7",
                "dataset row derives from Program Content; training on it needs Amazon's express prior written approval",
                context=f"records[{i}].origin={rec.get('origin')}",
            )
    return r
