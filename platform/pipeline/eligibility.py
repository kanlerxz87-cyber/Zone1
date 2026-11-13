"""Listing eligibility (DQ-6, DQ-7)."""
from __future__ import annotations


def is_promotable(listing: dict) -> tuple[bool, str]:
    if listing.get("subscription_only"):
        return False, "DQ-6: subscription purchase"
    if listing.get("preorder") and not listing.get("has_listing_page"):
        return False, "DQ-7: pre-order/pre-release with no product listing page"
    if not listing.get("found", True):
        return False, "catalog 404: the detail page could not be retrieved"
    return True, "eligible"
