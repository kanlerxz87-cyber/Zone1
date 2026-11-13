# Independent cross-check — session `arena-4ba9e055`

**Purpose:** a second, independent read of the published data on `main` (built by session `d14c5409`). Every value was checked against an official page on 2026-11-13. Nothing here changes a value on the published site. Where the check found a gap, it was added as a flag (F17–F23) in `data/flags.json`, with a source ID in `data/sources.json`.

**Files in this folder:** `data/` and `reports/` hold this session's independent build (for comparison only). `main`'s published site is in `docs/` and is built by `scripts/build.mjs`.

## 1. Product values (3 rows)

| Field | `main` (published) | This cross-check | Result |
| --- | --- | --- | --- |
| P1 ASIN | B0CDY277D3 · [source](https://www.amazon.com/dp/B0CDY277D3) | B0CDY277D3 | match |
| P1 title | CHEFMAN 6 Quart Dual Basket … - Black | same | match |
| P1 department | Home & Kitchen | Home & Kitchen | match |
| P2 ASIN | B09B7SB46R · [source](https://www.amazon.com/dp/B09B7SB46R) | B09B7SB46R | match |
| P2 title | Emeril Lagasse 26QT French Door … | same | match |
| P2 department | Home & Kitchen | Home & Kitchen | match |
| P3 ASIN | B08DKYBTPH · [source](https://www.amazon.com/dp/B08DKYBTPH) | B08DKYBTPH | match |
| P3 title | "Chefman Air Fryer 8 Qt \| TurboFry 4-in-1 …" | "TurboFry® 4-in-1 …" (registered-trademark sign present) | minor difference → **F23** |
| P3 department | Home & Kitchen | Home & Kitchen | match |
| Price, rating, review count, commission rate (all 3) | blank, unverified | blank, unverified | match |
| Best-sellers rank, availability (all 3) | not listed | blank, unverified | gap → **F22** |
| Identity of each short link | "short codes ≠ ASINs" (F04) | short codes ≠ ASINs, **plus** redirect fallback parameters, fake-code 403, and a disputed repeat result | gap → **F17** |

## 2. Short-link test (2026-11-13)

| Test | Result |
| --- | --- |
| `https://link.amazon/ZZZZZZZZZ` (fake code) | `403 Forbidden` |
| `https://www.amazon.com/dp/B04G1MEwY` (code used as ASIN) | `Page Not Found` |
| `https://link.amazon/B04G1MEwY` | redirects to `amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&btn_ref=srctok-2cef40d2904c29d8&channelId=704&plpRedirect=mhFallback` |
| Second request for the same code | same ASIN, same `srctok` |
| Other session's report (`arena/f28312ac-zone1`, its F-07) | different featured product on later requests; not reproduced here |

**Conclusion:** the codes are valid redirect tokens, not ASINs. Whether each one leads to the intended product cannot be confirmed from here. The redirect parameters (`lv=shuf`, `plpRedirect=mhFallback`) suggest a fallback path. The owner should open each link and confirm (F17).

## 3. Compliance (official text)

Read on 2026-11-13. Compared with the 11 rows already on `main`.

| Topic | On `main`? | Source | Action |
| --- | --- | --- | --- |
| Associate disclosure sentence (Operating Agreement §5) | yes (C01) | [agreement](https://affiliate-program.amazon.com/help/operating/agreement) | none |
| Associates tag on every link (Policies, Participation §2) | yes (C02) | [policies](https://affiliate-program.amazon.com/help/operating/policies) | none |
| Prices shown only from Amazon or Creators API (§2(b)) | yes (C03) | policies | none |
| Program Content may not be altered (§6(a)) | **no** | policies | **F19** |
| Privacy and cookie disclosure (§3(e)) | **no** | policies | **F20** |
| Creators API prerequisites: 10 qualifying sales in 30 days | **no** | [Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction) | **F18** |
| PA-API 5 deprecated, 403 AccessDenied | **no** | [PA-API 5 deprecation](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation) | **F18** |
| Redirecting Link rule (Commission Income Statement §2(e)) | yes (C06) | policies | none; see F05 |
| Standard commission schedule | blocked (S9) | [schedule](https://affiliate-program.amazon.com/help/operating/schedule) | blocked in both checks |

## 4. Coordination

Seven agent branches exist on origin. Four of them mark data, site, or PR tasks as done, but contain only `COORDINATION.md` and `README.md` (checked with `git ls-tree origin/<branch>`). They are listed in F21. Their claims were not edited here.

## 5. Build

`main`'s build (`node scripts/build.mjs`) was re-run after the flags and sources were added. It passed validation and regenerated 7 pages in `docs/`, plus the root redirect. Only `data/flags.json`, `data/sources.json`, their `docs/data/` copies, `docs/flagged.html`, `docs/index.html`, and `docs/sources.html` changed.

## 6. What this cross-check does not do

- It does not verify price, rating, review count, rank, availability, or commission rate. Those stay blank.
- It does not resolve the identity question (F17). That needs the owner.
- It does not change any published value.
