#!/usr/bin/env python3
"""One-shot patch: keep the flag register and the executive summary consistent with
the site's stated position after the 2026-11-15 re-read.

Applied by session arena/88bb2db6 on 2026-11-15.

F29  sess-54c66535 recorded the Emeril preset count as "stated five different ways",
     with two official sources agreeing on 24 and the brand page still contradicting
     itself, and concluded that "no preset count is asserted anywhere on this site".
     That conclusion was true when it was written. The 2026-11-15 re-read changed
     the site's position: the owner's manual lists 24 by name in two separate tables
     and the Amazon listing title says 24, so the site now states 24 on the manual
     and flags the one disagreeing line.

     sess-54c66535's finding is kept verbatim and the change of position is appended,
     so the row still carries the original evidence and no earlier session's work is
     discarded. F29 and F4 both stay open.

Exec  the executive summary's "Hard source conflicts" row said all three conflicts
     were re-checked on 2026-11-14 and are still live. The preset count is no longer
     in that state, so the row now says what is actually true.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

OLD_F29 = """The conflict is narrowed, not closed - the same brand page still contradicts itself - so no preset count is asserted anywhere on this site. Decision needed: confirm the figure against the unit's own control panel before any copy states a number."""

NEW_F29 = """The conflict is narrowed, not closed - the same brand page still contradicts itself - so no preset count is asserted anywhere on this site. Decision needed: confirm the figure against the unit's own control panel before any copy states a number. <strong>Re-read 2026-11-15 by arena/88bb2db6, which changes that last sentence.</strong> The owner's manual for FAFO-001 was read row by row: its Preset Mode Chart and its Recommended Accessory Positions table each list exactly 24 presets by name, and the manual never states the numeral. The Amazon listing title independently says '24 One-Touch Preset Options'. The site now states 24 on the strength of the manual, names the one official line that disagrees (the brand page's specification block, '25 Cooking Pre-sets'), and flags it. This row and F4 both stay open, but the site no longer asserts nothing. The 10-in-1 and 11-in-1 labels remain marketing wording and are not presented as specifications. Decision still needed: confirm the figure against the unit's own control panel."""

OLD_EXEC = """("Hard source conflicts", "One serious (Chefman 8 Qt 450 °F claim vs its own manual), plus preset-count and SKU ambiguity issues. All of them were re-checked on 2026-11-14 and are still live on the official pages.", ["S12", "S13", "S14"]),"""

NEW_EXEC = """("Hard source conflicts", "One serious and still live (Chefman 8 Qt 450 °F claim vs its own manual), plus SKU ambiguity. The Emeril preset count was narrowed on 2026-11-15: the owner's manual lists 24 presets by name in two separate tables and the Amazon listing title says 24, while the brand page's specification block still says 25 - the site states 24 and flags the 25.", ["S12", "S13", "S14"]),"""

for old, new, why in ((OLD_F29, NEW_F29, "F29 position change appended"),
                      (OLD_EXEC, NEW_EXEC, "executive summary conflict row corrected")):
    if s.count(old) != 1:
        raise SystemExit(f"PATCH FAILED ({s.count(old)} matches) - {why}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print("applied 2 patches:")
print("  - F29: sess-54c66535's finding kept verbatim; the 2026-11-15 position change appended")
print("  - executive summary: the 'Hard source conflicts' row now says what is actually true")
