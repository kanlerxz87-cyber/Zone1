#!/usr/bin/env python3
"""Namespace the accessible-name ids of the four generated SVG figures.

The four figures are inlined into one page (figures.html). Each SVG carried
`<title id="t">` and `aria-labelledby="t"`, so the page carried four elements with
the same id and every figure's accessible name resolved to the first one.

This edits the generator, not the generated files: the SVGs are rebuilt by
`build.py` on every run, so patching the output would be undone on the next
build. It was found by `scripts/audit_pages.py` (duplicate-id check), not by
eye.
"""
from __future__ import annotations

import re
import sys

PATH = "build.py"

REPLACEMENTS = [
    # the frame helper: give each figure its own id
    (
        "def _svg_frame(title, note, src_lines):",
        "def _svg_frame(title, note, src_lines, uid=\"fig\"):\n"
        "    # The four figures are inlined into a single page, so each <svg> needs its own\n"
        "    # accessible-name id: a shared id=\"t\" made every figure's title point at the\n"
        "    # first one, and four <title id=\"t\"> elements on one page are a duplicate-id\n"
        "    # defect. Found 2026-11-16 by the page audit, not by eye.",
    ),
    (
        'aria-labelledby="t"><title id="t">',
        'aria-labelledby="{uid}-title"><title id="{uid}-title">',
    ),
    (
        'src_lines) + panels + axis + _svg_close())',
        'src_lines, uid="fig-footprint") + panels + axis + _svg_close())',
    ),
    (
        'src_lines) + bars + axis + _svg_close())',
        'src_lines, uid="fig-temperature") + bars + axis + _svg_close())',
    ),
    (
        'src_lines) + rows + _svg_close())',
        'src_lines, uid="fig-presets") + rows + _svg_close())',
    ),
    (
        '[(yq + 2 * step + 90, "Sources: Chefman 6 Qt — S10 · Emeril 26 QT — S15/S14 · Chefman 8 Qt — S12/S13")]) + lines + boxes + _svg_close())',
        '[(yq + 2 * step + 90, "Sources: Chefman 6 Qt — S10 · Emeril 26 QT — S15/S14 · Chefman 8 Qt — S12/S13")], uid="fig-decision-tree") + lines + boxes + _svg_close())',
    ),
]


def main() -> int:
    text = open(PATH, encoding="utf-8").read()
    changed = 0
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new, 1)
            changed += 1
        else:
            print(f"NOT FOUND: {old[:70]!r}")
    open(PATH, "w", encoding="utf-8").write(text)
    print(f"applied {changed}/{len(REPLACEMENTS)} replacements")
    return 0 if changed == len(REPLACEMENTS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
