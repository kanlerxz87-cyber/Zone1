"""Pass 13, patch 5: honest product counts, buyer questions, data strip,
and the picks page covering all five products.

Historical rows - dated flag-register entries describing what was true on an
earlier pass - are deliberately left alone. Rewriting a record of an earlier
finding would destroy the evidence it exists to preserve.
"""
import sys

P = "build.py"
s = open(P, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"expected {count} occurrence(s), found {n} of:\n{old[:220]}")
    s = s.replace(old, new)


DASH = "\u2014"

# ------------------------------------------------- labels for the two new ----
sub(
    '''    format_labels = {
        "chefman-6qt-dual-basket": "Two-basket air fryer",
        "emeril-26qt-french-door": "French-door countertop oven",
        "chefman-8qt-turbofry": "Single-basket air fryer",
    }''',
    '''    format_labels = {
        "chefman-6qt-dual-basket": "Two-basket air fryer",
        "emeril-26qt-french-door": "French-door countertop oven",
        "chefman-8qt-turbofry": "Single-basket air fryer",
        # The two links added on 2026-11-17 resolve to thermometers, not air fryers.
        # They are labelled by what the listing actually is, and F77/F78 publish the
        # category mismatch rather than letting the label paper over it (SG-31).
        "thermomaven-1-sec-thermometer": "Instant-read thermometer",
        "chef-iq-sense-gen3-thermometer": "Wireless probe thermometer",
    }''',
)

# ------------------------------------------------------------ hero lede ------
sub(
    """<p class="lede">Two baskets, one 8 Qt basket, or a countertop oven? Compare three formats using manufacturer pages and owner's manuals""" + DASH + """without pretending we tested them.</p>""",
    """<p class="lede">Two baskets, one 8 Qt basket, or a countertop oven &mdash; and a thermometer for when the answer is &ldquo;cook to temperature, not to time&rdquo;. Compare {len(PRODUCT_LIST)} tracked products across {n_categories} categories using manufacturer pages and owner's manuals""" + DASH + """without pretending we tested them.</p>""",
)

sub(
    '''  <aside class="hero-panel" aria-label="Three air-fryer formats">''',
    '''  <aside class="hero-panel" aria-label="{len(PRODUCT_LIST)} tracked products across {n_categories} categories">''',
)

sub(
    '''    <p class="hero-footnote">Sourced specifications · visible gaps · no hands-on testing claimed</p>''',
    '''    <p class="hero-footnote">Sourced specifications · visible gaps · no hands-on testing claimed</p>
    <ul class="front-questions" aria-label="Questions this site answers">
      {question_chips}
    </ul>''',
)

# ------------------------------------------------------ section headings -----
sub(
    '''<h2>The three, side by side</h2>''',
    '''<h2>{len(PRODUCT_LIST)} tracked products, side by side</h2>
<p class="small muted">{verified} specification rows confirmed from official sources, {unverified} left blank and <a href="flagged.html">flagged</a>. The product rows are the answer; everything behind them is the proof, and every dashboard that holds it is one click away.</p>''',
)

sub(
    '''    <p class="small muted">These are product formats''' + DASH + '''not a ranked top-three list. Follow a link for the full sourced breakdown.</p>''',
    '''    <p class="small muted">These are product formats''' + DASH + '''not a ranked list. Follow a link for the full sourced breakdown. Two of the five supplied links land in a different Amazon category from the rest; that mismatch is published rather than smoothed over (<a href="flagged.html#f77">F77</a>, <a href="flagged.html#f78">F78</a>).</p>''',
)

sub(
    '''<span class="cardtitle">Three air fryers, three jobs &#8594;</span>''',
    '''<span class="cardtitle">Each product, the job it wins &#8594;</span>''',
)

# -------------------------------------------------------------- stat tile ----
sub(
    '''<div class="h">{n_total_flags} recorded across the three products and the programme; the Flagged page lists them as {n_open_flags} distinct rows</div>''',
    '''<div class="h">{n_total_flags} recorded across {len(PRODUCT_LIST)} products and the programme; the Flagged page lists them as {n_open_flags} distinct rows</div>''',
)

# ------------------------------------------------------- live link claims -----
sub(
    '''  <p class="small">A targeted live re-check on 2026-11-16 again observed fallback-style redirects for all three supplied short links.''',
    '''  <p class="small">A targeted live re-check on 2026-11-17 observed fallback-style redirects for all {len(LINK_ROWS)} supplied short links.''',
)

sub(
    '''  <a href="reverification.html">Full line-by-line re-read: {REVERIFIED}</a>. A targeted follow-up on 2026-11-16 rechecked all three link destinations and refreshed two dated manufacturer review counters; it was not a full re-read.''',
    '''  <a href="reverification.html">Full line-by-line re-read: {REVERIFIED}</a>. A targeted follow-up on 2026-11-17 rechecked all {len(LINK_ROWS)} supplied link destinations, two of them for the first time; it was not a full re-read. Each link's intended destination and its observed destination are recorded as two separate fields on the <a href="links.html">product link register</a>.''',
)

# ------------------------------------------------------ structured data ------
sub(
    '''            "name": "Three air-fryer formats compared",''',
    '''            "name": f"{len(PRODUCT_LIST)} tracked kitchen products compared",''',
)

sub(
    '''                  description="A source-led comparison of three air-fryer formats, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.",''',
    '''                  description=f"A source-led comparison of {len(PRODUCT_LIST)} tracked kitchen products, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.",''',
)

# ---------------------------------------------------------- computations -----
sub(
    '''    verified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is not None)
    unverified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None)''',
    '''    verified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is not None)
    unverified = sum(1 for p in PRODUCT_LIST for s in p["specs"] if s["value"] is None)
    # Two categories now exist: air fryers, and the thermometers that two of the
    # supplied links resolve to. Counting them from the data keeps the front page
    # honest the next time the product set changes.
    n_categories = len({p["category"] for p in PRODUCT_LIST})
    # The buyer questions this site exists to answer. They are editorial hypotheses
    # supplied with the brief - working titles, not claims about search volume or
    # about how many people ask them.
    BUYER_QUESTIONS = (
        ("Basket or oven-style air fryer: what should you compare?",
         "guides/buying-guide-air-fryers.html"),
        ("How do I compare air-fryer capacity without the hype?", "compare.html"),
        ("What are the cleanup and counter-space trade-offs?",
         "articles/how-to-clean-an-air-fryer.html"),
        ("What should I ask before buying a multi-function appliance?", "picks.html"),
    )
    question_chips = "".join(
        f'<li><a href="{href}">{e(q)}</a></li>' for q, href in BUYER_QUESTIONS)''',
)

# --------------------------------------------------------- nav + metadata ----
sub(
    '    ("index.html", "Home", "A clear guide to three air-fryer formats"),\n',
    '    ("index.html", "Home", "Sourced answers to the questions buyers actually ask"),\n',
)

sub(
    '    ("picks.html", "This week\'s picks", "Three products, three jobs, one decision rule"),\n',
    '    ("picks.html", "Which one is for you", "Each product wins a different job — pick by the job"),\n',
)

# ------------------------------------------------------- footer disclosure ---
sub(
    '''      <p>We may earn a commission from a qualifying purchase made through an eligible link. The three supplied Amazon short links have not been confirmed to match the named models or carry this site's Associates tracking ID. Amazon prices, availability and ratings are not published here.</p>''',
    '''      <p>We may earn a commission from a qualifying purchase made through an eligible link. The {len(LINK_ROWS)} supplied Amazon short links have not been confirmed to match the named models or to carry this site's Associates tracking ID; the intended destination and the observed destination of each are recorded separately on the <a href="{prefix}links.html" style="color:inherit;text-decoration:underline">product link register</a>. Amazon prices, availability and ratings are not published here.</p>''',
)

# ------------------------------------------------------------ picks page -----
sub(
    '''        ("chefman-8qt-turbofry", "Feed four to six people from one basket",
         "A single large basket with a documented 4\\u20136 person household size and a shake reminder."),
    ]''',
    '''        ("chefman-8qt-turbofry", "Feed four to six people from one basket",
         "A single large basket with a documented 4\\u20136 person household size and a shake reminder."),
        # The two thermometers registered on 2026-11-17. Their rows are blank by
        # design - no brand page or manual for them has been read - so the card
        # states that instead of a capacity figure.
        ("thermomaven-1-sec-thermometer", "Know the temperature in about a second",
         "An instant-read thermometer for cooking to temperature rather than to time. No manufacturer specification has been confirmed for this unit yet: every cell on its page is blank and flagged."),
        ("chef-iq-sense-gen3-thermometer", "Watch a cook without opening the door",
         "A wireless probe thermometer for long cooks where opening the oven loses heat. As with the other thermometer, no specification is confirmed yet - the listing title's claims are recorded as claims, not as specifications."),
    ]''',
)

sub(
    '''        cap = next(s for s in p["specs"] if s["label"] in ("Capacity",))''',
    '''        # Not every tracked product has a capacity - a thermometer does not - so the
        # fact shown is the product's own first confirmed row, or an honest blank.
        cap = next((s for s in p["specs"] if s["label"] == "Capacity"), None)
        if cap is None or cap.get("value") is None:
            cap = next((s for s in p["specs"] if s["value"] is not None), None)
        cap_label = cap["label"] if cap else "Key specification"
        cap_value = (e(cap["value"]) if cap and cap.get("value")
                     else '<span class="blank">&mdash; not confirmed &mdash;</span>')
        cap_src = src_links(cap.get("source", [])) if cap else ""''',
)

sub(
    '''  <div class="product-fact">
    <span>Manufacturer-stated capacity</span>
    <strong>{e(cap['value'])}</strong>
    <span class="tiny">{src_links(cap['source'])}</span>
  </div>''',
    '''  <div class="product-fact">
    <span>{cap_label}</span>
    <strong>{cap_value}</strong>
    <span class="tiny">{cap_src}</span>
  </div>''',
)

sub(
    '''    <p class="lede">A picks page is usually a ranking. This one is a decision rule: each of the three products wins a different job, and the job you have decides the product. Every claim below is a manufacturer specification you can check in one click.</p>''',
    '''    <p class="lede">A picks page is usually a ranking. This one is a decision rule: each product wins a different job, and the job you have decides the product. Every claim below is a manufacturer specification you can check in one click &mdash; and where no specification has been confirmed, the card says so instead of filling the gap.</p>''',
)

# ------------------------------------------------------------ data.html ------
sub(
    '''{total} specification rows across three products.''',
    '''{total} specification rows across {len(PRODUCT_LIST)} tracked products.''',
)

# ---------------------------------------------------- category page lede -----
sub(
    '''<p class="lede">The three supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14; product identity from the tokens is still unconfirmed (F14–F16), so this category label is provisional. The table below lists every tracked product with its verified capacity, the manufacturer's list price and its open flags. Amazon price is blank on every row by policy, not by oversight.</p>''',
    '''<p class="lede">Three of the {len(LINK_ROWS)} supplied links were observed landing on air fryer or air fryer-oven listings on 2026-11-13/14; the two added on 2026-11-17 land on meat thermometers instead. Product identity from the tokens is still unconfirmed (F14&ndash;F16), so every category label here is provisional and the two thermometers carry a published mismatch (<a href="../flagged.html#f77">F77</a>, <a href="../flagged.html#f78">F78</a>). The table below lists every tracked product with its verified capacity, the manufacturer's list price and its open flags. Amazon price is blank on every row by policy, not by oversight.</p>''',
)

# ------------------------------------------------------ requirements page ----
sub(
    '''This site has three products, one category, no traffic and no confirmed affiliate tag, so no row on this''',
    '''This site has {len(PRODUCT_LIST)} products, {n_categories} categories, no traffic and no confirmed affiliate tag, so no row on this''',
)

open(P, "w", encoding="utf-8").write(s)
print("patch 5 applied")
