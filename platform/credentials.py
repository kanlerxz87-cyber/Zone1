"""Credential gating.

Every networked stage of the pipeline asks here first. If credentials are
absent the stage returns SKIPPED_NO_CREDENTIALS -- it must never fall back to
simulated data, because simulated data on this site would be indistinguishable
from research.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from _common import Status

ASSOCIATE_TAG_VAR = "AMAZON_ASSOCIATE_TAG"
PA_ACCESS_VAR = "AMAZON_PA_ACCESS_KEY"
PA_SECRET_VAR = "AMAZON_PA_SECRET_KEY"
PA_PARTNER_VAR = "AMAZON_PA_PARTNER_TYPE"


@dataclass(frozen=True)
class CredentialState:
    has_tag: bool
    has_pa_access_key: bool
    has_pa_secret_key: bool
    has_partner_type: bool

    @property
    def can_publish_links(self) -> bool:
        return self.has_tag

    @property
    def can_fetch_product_data(self) -> bool:
        return self.has_pa_access_key and self.has_pa_secret_key and self.has_partner_type

    @property
    def status(self) -> Status:
        if self.can_publish_links and self.can_fetch_product_data:
            return Status.VERIFIED
        return Status.SKIPPED_NO_CREDENTIALS

    def missing(self) -> list[str]:
        out = []
        if not self.has_tag:
            out.append(ASSOCIATE_TAG_VAR)
        if not self.has_pa_access_key:
            out.append(PA_ACCESS_VAR)
        if not self.has_pa_secret_key:
            out.append(PA_SECRET_VAR)
        if not self.has_partner_type:
            out.append(PA_PARTNER_VAR)
        return out


def detect(env: dict | None = None) -> CredentialState:
    env = os.environ if env is None else env

    def present(name: str) -> bool:
        val = (env.get(name) or "").strip()
        if not val:
            return False
        # Reject placeholder values that would otherwise silently "work".
        lowered = val.lower()
        if "<" in val or ">" in val:
            return False
        for junk in ("changeme", "your-", "your_", "placeholder", "xxxxx"):
            if junk in lowered:
                return False
        return True

    return CredentialState(
        has_tag=present(ASSOCIATE_TAG_VAR),
        has_pa_access_key=present(PA_ACCESS_VAR),
        has_pa_secret_key=present(PA_SECRET_VAR),
        has_partner_type=present(PA_PARTNER_VAR),
    )
