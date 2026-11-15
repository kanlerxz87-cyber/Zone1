#!/usr/bin/env python3
"""Generate the social card assets/og-card.png (1200x630).

Drawn deterministically from the site's own palette and copy so the card cannot
drift from the site. It states only what the site itself states: that the guide is
documentation-based and that specifications link to the manufacturer's own page.
No price, rating or review count appears, because the site publishes none.

Run:  python3 session-88bb2db6/make_og_card.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.parent
OUT = ROOT / "assets" / "og-card.png"
W, H = 1200, 630

INK = (12, 38, 35)        # deep teal, matches --brand #245746 family
DEEP = (8, 32, 30)
CREAM = (246, 247, 249)   # --bg
MINT = (204, 251, 241)    # --brand-soft
AMBER = (180, 83, 9)      # --warn

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

img = Image.new("RGB", (W, H), DEEP)
d = ImageDraw.Draw(img)

# ---- background: a soft radial glow in the upper right, plus a mint rule ----
glow = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(glow)
for r in range(520, 0, -12):
    a = int(46 * (1 - r / 520) ** 2)
    gd.ellipse([W - 380 - r, -300 - r, W - 380 + r, -300 + r], fill=a)
img = Image.composite(Image.new("RGB", (W, H), (20, 92, 82)), img, glow)
d = ImageDraw.Draw(img)

d.rectangle([0, 0, W, 10], fill=(16, 122, 110))
d.rectangle([0, H - 8, W, H], fill=(16, 122, 110))


def text(xy, s, font, fill, anchor=None):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


f_brand = ImageFont.truetype(F_BOLD, 74)
f_h1 = ImageFont.truetype(F_BOLD, 60)
f_sub = ImageFont.truetype(F_REG, 30)
f_small = ImageFont.truetype(F_REG, 24)
f_tiny = ImageFont.truetype(F_REG, 21)
f_mark = ImageFont.truetype(F_BOLD, 40)
f_chip = ImageFont.truetype(F_BOLD, 23)

# ---- brand mark -------------------------------------------------------------
d.rounded_rectangle([80, 72, 176, 168], radius=18, fill=(16, 122, 110))
text((128, 120), "Z1", f_mark, (255, 255, 255), anchor="mm")
text((200, 98), "Zone1 Kitchen", f_small, MINT)
text((200, 126), "Air-fryer decisions, backed by sources", f_tiny, (150, 200, 190))

# ---- headline ---------------------------------------------------------------
text((80, 232), "Choose the shape", f_h1, CREAM)
text((80, 302), "before the model.", f_h1, CREAM)

d.rectangle([80, 386, 268, 392], fill=(16, 122, 110))
text((80, 412), "Three air-fryer formats, compared from the", f_sub, (222, 232, 230))
text((80, 452), "manufacturer's own pages and owner's manuals.", f_sub, (222, 232, 230))

# ---- three format chips ----------------------------------------------------
chips = [
    ("Two baskets", "Chefman 6 Qt"),
    ("Countertop oven", "Emeril 26 QT"),
    ("One big basket", "Chefman 8 Qt"),
]
x = 80
for label, name in chips:
    w = 330
    d.rounded_rectangle([x, 516, x + w, 588], radius=12, outline=(30, 110, 100), width=2)
    text((x + 22, 528), name, f_chip, CREAM)
    text((x + 22, 556), label, f_tiny, (150, 200, 190))
    x += w + 22

# ---- the two honest lines, in the empty upper-right corner -----------------
text((W - 80, 92), "Every specification links to", f_tiny, (150, 200, 190), anchor="ra")
text((W - 80, 120), "its official page.", f_tiny, (150, 200, 190), anchor="ra")
text((W - 80, 152), "No hands-on testing is claimed.", f_tiny, (150, 200, 190), anchor="ra")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {W}x{H})")
