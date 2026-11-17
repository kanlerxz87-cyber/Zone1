"""Pass 13, patch 3: page_links(), page_measurement(), register them, and add
three guards: link-intent separation, disclosure above the fold, and analytics
disclosure realism."""
import sys

P = "build.py"
s = open(P, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"expected {count} occurrence(s), found {n} of:\n{old[:300]}")
    s = s.replace(old, new)


PAGES = r'''

# --------------------------------------------------------------------------- #
# product link register (added 2026-11-17, arena/9fe0b6b3)
# --------------------------------------------------------------------------- #
def page_links():
    """Every supplied link, with intent and observation published as separate blocks.

    The requirement behind this page is that the two are never merged. A redirect that
    lands on the same ASIN eight times running is still not a statement about what the
    account holder meant, and the difference is the whole commercial risk: a link can
    send every click it earns to the wrong place, or to the right place with no
    attribution, and neither failure is visible from outside Associates Central.
    """
    intent_rows, obs_rows, special_rows = [], [], []
    for row in LINK_ROWS:
        it, ob, sp = row["intent"], row["observation"], row["special_link"]
        intent_rows.append(f"""<tr>
          <td><strong>{e(row["id"])}</strong><div class="tiny muted">token {e(row["token"])}</div></td>
          <td><code class="tiny">{e(row["submitted_link"])}</code></td>
          <td class="blank">&mdash; not confirmed &mdash; {flag_pill("unverified")}<div class="tiny muted">{e(it["note"])}</div></td>
          <td class="blank">&mdash; not confirmed &mdash;</td>
          <td class="blank">&mdash;</td>
          <td class="blank">&mdash;</td>
          <td>{src_links(row.get("sources", []))} <a class="tiny" href="flagged.html#f76">F76</a></td>
        </tr>""")
        obs_rows.append(f"""<tr>
          <td><strong>{e(row["id"])}</strong></td>
          <td><code class="tiny">{e(ob["observed_redirect_asin"])}</code> {src_links(ob.get("sources", []))}</td>
          <td class="small">{e(ob["observed_listing_title"])}</td>
          <td class="small muted">{e(ob.get("observed_category_breadcrumb", ""))}</td>
          <td>{e(ob["observed_date"])}</td>
          <td class="small muted">{e(ob["note"])}</td>
        </tr>""")
        special_rows.append(f"""<tr>
          <td><strong>{e(row["id"])}</strong><div class="tiny muted">{e(row["token"])}</div></td>
          <td class="blank">&mdash; not validated &mdash; {flag_pill("unverified")}</td>
          <td class="blank">&mdash;</td>
          <td class="blank">&mdash;</td>
          <td>{e(sp["status"])}<div class="tiny muted">{e(sp["note"])}</div></td>
        </tr>""")

    tid = LINK_INTENT.get("tracking_id_supplied", "")
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Product link register</p>
<h1>Product link register: five supplied links, two kinds of statement</h1>
<p class="lede">This page keeps two things apart that are easy to collapse into one. <strong>Intent</strong> is what a link was created to point at &mdash; only the account holder can state it, and only Associates Central can confirm it. <strong>Observation</strong> is what the link did when this repository followed it. A destination that reproduces every time is still not an intention.</p>

<div class="callout warn">
  <strong>Why they are not merged.</strong> {e(LINK_INTENT.get("field_discipline", ""))}
</div>

<h2>Supplied tracking ID</h2>
<div class="tablewrap">
<table>
  <caption>Tracking ID as supplied, and what is and is not established about it</caption>
  <thead><tr><th style="width:22%">Field</th><th style="width:44%">Value</th><th style="width:34%">Basis</th></tr></thead>
  <tbody>
    <tr><td>Selected Tracking ID</td><td><code>{e(tid)}</code></td><td>Supplied by the account holder on 2026-11-17. {src_links(["S36"])}</td></tr>
    <tr><td>Format</td><td>Consistent with Amazon's documented US convention</td><td>Amazon's own help states its software &ldquo;automatically adds &quot;-20&quot; to the end of all Associate IDs&rdquo;. {src_links(["S36"])}</td></tr>
    <tr><td>Ownership</td><td class="blank">&mdash; not confirmed &mdash; {flag_pill("unverified")}</td><td>Format is not ownership. Confirm under <em>Manage your Tracking IDs</em> in Associates Central. <a href="flagged.html#f79">F79</a> {src_links(["S36", "S2"])}</td></tr>
    <tr><td>Attached to these links</td><td class="blank">&mdash; not confirmed &mdash; {flag_pill("unverified")}</td><td>No resolved URL has carried a visible <code>tag=</code> parameter in eight recorded rounds. <a href="flagged.html#f6">F6</a> {src_links(["S17", "S40"])}</td></tr>
  </tbody>
</table>
</div>

<h2>1. Intent &mdash; what each link was created to point at</h2>
<p class="small">Every cell in this table is blank, and that is the finding. These four fields can only be filled by a person who has checked Associates Central, so the register leaves them empty rather than copying the observed ASIN across. Filling them from the table below is exactly the error this page exists to prevent.</p>
<div class="tablewrap">
<table>
  <caption>Product-intent confirmation record &mdash; {len(LINK_ROWS)} supplied links</caption>
  <thead><tr>
    <th>Link</th><th>Submitted link</th><th>Intended ASIN</th><th>Official listing URL</th>
    <th>Confirmation date</th><th>Confirmation source</th><th>Status / flag</th>
  </tr></thead>
  <tbody>{"".join(intent_rows)}</tbody>
</table>
</div>

<h2>2. Observation &mdash; what each link did when followed</h2>
<p class="small">Read live on the date shown. These are recorded redirect responses, not confirmations of identity, attribution or approval. Two of the five land in a different browse category from the rest &mdash; <a href="flagged.html#f77">F77</a> and <a href="flagged.html#f78">F78</a>.</p>
<div class="tablewrap">
<table>
  <caption>Observed redirect targets &mdash; a separate field, never merged with intent</caption>
  <thead><tr>
    <th>Link</th><th>Observed ASIN</th><th>Observed listing title</th>
    <th>Observed browse path</th><th>Observed date</th><th>Note</th>
  </tr></thead>
  <tbody>{"".join(obs_rows)}</tbody>
</table>
</div>

<h2>3. Validated Special Links &mdash; the gate before scaling</h2>
<p class="small">Empty until each link has been generated, opened and confirmed inside the enrolled Associates workflow. This site does not assert that the supplied short links are invalid; it records that they have not been validated.</p>
<div class="tablewrap">
<table>
  <caption>Validated Special Link per product &mdash; one confirmed link, then scale</caption>
  <thead><tr><th>Link</th><th>Validated Special Link</th><th>Validation date</th><th>Validation source</th><th>Status</th></tr></thead>
  <tbody>{"".join(special_rows)}</tbody>
</table>
</div>

<div class="callout ok">
  <strong>The procedure, in order.</strong>
  <ol class="tight small">
    <li>Sign in and confirm the supplied tracking ID appears under <em>Manage your Tracking IDs</em>. {src_links(["S36"])}</li>
    <li>Generate one Special Link for one product, for that ASIN, with that ID.</li>
    <li>Open it. Confirm the destination is the product you intended.</li>
    <li>Confirm the click appears against that tracking ID in the tracking report.</li>
    <li>Only then repeat for the remaining products, and record each validated link above.</li>
  </ol>
  <p class="small" style="margin-bottom:0">Steps 1&ndash;4 are the gate. Doing them for one link first proves the mechanism before five unconfirmed links are scaled across a growing article set. {src_links(["S2"])} See <a href="suggestions.html#sg-38">SG-38</a> and <a href="questions.html#q-28">Q-28</a>.</p>
</div>

<p class="small" style="margin-top:1.5rem">Related: <a href="measurement.html">Measurement</a> &middot; <a href="compliance.html">Compliance</a> &middot; <a href="flagged.html">Flagged for review</a> &middot; <a href="questions.html#q-27">Q-27 product set</a></p>
"""
    return layout("links.html", "Product link register", body, active="links.html",
                  description="Every supplied Amazon link, with the intended product and the observed "
                              "redirect destination recorded as two separate fields.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_URL + "/"),
                      ("Product link register", page_url("links.html")),
                  ])])


# --------------------------------------------------------------------------- #
# measurement (added 2026-11-17, arena/9fe0b6b3)
# --------------------------------------------------------------------------- #
def page_measurement():
    event_rows = "".join(
        f"""<tr>
          <td><strong>{e(x["id"])}</strong></td>
          <td>{e(x["name"])}</td>
          <td class="small">{e(x["fires_when"])}</td>
          <td class="small"><code class="tiny">{e(", ".join(sorted(x["payload"].keys())))}</code></td>
          <td class="small">{e(x["measures"])}</td>
          <td class="small muted">{e(x["privacy"])}</td>
          <td class="small">{e(x["status"])}</td>
        </tr>"""
        for x in ANALYTICS_EVENTS)

    ep = ANALYTICS.get("endpoint") or {}
    rules = "".join(f"<li>{e(r)}</li>" for r in ep.get("server_rules", []))
    payload_rows = "".join(
        f'<tr><td><code class="tiny">{e(k)}</code></td><td class="small">{e(v)}</td></tr>'
        for k, v in (ep.get("payload_shape") or {}).items())

    col_rows = "".join(
        f"""<tr><td><code class="tiny">{e(c["name"])}</code></td>
          <td class="small">{e(c["type"])}</td>
          <td class="small">{e(c["meaning"])}</td>
          <td class="blank">&mdash; empty &mdash;</td></tr>"""
        for c in LEDGER.get("columns", []))

    prov_rows = "".join(
        f'<tr><td>{e(p["date"])}</td><td class="small">{e(p["action"])}</td>'
        f'<td class="small muted">{e(p["by"])}</td><td class="small muted">{e(p.get("note", ""))}</td></tr>'
        for p in LEDGER.get("provenance_trail", []))

    status = e(ANALYTICS.get("status", ""))
    endpoint_cell = (f'<code class="tiny">{e(ep.get("url"))}</code>' if ep.get("url")
                     else '<span class="blank">&mdash; not configured &mdash;</span>')
    ledger_rows = ("".join(col_rows))

    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Measurement</p>
<h1>Measurement: five events, one endpoint, an empty ledger</h1>
<p class="lede">Measurement ships before the next guide is written, because a topic chosen from a number nobody can audit is the same as a topic chosen by instinct. The counter is on every page. The endpoint contract is fixed. The ledger is empty on purpose.</p>

<div class="callout warn">
  <strong>Status: {status}.</strong> {e(ANALYTICS.get("status_note", ""))}
</div>

<h2>The five events</h2>
<div class="tablewrap">
<table>
  <caption>Defined events &mdash; counts, not people</caption>
  <thead><tr>
    <th>Event</th><th>Name</th><th>Fires when</th><th>Payload</th>
    <th>What it measures</th><th>Privacy</th><th>Status</th>
  </tr></thead>
  <tbody>{event_rows}</tbody>
</table>
</div>

<h2>Endpoint contract</h2>
<div class="tablewrap">
<table>
  <caption>The collector this site will send events to</caption>
  <thead><tr><th style="width:26%">Field</th><th style="width:74%">Value</th></tr></thead>
  <tbody>
    <tr><td>URL</td><td>{endpoint_cell}</td></tr>
    <tr><td>Method</td><td><code class="tiny">{e(ep.get("method", ""))}</code> &middot; <code class="tiny">{e(ep.get("content_type", ""))}</code></td></tr>
    <tr><td>Kind</td><td>{e(ep.get("kind", ""))} &mdash; reference implementation at <code class="tiny">{e(ep.get("reference_implementation", ""))}</code></td></tr>
    <tr><td>Why it is blank</td><td class="small">{e(ep.get("why_blank", ""))}</td></tr>
  </tbody>
</table>
</div>

<h2>Payload</h2>
<div class="tablewrap">
<table>
  <caption>Fields the collector will accept, and nothing else</caption>
  <thead><tr><th style="width:20%">Field</th><th style="width:80%">Meaning</th></tr></thead>
  <tbody>{payload_rows}</tbody>
</table>
</div>

<h2>Rules the collector must follow</h2>
<ul class="tight small">{rules}</ul>
<p class="small muted">Client side: {e((ANALYTICS.get("client") or {}).get("failure_mode", ""))}</p>

<h2>Campaign ledger &mdash; empty by design</h2>
<p class="small">{e(LEDGER.get("status_note", ""))}</p>
<div class="callout warn"><strong>Fill rule.</strong> {e(LEDGER.get("fill_rule", ""))}</div>
<div class="tablewrap">
<table>
  <caption>Ledger columns, fixed now so they cannot be redefined later</caption>
  <thead><tr><th>Column</th><th>Type</th><th>Meaning</th><th>Value</th></tr></thead>
  <tbody>{ledger_rows}</tbody>
</table>
</div>

<h2>Provenance trail</h2>
<div class="tablewrap">
<table>
  <caption>Every action taken on this ledger, dated</caption>
  <thead><tr><th>Date</th><th>Action</th><th>By</th><th>Note</th></tr></thead>
  <tbody>{prov_rows}</tbody>
</table>
</div>
<p class="small muted">{len(LEDGER.get("rows", []))} rows recorded.</p>

<div class="callout ok">
  <strong>What this site does not measure or publish.</strong>
  <ul class="tight small">{"".join(f"<li>{e(x)}</li>" for x in ANALYTICS.get("not_measured_here", []))}</ul>
</div>

<p class="small" style="margin-top:1.5rem">Related: <a href="links.html">Product link register</a> &middot; <a href="suggestions.html#sg-37">SG-37 turn on measurement</a> &middot; <a href="questions.html#q-29">Q-29 where the endpoint runs</a> &middot; <a href="topics.html">Content and traffic plan</a></p>
"""
    return layout("measurement.html", "Measurement", body, active="measurement.html",
                  description="The five measured events, the self-hosted endpoint contract, and a "
                              "campaign ledger that is empty until a real report fills it.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_URL + "/"),
                      ("Measurement", page_url("measurement.html")),
                  ])])


# --------------------------------------------------------------------------- #
# build guards (added 2026-11-17, arena/9fe0b6b3)
# --------------------------------------------------------------------------- #
def check_link_intent():
    """Build guard: intent and observation must stay separate fields.

    The requirement is that a link's *intended* ASIN and its *observed* redirect
    target are two different statements and are never merged. The failure this
    guards against is quiet and tempting: the observed ASIN reproduces on every
    read, so copying it into the intent block looks like tidying up. It is not -
    it converts an observation into a claim about somebody else's intention,
    which is the exact class of error the rest of this site exists to avoid.

    A row may only carry an intended ASIN when a human has recorded a
    confirmation date and a confirmation source alongside it.
    """
    problems = []
    seen = set()
    for row in LINK_ROWS:
        rid = row.get("id", "<no id>")
        if rid in seen:
            problems.append(f"{rid}: duplicate link id in data/link-intent.json")
        seen.add(rid)
        intent, obs = row.get("intent") or {}, row.get("observation") or {}
        intended = (intent.get("intended_asin") or "").strip()
        observed = (obs.get("observed_redirect_asin") or "").strip()
        if intended:
            if not (intent.get("confirmation_date") or "").strip():
                problems.append(f"{rid}: intended_asin is set but confirmation_date is blank")
            if not (intent.get("confirmation_source") or "").strip():
                problems.append(f"{rid}: intended_asin is set but confirmation_source is blank")
            if not (intent.get("official_listing_url") or "").strip():
                problems.append(f"{rid}: intended_asin is set but official_listing_url is blank")
        if intended and observed and intended == observed and not (intent.get("confirmation_date") or "").strip():
            problems.append(
                f"{rid}: intended_asin equals observed_redirect_asin with no confirmation "
                "date - the observed destination was copied into the intent field")
        sp = row.get("special_link") or {}
        if (sp.get("validated_special_link") or "").strip():
            if not (sp.get("validation_date") or "").strip():
                problems.append(f"{rid}: validated_special_link is set but validation_date is blank")
            if not (sp.get("validation_source") or "").strip():
                problems.append(f"{rid}: validated_special_link is set but validation_source is blank")
    return problems


def check_disclosure_above_fold(pages):
    """Build guard: the disclosure must be above the fold on every page, and repeated in the footer.

    The brief asks for the disclosure strip under the masthead on every page. It is
    currently the first element in the body - above the masthead - which is the
    stronger position, and this guard stops it drifting below the fold. It also
    requires the footer to repeat it, because a reader who scrolls to the bottom of
    a long guide should not have to scroll back up to find the commercial
    relationship. check_disclosure() only proves the string exists; this proves
    where.
    """
    problems = []
    for rel, text in pages:
        bar = text.find('class="disclosure-bar"')
        main = text.find("<main")
        if bar == -1:
            problems.append(f"{rel}: no disclosure strip rendered")
            continue
        if main != -1 and bar > main:
            problems.append(f"{rel}: disclosure strip appears after <main>, so it is not above the fold")
        foot = text.find('<footer class="site">')
        if foot == -1 or text.rfind(DISCLOSURE) < foot:
            problems.append(f"{rel}: the disclosure is not repeated in the footer")
    return problems


def check_analytics_disclosure_realism(pages):
    """Build guard: the privacy notice must match whether collection is actually on.

    Program Policies require an accurate statement of cookie and third-party
    technology use. The footer sentence is generated from data/analytics.json, so
    the remaining risk is a stale page: a build where an endpoint is configured
    but some page still claims the site runs no analytics. That sentence is the
    one a regulator and a reader both take at face value, so it fails the build.
    """
    problems = []
    configured = bool(ANALYTICS_ENDPOINT)
    for rel, text in pages:
        foot_at = text.find('<footer class="site">')
        if foot_at == -1:
            continue
        footer = text[foot_at:]
        says_none = "runs no analytics" in footer
        if configured and says_none:
            problems.append(
                f"{rel}: footer says the site runs no analytics but an endpoint is configured")
        if not configured and not says_none:
            problems.append(
                f"{rel}: footer does not state that analytics is off, but no endpoint is configured")
    return problems


'''

sub('def main():\n    assets = ROOT / "assets"\n',
    PAGES.lstrip("\n") + '\ndef main():\n    assets = ROOT / "assets"\n')

# register the pages
sub('    pages["compliance.html"] = page_compliance()\n',
    '    pages["compliance.html"] = page_compliance()\n'
    '    pages["links.html"] = page_links()\n'
    '    pages["measurement.html"] = page_measurement()\n')

# run the guards
sub('    seo_problems = check_seo_metadata(pages)\n',
    '    link_intent_problems = check_link_intent()\n'
    '    if link_intent_problems:\n'
    '        raise SystemExit("BUILD FAILED — product-link register mixed intent with "\n'
    '                         "observation:\\n  " + "\\n  ".join(link_intent_problems))\n'
    '    fold_problems = check_disclosure_above_fold(list(pages.items()))\n'
    '    if fold_problems:\n'
    '        raise SystemExit("BUILD FAILED — disclosure is not both above the fold and in "\n'
    '                         "the footer:\\n  " + "\\n  ".join(fold_problems))\n'
    '    analytics_problems = check_analytics_disclosure_realism(list(pages.items()))\n'
    '    if analytics_problems:\n'
    '        raise SystemExit("BUILD FAILED — privacy notice disagrees with the measurement "\n'
    '                         "configuration:\\n  " + "\\n  ".join(analytics_problems))\n'
    '    seo_problems = check_seo_metadata(pages)\n')

open(P, "w", encoding="utf-8").write(s)
print("patch 3 applied")
