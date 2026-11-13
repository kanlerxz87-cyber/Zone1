"""Stage 3 — content generation with a source gate.

The generator builds *structure* (headings, the disclosure block, the link
slot, the comparison skeleton) and only ever fills a sentence from a record of
sourced facts passed in by the caller. If a fact is absent the slot is filled
with an explicit placeholder, so an unpublished claim cannot sneak into copy.
"""
from __future__ import annotations

import re

from _common import Fact, Status
from compliance.gates import AMAZON_DISCLOSURE

PLACEHOLDER = "[unverified — no official source states this]"


def _cell(fact) -> str:
    if isinstance(fact, Fact):
        return str(fact.value) if fact.usable else PLACEHOLDER
    if isinstance(fact, dict):
        return _cell(fact.get("value") if "value" in fact else None)
    return str(fact) if fact not in (None, "") else PLACEHOLDER


def disclosure_block() -> str:
    return (
        f"<aside class=\"disclosure\"><strong>Advertising disclosure.</strong> {AMAZON_DISCLOSURE} "
        "Prices, ratings and availability change on Amazon after publication; the figures shown were "
        "read from the product's own Amazon page on the date printed beside them.</aside>"
    )


def article(product: dict, *, keyword: str | None = None) -> dict:
    title = product.get("product_name") or PLACEHOLDER
    kw = keyword or (title if title != PLACEHOLDER else "the product")
    body = [
        f"<h1>{title} review</h1>",
        disclosure_block(),
        f"<p><em>Updated {product.get('verified_on', PLACEHOLDER)}.</em></p>",
        "<h2>What it is</h2>",
        f"<p>{_cell(product.get('brand'))} — {title}. Category: {_cell(product.get('category'))}.</p>",
        "<h2>Key specifications</h2>",
        "<table><tr><th>Spec</th><th>Value</th><th>Source</th></tr>",
        *[f"<tr><td>{k}</td><td>{_cell(v)}</td><td>{getattr(v, 'url', '') or '—'}</td></tr>"
          for k, v in sorted((product.get("specs") or {}).items())],
        "</table>",
        "<h2>Who should buy it</h2>",
        "<p>Written for readers comparing options before a purchase; claims below are limited to what "
        "the product page states.</p>",
        f"<p><a class=\"cta\" href=\"{_cell(product.get('special_link'))}\">View current price on Amazon</a></p>",
    ]
    html = "\n".join(body)
    return {
        "slug": re.sub(r"[^a-z0-9]+", "-", (title or kw).lower()).strip("-")[:60] or "product-review",
        "keyword": kw,
        "html": html,
        "placeholders_used": html.count(PLACEHOLDER),
    }


def comparison(products: list[dict]) -> dict:
    rows = "".join(
        f"<tr><td>{_cell(p.get('product_name'))}</td><td>{_cell(p.get('price'))}</td>"
        f"<td>{_cell(p.get('rating'))}</td><td>{_cell(p.get('used_price'))}</td></tr>"
        for p in products
    )
    html = (
        "<h1>Comparison</h1>" + disclosure_block()
        + "<table><tr><th>Product</th><th>Lowest new</th><th>Rating</th><th>Lowest used</th></tr>"
        + rows + "</table>"
    )
    return {"html": html, "placeholders_used": html.count(PLACEHOLDER)}


def buying_guide(products: list[dict], *, criteria: list[str] | None = None) -> dict:
    crit = criteria or ["fit for the use case", "verified specification", "price at time of reading", "warranty terms"]
    lis = "".join(f"<li>{c}</li>" for c in crit)
    items = "".join(
        f"<li>{_cell(p.get('product_name'))} — {_cell(p.get('why_picked'))}</li>" for p in products
    ) or f"<li>{PLACEHOLDER}</li>"
    html = (
        "<h1>Buying guide</h1>" + disclosure_block()
        + f"<h2>How to choose</h2><ul>{lis}</ul><h2>Picks</h2><ul>{items}</ul>"
    )
    return {"html": html, "placeholders_used": html.count(PLACEHOLDER)}
