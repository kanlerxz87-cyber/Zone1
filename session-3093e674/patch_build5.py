import pathlib, sys

P = pathlib.Path('build.py')
s = P.read_text()
fails = []


def lit(old, new, label):
    """Exact-substring patch, counted. Replacement is used verbatim - no regex escaping games."""
    global s
    if new in s and old not in s:
        print('already', label); return
    n = s.count(old)
    if n != 1:
        fails.append((label, n)); return
    s = s.replace(old, new, 1)
    print('ok', label)


# ---------------------------------------------------------------- 0. datetime for the expiry guard
lit('import html\nimport json', 'import datetime\nimport html\nimport json', 'import-datetime')

# ---------------------------------------------------------------- 1. picks cards get the CTA
lit(r'''  <a class="pick-cta" href="products/{e(p['slug'])}.html">Read the sourced breakdown \u2192</a>
</article>''',
    r'''  <a class="pick-cta" href="products/{e(p['slug'])}.html">Read the sourced breakdown \u2192</a>
  {cta_inline(p['slug'])}
</article>''', 'picks-cta')

# ---------------------------------------------------------------- 2. index: the link-status callout names the scope split
lit('''· <a href="questions.html#q-03">Account-status question</a>.</p>''',
    '''· <a href="questions.html#q-03">Account-status question</a> · <a href="links.html">Full link record</a>.</p>
  <p class="small"><strong>Scope, as at 2026-11-17.</strong> The project brief names five product links and this guide markets three of them: the other two resolve to meat thermometers, are recorded with their sources on the <a href="links.html">link record</a>, and are <strong>not</strong> marketed or recommended by these pages until the owner settles <a href="questions.html#q-27">the scope question</a>.</p>''',
    'index-scope-note')

# ---------------------------------------------------------------- 3. index: the four buyer questions, above the format guide
BAND = '''
<section id="start-with-a-question" class="qband" aria-label="Four questions worth asking first">
  <div class="section-heading">
    <p class="section-eyebrow">Start with the question, not the model</p>
    <h2>Four things a shopper asks before they narrow it down.</h2>
    <p class="small muted">Each one is an article that answers it from manufacturer documents and manuals \u2014 no tester, no video, no invented hands-on verdict.</p>
  </div>
  <div class="grid grid-4 qgrid">
    <article class="card qcard"><p class="qnum">Q1</p>
      <h3>Basket or countertop oven?</h3>
      <a href="articles/dual-basket-vs-oven-air-fryer.html">Two formats, on their documented differences \u2192</a></article>
    <article class="card qcard"><p class="qnum">Q2</p>
      <h3>How much capacity do I actually need?</h3>
      <a href="articles/air-fryer-capacity-guide.html">What a quart is a measurement of \u2192</a></article>
    <article class="card qcard"><p class="qnum">Q3</p>
      <h3>Will it be a pain to clean and store?</h3>
      <a href="articles/small-kitchen-air-fryer-dimensions.html">The footprint numbers, then the clearance \u2192</a></article>
    <article class="card qcard"><p class="qnum">Q4</p>
      <h3>What should I ask before a multi-function machine?</h3>
      <a href="articles/questions-before-a-multi-function-appliance.html">Seven questions, in order \u2192</a></article>
  </div>
</section>

'''
lit('<section id="quick-guide" class="quick-guide">', BAND + '<section id="quick-guide" class="quick-guide">',
    'index-qband')

# ---------------------------------------------------------------- 4. CSS for the band
lit('.cta-row { margin-top:.6rem; }',
    '''.cta-row { margin-top:.6rem; }
.qband { padding:1.6rem 0 .4rem; border-top:1px solid var(--line); }
.qgrid { align-items:stretch; }
.qcard { padding:1rem 1.1rem; }
.qcard h3 { font-size:1.02rem; margin:.25rem 0 .45rem; line-height:1.3; }
.qcard a { font-size:.86rem; }
.qnum { font-family:var(--mono); font-size:.68rem; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin:0; }''',
    'css-qband')

# ---------------------------------------------------------------- 5. seasonal scope block in page_article
lit('''def page_article(a):
    prods = ""''',
    '''def page_article(a):
    # A seasonal page carries its validity window in the register so the page itself states what it
    # was written for and when it stops being true. Program Policies 2(b) requires that references
    # to limited-time promotions come down "as soon as that promotion on the relevant Amazon Site
    # ends", so the date is data rather than somebody's memory: check_seasonal_expiry() stops the
    # build the day after it passes. Nothing here branches on today's date - the rendered page is
    # the same on every build of the same input, which is what keeps the generator deterministic.
    season = ""
    if a.get("season"):
        sd = a["season"]
        season = (f'<div class="callout info" id="season-scope">'
                  f'<div class="link-status-heading"><span class="pill pill-warn">Seasonal</span>'
                  f'<strong>{e(sd["scope"])}</strong></div>'
                  f'<p class="small">Validity recorded in the article register: written for '
                  f'{e(sd["window"])}, and this page stops being true on <strong>{e(sd["expires"])}</strong>. '
                  f'Past that date the generator refuses to build until someone re-dates it with a fresh read '
                  f'or takes the row out of the register. What is not claimed here: any price, discount or '
                  f'stock figure \u2014 '
                  f'{e(sd["no_price_claims"])}</p></div>')
    prods = ""''', 'article-season-var')

# ---------------------------------------------------------------- 6. render it above the product callout
lit('''{prods}

{article_body(a)}''',
    '''{season}
{prods}

{article_body(a)}''', 'article-season-render')

# ---------------------------------------------------------------- 7. the guard
lit('def check_campaign_ledger():',
    '''def check_seasonal_expiry():
    """A seasonal article must carry a validity window, and the build stops the day after it closes.

    Program Policies 2(b), read live 2026-11-17: "You must remove from your Site any links and
    related references to limited time promotions as soon as that promotion on the relevant Amazon
    Site ends." This site publishes a Black Friday investigation and a holiday gift guide, so the
    duty is real and it is dated. Enforcing it in the generator is the only version that survives a
    busy owner: the failure is loud, and it names the two permitted remedies instead of tempting
    anyone to ship a stale page quietly.

    Rules: a season block needs all five fields; the dates must parse; expires must fall after the
    window opens; and today must still be inside the window. The gate reads the calendar, which is
    the one place this generator looks at a date - so the check can fail on a day, while the
    rendered output never depends on one and stays reproducible.
    """
    problems = []
    today = datetime.date.today().isoformat()
    for a in ARTICLES["articles"]:
        sd = a.get("season")
        if not sd:
            continue
        slug = a["slug"]
        missing = [k for k in ("label", "window", "expires", "scope", "no_price_claims") if not sd.get(k)]
        if missing:
            problems.append(f'{slug}: season block is missing {", ".join(missing)}')
            continue
        try:
            w0 = datetime.date.fromisoformat(sd["window"].split(" to ")[0])
            exp = datetime.date.fromisoformat(sd["expires"])
        except ValueError as exc:
            problems.append(f'{slug}: season dates must be ISO dates ({exc})')
            continue
        if exp <= w0:
            problems.append(f'{slug}: season expires {sd["expires"]} on or before its window opens ({sd["window"]})')
        if today > sd["expires"]:
            problems.append(
                f'{slug}: its seasonal window closed on {sd["expires"]} and the page is still live. Decide, '
                f'do not defer: re-date window/expires against a fresh read of the sources and record the '
                f'choice on decision-log.html, or take the article row out of data/articles.json so the page '
                f'leaves the sitemap, the feed and the nav (its URL then 404s, so add the removal to '
                f'flagged-entries-style disclosure rather than doing it silently)')
    return problems


def check_campaign_ledger():''', 'guard-seasonal-def')

# ---------------------------------------------------------------- 8. wire it
lit('''    ledger_problems = check_campaign_ledger()''',
    '''    season_problems = check_seasonal_expiry()
    if season_problems:
        raise SystemExit("BUILD FAILED - a seasonal page has outlived the promotion it describes (Amazon "
                         "Program Policies 2(b) requires those references to come down when the promotion ends):\\n  "
                         + "\\n  ".join(season_problems))
    ledger_problems = check_campaign_ledger()''', 'guard-seasonal-wire')

P.write_text(s)
if fails:
    print("\n".join(f'!! MISS [{n}]  found {c}' for n, c in fails)); sys.exit(1)
import ast
ast.parse(s)
print('bytes', len(s), 'parses OK')
