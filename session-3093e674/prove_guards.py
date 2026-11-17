"""Prove each new guard fails in the direction that matters, then restore the tree exactly.

Every case mutates a register or the shipped JavaScript, runs the generator, records the exit status
and the first line of its complaint, then puts the file back byte-for-byte. A guard that has never been
seen to fire is a sentence about a guard, which is the thing this repository keeps finding out.
"""
import json, pathlib, subprocess, sys, collections

ROOT = pathlib.Path('.')
OD = collections.OrderedDict


def run():
    r = subprocess.run([sys.executable, 'build.py'], capture_output=True, text=True, cwd=ROOT)
    out = (r.stdout + r.stderr).strip().splitlines()
    first = next((l for l in out if 'BUILD FAILED' in l or 'Traceback' in l), out[0] if out else '')
    detail = ''
    for i, l in enumerate(out):
        if 'BUILD FAILED' in l and i + 1 < len(out):
            detail = out[i + 1].strip()
            break
    return r.returncode, first, detail


def case(name, mutate, expect_fail=True):
    targets = ['build.py', 'data/config.json', 'data/questions.json', 'data/campaign-ledger.json',
               'data/link-intent.json', 'data/articles.json', 'assets/app.js', 'data/measurement.json']
    saved = {t: (ROOT / t).read_bytes() for t in targets}
    try:
        mutate()
        code, first, detail = run()
        verdict = 'FIRED' if code != 0 else 'silent'
        ok = (code != 0) == expect_fail
        print(f'{"PASS" if ok else "FAIL"}  {name:52s} exit={code} {verdict}')
        print(f'        {first[:120]}')
        if detail:
            print(f'        {detail[:150]}')
        return ok
    finally:
        for t, blob in saved.items():
            (ROOT / t).write_bytes(blob)


def jload(p):
    return json.load(open(p, encoding='utf-8'), object_pairs_hook=OD)


def jsave(p, d):
    json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)


results = []

# 1. a money CTA that loses its tag must stop the build
def m1():
    cfg = jload('data/config.json'); cfg['associate_tag'] = ""
    jsave('data/config.json', cfg)
results.append(case('check_special_links: tag removed from config', m1))

# 2. a malformed tag must stop the build
def m2():
    cfg = jload('data/config.json'); cfg['associate_tag'] = "shop now-20"
    jsave('data/config.json', cfg)
results.append(case('check_special_links: tag violates XXXXX-## shape', m2))

# 3. intended and observed must not be merged into a "confirmed" product without the owner
def m3():
    li = jload('data/link-intent.json')
    rec = li['records'][0]
    rec['observed']['final_asin'] = rec['intended']['asin']
    jsave('data/link-intent.json', li)
results.append(case('check_link_intent: a row merges intended into observed', m3))

# 4. the campaign ledger must refuse a row with no provenance, and any revenue field at all
def m4a():
    led = jload('data/campaign-ledger.json')
    led['rows'].append(OD([("period_start", "2026-11-01"), ("period_end", "2026-11-07"),
                           ("impressions", 100)]))
    jsave('data/campaign-ledger.json', led)
results.append(case('check_campaign_ledger: row with no source or date', m4a))


def m4b():
    led = jload('data/campaign-ledger.json')
    led['rows'].append(OD([("period_start", "2026-11-01"), ("period_end", "2026-11-07"),
                           ("source", "https://affiliate-program.amazon.com/reports"),
                           ("obtained_on", "2026-11-17"), ("revenue", "340.00")]))
    jsave('data/campaign-ledger.json', led)
results.append(case('check_campaign_ledger: a revenue field appears', m4b))

# 5. the counter must not be able to become a tracker
def m5():
    # assets/app.js is emitted from the JS constant, so the file on disk cannot be the input to
    # this test - the mutation has to go where a later pass would put it, in the generator.
    b = pathlib.Path('build.py'); src = b.read_text()
    marker = 'JS = r' + chr(34) * 3
    assert src.count(marker) == 1, src.count(marker)
    b.write_text(src.replace(marker, marker + "\nfetch('/collect');", 1))
results.append(case('check_measurement_contract: fetch() added to the shipped JS', m5))


def m5b():
    # The other half of the contract: a page may not keep claiming "runs no analytics" once an
    # endpoint is configured.
    cfg = jload('data/config.json'); cfg['analytics_endpoint'] = "https://collect.example/1x1"
    jsave('data/config.json', cfg)
results.append(case('check_measurement_contract: endpoint set, pages still say no analytics', m5b))

# 6. a seasonal page cannot outlive the promotion it describes
def m6():
    art = jload('data/articles.json')
    for a in art['articles']:
        if a['slug'] == 'black-friday-model-number-switch':
            a['season']['expires'] = "2026-11-01"
    jsave('data/articles.json', art)
results.append(case('check_seasonal_expiry: window already closed', m6))

# 7. the published-page guard must reject a question id that is not in the register
def m7():
    q = jload('data/questions.json')
    q['questions'] = [x for x in q['questions'] if x['id'] != 'Q-27']
    jsave('data/questions.json', q)
results.append(case('cross-reference guard: a cited question is deleted', m7))

# Rebuild from the restored tree so no generated page is left holding a mutant's output: the
# generator is deterministic, so this lands the files back exactly where they were before the run.
code, first, _ = run()
print(f'\npost-restore rebuild exit={code} {first[:80]}')
print(f'{sum(1 for r in results if r)}/{len(results)} guards proven to fire')
sys.exit(0 if all(results) else 1)
