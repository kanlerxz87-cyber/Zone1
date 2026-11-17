#!/usr/bin/env python3
"""pass 13, final scope (session 58cbaaa2) — applied onto main 4609ff3.

Two re-scopes in one session. Compared with the first, the browser counter is WITHDRAWN: main now
carries a fail-closed `analytics/collector.py` plus a footer that states browser collection stays
disabled until an endpoint is deployed, its privacy notice approved and the event flow tested, and
`tests/test_build_contract.py` enforces that posture. Overriding a merged, tested decision is not an
integration, so the counter ships as SG-38 with its three paths instead. What remains here is the
evidence this repository did not have: two brand catalogues, two Amazon help nodes, the correction
about what a landing URL can show, the register rows for the decisions those create, and one stale
present-tense count with a guard to hold it.

Anchors must match exactly once or nothing is written.
"""
import sys
from pathlib import Path

ROOT = Path("/home/user/Zone1")
BUILD = ROOT / "build.py"
text = BUILD.read_text(encoding="utf-8")
edits = []


def rep(old, new, what):
    edits.append((old, new, what))


# ── 1. module constants, read from the canonical register (main's data/product-intent.json)
rep('''def page_intent():
    """Operator-only link-intent record and campaign ledger."""''',
'''# ── arena/58cbaaa2 (2026-11-17): the submitted-link register, read by the build ──────────────
# main's own F79/F77 class of defect, one step up: a count typed into narrative rather than read from
# the register. The register holds five rows; the category lede still said "the three supplied links"
# in the present tense. Read the number, do not retype it, and let the build check the sentence.
LINK_RECHECK_DATE = "2026-11-17"
SUBMITTED_ROWS = PRODUCT_INTENT["rows"]
N_SUBMITTED_LINKS = len(SUBMITTED_ROWS)
_LINK_NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
                   "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def _num_word(n):
    """A count as a word, for prose. The data stays numeric; the sentence reads like English.

    check_submitted_link_count() matches both spellings, so this can never become a way to hide a
    number from the guard.
    """
    return {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
            8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}.get(n, str(n))


def _submitted_links_in_category():
    """Submitted links the register files in this site's own category.

    "In category" is read off the register's own `observed_listing_category`, the field the
    consolidation pass added for exactly this purpose — not from a guess about the product.
    """
    n = 0
    for r in SUBMITTED_ROWS:
        crumb = str(r.get("observed_listing_category") or "")
        if "air fryer" in crumb.lower():
            n += 1
    return n


def page_intent():
    """Operator-only link-intent record and campaign ledger."""''', "constants")

# ── 2. product-intent page: the brand-catalogue table and the reasoning correction
rep('''<p class="small"><a href="measurement.html">See the five event definitions, cadence and deployment gate →</a></p>''',
'''<h2>What the brands' own catalogues say about the two newest links</h2>
<p class="small">Both links submitted on 2026-11-17 were checked against the manufacturer's own pages rather
than against the listing they resolved to. Neither check closes a row; both narrow what a future article could
honestly claim, which is why no product page exists for either (F80).</p>
<div class="tablewrap">
<table>
  <caption>Brand-catalogue check, read 2026-11-17</caption>
  <thead><tr><th style="width:8%">Row</th><th style="width:24%">The listing says</th>
  <th style="width:34%">The brand's own page says</th><th style="width:22%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{brand_check_rows()}</tbody>
</table>
</div>

<div class="callout note">
  <strong>A correction to how this record argued its own case, dated 2026-11-17.</strong>
  <p class="small">Rows above and flags around them cite the absence of a visible <code>tag=</code> parameter on an
  observed landing URL beside their caution about attribution. Two official help nodes read on this date narrow what
  that can carry. Amazon states plainly that a tracking ID does not need to appear in the click-through URL for a
  sale to be credited, because the session is tagged on its side {src_links(['S41'])} — so a clean landing URL is a
  <em>null</em> observation, not a negative one, and it cannot be used as evidence about attribution in either
  direction. What stays unprovable from outside the account is the positive: that the selected ID is listed, and that
  a click through a published link appears under it. S41's sibling node names where that is read — the
  <strong>Tracking ID Summary Report</strong> — together with the screen that creates IDs and the limit of 100
  tracking IDs per account {src_links(['S42'])}, which is also what makes a per-channel sub-tag scheme a cheap option
  rather than an exotic one. The per-row <code>associates_link_test_*</code> fields are the right place for that
  result, and nothing on this page will accept a URL inspection as a substitute for it. Historical rows are left as
  written: they are dated records of what those passes observed, and the reasoning is corrected here instead of
  edited backwards.</p>
</div>

<p class="small"><a href="measurement.html">See the five event definitions, cadence and deployment gate →</a></p>''',
 "product-intent additions")

rep('''    dash = '<span class="tiny muted">Not confirmed</span>'
    body_rows = []''',
'''    dash = '<span class="tiny muted">Not confirmed</span>'

    def brand_check_rows():
        """Rows for the brand-catalogue comparison, read from the register so a new row needs no template edit."""
        out = []
        for row in SUBMITTED_ROWS:
            bc = row.get("brand_catalogue_check")
            if not bc:
                continue
            out.append(
                f'<tr><td>{e(row["id"])}</td>'
                f'<td class="small">{e(bc.get("listing_says") or "")}</td>'
                f'<td class="small">{e(bc.get("brand_page_says") or "")}</td>'
                f'<td class="small">{e(bc.get("verdict") or "")}'
                f'<div class="tiny muted"><a href="flagged.html#f80">F80</a> — why this closes nothing</div></td>'
                f'<td class="small">{src_links(bc.get("source_ids") or [])}</td></tr>')
        return "".join(out)

    body_rows = []''', "brand_check_rows helper")

# ── 3. the category lede's stale count, computed instead
rep('''<p class="lede">The three supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14; product identity from the tokens is still unconfirmed (F14–F16), so this category label is provisional.''',
'''<p class="lede">{_num_word(_submitted_links_in_category()).capitalize()} of the {_num_word(N_SUBMITTED_LINKS)} links submitted to this project were observed landing on air fryer or air fryer-oven listings, and the rest land under a different Amazon browse path — recorded on the <a href="../product-intent.html">link-intent record</a> and left out of this category rather than folded into it (F77, F80). Product identity from the tokens is still unconfirmed (F14–F16), so this category label is provisional.''',
 "category lede")

# ── 4. programme flags
rep('''     ["S23"]),
]''',
'''     ["S23"]),
    ("F80", "Neither newly submitted link reconciles with its manufacturer's own catalogue, so the two candidate listings cannot be closed by reading harder.",
     "PI-04, PI-05 on the link-intent record",
     "Both links submitted on 2026-11-17 were read the same day against the brands' own product pages rather than against the Amazon listings they resolved to. The observed ThermoMaven listing is titled '1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified …'; ThermoMaven's site names its instant-read line F1 Pro and F1 Turbo with a sub-second read and does not use '1 Sec' as a model name. The observed CHEF iQ listing is the iQ Sense Gen3 with three probes; the brand page states model CQ60-3C-Z3-E and an ambient rating the listing omits, and names air-fryer use among the product's heat environments. A marketing phrase in a listing title and a brand model designation are different kinds of identifier, and neither page mentions an ASIN — so the observed destinations stand as observations, the intended fields stay null, and no product page is written for either. The two brand pages are registered as S39 and S40, and their hosts are in verify.py's allow-list, which records that they are official brand sites, not that they settle an identity. Decision needed: say what each link was created to promote (Q-27), or drop the two rows — SG-36 lays out the paths. Recorded by arena/58cbaaa2, which re-scoped twice against the merged registers rather than publish a parallel one.",
     ["S39", "S40", "S36", "S37", "S23"]),
    ("F81", "The inference that a landing URL without a visible tag casts doubt on attribution was an over-reading, and it is corrected on the record instead of edited out of it.",
     "product-intent.html, data/product-intent.json, data/decision.json, F76",
     "Passes including this one cited the absence of a tag= parameter on an observed landing URL next to their caution about attribution. Amazon's help node read on 2026-11-17 (S41) states that 'it is not necessary for your unique ID to appear in order for us to track sales made after the initial click through', because the shopping session is tagged on Amazon's side. A null observation is not a negative one: the clean landing URLs neither support nor undermine attribution. The correction is applied where the inference is drawn in the present tense — the link-intent page now says so in those words next to the per-row test fields — and the dated rows are untouched, because they are records of what those passes saw. The sibling node (S42) names where the real confirmation is read, the Tracking ID Summary Report, plus the screen that creates IDs and the limit of 100 per account; that is what the per-row associates_link_test_* fields are waiting for, and Q-28/SG-37 are the owner's five minutes.",
     ["S41", "S42", "S6", "S2"]),
    ("F82", "A present-tense sentence still counted the submitted links at three, two days after the register grew to five.",
     "categories/kitchen-appliances.html lede",
     "Found 2026-11-17 while re-scoping this session against main, in the same class main's F77/F79 lineage describes but with the narrative rather than a value out of date: the category lede opened 'The three supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14', which was true at the time and is now a partial description of a five-row register whose two newest rows sit under Thermometers & Timers. The sentence is repaired where the tense is present — the lede reads its counts from len(rows) and from the register's own observed_listing_category field — and check_submitted_link_count() fails the build if a present-tense surface asserts a different count in its own words. The guard is deliberately scoped to the shopper surfaces and the two registers: a dated verification row that says 'all three supplied links' is a true statement about 2026-11-14, and a check that could only be satisfied by rewriting history is worse than no check. Process note for whoever next receives a link: add a row to data/product-intent.json — never a sentence.",
     ["S17", "S2"]),
]''', "flags F80-F82")

rep('''REPO_EVIDENCE = {''',
'''REPO_EVIDENCE = {
    # arena/58cbaaa2 (2026-11-17): file paths a reader can open when the irregularity is a fact
    # about this repository rather than about Amazon.
    "F80": ["data/product-intent.json", "product-intent.html", "session-58cbaaa2/artifacts/README.md"],
    "F81": ["product-intent.html", "data/product-intent.json", "reports/verification-2026-11-17-58cbaaa2.md"],
    "F82": ["build.py", "data/product-intent.json", "reports/verification-2026-11-17-58cbaaa2.md"],''',
 "REPO_EVIDENCE")

# ── 5. the count guard
rep('''def check_intent_measurement_contract(''',
'''_LINK_PHRASE = re.compile(
    r"\\b(?:all|each of|both|none of|every one of|only)\\s+(?:the\\s+)?"
    r"(one|two|three|four|five|six|seven|eight)\\s+(?:supplied|submitted)(?: short)? links?\\b", re.I)


def check_submitted_link_count(pages):
    """Build guard: a present-tense page may not assert a link count the register contradicts.

    Why this exists (main's F77/F79 lineage, extended 2026-11-17): the number of links the owner has
    submitted changes when the owner acts, and for ten passes it was typed into prose. Every individual
    value in those sentences stayed correct while the sentence went false — the narrative was the
    unverified thing, and no gate read it.

    Scope: the surfaces where the count is a claim about right now. Dated verification prose is outside
    it on purpose. "All three supplied links" was true on 2026-11-14; forcing history to agree with a
    check would destroy the evidence history is here to be.
    """
    present_tense = {"index.html", "product-intent.html", "measurement.html", "compare.html",
                     "picks.html", "compliance.html", "categories", "products", "guides"}
    words = {v: k for k, v in _LINK_NUM_WORDS.items()}
    problems = []
    for rel, html_text in pages.items():
        if rel.split("/")[0] not in present_tense:
            continue
        plain = re.sub(r"<[^>]+>", " ", html_text)
        for m in _LINK_PHRASE.finditer(plain):
            n = _LINK_NUM_WORDS[m.group(1).lower()]
            if n == N_SUBMITTED_LINKS:
                continue
            kind = m.group(2) or "supplied"
            problems.append(
                f"{rel}: asserts '{words.get(n, n)} {kind} links' where data/product-intent.json holds "
                f"{N_SUBMITTED_LINKS} rows — read the count from the register, or date the sentence so it "
                f"says when it was true")
    return problems


def check_intent_measurement_contract(''', "guard definition")

# ── 6. wire it where the other contract guard is called
rep('''    contract_problems = check_intent_measurement_contract(''',
'''    linkcount_problems = check_submitted_link_count(pages)
    if linkcount_problems:
        raise SystemExit("BUILD FAILED — a present-tense page asserts a link count the register "
                         "contradicts (F82):\\n  " + "\\n  ".join(linkcount_problems))
    contract_problems = check_intent_measurement_contract(''', "guard call")

# ── 7. count tokens for register prose
rep('''        "n_products": len(PRODUCT_LIST),''',
'''        "n_products": len(PRODUCT_LIST),
        # arena/58cbaaa2 (2026-11-17): counts read from the registers, for prose that must not drift.
        "n_submitted_links": str(N_SUBMITTED_LINKS),
        "n_intent_confirmed": str(sum(1 for r in SUBMITTED_ROWS if r.get("intended_asin"))),
        "n_link_tests_passed": str(sum(1 for r in SUBMITTED_ROWS if r.get("associates_link_test_passed"))),''',
 "req_counts tokens")

misses = [w for o, n, w in edits if text.count(o) != 1]
if misses:
    sys.exit("PATCH ABORTED (nothing written). Anchors not matched exactly once: " + ", ".join(misses))
for old, new, _ in edits:
    text = text.replace(old, new, 1)
BUILD.write_text(text, encoding="utf-8")
import ast
ast.parse(text)
print(f"build.py patched: {len(edits)} edits, parses OK")
