"""Resolve the five three-way-merge regions in build.py, then rewrite the cluster's CTA to main's
convention. Run once against the conflicted tree; it fails loudly rather than writing a guess.

Decisions, each deliberate rather than mechanical:
  * #132's `CONFIG`/`ASSOCIATE_TAG` block is NOT restored. Main's published position (flag F76) is that the
    owner-selected ID is recorded but deliberately not applied, and its new gate fails the build if the two
    ever disagree. Re-importing that block would resurrect a reversed policy and trip the gate that replaced it.
  * Main's rewritten landing page wins: finder, product cards, compare CTA and article grid replace the version
    this pass was written against. The accessory shelf is re-attached below main's compare CTA, which is the
    position SG-43 option A describes.
  * Main's F76–F79 replace the parallel rows this branch carried; F83 is reworded to cite the flags that exist
    on main now rather than F81, which main removed.
  * Main's `page_intent()` keeps its own ledger rendering; this pass's re-read block is prepended inside the
    same function so the control test still reaches a published page.
  * The cluster's CTA is rewritten to main's link convention — supplied link, `rel="nofollow sponsored
    noopener"`, "Affiliate link · tracking unconfirmed" — because a second button style on a page whose tag
    status is the site's biggest open flag would be a worse reader experience and an inconsistency in policy.
"""

import re

P = "build.py"
s = open(P, encoding="utf-8").read()

pat = re.compile(r"^<<<<<<< ours\n(.*?)^=======\n(.*?)^>>>>>>> theirs\n", re.M | re.S)
found = list(pat.finditer(s))
assert len(found) == 5, f"expected 5 conflict regions, found {len(found)}"


def keep_for(i, m):
    ours, theirs = m.group(1), m.group(2)
    if i == 1:
        return theirs[theirs.index("# Pass 13 (2026-11-17, arena/00bc7156)"):]
    if i == 2:
        return ours + theirs[theirs.index("    # Pass 13 (2026-11-17, arena/00bc7156): the accessory shelf"):]
    if i == 3:
        return ours
    if i == 4:
        return ours + theirs[theirs.index('    ("F83", "The two supplied links'):]
    return theirs[:theirs.index("    ledger_cols = ")] + ours


resolved = [(m.start(), m.end(), keep_for(i, m)) for i, m in enumerate(found, 1)]
for a, b, keep in reversed(resolved):
    s = s[:a] + keep + s[b:]

# line-start check, not a substring check: the marker gate added in this pass quotes the literal patterns
# it hunts, so a substring assert fires on the guard itself.
left = [n for n, ln in enumerate(s.splitlines(), 1) if ln.startswith(("<<<<<<< ", ">>>>>>> ", "======="))]
assert not left, f"markers survive at {left[:5]}"
assert "ASSOCIATE_TAG = (CONFIG" not in s, "the reversed tag policy must not come back"  # (SITE_CONFIG contains that substring; check the real marker)

# --- re-attach the shelf placeholder below main's compare CTA ---------------------------------
cta_close = '''  <a class="btn" href="compare.html">Open the comparison <span aria-hidden="true">→</span></a>
</div>'''
assert s.count(cta_close) == 1, "compare CTA anchor"
s = s.replace(cta_close, cta_close + "\n{shelf}", 1)

# --- re-attach {reads_block} inside main's page_intent body ------------------------------------
i = s.index("def page_intent():")
j = s.index("<h2>Campaign ledger</h2>", i)
s = s[:j] + "{reads_block}\n" + s[j:]

# --- the cluster CTA, rewritten to main's convention -------------------------------------------
old_card = s[s.index("    def _tool_card(x):"):s.index('    intro = "".join(_tool_card(x) for x in prods)')]
new_card = '''    # Main's convention, adopted 2026-11-17 in the merge resolution: the supplied link is what the
    # reader is sent along, labelled honestly as an affiliate link whose tracking is unconfirmed, and
    # the observed destination is stated as a fact about the record rather than as a second button.
    # Two deliberate differences from the air-fryer pages: the button says "verify the model", because
    # here even the destination is only an observation, and the note names the flag that would have to
    # change before this cluster is treated as an onboarding decision rather than a shelf.
    def _tool_card(x):
        asin = (x.get("asin") or {}).get("v") or ""
        ls = x.get("link_source")
        return (
            f'<div class="card"><span class="kicker">{e(x["brand"])}</span>'
            f'<span class="cardtitle">{e(x["name"])}</span>'
            f'<span class="cardtext">Candidate ASIN {e(asin or "not stated")} — {e(x.get("asin_status", ""))}</span>'
            f'<div class="cta-row" style="margin-top:.6rem">'
            f'<a class="btn" href="{e(x["link"])}" target="_blank" rel="nofollow sponsored noopener" '
            f'data-analytics-event="outbound_click" data-analytics-target-id="{e(x["slug"])}">'
            f'Open supplied Amazon link — verify the model <span aria-hidden="true">→</span></a>'
            f'<span class="paid-tag">Affiliate link · tracking unconfirmed</span></div>'
            f'<p class="cta-note tiny">The destination observed on {e(ADJACENT["prepared_on"])} was '
            f'<code>{"https://www.amazon.com/dp/" + asin if asin else "not recorded"}</code>{(" " + src_links([ls])) if ls else ""}. '
            f'That is a record of where the link led, not a confirmation of what it was meant to promote — '
            f'see <a href="../product-intent.html">the product-intent record</a> and '
            f'<a href="../flagged.html#f78">F78</a>.</p></div>'
        )
'''
s = s.replace(old_card, new_card, 1)

# --- F83 reworded against the flags main actually carries --------------------------------------
subs = [
    ("The coverage gap itself is F81's finding, reached independently the same day by three sessions on one brief - a grep for both tokens returned zero files after twelve passes had each re-read only the three links already registered.",
     "The coverage gap was found three times on the same day: by this session, by arena/02b4e9c7-zone1 in a ledger, and by the pass whose F78 now sits on this register - a grep for both tokens returned zero files after twelve passes had each re-read only the three links already recorded."),
    ("and requirements.html row C-01 still quotes the brief as three links while its note spells the redirect parameter plmRedirect where every served URL in this repository reads plpRedirect - a wording drift, not a data error, and the two are fixed together in this pass.",
     ("Two other statements are now stale by this pass's doing and are recorded rather than edited in another session's voice: "
      "F78's instruction that no thermometer specification be published until intent and scope are confirmed is contradicted "
      "here on purpose - see the cluster's `contradicts` field, and SG-36's unpublish trigger, which is printed on the page - "
      "and requirements.html row C-01 quoted the brief as three links while spelling the redirect parameter plmRedirect where "
      "every served URL in this repository reads plpRedirect. Both are corrected in this pass; the row's blocked status stands, "
      "because fixing a count does not confirm an identity.")),
    ('Supplied links 4 and 5 (B0c8moW59, B0f3GKalj); flags F78, F81; requirements row C-01',
     'Supplied links 4 and 5 (B0c8moW59, B0f3GKalj); flags F76, F77, F78; requirements row C-01'),
    ("and F81's 'makes no claim about them' is overtaken: this pass publishes sourced specification rows for both",
     "and F78's 'do not publish thermometer specifications' is contradicted here on purpose, with the disagreement published rather than merged away"),
    ("F78's stated position - 'No thermometer page or specification has been published' - overtaken by events rather than edited by a stranger. F78's owner question is still open, because publishing the products is not confirming the intent: both intent fields stay null (PI-04, PI-05) and only the account holder can fill them (Q-27).",
     "F78's owner question is still open, because publishing the products is not confirming the intent: both intent fields stay null (PI-04, PI-05) and only the account holder can fill them (Q-27)."),
    ("and the last is not published anywhere in this register for either item {src_links(['S3'])}. The button under each name\n  goes to the ASIN this site recorded, tagged with the site's Associates ID; the short link the project was\n  handed is printed as evidence in <code>form, not as the path a reader is sent along — the same rule the rest\n  of the site adopted on 2026-11-17 (F81).</p>",
     ("and the last is not published anywhere in this register for either item {src_links(['S3'])}. The button under each name\n"
      "  is the link this project was handed, labelled the way the rest of the site labels it: an affiliate link whose\n"
      "  tracking is unconfirmed, because the ID the owner selected is recorded but deliberately not applied until the\n"
      "  account-side checks pass (F76). The destination it was observed at is printed under the button as a record, not\n"
      "  as a second call to action.</p>")),
]
for a, b in subs:
    if a in s:
        s = s.replace(a, b, 1)
        print("  · reworded:", a[:58])
    else:
        print("  · (already absent):", a[:58])

open(P, "w", encoding="utf-8").write(s)

import ast

ast.parse(s)
print("build.py resolved; parses clean")
