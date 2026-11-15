#!/usr/bin/env python3
"""One-shot patch: data/products.json — precise F4 wording + new flag F44.

Applied by session arena/88bb2db6 on 2026-11-15, after re-reading the sources live.

F4 (wording)  The old action said the manual "names exactly 24 presets". Re-read on
    2026-11-15, the manual does not state the numeral 24 anywhere; it *lists* 24
    presets by name, and it lists them twice — the Preset Mode Chart and the
    Recommended Accessory Positions table each carry the same 24 rows. The wording
    now says that, so the claim matches exactly what the document does. The verdict
    is unchanged: the count is 24.

F44 (new)     A discrepancy no earlier pass had recorded. The Emeril brand page
    says "Included are 7 premium accessories to maximize versatility". The Amazon
    listing title for the supplied link says "Six Cooking Accessories Included".
    The site publishes the manufacturer's own figure (7), which is what its spec
    row claims, but a buyer comparing the listing they would click against the
    product page sees two different numbers. Recorded as a flag rather than
    resolved, because which is right depends on what is actually in the box.
"""
import json
from pathlib import Path

p = Path("data/products.json")
raw = p.read_text(encoding="utf-8")
d = json.loads(raw)

emeril = next(x for x in d["products"] if x["slug"] == "emeril-26qt-french-door")

# ---------------------------------------------------------------- F4 wording
f4 = next(f for f in emeril["flags"] if f["id"] == "F4")
old_issue = f4["issue"]
old_action = f4["action"]
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

# ---------------------------------------------------------------- F44 new flag
if not any(f["id"] == "F44" for f in emeril["flags"]):
    emeril["flags"].append({
        "id": "F44",
        "issue": (
            "The number of included accessories differs between the two official "
            "documents: the Emeril brand page says \"Included are 7 premium accessories "
            "to maximize versatility\", while the Amazon listing title for the supplied "
            "link says \"Six Cooking Accessories Included\". Found on 2026-11-15; no "
            "earlier pass had recorded it."
        ),
        "action": (
            "The site publishes the manufacturer's own figure (7) because that is what "
            "the brand page states, and it is labelled as a manufacturer statement. The "
            "listing's \"Six\" is not repeated as fact and is not silently dropped "
            "either. Which number is right depends on what is physically in the box, "
            "so the account holder should open the delivered product's packing list "
            "before this row is relied on. The owner's manual adds only that \"some "
            "accessories may not be included with purchase\"."
        ),
        "sources": ["S14", "S15", "S28"],
    })

p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("F4 wording updated; F44 added to the Emeril product")
