#!/usr/bin/env python3
"""Correct the "Included accessories" row's source list after re-reading the manual.

Applied by session arena/88bb2db6 on 2026-11-15, after PR #74 merged.

The mistake this fixes
----------------------
This session set the row's sources to ["S14", "S28"] and put the conflict in the
note. That was wrong in a way that mattered: the source list next to a value is
read as "these documents support this value". S14 (the Emeril product page) says
"7 premium accessories" and supports 7. S28 is the Amazon listing title, which
says "Six Cooking Accessories Included" and does NOT support 7 - it contradicts
it. Citing a contradicting document as a source for the value is the same error
as the site is built to avoid.

What the manual actually says
-----------------------------
Re-read on 2026-11-15, the owner's manual's "Parts & Accessories" section
enumerates 13 numbered items. Six of them are built into the appliance:

  1 Main Unit   2 Door Handle   3 Glass Door
  4 LED Display   5 Control Panel   6 Control Knob

and seven are removable accessories:

  7 Drip Tray   8 Wire Rack   9 Baking Pan   10 Rotisserie Spit
  11 Crisper Tray   12 Rotisserie Fetch Tool   13 Plate Handle

The manual marks item 8 "Quantity may vary", item 13 "*May be sold separately*",
and elsewhere "NOTE: Some accessories may not be included with purchase".

So the manual reproduces 7 by its own enumeration, which is a third official
document supporting the published value - and it is the one the site actually
cites for the row. The correct source list for the value "7" is therefore
["S14", "S15"], both of which support it. S28 belongs in the flag register
(F48, F50), where it already is, because there it is the evidence of the
conflict rather than a source for the value.

This session had already been corrected once on this point by upstream's own
re-read, which counted the same 13 items and reached the same 7. The row's
source list simply had not been updated to match.
"""
import json
from pathlib import Path

p = Path("data/products.json")
d = json.loads(p.read_text(encoding="utf-8"))
emeril = next(x for x in d["products"] if x["slug"] == "emeril-26qt-french-door")
row = next(s for s in emeril["specs"] if s["label"] == "Included accessories")

row["source"] = ["S14", "S15"]
row["note"] = (
    "Two official documents state 7: the Emeril product page says \"Included are 7 "
    "premium accessories\", and the owner's manual enumerates 13 numbered parts, of "
    "which 6 are built into the appliance (main unit, door handle, glass door, LED "
    "display, control panel, control knob), leaving 7 removable accessories (drip "
    "tray, wire rack, baking pan, rotisserie spit, crisper tray, rotisserie fetch "
    "tool, plate handle). The Amazon listing title for the supplied link instead says "
    "\"Six Cooking Accessories Included\"; that conflicting document is in the flag "
    "register, not here, because a row's source list is read as the evidence for the "
    "value and that title does not support 7. The manual adds that \"Some accessories "
    "may not be included with purchase\", so count the box before relying on this."
)

# The F50 flag row records the same conflict; point it at the enumeration evidence.
f50 = next((f for f in emeril["flags"] if f["id"] == "F50"), None)
if f50:
    f50["action"] = (
        "The site publishes 7, which two official documents support: the Emeril "
        "product page (\"Included are 7 premium accessories\") and the owner's manual, "
        "whose Parts & Accessories section enumerates 13 numbered items of which 6 are "
        "built into the appliance, leaving 7 removable accessories. The listing's "
        "\"Six\" is not repeated as fact and is not silently dropped either - it is "
        "recorded here as the conflicting document, because a specification row's "
        "source list is read as the evidence for its value and the listing title does "
        "not support 7. Which count matches the delivered box still has to be checked "
        "physically, because the manual says \"Some accessories may not be included "
        "with purchase\", marks the wire rack \"Quantity may vary\" and marks the plate "
        "handle \"May be sold separately\"."
    )

p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("'Included accessories' row:")
print("  source :", row["source"], "(both documents state 7; S28 is the conflicting one and stays in the flag register)")
print("  note   :", row["note"][:90] + "...")
print("  F50    : action updated with the manual's 13-item enumeration")
