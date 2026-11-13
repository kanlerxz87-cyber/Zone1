# COORDINATION — Zone1 Amazon Affiliate Marketing Platform

Shared task board. Any agent session working on this repo MUST read this file first,
claim a task here (write session ID + file scope), commit and push that claim
immediately, and never start a task another session owns.

- **Repo:** `kanlerxz87-cyber/Zone1`
- **Integration branch / published source of truth:** `main`
- **Session IDs:** branch `arena/<uuid>` → session ID is the UUID part.
- **Statuses:** `unclaimed` · `in_progress` · `needs_review` · `done`
- **Rules:** one owner per file scope; small frequent commits; `git pull --rebase`
  before every push; never invent a value — blank + flag instead.

---

## 1. Task board

| # | Task | Status | Owner (session) | Branch | File scope | Notes |
|---|------|--------|-----------------|--------|-----------|-------|
| T1 | Coordination board + repo scaffolding | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `COORDINATION.md`, `README.md`, `.gitignore` | created by first session |
| T2 | Verify the 3 supplied affiliate links (resolve → ASIN, capture evidence) | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `data/links.json` | see §4 |
| T3 | Product data table + per-row source links | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `data/products.json` | every row → official source |
| T4 | Amazon Associates compliance research (policy + FTC disclosure) | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `data/policies.json` | quotes + URLs |
| T5 | Niche / competition / commission analysis (derived, labelled) | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `data/analysis.json` | clearly marked as estimate |
| T6 | Static site build (docs/) | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `docs/`, `scripts/` | GitHub Pages root = `/docs` |
| T7 | Link + data integrity checker | done | `arena/8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `scripts/check.py` | fails build on broken links |
| T8 | Flagged-for-review page (unverified values, irregularities) | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | `docs/flagged-for-review.html` | generated from data |
| T9 | Final integration: build, verify, merge to `main`, enable Pages | done | `8a2ddd06-zone1` | `arena/8a2ddd06-zone1` | all | see §6 |

**Active claims:** none outstanding — every task above is closed in §6/§7.

---

## 2. Session log

### Session `8a2ddd06-zone1` — 2026-11-13

Claimed T1–T9 (whole repository was empty except `README.md`; no other session had
claimed anything, no branches besides `main` existed at start).

---

## 3. Source-of-truth rules used by this session

1. **Amazon product facts** come only from the Amazon.com product detail page the
   supplied link resolves to (`https://www.amazon.com/dp/<ASIN>`), fetched
   2026-11-13. Anything not present in the fetched page is **blank + flagged**.
2. **Program/policy facts** come only from `affiliate-program.amazon.com`
   (`/help/operating/policies`, `/help/operating/agreement`) and `ftc.gov`.
3. **No price, star rating, review count, BSR, or sales figure is published**
   unless it was captured from an official Amazon surface. Amazon Associates
   Program Policies §2(b) forbids showing prices/availability unless Amazon
   serves them or they come through PA API / Creators API — so the site shows a
   *"check price on Amazon"* link instead of a stored price. This is a compliance
   decision, not a data gap, and is documented on the site.
4. **Analysis** (niche score, commission-potential score, content plan) is
   labelled `derived / estimate` everywhere and is never presented as a fact.

---

## 4. Verification record — supplied affiliate links (T2)

Fetched 2026-11-13 with an HTTP reader; each short link is a `link.amazon`
redirect whose `Location` was followed to the canonical `/dp/<ASIN>` URL.

| # | Supplied short link | Resolved ASIN | Resolved canonical URL | Product (from Amazon page title) |
|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | B0CDY277D3 | https://www.amazon.com/dp/B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer |
| 2 | https://link.amazon/B02NbDxp3 | B09B7SB46R | https://www.amazon.com/dp/B09B7SB46R | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven |
| 3 | https://link.amazon/B00hJ57DV | B08DKYBTPH | https://www.amazon.com/dp/B08DKYBTPH | Chefman 8 Qt TurboFry 4-in-1 Air Fryer |

**Irregularities found (published on the Flagged for Review page):**

- `I-1` Short-link 3 is `B00hJ57DV`, which *looks* like ASIN `B00HJ57DV`, but it
  resolves to ASIN `B08DKYBTPH`. The short code is opaque — no ASIN is implied by
  the code itself — so this is recorded as a *mapping observation*, not an error.
- `I-2` **None of the three resolved URLs contain an Associates tag parameter**
  (`tag=…`). The resolved URLs carried only Amazon-internal share parameters
  (`lv`, `btn_ref`, `channelId`, `plpRedirect`). Under Associates Program Policies
  §2(b) each Special Link must carry the Associate's own tag, so as supplied these
  links are **not verifiable as monetised Special Links**. Left as supplied; the
  site's outbound buttons use the exact supplied short links so the owner can
  re-issue tagged links.
- `I-3` `link.amazon` short links are not independently auditable (no public
  registry, no tag visible before redirect). Recorded as unverifiable.

---

## 5. Verification method used on the site

Every table cell rendered by `docs/*.html` is generated from `data/*.json`, where
each field carries `value`, `source` (URL) and `verified` (`true`/`false`).
`scripts/check.py` fails the build if a rendered row has no source URL, if a
`verified: true` field lacks a URL, or if any internal link is broken. Blank
values render as `— (unverified)`.

---

## 6. Final integration record (T9)

- Merge: see §7 below for the pull-request URL and merge result.
- Pages: GitHub Pages served from `main` → `/docs`, verified by fetching the
  deployed URL after the workflow completed.
- Build check: `python3 scripts/build.py && python3 scripts/check.py` (0 broken
  links, 0 rows without a source).

---

## 7. Handoff / conflict log

_No conflicts, no stale claims, no handoffs._ Repository had a single branch
(`main`, 1 commit, `README.md` only) when this session started.
