# Air Fryer Affiliate Intelligence — Zone1

A static, source-verified Amazon Associates property covering three air fryers, plus the
compliance and verification machinery behind it.

**Live site:** https://kanlerxz87-cyber.github.io/Zone1/

---

## The rule this repo is built on

> Every factual cell on the site links to the official page it was read from. Anything that
> could not be confirmed from an official source is left **blank** and published as unverified.

That rule is not documentation — it is enforced in code. `scripts/verify_site.py` fails the
build if a populated value has no source, if an unverified row has a value, if an internal link
is broken, or if an Amazon price or rating is published.

## What is here

| Path | What it is |
| --- | --- |
| `data/sources.json` | Registry of the 16 official documents used, with what each verifies |
| `data/products.json` | The three products, 53 spec fields, every field carrying a status and a source |
| `data/compliance.json` | 20 Amazon Associates / FTC requirements, each with the operative quote |
| `data/flagged.json` | 13 irregularities and open items, each with evidence and a settling test |
| `data/opportunities.json` | Fit scoring where the weights and inputs are both published |
| `data/config.json` | Site config and the **Associates tag injection point** |
| `scripts/build_site.py` | Generates every HTML page from `data/*.json` |
| `scripts/verify_site.py` | 371 assertions; fails on any unsourced value or broken link |
| `*.html` | **Generated.** Do not hand-edit — run the build |

## Build and verify

```bash
python3 scripts/build_site.py    # regenerate every page from data/
python3 scripts/verify_site.py   # assert the guarantees
```

No dependencies. Python 3.9+.

## The one action that switches on revenue

No Amazon Associates tag is configured, so **no link on the site can currently earn**.
Set it and rebuild:

```json
// data/config.json
{ "associate_tag": "yourtag-20" }
```

```bash
python3 scripts/build_site.py && python3 scripts/verify_site.py
```

The build validates the tag format and refuses to emit a malformed one. Until then every page
displays a visible warning. Tracked as [F-10](https://kanlerxz87-cyber.github.io/Zone1/flagged.html#F-10).

## What is deliberately not built

These are excluded because Amazon's Associates Program Policies prohibit them, not because they
were overlooked:

- **Price tracking and price-drop alerts** — participation requirements §3(y)
- **Amazon prices, availability and star ratings** — §2(b) and §3(t) restrict these to
  Creators API / PA API-served data. Every such cell on this site is blank.
- **Cloaked or shortened outbound links** — §3(v). Every link prints its full
  `amazon.com/dp/<ASIN>` destination.
- **Click incentives, rebates or loyalty points** — §3(g)
- **Amazon logos or brand imagery** — Trademark Guidelines; brand names appear as plain text only
- **Third-party analytics, cookies or pixels** — none present, so the privacy page can make a
  clean claim

## Products covered

| ASIN | Product | Manufacturer model | Capacity |
| --- | --- | --- | --- |
| `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven | `RJ38-3DBW-V2` | 6 Qt (2 × 3 Qt) |
| `B09B7SB46R` | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven | `4-00675-02A-VN` | 26 Qt / 24.6 L |
| `B08DKYBTPH` | Chefman Air Fryer 8 Qt TurboFry 4-in-1 | `RJ38-8T-BLACK` | 8 Qt / 7.57 L |

All three fall in Amazon's **Kitchen** category, published standard rate **4.50%**
([Amazon rate card](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)).

## Disclosure

As an Amazon Associate I earn from qualifying purchases.

I get commissions for purchases made through links on this site. This site is not endorsed by,
sponsored by, or affiliated with Amazon or with any brand named here.

## Coordination

Multi-session task board and audit log: [`COORDINATION.md`](COORDINATION.md).
