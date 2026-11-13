"""Offline and unsolicited channels are prohibited (CN-10)."""
from __future__ import annotations

from _common import Report

OFFLINE = {"print", "ebook", "direct_mail", "flyer", "oral_solicitation", "packaging_insert"}
GATED = {"email", "sms", "direct_message"}


def channel_allowed(channel: str, *, solicited: bool = False, opted_in: bool = False) -> tuple[bool, str]:
    ch = (channel or "").lower()
    if ch in OFFLINE:
        return False, f"{ch} is an offline Promotional Activity and is not permitted"
    if ch in GATED:
        if not (solicited and opted_in):
            return False, f"{ch} may carry Special Links only when the recipient solicited the message and opted in"
        return True, "permitted: solicited opt-in communication"
    return True, "permitted channel"


def audit_plan(plan: list[dict]) -> Report:
    r = Report()
    for i, step in enumerate(plan):
        ok, why = channel_allowed(step.get("channel", ""), solicited=bool(step.get("solicited")), opted_in=bool(step.get("opted_in")))
        if not ok:
            r.add("CN-10", why, context=f"plan[{i}] channel={step.get('channel')}")
    return r
