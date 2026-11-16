# Executive summary — pass 10 (session `121929a5`), 2026-11-16

**What this is.** The one-page briefing for pass 10 of the Zone1 affiliate project: what this
session verified live, what it wrote, what it corrected, and what still needs the account
holder. The full evidence is in [`reports/verification-2026-11-16-121929a5.md`](reports/verification-2026-11-16-121929a5.md);
the previous briefing is [`EXECUTIVE-SUMMARY-PASS9-42CA97AD.md`](EXECUTIVE-SUMMARY-PASS9-42CA97AD.md).
A same-day independent round 10 by session `c334fb1c` (PR #86) re-read the short links and
gates; this pass widens the coverage and ships content. Neither supersedes the other.

- **Live site:** https://kanlerxz87-cyber.github.io/Zone1/
- **This pass:** branch `arena/121929a5-zone1`, based on `main` at `6dbfa7c` (PR #85 merge)

---

## 1. What changed, in one paragraph

Pass 10 re-read the official sources behind the site's load-bearing rows live (all three
short-link resolutions, two Amazon detail pages directly, all three manufacturer pages, the
Chefman 6 Qt owner's manual, the Associates Operating Agreement and Program Policies, the
commission schedule, and the FTC/eCFR pages), then used the already-verified dataset to write
the five articles the topic queue had planned but nobody had written. It also corrected three
stale status rows that disagreed with the article set, and closed one blank spec row with a
value read from a live official page. All build gates are green.

## 2. Verification findings (nothing published was wrong)

| Finding | Consequence |
|---|---|
| All three `link.amazon` tokens still resolve to the same three ASINs, and every listing title matches the stored record character-for-character | Identity layer re-confirmed on 2026-11-16 |
| `amazon.com/dp/B0CDY277D3` served a bot checkpoint on direct fetch this pass; the same page was readable via the resolver | Recorded as intermittent; no value inferred |
| No Associates `tag=` on any resolved URL (F03/Q-02) | Still open; only the account holder can close it |
| **The Standard Commission Income Statement is now publicly readable** — it was a sign-in wall when flag F02 was written. Table 1 states "Physical Books, Kitchen, Automotive — 4.50%" and "All Other Categories — 4.00%" | Matches the site's candidate rows exactly; the candidate framing stays because the ASIN→category mapping is still only authoritative inside Associates reporting. F02's own row was not edited (another session's record); the commission note in `data/products.json` records today's public read |
| Emeril conflict still live on the brand page: "25 Cooking Pre-sets" in the spec block vs "24 one-touch cooking presets" in the description (F4) | Manual's 24 named presets remain the controlling document |
| Exact Emeril accessories sentence re-confirmed verbatim: "Included are 7 premium accessories to maximize versatility—air fry basket, rotisserie spit, bake pan, and more." | Supports `Included accessories: 7` and the 7-vs-6 local flag (Amazon title says "Six") |
| Chefman brand-page review counters drifted: 1,305→1,307 (6 Qt) and 716→717 (8 Qt) | Normal widget drift; stored rows keep their own access dates; next full re-stamp refreshes them |
| eCFR current as of 11/12/2026; Program Policies "Updated: April 14, 2026" (same date session c334fb1c saw) | Regulatory layer unchanged |

## 3. Content shipped (five articles, no new research needed)

The topic queue had already verified that these five pieces could be written entirely from
published values; pass 10 wrote them. Every highlighted value is a verbatim value from
`data/products.json` (build-enforced), and every manual/policy quote was transcribed from the
live fetches of 2026-11-16.

| Topic ID | Article | What it does |
|---|---|---|
| TP-07 | `articles/whats-in-the-box.html` | 7 accessories vs Amazon's "Six Cooking Accessories Included" vs the manual's own caveat "Some accessories may not be included with purchase" |
| TP-08 | `articles/rotisserie-at-home.html` | What the 26 QT's manual documents about the rotisserie — and the rotisserie numbers it never publishes |
| TP-09 | `articles/sync-finish-two-buttons.html` | Sync Finish vs Sync Baskets, verbatim definitions, and the exact mid-cook actions that break the sync (+2 MIN, HI-FRY, timer edits) |
| TP-10 | `articles/aerosol-oil-warning.html` | The aerosol-oil caution quoted verbatim from the 6 Qt manual, the warranty's "Poor Maintenance" exclusion, and why no listing title repeats it |
| A-9 | `articles/associates-disclosure-explained.html` | OA §5's mandated sentence and breach clause, FTC placement guidance, 16 CFR §255.5, and what the sentence does not permit |

Article set: 12 → 17. Sitemap: 36 → 41 URLs.

## 4. Register corrections (stale statuses, minimal edits, logged)

- `data/topics.json`: TP-04 and TP-11 said `proposed` while their articles were already live
  (`small-kitchen-air-fryer-dimensions`, `energy-cost-of-an-air-fryer`); statuses corrected to
  `published` with links, previous notes preserved in `status_note_prev`.
- `data/design-prompt.json`: A-11 said `not-written` while its article was live — corrected;
  A-9 moved to `published` with the new article.
- Still honestly unwritten: A-8 (Chefman vs Emeril head-to-head) and A-10 ("98% less oil"
  claim check). Nothing claims them.

## 5. Dataset improvement (one blank row closed)

The Emeril row's `Amazon browse node` was blank. Both live fetches of its detail page today
show the official breadcrumb trail `Home & Kitchen > Kitchen & Dining > Small Appliances >
Fryers > Air Fryers` — the same node both Chefman rows carry — so the blank was filled from
S28 with a dated note. Spec rows now read 44 verified / 2 blank-and-flagged (was 43/3).

## 6. What still needs the account holder (unchanged)

1. Confirm the three products are the intended ones (the short-link → ASIN resolution is
   recorded evidence, not a confirmation from the account side).
2. Supply the Associates ID / tag (F03) — no purchase credits without it.
3. Read the commission category assignment for each ASIN in Associates Central (now easier:
   the schedule itself is public).
4. The one executable suggestion that changes revenue fastest is still the handover list on
   `handover.html` — pass 10 did not change it because nothing in it became stale.

## 7. Gates at the end of the pass

| Gate | Result |
|---|---|
| `python3 build.py` | exit 0; 41 sitemap URLs; all article guards (verbatim values, voice rules, disclosure-in-header, no price/rating patterns) enforced |
| `python3 verify.py` | 120 pages, 46 spec rows (44 verified / 2 blank+flagged), 34 sources, 0 errors |
| `bash scripts/ci-check.sh` | OK — 33 unit tests, data audit clean, 6,652 links / 0 broken |
| `python3 research/check_research.py` | OK |
| `python3 scripts/verify_site.py` | 393 assertions, ALL CHECKS PASSED |
| `git diff --check` | clean (a generator fix removed the trailing-whitespace line that empty-product cards emitted; logged) |
