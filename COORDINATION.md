# COORDINATION.md — Shared Task Board

**Repo:** `kanlerxz87-cyber/Zone1`
**This session:** `session-arena-3740f69d`
**Session branch:** `arena/3740f69d-zone1` (branched from `main` @ `42f403657fd1b6b1e0af6fcd3f67ca74b7f0ec06`)
**Session started:** 2026-11-13 (UTC)

> NOTE ON BRANCHING: The Arena session for this board entry is pinned to the branch
> `arena/3740f69d-zone1` and works all tasks on that branch (the session cannot create or
> switch branches). The `session-<id>/<task>` branch naming convention is recorded here for
> other sessions; this session's integration branch is `arena/3740f69d-zone1`, which will be
> PR'd to `main` at the end.

## Task list

| ID  | Task | Status | Owner | Files touched | Notes |
|-----|------|--------|-------|---------------|-------|
| T1  | Repo review & baseline | done | session-arena-3740f69d | COORDINATION.md, README.md | Repo contained only README.md ("# Zone1"). No irregular code. Baseline = 42f4036. |
| T2  | Source research & line-by-line verification (Amazon + FTC official sources) | done | session-arena-3740f69d | data/sources.json, docs/SOURCES.md | See "Verification log" below. Every published value traces to an official URL. |
| T3  | Product registry + analysis tables (products, pricing/reviews/competition/commission, niches) | done | session-arena-3740f69d | data/products.json, docs/EXECUTIVE_SUMMARY.md, site/products/, site/analysis/, site/niches/ | Unverifiable values left blank and flagged. See Flagged items. |
| T4  | Platform & automation design (research pipeline, SEO content, link mgmt, tracking, optimization) | done | session-arena-3740f69d | site/platform/, site/content/, site/links/, site/tracking/ | Compliance constraints (PR §2(y), §6(t), IP License §2(e), Agent Terms) baked into design. |
| T5  | Compliance documentation (Amazon Associates OA/Policies + FTC) | done | session-arena-3740f69d | site/compliance/ | Exact required disclosure text (OA §5) captured and used on every page. |
| T6  | Site build (GitHub Pages dashboard, tables, nav, Flagged page) | done | session-arena-3740f69d | site/** | Static HTML/CSS. All rows carry source links. |
| T7  | Final integration: re-verify combined data, link check, PR → main, enable GitHub Pages | in progress | session-arena-3740f69d | (all) | See "Integration record" below. |

## Conventions (all sessions)

- **Never** publish a value without a link to an official source (amazon.com, affiliate-program.amazon.com,
  webservices.amazon.com, kdp.amazon.com, ftc.gov, ecfr.gov). If unverifiable → leave **blank** and flag it.
- Status meanings: `unclaimed` / `in progress` / `done` / `needs review`.
- `needs review` items are published on the site's **Flagged for Review** page and block nothing.
- Small, frequent commits. `git pull --rebase` before every push.
- Log here: sources used, verification performed, irregularities found.

## Verification log

All verification performed 2026-11-13 → see docs/SOURCES.md for the full source register.
Summary (details and URLs in the site + docs/SOURCES.md):

1. Provided product links (`link.amazon/B04G1MEwY`, `link.amazon/B02NbDxp3`, `link.amazon/B00hJ57DV`)
   resolved **stably** (2× cache-busted fetches each) to amazon.com product pages
   B0CDY277D3, B09B7SB46R, B08DKYBTPH — all air fryers (Home & Kitchen › Small Appliances › Fryers › Air Fryers).
2. Provided IDs are **9 characters**; ASINs are **10 characters** (PA API 5.0 docs `get-items.html`;
   KDP help G200652190). `amazon.com/dp/<provided-ID>` returns "Page Not Found" (verified for all three IDs).
3. Amazon Associates Operating Agreement (updated 2025-10-15) and Program Policies (updated 2026-04-14)
   read in full from affiliate-program.amazon.com. Required disclosure text (OA §5) captured verbatim.
4. Standard Commission Income rate table is **account-gated**: `/help/operating/schedule` redirects to
   sign-in (`home/account/payment/customratecard`). Commission rates left BLANK + flagged.
5. FTC "Disclosures 101 for Social Media Influencers" (ftc.gov) verified and cited.

## Flagged items (needs review — published on Flagged page)

| ID | Item | Why flagged | Status |
|----|------|-------------|--------|
| F1 | Provided IDs `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV` | Not valid ASIN format (9 chars vs 10, mixed case); amazon.com/dp lookup 404s. Resolved only via `link.amazon` short-link redirects. | needs review |
| F2 | `link.amazon` domain provenance | Not documented among Amazon's published short-link domains (a.co, amzn.to, amzn.com). Redirects are stable and land on amazon.com, but owner/provenance unconfirmed. | needs review |
| F3 | ID→product mapping | Resolved ASINs ≠ provided IDs (expected for short links, but mapping origin unverifiable). Marketing targets the **observed** stable targets; confirm these are the intended products. | needs review |
| F4 | Commission rates | Official rate table requires Associates sign-in; rate card appears account-specific. Not guessed. | needs review |
| F5 | Price / star-rating / review-count values | Not republished: Participation Requirements §2(b) (prices) and §6(t) (reviews/ratings) restrict display to data served by Amazon or obtained via PA API/Creators API. Obtain via PA API after account approval. | needs review |
| F6 | Product PDP deep specs (wattage, dimensions) | PDP fetches intermittently served stripped/anti-bot pages; only listing-title-level attributes recorded. | needs review |

## Integration record

_(filled in by the final integration session — T7)_

- PR: (see below)
- Merge result: (see below)
- GitHub Pages deployment: (see below)

## Handoff / conflicts log

- 2026-11-13 session-arena-3740f69d: no other session claims found; board created. No conflicts.
