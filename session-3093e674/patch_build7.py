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


# 1. count tokens for the three registers this pass published, so their rows cannot type a total
lit('''        "n_guards": len(re.findall(r"^def check_", open(__file__).read(), re.M)),''',
    '''        "n_link_rows": len(LINK_INTENT.get("records") or []),
        "n_ledger_rows": len(LEDGER.get("rows") or []),
        "n_measure_events": len(MEASUREMENT.get("events") or []),
        "n_guards": len(re.findall(r"^def check_", open(__file__).read(), re.M)),''',
    'req-count-tokens')

# 2. the product page's buy block should be attributable once sub-tags exist
lit('''{product_cta(p, prefix="../")}''',
    '''{product_cta(p, prefix="../", page_key=f"product/{p['slug']}")}''', 'product-cta-pagekey')

p.write_text(s)
if f:
    print("\n".join(f'!! MISS [{n}] found {c}' for n, c in f)); sys.exit(1)
import ast; ast.parse(s); print('parses OK', len(s))
