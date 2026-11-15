#!/usr/bin/env python3
"""Resolve data/products.json against origin/main.

Applied by session arena/88bb2db6 on 2026-11-15, during the merge of origin/main
@ 8f40f04 (PRs #70, #71, #72) into arena/88bb2db6-zone1.

The other sessions changed the same file, so the file is taken from origin/main and
this session's three changes are re-applied onto it. Every change is additive and
none of the other sessions' work is discarded.

C1  amazon_listing_title gains a "read" date on all three products.
    origin/main added it (arena/792c279e, 2026-11-15) because the value is
    volatile - the Emeril title changed between the 2026-11-14 and 2026-11-15
    reads, which is what flag F38 is about. Taken from origin/main, kept.

C2  F4's wording, tightened by this session.
    origin/main still says the manual "names exactly 24 presets". The manual does
    not state the numeral 24 anywhere - it *lists* 24 presets by name, twice: the
    Preset Mode Chart and the Recommended Accessory Positions table each carry the
    same 24 rows. The wording is corrected to say so, and the 2026-11-15 re-read
    is recorded. The verdict is unchanged: 24.

C3  The "Included accessories" row carries both documents and a note.
    origin/main's F48 records the conflict but leaves the row sourced to the brand
    page alone, with no note on the row a buyer reads. This session's 2026-11-15
    re-read confirmed the brand page says "Included are 7 premium accessories" and
    the Amazon listing title for the supplied link says "Six Cooking Accessories
    Included", and that the owner's manual adds only "Some accessories may not be
    included with purchase". The row now links both documents and says what each
    says. The published value stays 7 - the manufacturer's own figure - and the
    value string is left as "7" so the row still parses as the number F48
    discusses. Only the note and the source list change.

C4  This session's product-level flag is renumbered F44 -> F50.
    F44 is already taken on origin/main: it records "the same site is published
    nine times from one repository", found by arena/792c279e. This session
    independently found the same accessory-count conflict and filed it as F44
    before reading origin/main. That is the F28/F40 class of collision this
    repository has been bitten by twice before, so the flag is renumbered to F50,
    the next free number after origin/main's F49. The programme-level F48 records
    the same underlying conflict from the other session's angle; F50 records this
    session's independent finding of the same fact, with the manual's wording that
    F48 does not carry. Both remain, and both say the same thing in different
    words, which is the keep-both outcome the board's protocol requires.
"""
import json
from pathlib import Path

src = Path("/tmp/main_products.json")
dst = Path("data/products.json")

d = json.loads(src.read_text(encoding="utf-8"))
emeril = next(x for x in d["products"] if x["slug"] == "emeril-26qt-french-door")

# ---------------------------------------------------------------- C2: F4 wording
f4 = next(f for f in emeril["flags"] if f["id"] == "F4")
f4["issue"] = (
    "The brand page states \"25 Cooking Pre-sets\" in its specification block but "
    "\"24 one-touch cooking presets\" in the description text on the same page; the "
    "Amazon title says 24. Re-read 2026-11-15: the brand page still states 25, so "
    "the conflict is live."
)
f4["action"] = (
    "Resolved in favour of the owner's manual, which lists 24 presets by name - the "
    "Preset Mode Chart and the Recommended Accessory Positions table each carry the "
    "same 24 rows (Airfry, Fries, Bacon, Grill, Eggs, Fish, Ribs, Defrost, Steak, "
    "Vegetables, Wings, Bake, Rotisserie, Toast, Chicken, Pizza, Pastry, Proof, Broil, "
    "Slow Cook, Roast, Dehydrate, Reheat, Warm). The manual does not state the numeral "
    "24 itself. The page's \"25\" is treated as a marketing error and is not repeated "
    "as fact. Re-read 2026-11-15."
)

# ---------------------------------------------------------------- C3: accessories row
row = next(s for s in emeril["specs"] if s["label"] == "Included accessories")
row["source"] = ["S14", "S28"]
row["note"] = (
    "The Emeril product page states \"Included are 7 premium accessories\". The Amazon "
    "listing title for the supplied link says \"Six Cooking Accessories Included\". Both "
    "documents are linked here; the owner's manual adds only that some accessories may "
    "not be included with purchase. See the flag register before relying on the count."
)

# ---------------------------------------------------------------- C4: renumber F44 -> F50
if any(f["id"] == "F44" for f in emeril["flags"]):
    for f in emeril["flags"]:
        if f["id"] == "F44":
            f["id"] = "F50"
    emeril["flags"] = sorted(emeril["flags"], key=lambda f: int(f["id"][1:]))
elif not any(f["id"] == "F50" for f in emeril["flags"]):
    emeril["flags"].append({
        "id": "F50",
        "issue": (
            "The number of included accessories differs between the two official "
            "documents: the Emeril brand page says \"Included are 7 premium accessories "
            "to maximize versatility\", while the Amazon listing title for the supplied "
            "link says \"Six Cooking Accessories Included\". Found independently on "
            "2026-11-15 by arena/88bb2db6; the programme-level row F48 records the same "
            "conflict from arena/792c279e's pass. Both are kept."
        ),
        "action": (
            "The site publishes the manufacturer's own figure (7) because that is what "
            "the brand page states, and the specification row links both documents and "
            "says what each one says. The listing's \"Six\" is not repeated as fact and "
            "is not silently dropped either. Which number is right depends on what is "
            "physically in the box, so the account holder should open the delivered "
            "product's packing list before this row is relied on. The owner's manual "
            "adds only that \"Some accessories may not be included with purchase\"."
        ),
        "sources": ["S14", "S15", "S28"],
    })
    emeril["flags"] = sorted(emeril["flags"], key=lambda f: int(f["id"][1:]))

dst.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("data/products.json resolved:")
print("  - taken from origin/main (keeps the 'read' dates on amazon_listing_title)")
print("  - F4 wording tightened to 'lists 24 presets by name'")
print("  - 'Included accessories' row now links S14 and S28 and carries the note")
print("  - this session's flag renumbered F44 -> F50 (F44 is taken on origin/main)")
print("  - Emeril product-level flags:", [f["id"] for f in emeril["flags"]])
