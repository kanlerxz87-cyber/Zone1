import re, sys, pathlib

p = pathlib.Path('build.py')
s = p.read_text(encoding='utf-8')
orig = s


def sub(old, new, count=1, label=''):
    global s
    n = s.count(old)
    if n != count:
        print(f'!! MISS [{label}] expected {count} got {n}: {old[:80]!r}')
        sys.exit(1)
    s = s.replace(old, new, count)
    print(f'ok [{label}]')


# ================================================================ 1. two new pages
NEW_PAGES = '''
# --------------------------------------------------------------------------- #
# pass 13 pages (2026-11-17, arena/3093e674-zone1): the link record and the
# measurement layer. Both are owner/reader trust surfaces, so they are rendered
# from their registers rather than authored: a reviewer edits data, never HTML.
# --------------------------------------------------------------------------- #

def page_links():
    li = LINK_INTENT
    recs = li["records"]
    rows = []
    for r in recs:
        ob, it = r["observed"], r["intended"]
        rows.append(f"""<tr>
          <td class="num"><strong>{e(r['id'])}</strong></td>
          <td><code>{e(r['submitted_link'])}</code><div class="tiny muted">received {e(r['received_on'])} · token {e(r['submitted_token'])} ({r['token_length']} characters)</div></td>
          <td><strong>{e(it['asin'] or '— blank —')}</strong><div class="tiny muted">{e(it['status'])}. {e(it['source'])}</div><div class="tiny muted">Official listing URL: {e(it['official_listing_url'] or 'not stated')}. Confirmed: {e(it['confirmed_on'] or 'no date yet')}.</div></td>
          <td><a href="{e(ob['final_url'])}" target="_blank" rel="noopener">{e(ob['final_asin'])}</a><div class="tiny muted">{e(ob['listing_title'])}</div><div class="tiny muted">{e(ob['browse_node'])}</div></td>
          <td>{e(ob['observed_on'])}<div class="tiny muted">{e(ob['stability'])}</div></td>
          <td>{flag_pill('unverified') if 'unconfirmed' in r['identity_status'] or 'unmapped' in r['identity_status'] else flag_pill('partial')}<div class="tiny muted">{e(r['identity_status'])}</div><div class="tiny muted">{repo_link('data/link-intent.json', 'record ' + r['id'])}</div></td>
        </tr>""")
    obs_cols = "".join(
        f'<tr><td>{e(r["id"])}</td><td><code>{e(r["observed"]["redirect_params"])}</code></td>'
        f'<td>{e(r["site_treats_it_as"])}</td><td>{src_links(["S17"])}</td></tr>'
        for r in recs)
    why = "".join(f"<li>{e(x)}</li>" for x in li["rules"])
    not_claimed = "".join(f"<li>{e(x)}</li>" for x in li["not_claimed"])
    reading = "".join(f"<li>{e(x)}</li>" for x in li["reading_order"])
    fmt = li["asin_format_check"]
    lf = li["link_format"]
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Trust &amp; evidence / Link record</p>
<h1>Where the links you sent actually go</h1>
<p class="lede">Five Amazon links were supplied to this project, and every buying decision on this
site rests on knowing which product each one points at. This page keeps two answers side by side and
deliberately apart: <strong>what the account holder intended</strong>, and <strong>where a fetch
landed</strong>. A reader following a link gets the second; only the first can justify a
recommendation, and it has not been given to us yet.</p>

<div class="callout note">
  <p><strong>Why the two columns are never merged.</strong> {e(li['why_two_fields'])}</p>
</div>

<div class="tablewrap">
<table>
  <caption>Product-intent confirmation record — {len(recs)} submitted links, read {e(li['compiled'])}</caption>
  <thead><tr>
    <th>Row</th><th>Submitted link</th><th>Intended (owner statement only)</th>
    <th>Observed destination (fetch only)</th><th>Read on</th><th>Status and evidence</th>
  </tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>
</div>

<h2>Rules this register is held to</h2>
<ul>{why}</ul>

<h2>Observed redirect behaviour, one row per link</h2>
<p class="small">The redirect parameters are published because they are the reason identity stays
"candidate": a landing URL produced by a fallback redirector is evidence about the redirector, not
about the product someone chose. Read on {e(li['compiled'])}.</p>
<div class="tablewrap">
<table>
  <caption>What each fetch saw</caption>
  <thead><tr><th>Row</th><th>Redirect parameters on the landing URL</th><th>How this site treats it</th><th>Source</th></tr></thead>
  <tbody>{obs_cols}</tbody>
</table>
</div>

<h2>The {e(fmt['claim'][:0])}ASIN check</h2>
<p>{e(fmt['claim'])}</p>
<p class="small">{e(fmt['why_it_matters'])} {src_link(fmt['source'])}</p>

<h2>What changed on {e(li['compiled'])}: the links now carry the Associates tag</h2>
<p>{e(lf['rule'])} {src_links(lf['sources'])}</p>
<div class="callout note">
  <p><strong>{e(lf['what_this_site_does'])}</strong></p>
</div>
<div class="tablewrap">
<table>
  <caption>Tag configuration, read from {repo_link('data/config.json')}</caption>
  <thead><tr><th>Field</th><th>Value</th><th>Provenance</th></tr></thead>
  <tbody>
    <tr><td>Tracking ID this site publishes with</td>
        <td><code>{e(ASSOCIATE_TAG or '(blank — the site earns nothing)')}</code></td>
        <td>{e(CONFIG.get('associate_tag_provenance', {}).get('where', 'not stated'))}. Shape check:
            {"matches Amazon's XXXXX-## pattern" if tag_is_wellformed(ASSOCIATE_TAG) else "does not match the published shape"};
            confirmed inside Associates Central: <strong>{'yes' if CONFIG.get('associate_tag_provenance', {}).get('verified_in_associates_central') else 'no'}</strong>.
            {src_links(['S2'])}</td></tr>
    <tr><td>Per-page sub-tag IDs</td>
        <td>{len(SUB_TAGS) and e(', '.join(f'{k} → {v}' for k, v in SUB_TAGS.items())) or 'none assigned'}</td>
        <td>{e(CONFIG.get('sub_tags', {}).get('why', ''))} {src_links(['S6'])}</td></tr>
    <tr><td>Hard limit on sub-tags</td>
        <td>No per-visitor tagging anywhere in this build</td>
        <td>{e(CONFIG.get('sub_tags', {}).get('hard_limit', ''))} {src_links(['S2'])}</td></tr>
  </tbody>
</table>
</div>
<p class="small">{e(lf['unresolved'])}</p>

<h2>How the link was checked, in order</h2>
<ol>
  <li>The submitted URL was fetched on {e(li['compiled'])}; its own landing link and document title were read.
      {src_links(['S17'])}</li>
  <li>The destination ASIN was compared against the ASIN this site already markets, so a moved redirect
      would be visible instead of quiet. {src_links(['S16', 'S28', 'S29', 'S36', 'S37'])}</li>
  <li>The tag parameter was looked for on the landing URL. It is not observable from outside an Associates
      account, which is why that half stays an owner action rather than a green tick. {src_links(['S6'])}</li>
  <li>The composed Special Link is published from data/config.json by one function, so no page can carry a
      product link that forgot the tag — and the build fails if one does.</li>
</ol>

<h2>What this page does not claim</h2>
<ul>{not_claimed}</ul>
<h2>If you are the account holder</h2>
<ol>{reading}</ol>
"""
    return layout("links.html", "Link record — where the supplied links go", body,
                  active="links.html",
                  description=("Every submitted Amazon link, its intended product and its observed destination, kept as "
                               "separate fields, plus the Associates tag the site now publishes with each buy link."),
                  jsonld_blocks=[json_ld("links.html", "Link record — where the supplied links go",
                                          "Five submitted Amazon links, their observed destinations and their unconfirmed "
                                          "intents, each row sourced to the live page it was read from.")])


def page_measurement():
    m = MEASUREMENT
    ev = "".join(
        f"<tr><td class='num'><strong>{e(x['id'])}</strong></td><td><code>{e(x['name'])}</code></td>"
        f"<td>{e(x['fires_on'])}</td><td>{e(x['feeds'])}</td>"
        f"<td>{repo_link('data/measurement.json', 'event spec')}</td></tr>"
        + (f"<tr><td></td><td colspan='3' class='tiny muted'>{e(x.get('honesty_note') or x.get('not_recorded') or '')}</td>"
           f"<td>{repo_link('data/measurement.json', 'limit recorded')}</td></tr>"
           if (x.get('honesty_note') or x.get('not_recorded')) else "")
        for x in m["events"])
    cols = "".join(f"<tr><td><code>{e(c['key'])}</code></td><td>{e(c['label'])}</td><td>{e(c['rule'])}</td>"
                   f"<td>{repo_link('data/campaign-ledger.json', 'ledger schema')}</td></tr>" for c in LEDGER["columns"])
    storage = "".join(f"<tr><td>{e(k.replace('_', ' '))}</td><td>{e(v)}</td>"
                      f"<td>{src_links(['S2'])}</td></tr>" for k, v in m["storage_model"].items() if k != "where")
    cannot = "".join(f"<li>{e(x)}</li>" for x in m["what_this_cannot_tell_you"])
    rules = "".join(f"<li>{e(x)}</li>" for x in LEDGER["derivation_rules"])
    first = "".join(f"<li>{e(x)}</li>" for x in LEDGER["first_rows_expected_from"])
    req = "".join(f"<li>{e(x)}</li>" for x in m["endpoint_contract"]["required_before_enabling"])
    ec = m["endpoint_contract"]["shape_when_enabled"]
    body = f"""
<p class="crumbs"><a href="index.html">Home</a> / Trust &amp; evidence / Measurement</p>
<h1>What this site counts, and what it refuses to count</h1>
<p class="lede">A shop that cannot see which shelf people walk past is guessing. This page is the
instrument panel: five defined events, recorded on your own device, sent nowhere — and the two
numbers that only Amazon's own reports are allowed to produce.</p>

<div class="callout note">
  <p><strong>{e(m['what_this_page_is'])}</strong></p>
</div>

<h2>The five events</h2>
<p class="small">{e(m['events_note'])}</p>
<div class="tablewrap">
<table>
  <caption>Event definitions, from {repo_link('data/measurement.json')}</caption>
  <thead><tr><th>Event</th><th>Name</th><th>Fires on</th><th>What it decides</th><th>Spec</th></tr></thead>
  <tbody>{ev}</tbody>
</table>
</div>

<h2>Where the data lives</h2>
<div class="tablewrap">
<table>
  <caption>The privacy model, in the same terms a disclosure has to state it</caption>
  <thead><tr><th>Aspect</th><th>What is true of this build</th><th>Rule it answers</th></tr></thead>
  <tbody>{storage}</tbody>
</table>
</div>

<h2 id="your-device">Your own counts on this device</h2>
<p class="small">Rendered from the one place those numbers exist: this browser. No row here was sent
anywhere, and no other visitor's counts can appear on it.</p>
<div id="z1k-panel" class="ledger-panel">
  <p class="tiny muted">Reading the local ledger…</p>
</div>
<noscript><p class="callout note">JavaScript is off, so nothing is counted and nothing is displayed. That is
the intended fallback: the ledger is optional, every claim on this page is readable without it, and the
build-time link audit runs whether or not a reader executes anything.</p></noscript>

<h2 id="ledger">Campaign ledger — {len(LEDGER['rows'])} rows</h2>
<p class="small">{e(LEDGER['why_it_is_empty'])}</p>
<div class="tablewrap">
<table>
  <caption>Ledger columns and their admission rules, from {repo_link('data/campaign-ledger.json')}</caption>
  <thead><tr><th>Field</th><th>Label</th><th>Rule for filling it</th><th>Register</th></tr></thead>
  <tbody>{cols}</tbody>
</table>
</div>
<h3>Derivation rules</h3>
<ul>{rules}</ul>
<h3>Where the first rows will come from</h3>
<ul>{first}</ul>
<p class="small">{e(LEDGER['provenance_gate'])}</p>

<h2>The endpoint that is not switched on</h2>
<p>{e(m['endpoint_contract']['why_it_cannot_be_faked'])}</p>
<div class="tablewrap">
<table>
  <caption>The contract, ready for whoever hosts it</caption>
  <thead><tr><th>Part</th><th>Specification</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>status</td><td><code>{e(m['endpoint_contract']['status'])}</code></td><td>{repo_link('data/measurement.json', 'decision recorded')}</td></tr>
    <tr><td>method and path</td><td><code>{e(ec['method'])} {e(ec['path'])}</code></td><td>{repo_link('data/measurement.json', 'contract')}</td></tr>
    <tr><td>body</td><td><code>{e(json.dumps(ec['body'], ensure_ascii=False))}</code></td><td>{repo_link('data/measurement.json', 'contract')}</td></tr>
    <tr><td>auth</td><td>{e(ec['auth'])}</td><td>{repo_link('data/measurement.json', 'contract')}</td></tr>
    <tr><td>response</td><td>{e(ec['response'])}</td><td>{repo_link('data/measurement.json', 'contract')}</td></tr>
  </tbody>
</table>
</div>
<h3>Required before it can be enabled</h3>
<ul>{req}</ul>
<p class="small">{e(m['endpoint_contract']['flip_switch'])}</p>

<h2>The only report that pays</h2>
<p>{e(m['authoritative_source_for_money']['text'])} {src_links(m['authoritative_source_for_money']['sources'])}</p>

<h2>What none of this can tell you</h2>
<ul>{cannot}</ul>
"""
    return layout("measurement.html", "Measurement — events, privacy and the empty ledger", body,
                  active="measurement.html",
                  description=("The five events this site counts on your own device, why nothing is sent "
                               "anywhere, and the campaign ledger that stays empty until Amazon's own reports "
                               "supply a dated number."),
                  jsonld_blocks=[json_ld("measurement.html", "Measurement — events, privacy and the empty ledger",
                                         "Five defined measurement events, a no-cookie on-device counter, and an "
                                         "empty campaign ledger gated on dated provenance from authorised reports.")])


'''
sub('''def page_category():''', NEW_PAGES.lstrip('\n') + '''
def page_category():''', label='new-pages')

# ================================================================ 2. register them
sub('''    pages["questions.html"] = page_questions()''',
    '''    pages["questions.html"] = page_questions()
    # Pass 13 (2026-11-17): the link record and the measurement layer.
    pages["links.html"] = page_links()
    pages["measurement.html"] = page_measurement()''', label='pages-dict')

sub('''    ("questions.html", "Questions and gaps", "Known facts, missing answers and discovery steps"),''',
    '''    # Added 2026-11-17 (arena/3093e674-zone1): the two trust surfaces the owner's brief of
    # that date asked for - what each submitted link is meant to point at, and what is counted.
    ("links.html", "Link record", "Intended product vs observed destination, and the tag we publish"),
    ("measurement.html", "Measurement", "Five events, counted on your device, sent nowhere"),
    ("questions.html", "Questions and gaps", "Known facts, missing answers and discovery steps"),''',
    label='nav-entries')

# sidebar: one entry each in the two groups a reader/owner would look in
sub('''      {N("compliance.html")}
      {N("flagged.html")}
      {N("data.html")}
      {N("reverification.html")}''',
    '''      {N("compliance.html")}
      {N("flagged.html")}
      {N("links.html")}
      {N("data.html")}
      {N("reverification.html")}''', label='sidebar-trust')

sub('''      {N("questions.html")}
      {N("requirements.html")}''',
    '''      {N("questions.html")}
      {N("measurement.html")}
      {N("requirements.html")}''', label='sidebar-owner')

p.write_text(s, encoding='utf-8')
print('patched build.py part 2:', len(orig), '->', len(s))
