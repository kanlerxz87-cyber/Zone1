# Zone1 — Amazon Affiliate Property

A static, source-verified Amazon Associates property covering three air fryers.

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/

---

## Two builds live in this repository

Two agent sessions worked this brief independently. Rather than overwrite one with the other, both
are published in **non-overlapping directories** with separate data sets and separate build scripts.

| | Build A | Build B |
| --- | --- | --- |
| Session | `d14c5409` | `1874bb64` |
| Published at | [`docs/`](docs/index.html) — answers the **root** Pages URL | [`site/`](site/index.html) |
| Build command | `node scripts/build.mjs` | `python3 scripts/build_site.py` |
| Verify command | `node scripts/build.mjs --check` | `python3 scripts/verify_site.py` |
| Data | `data/*.json` | `data/verified/*.json` |
| Scope | Repo review, product titles, 11 compliance rows, category site | 53 manufacturer spec fields, published rate card, 20 compliance rows, 17 flags |
| Fields verified | 18/30 (60%) | 40/53 (75%) |

Both builds independently resolved the same three ASINs from the same three short links — a useful
cross-check. Neither overwrote the other. See [`COORDINATION.md`](COORDINATION.md) for the full
reconciliation and **F-16** for the open decision about which site should be canonical.

## The rule both builds follow

> Every factual value links to the official page it was read from. Anything that could not be
> confirmed from an official source is left **blank** and published as unverified.

Build B enforces this in code: `scripts/verify_site.py` fails on an unsourced value, a blank
`verified` row, a populated `unverified` row, a broken internal link, or a published Amazon price.

## The one action that switches on revenue

**No Amazon Associates tag is configured, so no link on either site can currently earn.** Amazon
requires the tag as a URL parameter on every Special Link.

Build B reads it from `data/verified/config.json`:

```json
{ "associate_tag": "yourtag-20" }
```

```bash
python3 scripts/build_site.py && python3 scripts/verify_site.py
```

The build validates the tag format and refuses to emit a malformed one. Until it is set, every page
shows a visible warning. Tracked as **F-10**.

## Products covered

| Given short link | ASIN | Product | Manufacturer model | Capacity |
| --- | --- | --- | --- | --- |
| `link.amazon/B04G1MEwY` | `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven | `RJ38-3DBW-V2` | 6 Qt (2 × 3 Qt) |
| `link.amazon/B02NbDxp3` | `B09B7SB46R` | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | `4-00675-02A-VN` | 26 Qt / 24.6 L |
| `link.amazon/B00hJ57DV` | `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 | `RJ38-8T-BLACK` | 8 Qt / 7.57 L |

All three are in Amazon's **Kitchen** category → published standard rate **4.50%**
([Amazon rate card](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)).
That is the public table rate; the account-specific card is behind sign-in and is not claimed.

## Deliberately not built (Amazon prohibits it)

- **Price tracking / price-drop alerts** — Program Policies §3(y)
- **Amazon prices, availability, star ratings** — §2(b) and §3(t) restrict these to Creators API /
  PA API-served data. Every such cell on `site/` is blank and flagged **F-08**.
- **Cloaked or shortened outbound links** — §3(v). Every link prints its full `amazon.com/dp/<ASIN>`.
- **Click incentives, rebates, loyalty points** — §3(g)
- **Amazon logos or brand imagery** — Trademark Guidelines; brand names are plain text only
- **Third-party analytics, cookies, pixels** — none present on `site/`

## Repository map

| Path | Owner | What it is |
| --- | --- | --- |
| `docs/**` | build A | Published site A (GitHub Pages, `main /`) |
| `data/*.json` | build A | Build A data |
| `scripts/build.mjs` | build A | Build A generator + validator |
| `site/**` | build B | Published site B (generated — do not hand-edit) |
| `data/verified/**` | build B | Build B data: sources, products, compliance, flags, opportunities |
| `scripts/build_site.py` | build B | Build B generator |
| `scripts/verify_site.py` | build B | 381 assertions |
| `.github/workflows/verify.yml` | shared | CI: rebuilds build B from data and re-verifies on every push |
| `EXECUTIVE_SUMMARY.md` | shared | Combined executive summary |
| `COORDINATION.md` | shared | Task board and reconciliation log |
| `REVIEW.md` | build A | Build A repo audit |

## Disclosure

As an Amazon Associate I earn from qualifying purchases.

I get commissions for purchases made through links on this site. This site is not endorsed by,
sponsored by, or affiliated with Amazon or with any brand named here.
