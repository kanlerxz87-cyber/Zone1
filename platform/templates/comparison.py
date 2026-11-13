"""Comparison template -- enforces CN-2 (lowest new AND lowest used)."""
from __future__ import annotations

from _common import Report


def render(rows: list[dict]) -> tuple[str, Report]:
    """rows: [{name, price_new, price_used}] -- blanks are rendered as
    'not verified', never as a number."""
    r = Report()
    html = ["<table class='cmp'><thead><tr><th>Product</th><th>Lowest new</th><th>Lowest used</th></tr></thead><tbody>"]
    for i, row in enumerate(rows):
        new = row.get("price_new")
        used = row.get("price_used")
        if new is None:
            r.add("CN-2", "comparison row has no lowest-new price from an approved source", context=f"rows[{i}]")
        if row.get("used_offered") and used is None:
            r.add("CN-2", "Amazon provided a used price but the row omits it", context=f"rows[{i}]")
        html.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                row.get("name") or "— unverified —",
                f"${new:.2f}" if isinstance(new, (int, float)) else "not verified",
                f"${used:.2f}" if isinstance(used, (int, float)) else "not offered / not verified",
            )
        )
    html.append("</tbody></table>")
    return "".join(html), r
