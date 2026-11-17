# Session report — arena/5b17c077-zone1 (2026-11-17 UTC)

Task: **I-5b17c077**. Tracking ID, product-intent record, disclosure/sponsored marking,
measurement specification. Branch `arena/5b17c077-zone1`, base `9c6e3f0`.

## What changed, and why each change was made

### 1. The Associates tracking ID is now real, and gated

Before this pass, `data/config.json` had `associate_tag: ""` and the root build never read
the field at all. Every outbound link on the site was therefore an **untagged** Amazon URL:
not a Special Link, and unable to earn. That was flag F-10, which had survived ten passes
because nothing in the build consumed the value.

The owner supplied the ID in the brief: *"Selected Tracking ID: shopnow047c-20"*.

- `data/config.json` → `associate_tag: "shopnow047c-20"`, with `associate_tag_added` and
  `associate_tag_source` recording where the value came from and when.
- `build.py` now loads it, validates the format, and exposes `amazon_product_url(asin)`.
- `tag_and_qualify_amazon_links()` applies the tag and `rel="sponsored"` in **one
  post-render pass**, so a future template edit cannot bypass it. The pass is idempotent
  (an existing `tag=` is replaced, never duplicated) — verified by running it twice.
- `check_associate_tagging()` is a **build failure**, not a warning, if any outbound
  Amazon product link ships without the tag or without `rel="sponsored"`.

**Gate proven to fire.** Checks run in this pass:

| Case | Result |
|---|---|
| Transform on an untagged `/dp/` anchor | adds `?tag=shopnow047c-20` and `rel="sponsored"` |
| Run the transform a second time | byte-identical (idempotent) |
| Untagged link handed to the gate | fails with 2 problems (tag + sponsored) |
| Tag config blanked, then gate run | fails with "no Associates tag configured" |
| Full build with the tag set | passes, all `/dp/` links carry `?tag=shopnow047c-20` |

Sources read live 2026-11-17:
- Program Policies §2(a): "Special Links must use the Associates ID we have assigned to you."
- Program Policies §2(b): "you must include your Associates ID or 'tag' (appearing as
  XXXXX-## …) as a parameter in the URL of each link you place on your Site to an Amazon Site."
- §3(w): no link shortening "in a manner that makes it unclear that you are linking to an
  Amazon Site."
- https://affiliate-program.amazon.com/help/operating/policies

Because §2(b) says *each* link, the citation badges that prove a spec (S16/S28/S29 point at
`/dp/` listing pages) were in scope too, and the post-render pass covers them.

### 2. The product CTA no longer sends readers through an untagged shortener

`product_cta()` pointed at the supplied `link.amazon/…` URL. Two verified reasons to stop:

1. Those short links carry **no `tag=`** — confirmed again this pass by fetching all five.
   An untagged link cannot earn (§2(a)).
2. §3(w) bars shorteners that obscure that the destination is Amazon. A `/dp/<ASIN>` URL
   states the destination in plain sight.

The button now reads "Check the <product> on Amazon" and points at the tagged `/dp/` URL.
The model-identity caveat is **kept**, because it is still true and still unresolved.

### 3. Product-intent confirmation record (new)

`data/intent-record.json` → `intent-record.html`.

The brief asked for a record per submitted link holding the intended ASIN, the official
listing URL, a confirmation date and a source, with the **observed redirect target in a
separate field that is never merged into the intent**. That separation is the whole point:
an intent is what the owner meant, an observation is what a fetch returned, and only a human
can say the two are the same product. Merging them would let an unchecked observation
silently overwrite an intent.

Five rows, one per supplied link. `confirmation_date` is `null` on all five, because no
human has confirmed any of them and no session may fill that in on the owner's behalf.

### 4. Two supplied links had never been examined — and they are a different product category

The brief lists **five** product links. Every earlier pass tracked **three**.
`B0c8moW59` and `B0f3GKalj` appeared in **zero** files in the repository before this pass.

Read live 2026-11-17 with redirects followed:

| Supplied link | Resolves to | Observed product |
|---|---|---|
| `link.amazon/B0c8moW59` | `B0DHZTCNR5` | ThermoMaven digital **meat thermometer** |
| `link.amazon/B0f3GKalj` | `B0DZFD6R9Z` | CHEF iQ Sense wireless **meat thermometer** |

Both are in Amazon's Thermometers & Timers tree, not Air Fryers (node 17659096011) — a
different category from the three air fryers this site covers. The brief names no product
for either link, so the **intended product is recorded as unknown** in IR-04/IR-05. It is
not inferred from the observation. This is published as flag **F-76**; it is an owner
question, not something a session can repair without inventing an intent.

Flag **F-77** records that none of the five supplied URLs carried a tag on 2026-11-17, and
states what was repaired on the site itself versus what stays open.

### 5. Measurement: five events defined, none sending — and no number invented

`data/measurement.json` → `measurement.html`.

The brief asks for a click and conversion counter. Three facts constrain what can honestly
ship, and all three are stated on the page:

1. GitHub Pages serves static files; there is no server in this repository to receive a
   beacon. A "self-hosted analytics endpoint" needs a host the owner controls.
2. The footer states, truthfully today, that the site sets no cookies and runs no analytics.
   Program Policies §3(e) requires that statement to be accurate, so a beacon without a
   simultaneous disclosure update would make the footer false.
3. A counter reporting a number with no endpoint behind it would be an invented value on a
   site that promises every value is sourced.

So the page defines EV-01…EV-05 precisely (what each records, what each **must never**
record), keeps the campaign ledger **empty on purpose**, and lists the three prerequisites
in order. **No count, rate or revenue forecast appears anywhere.** That is the honest form
of "turn on measurement": a specification that cannot be mistaken for data.

## Live verification performed this pass

All reads on 2026-11-17, from the sandbox with `fetch_page`.

| What | Result |
|---|---|
| `link.amazon/B04G1MEwY` | → `/dp/B0CDY277D3`, CHEFMAN 6 Quart Dual Basket. No `tag=`. |
| `link.amazon/B02NbDxp3` | → `/dp/B09B7SB46R`, Emeril Lagasse 26QT French Door. No `tag=`. |
| `link.amazon/B00hJ57DV` | → `/dp/B08DKYBTPH`, Chefman 8 Qt TurboFry. No `tag=`. |
| `link.amazon/B0c8moW59` | → `/dp/B0DHZTCNR5`, ThermoMaven meat thermometer. No `tag=`. **New.** |
| `link.amazon/B0f3GKalj` | → `/dp/B0DZFD6R9Z`, CHEF iQ meat thermometer. No `tag=`. **New.** |
| Program Policies `Updated:` | April 14, 2026 — unchanged. |
| §2(a)/§2(b)/§3(w) quoted text | read verbatim, quoted above. |

## Gates on the final tree

| Gate | Result |
|---|---|
| `python3 build.py` | 52 pages, 51 sitemap URLs, feed 21 items, exit 0, rebuild idempotent |
| `python3 verify.py` | 130 pages, 77 spec rows (75 verified / 2 blank+flagged), 35 sources, 0 errors, 0 external warnings |
| `scripts/ci-check.sh` | 33 tests OK, data audit clean, **8,683 links / 0 broken** |
| Disclosure above the fold | 52/52 root pages — computed position of `.disclosure-bar` precedes `<main>` on every one |
| Outbound `/dp/` links tagged + sponsored | 100% (gate-enforced) |

## Irregularities left open (published, none blocking)

- **F-76** — two supplied links resolve to a different product category; intended product
  unknown. Owner must say what they were meant to be, or drop them.
- **F-77** — none of the five supplied URLs carried a tag. Repaired on this site; the
  supplied URLs themselves are untouched and still untagged, so they should not be reused.
- **F-6 / Q-03** — whether `shopnow047c-20` is the right tag for the account, and whether
  the account is approved, cannot be read from outside Associates Central.
- Unchanged from earlier passes: F-3 (8 Qt temperature conflict), F-15 (fallback redirect
  parameters), F-71 (listing self-contradictions), 2 blank+flagged spec rows.
- **Measurement is specified, not shipped** — blocked on the owner choosing an endpoint
  and approving the §3(e) disclosure update in the same commit.
