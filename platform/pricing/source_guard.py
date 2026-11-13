"""Price and availability may only be shown from an approved source (CN-1)."""
from __future__ import annotations

from _common import Fact, Status

APPROVED_SOURCES = ("special_link_served_by_amazon", "creators_api", "pa_api")


def may_show_price(source: str, obtained_via: str | None) -> bool:
    if source not in APPROVED_SOURCES:
        return False
    return obtained_via in ("creators_api", "pa_api") or source == "special_link_served_by_amazon"


def price_fact(value, source: str, *, url: str = "", retrieved: str = "") -> Fact:
    """Build the price cell. Anything not from an approved source stays blank."""
    if value is None:
        return Fact("price", None, Status.UNVERIFIED, note="no official source stated a price")
    if not may_show_price(source, source):
        return Fact(
            "price",
            None,
            Status.UNVERIFIED,
            note=f"refused: {source!r} is not an approved pricing source (CN-1)",
        )
    return Fact("price", value, Status.VERIFIED, url=url, note=f"retrieved {retrieved} via {source}")
