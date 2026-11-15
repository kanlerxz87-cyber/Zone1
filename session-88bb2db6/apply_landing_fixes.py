#!/usr/bin/env python3
"""One-shot patch: landing-page and product-page corrections.

Applied by session arena/88bb2db6 on 2026-11-15.

E1  The landing comparison table published the Emeril preset row as an open
    conflict ("Neither count is selected as definitive"), while the product page
    and flag F4 resolve the same row to 24. A reader comparing the two pages was
    told two different things about one fact. Re-read on 2026-11-15: the owner's
    manual lists exactly 24 presets by name in two separate tables (Preset Mode
    Chart and Recommended Accessory Positions), and the Amazon listing title says
    "24 One-Touch Preset Options". The brand page's specification block still says
    "25 Cooking Pre-sets". The cell now states that, and keeps the conflict and
    its flag visible.

E2  The landing page and the product pages linked "redirect evidence" to
    reports/link-check-2026-11-14.md, a raw markdown file that GitHub Pages
    serves as plain text and whose conclusion ("does not treat the three ASINs as
    confirmed identities") was later superseded by four further sessions. The
    buyer-facing link now points at the rendered in-site re-verification page.
    The raw document is still cited by name in the evidence register, where it is
    a legitimate archive citation.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

PATCHES = []


def sub(old, new, why):
    PATCHES.append((old, new, why))


# ---------------------------------------------------------------- E1
sub(
    '''      <td class="small"><span class="pill pill-warn">Conflicting claims</span><div class="tiny">Owner's manual names 24; product page states 25. Neither count is selected as definitive.</div><div class="tiny">{src_links(['S15', 'S14'])} <a href="flagged.html">Flagged</a></div></td>''',
    '''      <td class="small">24 presets named in the owner's manual<div class="tiny">Airfry, Fries, Bacon, Grill, Eggs, Fish, Ribs, Defrost, Steak, Vegetables, Wings, Bake, Rotisserie, Toast, Chicken, Pizza, Pastry, Proof, Broil, Slow Cook, Roast, Dehydrate, Reheat, Warm.</div><div class="tiny"><span class="pill pill-warn">One page disagrees</span> The brand page's specification block says "25 Cooking Pre-sets"; its own description and the Amazon listing title both say 24.</div><div class="tiny">{src_links(['S15', 'S14', 'S28'])} <a href="flagged.html">Flagged</a></div></td>''',
    "E1: the Emeril preset cell now matches the resolved flag instead of contradicting the product page",
)

# ---------------------------------------------------------------- E2
sub(
    '''<a href="reports/link-check-2026-11-14.md">Read the redirect evidence</a>''',
    '''<a href="reverification.html">Read the redirect evidence</a>''',
    "E2a: the landing page points at the rendered re-verification page, not a raw markdown file",
)

sub(
    '''<a href="reports/link-check-2026-11-14.md">link check, 2026-11-14</a>''',
    '''<a href="reverification.html">link checks, 2026-11-14 and 2026-11-15</a>''',
    "E2b: both landing-page stat links point at the rendered re-verification page",
)

sub(
    '''<a href="../reports/link-check-2026-11-14.md">redirect evidence</a>''',
    '''<a href="../reverification.html">redirect evidence</a>''',
    "E2d: the product pages point at the rendered re-verification page",
)

for old, new, why in PATCHES:
    n = s.count(old)
    if n < 1:
        raise SystemExit(f"PATCH FAILED (0 matches) - {why}\n{old[:160]}")
    if n > 1 and "E2b" not in why:
        raise SystemExit(f"PATCH FAILED ({n} matches) - {why}\n{old[:160]}")
    s = s.replace(old, new)
    print(f"  - {why}  ({n} occurrence(s))")

p.write_text(s, encoding="utf-8")
print(f"applied {len(PATCHES)} patches")
for _o, _n, why in PATCHES:
    print("  -", why)
