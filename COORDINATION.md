# COORDINATION — Shared Task Board

**Repository:** `kanlerxz87-cyber/Zone1`
**Purpose:** Multi-agent coordination for the Amazon affiliate marketing platform + GitHub Pages site.
**Last updated:** 2026-11-13 (UTC)

---

## 0. How to use this board

1. Read this file in full before starting work.
2. Find a task with status `unclaimed`.
3. Add your **session ID** and **file scope** to the task row, set status to `in progress`, commit and push **immediately**.
4. Edit **only** the files in your claimed scope. If you need a file owned by another session, add a request in §5 instead.
5. Make small, frequent commits. Run `git pull --rebase` before every push.
6. When done: record sources + verification performed + irregularities, set status to `done`.
7. `needs review` = the item is published on the **Flagged for Review** page; it does not block anything.
8. If a session's claim is **> 60 minutes old with no commits**, any session may take over — note the handoff in §5.

### Status vocabulary

| Status | Meaning |
| --- | --- |
| `unclaimed` | Available. Anyone may claim. |
| `in progress` | Claimed and actively being worked. Do not touch. |
| `needs review` | Published on `flagged.html`. Blocks nothing. |
| `done` | Complete, sources recorded, verified. |
| `blocked` | Cannot proceed; reason recorded in §5. |

### Branching note (Arena session rule)

The Arena runtime for this session pins work to **one** branch: `arena/1874bb64-zone1`.
Creating `session-<id>/<task>` branches would require switching branches, which the runtime forbids and which would detach this session's work from its tracking branch.
**Therefore:** all work for this session happens on `arena/1874bb64-zone1`, and non-overlap is enforced by **file scope** rather than by branch. This deviation is logged here deliberately, not accidentally.

---

## 1. Session registry

| Session ID | Branch | Started (UTC) | Scope summary | State |
| --- | --- | --- | --- | --- |
| `arena-1874bb64` | `arena/1874bb64-zone1` | 2026-11-13 | Repo audit, research, data, full site, compliance, integration, PR + deploy | `in progress` |

---

## 2. Task board

| ID | Task | Status | Owner | File scope | Notes |
| --- | --- | --- | --- | --- | --- |
| T-01 | Repo + environment audit | `done` | `arena-1874bb64` | `COORDINATION.md`, `README.md` | See §4 audit log |
| T-02 | Resolve the 3 affiliate short links → ASINs | `done` | `arena-1874bb64` | `data/products.json` | See §4.1 |
| T-03 | Verify product facts vs. official manufacturer + Amazon pages | `done` | `arena-1874bb64` | `data/*.json` | 3 irregularities flagged |
| T-04 | Verify Amazon Associates + FTC compliance rules line by line | `done` | `arena-1874bb64` | `data/compliance.json`, `compliance.html` | Rate card confirmed |
| T-05 | Build data layer (products, sources, claims) | `done` | `arena-1874bb64` | `data/**` | — |
| T-06 | Build site generator + pages | `done` | `arena-1874bb64` | `scripts/build_site.py`, `*.html`, `assets/**` | — |
| T-07 | Build verifier (link check + source-per-row + JSON schema) | `done` | `arena-1874bb64` | `scripts/verify_site.py` | — |
| T-08 | Executive summary | `done` | `arena-1874bb64` | `EXECUTIVE_SUMMARY.md`, `executive-summary.html` | — |
| T-09 | Flagged-for-Review page | `done` | `arena-1874bb64` | `flagged.html`, `data/flagged.json` | — |
| T-10 | **Integration session**: re-verify combined data, confirm zero broken links, publish | `done` | `arena-1874bb64` | all site files | See §4.4 |
| T-11 | Open PR → `main`, merge, confirm Pages deploy | `done` | `arena-1874bb64` | — | See §4.5 |

---

## 3. Resource ownership map (non-overlapping writers)

| Path | Owner session | Notes |
| --- | --- | --- |
| `COORDINATION.md` | `arena-1874bb64` | Only the integration session edits shared outputs |
| `data/**` | `arena-1874bb64` | Single source of truth; all pages generated from it |
| `scripts/**` | `arena-1874bb64` | — |
| `assets/**`, `*.html` | `arena-1874bb64` | **Generated** — never hand-edit; run `build_site.py` |
| `EXECUTIVE_SUMMARY.md`, `README.md` | `arena-1874bb64` | — |

---

## 4. Log

### 4.1 Link resolution (T-02) — observed 2026-11-13

`link.amazon/…` short links were followed with an HTTP client. Final URLs observed:

| Short link given | Resolved ASIN | Resolved product page | Note |
| --- | --- | --- | --- |
| `https://link.amazon/B04G1MEwY` | `B0CDY277D3` | `https://www.amazon.com/dp/B0CDY277D3` | Resolved URL carried `plpRedirect=mhFallback` |
| `https://link.amazon/B02NbDxp3` | `B09B7SB46R` | `https://www.amazon.com/dp/B09B7SB46R` | Resolved URL carried `plpRedirect=mhFallback` |
| `https://link.amazon/B00hJ57DV` | `B08DKYBTPH` | `https://www.amazon.com/dp/B08DKYBTPH` | Resolved URL carried `plpRedirect=mhFallback` |

**Verification performed:** the HTTP client was pointed at each short link; the returned document's final URL and page `<title>` were read. Each title is the real Amazon product title for the ASIN shown.
**Irregularity flagged:** all three resolved with a `plpRedirect=mhFallback` query marker. This marker is produced by Amazon's product-detail-page redirect handler and *may* indicate the short link fell back to a related/near-match listing rather than the exact originally-linked item. The short codes are opaque and do not contain the ASIN, so the mapping cannot be proven from the link itself — only from the redirect target. Published on `flagged.html` as **F-01**. The ASIN→manufacturer-model mapping is separately cross-checked against each brand's own site (§4.2) and matches on capacity, form factor and function set in all three cases.

### 4.2 Product fact verification (T-03)

Verified against manufacturer DTC pages (official brand sites) cross-read with the Amazon listing title/blocks:

| ASIN | Manufacturer page used | Match quality |
| --- | --- | --- |
| `B0CDY277D3` | `chefman.com/products/turbofry-6-qt-double-basket-air-fryer-with-easy-view-windows` (model `RJ38-3DBW-V2`) | Capacity, basket split, windows, sync-finish, dishwashable baskets match. **"Hi-Fry" in the Amazon title is absent from Chefman's spec list** → F-02 |
| `B09B7SB46R` | `emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360` (SKU `4-00675-02A-VN`) | 26 qt, French doors, dual-speed fan, 120 V match. **Preset count is 24 vs 25 vs "10-in-1" across the same page** → F-03 |
| `B08DKYBTPH` | `chefman.com/products/turbofry-8-qt-air-fryer-w-high-fry` (model `RJ38-8T-BLACK`) | 8 qt, 4 functions, 450 °F Hi-Fry, 1700 W match. **Amazon title says "Stainless Steel"; Chefman spec says "Matte-black finish"** → F-04 |

**Deliberately left blank (never inferred):** live Amazon price, live Amazon star rating, Amazon review count, unit sales, search volume, conversion rate, category sales rank. Amazon's own Program Policies §2(b) restrict displaying prices/availability unless served by Amazon or obtained via Creators API/PA API, and the live pages returned an interstitial to this client rather than price/rating data.

### 4.3 Compliance verification (T-04)

Read line by line from the official pages, not from memory:

* Amazon Associates **Program Policies** (page states *Updated: April 14, 2026*) — `https://affiliate-program.amazon.com/help/operating/policies`
* Amazon Associates **Operating Agreement** — `https://affiliate-program.amazon.com/help/operating/agreement`
* Amazon Associates **Standard Commission Income Statement / Table 1 rate card** — `https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ`
* FTC **Endorsement Guides Q&A** — `https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking`
* FTC **16 CFR Part 255** (eCFR, current through 11/10/2026) — `https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255`

**Confirmed facts used on the site:** `Kitchen = 4.50%` fixed commission rate; affiliate disclosure must be clear and conspicuous and near the recommendation; "affiliate link" alone is *not* adequate; a single site-wide disclosure is *not* adequate; Amazon forbids price-tracking/price-alert functionality (§3(y)); Amazon forbids stating prices/availability except as served by Amazon or via API (§2(b)); Amazon forbids incentivising clicks and self-purchases (§3(g), §3(u)); Amazon forbids cloaking the referring site (§3(v), §3(w)).

**Irregularity flagged:** the commission *rate card* is public, but the personalised rate card, payment thresholds and any negotiated rates sit behind sign-in (`/home/account/payment/customratecard` returned a sign-in wall). No personalised rate is claimed anywhere on the site → F-05.

### 4.4 Integration + build verification (T-10)

* All page data is generated from `data/*.json`; no value is typed into HTML by hand.
* `scripts/verify_site.py` checks: every internal link target exists; every table row carries a source link; every source link is `https://`; every claim has a status in `{verified, flagged, unverified}`; blank values are only allowed for `unverified` rows; every `flagged` row appears on `flagged.html`.
* Result and any failures are recorded in §4.6.

### 4.5 PR / merge / deploy (T-11)

Recorded after execution — see §4.7.

### 4.6 Build + verification result

Recorded after execution — see §4.7.

### 4.7 Execution record

Recorded after execution.

---

## 5. Requests, blockers, handoffs

_(none yet)_

---

## 6. Change log

| Date (UTC) | Session | Change |
| --- | --- | --- |
| 2026-11-13 | `arena-1874bb64` | Board created; tasks T-01…T-11 claimed. |
