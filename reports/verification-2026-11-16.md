# Verification round 10 — 2026-11-16 (session c334fb1c)

Scope: independent live re-read of the three supplied `link.amazon` short links, the Amazon Associates policy "Updated" date, and the live GitHub Pages landing page. No product values, articles, or site content were changed. Anything not re-read in this round is listed under "Not re-read".

## 1. Short links (fetched 2026-11-16, UTC)

| Supplied link | Final URL reached (path only, tracking params omitted) | ASIN | Title read today | Repo record | Match |
|---|---|---|---|---|---|
| https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 | B0CDY277D3 | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" | `data/products.json` → Chefman 6 Qt Dual Basket, B0CDY277D3 | Yes |
| https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R | B09B7SB46R | "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven … 24 One-Touch Preset Options …" | `data/products.json` → Emeril 26 QT, B09B7SB46R | Yes |
| https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH | B08DKYBTPH | "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option … Stainless Steel" | `data/products.json` → Chefman 8 Qt TurboFry, B08DKYBTPH | Yes |

What this shows: each short link resolves to the ASIN the repository records. It does **not** show that the link carries the account holder's Associates tag, and it does not show that the account is approved (see §3).

## 2. Associates Program Policies (S2)

- Page: https://affiliate-program.amazon.com/help/operating/policies
- Read today: "**Updated:** April 14, 2026."
- Repo record: the same date, stated in `data/sources.json` (S2). **Match.**

## 3. Live site

- Page: https://kanlerxz87-cyber.github.io/Zone1/ — loaded; the affiliate disclosure, the "Product identity, account approval and affiliate tracking are not confirmed" notice, and the source links render.

## 4. Irregularities observed today (none new; each already on the Flagged for review register)

1. **Short-link destinations carry no Associates tag in the resolved URL.** The final URLs contain Amazon's own `btn_ref=srctok-…` / `plpRedirect=mhFallback` parameters and no `tag=`. Attribution therefore cannot be confirmed from outside Associates Central. Already flagged as **F6**.
2. **Emeril preset count still conflicts across sources.** Today's Amazon title says "24 One-Touch Preset Options"; the brand page's specification block says 25 (as recorded in the landing page's Emeril row). Left open, not resolved.
3. **Chefman 8 Qt maximum temperature conflicts.** The Amazon title says "450°F Hi-Fry"; the brand listing records a 400 °F maximum. Already flagged as **F3**.

## 5. Gates run on the same tree (2026-11-16)

| Gate | Result |
|---|---|
| `bash scripts/ci-check.sh` | OK — 33 unit tests, data audit clean, build current, 6,372 links / 0 broken |
| `python3 build.py` | exit 0; output byte-identical to the committed tree |
| `python3 verify.py` | 46 spec rows (43 verified, 3 blank+flagged), 34 sources, 0 errors |

## 6. Not re-read in this round

- The FTC disclosure guidance (S8) and the 16 CFR 255 text were not re-fetched today; their last check is recorded on the board.
- Brand pages (S10, S12, S14) and owner's manuals (S13, S15, S18) were not re-fetched today.
- Amazon detail pages for prices, availability, and ratings: **intentionally not displayed** by this project (see `data/products.json` → `amazon_price_policy`, which cites S2 §2(b) and §6(t)).
- Whether the Associates account is approved, and which tag each short link carries: only the account holder can confirm these (questions Q-01 and Q-03 on `questions.html`).

## 7. Result

Every value re-read today matches the stored record. No content was changed. The open items above remain open and are published, not resolved.
