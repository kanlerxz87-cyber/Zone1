import re, sys, pathlib

p = pathlib.Path('build.py')
s = p.read_text(encoding='utf-8')
orig = s


def sub(old, new, count=1, label=''):
    global s
    n = s.count(old)
    if n != count:
        print(f'!! MISS [{label}] expected {count} got {n}: {old[:70]!r}')
        sys.exit(1)
    s = s.replace(old, new, count)
    print(f'ok [{label}]')


# ---------------------------------------------------------------- 1. published values + row gate
sub('''def _published_values():
    """Every value string this build publishes for a product, for placeholder checks."""
    global _PRODUCT_VALUES
    if _PRODUCT_VALUES is not None:
        return _PRODUCT_VALUES
    vals = set()
    for p in PRODUCT_LIST:''',
    '''def _published_values():
    """Every value string this build publishes for a product, for placeholder checks.

    Candidates (the two products the brief added on 2026-11-17) are included on purpose: an
    article may only quote a number this register already publishes, and that rule has to hold
    for the new rows too or the anti-drift guard becomes a three-product guard again.
    """
    global _PRODUCT_VALUES
    if _PRODUCT_VALUES is not None:
        return _PRODUCT_VALUES
    vals = set()
    for p in list(PRODUCT_LIST) + list(CANDIDATE_LIST):''', label='published-values-loop1')

sub('''    # Values the dataset states inside an evidence/note string are still published;
    # scan those too so a quoted dimension can be cited without re-typing it.
    for p in PRODUCT_LIST:''',
    '''    # Values the dataset states inside an evidence/note string are still published;
    # scan those too so a quoted dimension can be cited without re-typing it.
    for p in list(PRODUCT_LIST) + list(CANDIDATE_LIST):''', label='published-values-loop2')

sub('''def check_rows_have_sources():
    """Build-time guard: an asserted value with no source id is a hard failure."""
    problems = []
    for p in PRODUCT_LIST:''',
    '''def check_rows_have_sources():
    """Build-time guard: an asserted value with no source id is a hard failure."""
    problems = []
    for p in list(PRODUCT_LIST) + list(CANDIDATE_LIST):''', label='row-sources-gate')

# ---------------------------------------------------------------- 2. product page CTA page_key
sub('{product_cta(p, prefix="../")}',
    '{product_cta(p, prefix="../", page_key=f"product/{p[\'slug\']}")}', label='product-cta-call')

# ---------------------------------------------------------------- 3. category table gets a CTA
sub('''          <td class="blank">not displayed {src_link("S2")}</td>
          <td>{len(p['flags'])}</td>
        </tr>"""
        for p in PRODUCT_LIST
    )''',
    '''          <td class="blank">not displayed {src_link("S2")}</td>
          <td>{len(p['flags'])}</td>
          <td>{cta_inline(p, "../", f"category/{p['slug']}")}</td>
        </tr>"""
        for p in PRODUCT_LIST
    )''', label='category-cta-cell')

sub('''    <th>#</th><th>Product</th><th>Brand</th><th>ASIN</th><th>Capacity (verified)</th>
    <th>Brand list price</th><th>Amazon price</th><th>Flags</th>''',
    '''    <th>#</th><th>Product</th><th>Brand</th><th>ASIN</th><th>Capacity (verified)</th>
    <th>Brand list price</th><th>Amazon price</th><th>Flags</th><th>Go to the listing</th>''',
    label='category-cta-head')

# a compact CTA fragment, defined next to product_cta
sub('''def spec_table(p, prefix=""):''',
    '''def cta_inline(p, prefix="", page_key=None):
    """The one-line version of the buy block, for tables and cards.

    Money pages that make a reader decide should let a reader act on the decision. Until
    2026-11-17 the only outbound link on the whole site sat on the three product pages, which
    is why the comparison and the category table read like a report: SG-25 proposed one CTA
    pattern on every money page, and this is that pattern in its compact form. The link is the
    same tagged canonical URL the product page uses, built by the same function.
    """
    url, state = amazon_out_link(p["asin"]["v"], page_key)
    label = "Open on Amazon" if state != "untagged" else "Open on Amazon (earns nothing yet)"
    return (f'<a class="btn btn-sm" href="{e(url)}" target="_blank" rel="nofollow sponsored noopener" '
            f'data-z1k="outlink" data-asin="{e(p["asin"]["v"])}">{e(label)} <span aria-hidden="true">↗</span></a>'
            f'<span class="tiny muted affiliate-tag">Affiliate link</span>')


def spec_table(p, prefix=""):''', label='cta-inline-def')

# ---------------------------------------------------------------- 4. affiliate host coverage
sub('''    return re.sub(r'<a\\b[^>]*' + AFFILIATE_HOST + r'[^>]*>', fix, html_text, flags=re.I)''',
    '''    return re.sub(AFFILIATE_ANCHOR, fix, html_text, flags=re.I)''', label='qualify-regex')

sub('''AFFILIATE_HOST = "link.amazon"''',
    '''AFFILIATE_HOST = "link.amazon"
# Extended 2026-11-17 (arena/3093e674-zone1). The site's product CTAs used to be the short
# links only, so matching `link.amazon` covered every clickable affiliate anchor. Now that the
# CTAs are tagged canonical detail pages, a guard that looks at only the shortener would let an
# unqualified sponsored link through unnoticed - and Google's rule is about the paid link, not
# about which Amazon domain it happens to sit on. amazon.com/dp/ is matched rather than the
# whole host so that a citation to a department or category page keeps its plain rel.
AFFILIATE_HOSTS_RE = r"(?:" + AFFILIATE_HOST + r"|www\\.amazon\\.com/dp/|amazon\\.com/dp/)"
AFFILIATE_ANCHOR = re.compile(r'<a\\b[^>]*' + AFFILIATE_HOSTS_RE + r'[^>]*>', re.I)''',
    label='affiliate-host-regex')

sub('''    anchor = re.compile(r'<a\\b[^>]*' + AFFILIATE_HOST + r'[^>]*>', re.I)
    problems = []
    for rel, html_text in pages.items():
        for tag in anchor.findall(html_text):''',
    '''    anchor = AFFILIATE_ANCHOR
    problems = []
    for rel, html_text in pages.items():
        for tag in anchor.findall(html_text):''', label='qualification-guard-regex')

p.write_text(s, encoding='utf-8')
print('patched build.py part 1:', len(orig), '->', len(s))
