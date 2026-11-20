# Executive summary — pass W-abbb9745, 20 November 2026

**Publication:** https://kanlerxz87-cyber.github.io/Zone1/ · **Session:** `arena/abbb9745-zone1`
**Full evidence:** [`reports/verification-2026-11-20-abbb9745.md`](reports/verification-2026-11-20-abbb9745.md)

---

## The one-paragraph version

The site is a documented, affiliate-funded kitchen buying publication covering three air-fryer formats and
two supplied thermometers. This pass made two reader-visible improvements — sources are now cited by name
("Chefman RJ38-SQSS-8T guide") instead of by register number, and every page's search-result title and
description now fit the space a search engine actually shows — and it put the most consequential
compliance question of the whole project into print with the official quotations beside it (**F109**).
Nothing about the products, prices, tracking ID or campaign data changed, because none of those can be
closed from inside the sandbox: they need your decisions or your Associates account.

---

## What was verified today (20 Nov 2026), not assumed

| Verified | Result |
|---|---|
| All five supplied `link.amazon` links | Each resolved to the ASIN the register already records, with a matching product title. No `tag=` parameter was visible in any final URL |
| Associates Operating Agreement §1 | Live; "Updated: October 15, 2025"; links must use the "special tagged link formats" to be Special Links |
| Program Policies §2(a), §2(b), Commission Income Statement §2(e) | Live; tag required as a URL parameter; Special Links "accessed directly from your Site"; "Redirecting Link" purchases disqualified |
| FTC Disclosures 101 | Live; disclosure must be hard to miss, with the endorsement, in plain language |
| Chefman 6 Qt dual-window page | Capacity 6 Qt / 5.67 L; **13.38 × 11.81 × 10.63 in**; 1700 W/120 V; 450 °F Hi-Fry — the published values match the page |
| USDA FSIS temperature chart | 145 °F + 3 min rest / 160 °F ground / 165 °F poultry, leftovers, casseroles — matches the thermometer pages |
| Repository and deployment state | `main` @ `1c7de82`; GitHub Pages `status=built`, `https_enforced=true`; nine pull requests open, seven of them from earlier sessions (F108) |

**Not verified today:** the other 43 registered sources, including the Emeril page and manual, both Chefman
8 Qt pages and both thermometer brand sites. Their published values keep the date of the pass that read
them. This report says so rather than implying a full re-read.

---

## What changed on the site

1. **Buyer-facing sources read like citations, not audit codes.** The front page went from 22 tiny `S10`
   badges to one "From the documents:" line per product card; article sections now say
   "Chefman RJ38-SQSS-8T guide". The register id is still on every link in `data-src-id`, and `verify.py`
   still checks that each id points at its registered URL — proven with a deliberate wrong-URL test.
2. **Search-result metadata fits.** 13 titles and 10 descriptions were over display length (one title at
   133 characters). The build now composes the `<head>` within budget, `verify.py` fails on regression,
   and a unit test pins it. Reader headlines are untouched.
3. **Two registers updated, with sources.** **C20** on the compliance page and **F109** on Flagged for
   Review carry the tag/redirect quotation; **F107** records the metadata repair; **F108** records the
   stale pull-request backlog.

---

## What needs your decision (nothing below can be resolved by an agent)

1. **Which listing did you mean, for each of the five links?** The register stores the *observed* ASIN and
   the *intended* ASIN as separate fields; the intended field is blank because only you can fill it. Until
   it is filled, every page correctly says "check the exact model".
   → [product-intent.html](product-intent.html)
2. **Is `shopnow047c-20` the tracking ID enrolled on the account?** It is recorded and deliberately applied
   to no link. A wrong tag earns nothing; an unverified tag cannot be tested.
   → [S6 tracking IDs](https://affiliate-program.amazon.com/help/node/topic/GJDYPQZK6E37RLPU) ·
   [S42 multiple IDs](https://affiliate-program.amazon.com/help/node/topic/GF4RJEQ)
3. **Run the one-link test in Associates Central** (SG-02/SG-37): generate one tagged Special Link per
   product, click it, and confirm the destination *and* the click report. This is the single act that
   closes F109, the intended-listing question and the attribution question at once. Until it is done, the
   site keeps the honest "check model" call to action rather than a "buy now" it cannot back.
4. **Decide the measurement gate.** Production analytics is off by design; the client, collector and the
   five events are built and tested. Turning it on needs a same-origin endpoint and a privacy decision
   that belongs to you, not to a session. → [measurement.html](measurement.html)
5. **Decide the pull-request backlog (F108).** Seven older branches carry partly-superseded work. A later
   integration session can diff and salvage them; that instruction has to come from you.
   → [flagged.html](flagged.html)

---

## What is still unknown, stated plainly

- Whether the supplied links carry an Associates tag server-side (it is not visible in the final URL).
- Whether `link.amazon` redirects are treated as "Redirecting Links" for commission purposes — the policy
  text is quoted in F109 and the question is left open rather than guessed.
- Whether any search engine has indexed the annex trees, or whether the canonical shop ranks for anything.
- Whether anyone arrives at all: the campaign ledger is empty and no traffic figure exists.
- Whether the Emeril preset count is 24 or 25, and the 8 Qt wattage (the listing itself says both 1000 W
  and 1700 W) — both stay blank and flagged rather than being resolved by preference.

---

## Where to look

- **Shop:** [home](index.html) · [air fryers](categories/kitchen-appliances.html) ·
  [thermometers](categories/cooking-thermometers.html) · [buying guides](articles/index.html) ·
  [compare](compare.html)
- **Decisions:** [suggestions & current decisions](suggestions.html) ·
  [questions and information gaps](questions.html) · [decision review queue](decision-review.html)
- **Evidence:** [source register](data.html) · [compliance](compliance.html) ·
  [flagged for review](flagged.html) · [verification history](reverification.html)
