# pass 13 — superseded draft work, kept as evidence (2026-11-17)

These are the artefacts of this session's **first** pass over the tree, written against base
`9c6e3f0`. While they were being built, six parallel PRs merged to `main` (#125, #127, #128, #130,
#131, #134) and two integration sessions published overlapping layers on paths this pass had chosen
for itself. The merged tree, not this draft, is canonical. Nothing here is published or read by the
build; `../pass13-original.patch` is the complete diff of the draft against its base.

| Draft | What main did instead, and what survived |
|---|---|
| `data/measurement.json` | `arena/5b17c077` published its own register at the same path with its own five-event dictionary (EV-01 `page_view` … EV-05 `reported_order`) and `status: defined_not_shipped`, plus `data/campaign-ledger.json`. **Their file wins; this one is dropped.** What survived of this layer is the collector itself — see the `collector` block added to their register and flag F83. |
| `links.html` + the schema-v2 rewrite of `data/product-intent-confirmations.json` | The intent record is `data/product-intent.json` → `product-intent.html`, consolidated by the integration session, which **retired** `product-intent-confirmations.json` (kept on disk as a dated artefact). A second register page would have been the duplicate this repository flags as F59-class. **Dropped**; the two facts this pass alone carried were moved onto the canonical page as F83/F84. |
| programme flags F76–F80 | `main` took **F76–F82** first (five-link divergence, unknown intent, the three-record consolidation). This pass's ids are therefore vacated, and its remaining findings are recorded as **F83/F84** with the collision named rather than renumbered silently. |
| `check_special_link_gate()` (refuse to emit a tagged link until the ID is confirmed) | The integration session reached the opposite conclusion and *wired* the tag: `data/config.json → associate_tag`, `check_associate_tagging()`, and every outbound link now points at a tagged canonical `/dp/` URL. Their approach is published and defensible; this pass does not revert a merged decision. What it adds is the half neither side could check from outside the account — the report-row confirmation (Q-28) and the S40 sub-tag mechanics. |
| `check_submitted_link_count()` and the "three supplied links" prose repair | Kept, re-pointed at main's register: main's landing-page note still says "all three supplied short links" while its own F76 and `data/product-intent.json` carry five. |
| brand-page reads (chefiq.com, thermomaven.com) and the two tracking-ID help nodes | **Kept in full** — main has the two `/dp/` listings (S36/S37) but not the brand catalogues, and nobody on main had read S40/S41. Now sources S38–S41. |

## Second re-scope (onto `4609ff3`) — what else was withdrawn, and why

Between the first re-scope and opening the PR, ten more PRs merged. `arena/c55fa0d8`'s "Integrate buyer-first brief and disabled measurement plan" reversed the
tracking-ID decision (`data/config.json → associate_tag` blank by contract, `analytics/collector.py` a
fail-closed service GitHub Pages does not run, `tests/test_build_contract.py` enforcing that browser
collection stays off), main renumbered its flags to F76–F79, registered S36–S38 and published its own
`TP-21`. That made three more pieces of this draft redundant, withdrawn rather than merged:

| Draft piece | Status after the second re-scope |
|---|---|
| The cookieless browser counter in `assets/app.js`, its `.tally` CSS, the `measurement.html` collector block and per-event wiring lines, and the footer §3(e) rewrite | **Withdrawn as a unilateral change.** It would have made main's footer sentence — "browser collection remains disabled" — false, against a decision merged with a test behind it. Offered instead as **SG-38** path C, with the reason it was not taken stated on the row. The code survives here (`pass13-original.patch`, and the earlier report draft in this folder) if the owner chooses C. |
| `data/measurement.json` status flip to `defined_and_wired_locally…` and its `collector` block | Withdrawn with the counter; main's `defined_not_shipped` is the accurate state of the merged tree. |
| Flags F83–F86 (first numbering) → F83–F86 (second attempt) | Renumbered to **F80–F82**; the fourth finding (the count repair) kept, the measurement-status flag dropped with the counter it described. |
| Sources S38–S41 | Renumbered to **S39–S42**, because main had taken S38 for its GitHub Pages reference. |
| Topics TP-21/TP-22 | Renumbered to **TP-22/TP-23**; main's TP-21 (66c32067) is a different guide, and this pass did not renumber anyone else's row. |
| `check_special_link_gate()` | Dropped for the second time: main's equivalent is `check_intent_measurement_contract()` plus the per-row `associates_link_test_*` fields, which are stronger than the gate this pass had designed. |

Individual draft files are not kept alongside the diff: `pass13-original.patch` contains them in full, and a second 483 KB copy of `build.py` in the repository would be exactly the duplicate-build clutter this project logs as F59. The patch applies to `9c6e3f0`.
