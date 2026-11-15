#!/usr/bin/env python3
"""One-shot patch: repair five defects in the two decision-page pairs.

Applied by session arena/88bb2db6 on 2026-11-15. Each replacement asserts the
exact original text and must match exactly once.

Defects repaired
----------------
D1  page_suggestions() passed page_rel="marketing-directions.html" to layout().
    Because the build dictionary writes page_suggestions() to suggestions.html,
    the Suggestions page carried the *other* page's path. Consequences:
      - the sidebar highlighted no nav item while you were on Suggestions;
      - canonical / og:url / breadcrumb all pointed at marketing-directions.html.
D2  page_suggestions_alt() had the mirror image of D1: it passed
    page_rel="suggestions.html" while being written to marketing-directions.html,
    so the parallel page claimed the canonical Suggestions URL and lit up the
    "Suggestions" nav entry.
D3  Both pages carried the identical <title>Suggestions · Zone1 Kitchen</title>.
D4  questions.html and decision-gate.html carried the identical
    <h1>What must be answered before a decision is reasonable</h1>.
D5  marketing-directions.html stated "{len(SUGGESTIONS)} suggestions" - 16 - while
    its table renders the 12 rows of the parallel register. It quoted the wrong
    register's count.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

PATCHES = []


def sub(old, new, why):
    PATCHES.append((old, new, why))


# ---------------------------------------------------------------- D1 + D3 + breadcrumbs
sub(
    '''    return layout("marketing-directions.html", "Suggestions", body, active="marketing-directions.html",
                  description="Sixteen reviewed, evidence-backed suggestions for the site, each with alternative paths and a recommendation, for the owner to choose before anything is implemented.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Suggestions (parallel pass)", page_url("marketing-directions.html")),
    ])]
              )''',
    '''    return layout("suggestions.html", "Suggestions", body, active="suggestions.html",
                  description="Sixteen reviewed, evidence-backed suggestions for the site, each with alternative paths and a recommendation, for the owner to choose before anything is implemented.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Suggestions", page_url("suggestions.html")),
    ])]
              )''',
    "D1: Suggestions page now carries its own path, nav state and canonical",
)

# ---------------------------------------------------------------- D2 + D3 + D5 + crumbs + cross-link
sub(
    '''<p class="crumbs"><a href="index.html">Home</a> / Suggestions</p>
<h1>Suggestions: choose the path before anything changes</h1>
<p class="lede">{len(SUGGESTIONS)} suggestions to improve the site's design, trust, content and measurement. <strong>None of them has been implemented.</strong> Each one lists the options. Pick an option for each ID you want, and only then will the change be made.</p>''',
    '''<p class="crumbs"><a href="index.html">Home</a> / Marketing directions (parallel pass)</p>
<h1>Suggestions: choose the path before anything changes</h1>
<p class="lede">{len(SUGGESTIONS_ALT)} suggestions to improve the site's design, trust, content and measurement. <strong>None of them has been implemented.</strong> Each one lists the options. Pick an option for each ID you want, and only then will the change be made.</p>''',
    "D5 + crumbs: the parallel page states its own register's count (12), not the other register's (16)",
)

sub(
    '''<p class="small">Several suggestions depend on a fact not yet known. Those facts are listed, with the way to find each one, on the <a href="questions.html">Questions and information gaps</a> page.</p>''',
    '''<p class="small">Several suggestions depend on a fact not yet known. Those facts are listed, with the way to find each one, on the <a href="decision-gate.html">Questions and information gaps</a> page.</p>''',
    "cross-link: the parallel suggestions page points at its own parallel questions page",
)

sub(
    '''    return layout("suggestions.html", "Suggestions", body, active="suggestions.html",
                  description="Site, design, trust, content and measurement suggestions, with options for the owner to choose before any change is made.")''',
    '''    return layout("marketing-directions.html", "Marketing directions (parallel pass)", body,
                  active="marketing-directions.html",
                  description="Site, design, trust, content and measurement suggestions, with options for the owner to choose before any change is made.",
                  jsonld_blocks=[breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Marketing directions (parallel pass)", page_url("marketing-directions.html")),
    ])]
              )''',
    "D2 + D3: the parallel page carries its own path, title and canonical",
)

# ---------------------------------------------------------------- D4: distinct H1 on the parallel questions page
sub(
    '''<p class="crumbs"><a href="index.html">Home</a> / Questions and information gaps</p>
<h1>What must be answered before a decision is reasonable</h1>
<p class="lede">{len(QUESTIONS_ALT)} questions.''',
    '''<p class="crumbs"><a href="index.html">Home</a> / Questions and information gaps (parallel pass)</p>
<h1>The parallel register: fourteen questions with their known facts, gaps and next steps</h1>
<p class="lede">{len(QUESTIONS_ALT)} questions.''',
    "D4: the parallel questions page no longer repeats the main register's H1 verbatim",
)

sub(
    '''<p class="small" style="margin-top:1.5rem">Related: <a href="suggestions.html">Suggestions</a> · <a href="flagged.html">Flagged for review</a> · <a href="executive-summary.html">Executive summary</a></p>''',
    '''<p class="small" style="margin-top:1.5rem">Related: <a href="marketing-directions.html">Marketing directions (parallel pass)</a> · <a href="questions.html">Questions and gaps (this register's main pass)</a> · <a href="flagged.html">Flagged for review</a> · <a href="executive-summary.html">Executive summary</a></p>''',
    "cross-link: the parallel questions page points at its own parallel suggestions page",
)

for old, new, why in PATCHES:
    if s.count(old) != 1:
        raise SystemExit(f"PATCH FAILED ({s.count(old)} matches) - {why}\n{old[:160]}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print(f"applied {len(PATCHES)} patches")
for _o, _n, why in PATCHES:
    print("  -", why)
