"""Special-link validation.

Rules enforced here come from Participation Requirements section 2(b):
tag must be present and in XXXXX-## form, links must be reached directly from
the site, no redirectors, and no sub-tag bound to an identified visitor.
"""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from _common import Report

TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*-\d{2}$")
TAG_PARAM = "tag"
AMAZON_HOSTS = ("amazon.com", "amzn.com", "amzn.to", "link.amazon", "amzn.asia")
# link.amazon is Amazon-owned but is a jump service, not a Special Link, so it is
# treated as an intermediate hop for attribution purposes (see flag F-01).
INTERMEDIATE_HOSTS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "link.amazon", "buff.ly", "is.gd", "ow.ly", "bit.do")


def tag_present(url: str, expected_tag: str | None = None) -> bool:
    q = parse_qs(urlparse(url).query)
    tags = q.get(TAG_PARAM) or []
    if not tags:
        return False
    if expected_tag is None:
        return True
    return any(t == expected_tag for t in tags)


def tag_param(url: str) -> str | None:
    q = parse_qs(urlparse(url).query)
    vals = q.get(TAG_PARAM) or []
    return vals[0] if vals else None


def tag_well_formed(tag: str) -> bool:
    """Amazon requires the tag to appear as XXXXX-## or a designated variant."""
    return bool(TAG_RE.match(tag or ""))


def no_redirector(url: str, *, link_format: str = "special") -> bool:
    """True when the URL goes straight to Amazon without an intermediate hop."""
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return False
    return not any(host == h or host.endswith("." + h) for h in INTERMEDIATE_HOSTS)


def points_at_amazon(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in AMAZON_HOSTS)


def no_per_user_tagging(sub_tag: str | None, bound_user_id: str | None) -> bool:
    """A sub-tag may vary per placement, never per identified visitor."""
    if sub_tag is None:
        return True
    return bound_user_id is None


def validate(url: str, *, expected_tag: str | None = None, rule_id: str = "LK") -> Report:
    r = Report()
    if not no_redirector(url):
        r.add("DQ-3", "link routes through an intermediate shortener (disqualified purchase)", context=url)
    if not points_at_amazon(url):
        r.add(f"{rule_id}-host", "link does not target an Amazon host", context=url)
        return r
    t = tag_param(url)
    if t is None:
        r.add("LK-1", "Special Link carries no tag parameter", context=url)
    else:
        if not tag_well_formed(t):
            r.add("LK-2", f"tag {t!r} is not in XXXXX-## form", context=url)
        if expected_tag and t != expected_tag:
            r.add("LK-1", f"tag {t!r} is not the assigned Associates ID {expected_tag!r}", context=url)
    return r
