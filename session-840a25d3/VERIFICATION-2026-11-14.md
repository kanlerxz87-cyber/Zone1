# Verification record — sess-840a25d3 (integration pass 7), 2026-11-14 (UTC)

Branch `arena/840a25d3-zone1`. Scope: re-check the facts this site depends on, directly against the
official pages, and record what was seen. No value in `data/*.json` or the generated pages was changed.
Every quote below was copied from the fetched page on the date above.

## 1. The three supplied `link.amazon` short links

| Supplied link | Destination (as fetched) | Page `<title>` (as fetched) | Matches stored title? |
|---|---|---|---|
| https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-0740a2e990c9bbb3&channelId=704&plpRedirect=mhFallback | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | Yes (same as prior passes) |
| https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-3541f5edba6b914c&channelId=704&plpRedirect=mhFallback | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. : Home & Kitchen" | Yes |
| https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-507e2d3d167072eb&channelId=704&plpRedirect=mhFallback | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | Yes |

What this does and does not show:
* The destinations are the same three ASINs recorded by earlier passes. The title text matches.
* Every destination still carries `lv=shuf` and `plpRedirect=mhFallback`, which are Amazon fallback parameters. This record does not
  establish that the short links are the products the owner intended. That remains open (flags F-01, F-07, F17, F21).
* **No `tag=` (Associates ID) parameter appears in any fetched destination URL.** Whether an Associates tag is attached to the short
  links cannot be confirmed from this page. See irregularity I-1 below.

## 2. Amazon Associates — disclosure wording

Source: https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 ("Why do I have to identify myself as an Associate?")

* "the Operating Agreement requires that the following statement clearly and conspicuously appears on your Site: "As an Amazon Associate I earn from qualifying purchases.""
* Link-level disclosure must be "Clear" (example given: "(paid link)", "#ad", "#CommissionsEarned") and "Conspicuous" ("placed near any affiliate link ... They shouldn't have to hunt for it.")
* "the disclosure must be made in the medium in which the recommendation was provided"

Result: the site's wording matches. Confirmed.

Source: https://affiliate-program.amazon.com/help/operating/agreement — page "Updated: October 15, 2025". Used for the cross-reference
only; the Agreement's §5 text was not re-quoted in this pass (the Help topic above quotes the same statement).

## 3. Amazon Program Policies §2(b) — price and availability

Source: https://affiliate-program.amazon.com/help/operating/policies (Program Policies, Links on Your Site, §2(b)):

* "Product prices and availability may vary from time to time. ... your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API ..."
* Comparison format: "you must display both the lowest "new" price and, if we provide it to you, the lowest "used" price ..."
* "You must not make inaccurate, overbroad, deceptive or otherwise misleading claims about any Product, an Amazon Site, or any of our policies, promotions, or prices."

Result: the site shows no Amazon price, star rating or review count, which is consistent with these rules. Confirmed.

## 4. FTC rule text — 16 CFR 255.5

Source: https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255/section-255.5 (eCFR, "up to date as of 11/12/2026").

* § 255.5(a): "such connection must be disclosed clearly and conspicuously. ... A disclosure of a material connection does not require the complete details of the connection, but it must clearly communicate the nature of the connection sufficiently for consumers to evaluate its significance."

Result: the site's disclosure bar and link-level notes are consistent with this text. Confirmed. The eCFR page itself says it is "authoritative but unofficial"; the
official print edition is at govinfo.gov (linked from the eCFR page).

## 5. Live site

* https://kanlerxz87-cyber.github.io/Zone1/ returned the dashboard with the disclosure bar, "0 Verified product identities", "42 Verified spec values", "1 Unconfirmed values" and "31 Open irregularities". The root build (`python3 build.py`) reports the same values from the same data: the landing, Flagged and executive-summary pages all show 31.

## Irregularities found in this pass

* **I-1 — Link-level disclosure is stated more firmly than the links can support.** Each product card says "this is an affiliate link and we may earn a commission". The fetched destinations carry no Associates tag, and the short links are fallback redirects (see §1). The disclosure text is correct for an affiliate link; whether these particular links earn commission is not confirmed. Already tracked as F21 / F17. No change made in this pass; the owner should confirm the tag in Associates Central.
* **I-2 — Articles discoverability (no change needed).** The three research articles are reachable: the root navigation links to `research/index.html`, which links to `articles/index.html`. An earlier plan to add a navigation entry was dropped for this reason.
* **I-3 — Historical open-item counts differ across old records** (28, 30, 31, 34 appear in older COORDINATION.md entries). The current build reports 31 on every page. The older numbers are records of earlier states, not current errors. Not edited.
