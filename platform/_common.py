"""Shared types for the Zone1 platform.

The whole engine rests on one idea: a value is either Sourced or Blank.
There is no third state, because a third state would be a guess.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Optional


class Status(str, Enum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NEEDS_REVIEW = "needs-review"
    SKIPPED_NO_CREDENTIALS = "skipped-no-credentials"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Fact:
    """One assertion. `value` may be None; a non-None value requires a url."""

    key: str
    value: Optional[Any]
    status: Status
    url: str = ""
    note: str = ""

    def __post_init__(self) -> None:
        if self.value is not None and self.status is Status.VERIFIED and not self.url:
            raise ValueError(f"{self.key}: a verified value must cite an official source url")

    @property
    def usable(self) -> bool:
        return self.value is not None and self.status is Status.VERIFIED


@dataclass
class Finding:
    rule: str
    severity: str
    message: str
    context: str = ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)

    def add(self, rule: str, message: str, severity: str = "error", context: str = "") -> None:
        self.findings.append(Finding(rule, severity, message, context))

    @property
    def ok(self) -> bool:
        return not [f for f in self.findings if f.severity == "error"]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": len([f for f in self.findings if f.severity == "error"]),
            "warnings": len([f for f in self.findings if f.severity != "error"]),
            "findings": [
                {"rule": f.rule, "severity": f.severity, "message": f.message, "context": f.context}
                for f in self.findings
            ],
        }


OFFICIAL_HOSTS = (
    "affiliate-program.amazon.com",
    "amazonservices.com",
    "link.amazon",
    "amazon.com",
    "amazon-adsystem.com",
    "advertising.amazon.com",
    "sell.amazon.com",
    "amazon.science",
    "ftc.gov",
    "ecfr.gov",
    "federalregister.gov",
    "docs.github.com",
    "api.github.com",
    "github.com",
)


def is_official(url: str) -> bool:
    from urllib.parse import urlparse

    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def blank_field(reason: str, key: str = "field") -> Fact:
    return Fact(key=key, value=None, status=Status.UNVERIFIED, note=reason)


def iter_rows(groups: Iterable[dict]) -> Iterable[dict]:
    for g in groups:
        for row in g.get("rows", []):
            yield row
