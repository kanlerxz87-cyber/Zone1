#!/usr/bin/env python3
"""Add a build guard: a specification row must not cite a document that contradicts it.

Applied by session arena/88bb2db6 on 2026-11-15.

The defect this prevents
------------------------
This session cited the Amazon listing title (S28) as a source on the Emeril
"Included accessories" row, whose value is 7. The listing says "Six Cooking
Accessories Included" - it contradicts the value. A row's source list is read by
a reader as "these are the documents this value came from", so citing a
contradicting document there asserts something false about the evidence, which is
the same error the site is built to avoid everywhere else.

The guard
---------
data/products.json gains a top-level "source_conflicts" register: rows where an
official document is known to contradict the published value, and which document it
is. check_spec_source_conflicts() then fails the build if a row cites a
contradicting document in its source list.

The register is deliberately explicit rather than inferred. There is no way to
automatically tell that an arbitrary document contradicts a value; the only
honest way is for a human who has read both to say so, in writing, once. The
guard then makes that knowledge permanent: the contradiction can be recorded in
the flag register, and it can never again leak into the row's evidence.

This is a narrow guard on purpose. It does not try to verify that a source
supports a value in general - it cannot - it only enforces the conflicts a
reviewer has already identified by reading both documents.
"""
import json
from pathlib import Path

# ---------------------------------------------------------------- 1. the register
p = Path("data/products.json")
d = json.loads(p.read_text(encoding="utf-8"))

d["source_conflicts"] = {
    "note": (
        "Official documents that contradict a published specification value. Each entry "
        "names a row and the source id that contradicts it. The build fails if that source "
        "id appears in the row's source list, because a row's source list is read as the "
        "evidence for its value. The contradicting document belongs in the flag register, "
        "where it is the evidence of the conflict. Added 2026-11-15 by arena/88bb2db6."
    ),
    "entries": [
        {
            "slug": "emeril-26qt-french-door",
            "label": "Included accessories",
            "value": "7",
            "conflicting_source": "S28",
            "reason": (
                "The Amazon listing title for the supplied link ends 'Six Cooking Accessories "
                "Included'. It contradicts the published 7. The brand page (S14) and the "
                "owner's manual (S15) both support 7 - the manual by enumerating 13 numbered "
                "parts of which 6 are built into the appliance, leaving 7 removable "
                "accessories - so the row cites those two and the listing is recorded in the "
                "flag register instead (F48, F50)."
            ),
        },
    ],
}

p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("data/products.json: source_conflicts register written")

# ---------------------------------------------------------------- 2. the guard
b = Path("build.py")
s = b.read_text(encoding="utf-8")

ANCHOR = '''def check_disclosure(pages):'''
GUARD = '''def check_spec_source_conflicts():
    """Build guard: a row must not cite a document that contradicts its own value.

    Written 2026-11-15 (arena/88bb2db6) after this session cited the Amazon listing
    title on the Emeril "Included accessories" row. That listing says "Six Cooking
    Accessories Included" while the row's value is 7, so listing it as a source
    asserted something false about where the value came from.

    The check is driven by an explicit register in data/products.json
    (source_conflicts.entries), not by inference: there is no way for a build to
    tell that an arbitrary document contradicts a value. A reviewer who has read
    both documents records the conflict once, and from then on the contradiction
    can live in the flag register but never in the row's evidence.
    """
    problems = []
    register = (PRODUCTS.get("source_conflicts") or {}).get("entries") or []
    for entry in register:
        slug = entry.get("slug")
        label = entry.get("label")
        bad = entry.get("conflicting_source")
        product = next((p for p in PRODUCT_LIST if p["slug"] == slug), None)
        if product is None:
            problems.append(f"source_conflicts: unknown product slug {slug!r}")
            continue
        row = next((s for s in product["specs"] if s["label"] == label), None)
        if row is None:
            problems.append(f"source_conflicts: {slug} has no row labelled {label!r}")
            continue
        if bad in (row.get("source") or []):
            problems.append(
                f'{slug} / "{label}": cites {bad}, which contradicts the published value '
                f'{row.get("value")!r}. The contradicting document belongs in the flag '
                f'register, not in the row\\'s source list.'
            )
    return problems


def check_disclosure(pages):'''

if s.count(ANCHOR) != 1:
    raise SystemExit(f"anchor PATCH FAILED ({s.count(ANCHOR)} matches)")
s = s.replace(ANCHOR, GUARD)

CALL_ANCHOR = '''    missing = check_disclosure(list(pages.items()))'''
CALL_NEW = '''    conflict_problems = check_spec_source_conflicts()
    if conflict_problems:
        raise SystemExit("BUILD FAILED — a row cites a document that contradicts its own value:\\n  "
                         + "\\n  ".join(conflict_problems))
    missing = check_disclosure(list(pages.items()))'''

if s.count(CALL_ANCHOR) != 1:
    raise SystemExit("call PATCH FAILED")
s = s.replace(CALL_ANCHOR, CALL_NEW)

b.write_text(s, encoding="utf-8")
print("build.py: check_spec_source_conflicts() added and wired into the build")
