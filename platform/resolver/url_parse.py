"""Identifier extraction from a URL (CT-5: the ASIN follows /dp/)."""
from __future__ import annotations

from catalog.asin import parse_url  # re-export: single definition, one place to test

__all__ = ["parse_url"]
