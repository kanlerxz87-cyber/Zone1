import pathlib, sys

p = pathlib.Path('build.py'); s = p.read_text()
f = []


def lit(old, new, label):
    global s
    if new in s and old not in s:
        print('already', label); return
    if s.count(old) != 1:
        f.append((label, s.count(old))); return
    s = s.replace(old, new, 1); print('ok', label)


# 1. picks card: cta_inline takes the product dict, and the page key namespaces any sub-tag
lit("""  {cta_inline(p['slug'])}""",
    """  {cta_inline(p, "", f"picks/{p['slug']}")}""", 'picks-cta-args')

# 2. comparison matrix: a CTA row, so the decision made here can be acted on here (SG-39)
lit("""        rows.append(f'<tr><td><strong>{e(label)}</strong></td>{"".join(cells)}</tr>')""",
    '''        rows.append(f'<tr><td><strong>{e(label)}</strong></td>{"".join(cells)}</tr>')
    # The last row is the only one allowed to be an action rather than a field. A reader who has
    # just worked through the blanks should not have to navigate back to a product page to act on
    # the decision - and the link must be the same tagged URL the product page uses, so it cannot
    # drift out of compliance. Candidate specs never appear here: this table is PRODUCT_LIST only.
    rows.append('<tr class="cta-footrow"><td><strong>Open the model on Amazon</strong>'
                '<div class="tiny muted">Same tagged link as the product page; the listing is the '
                'place that states a price.</div></td>'
                + "".join('<td>' + cta_inline(p, "../", "compare/" + p["slug"]) + '</td>'
                          for p in PRODUCT_LIST)
                + '</tr>')''', 'compare-cta-row')

p.write_text(s)
if f:
    print("\n".join(f'!! MISS [{n}] found {c}' for n, c in f)); sys.exit(1)
import ast; ast.parse(s); print('parses OK', len(s))
