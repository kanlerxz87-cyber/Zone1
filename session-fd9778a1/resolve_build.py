"""Resolve the build.py conflict hunks between origin/main and this pass's patch.

Run after `git apply --3way`, so "ours" is the merged main and "theirs" is pass 13. The four
regions are matched by what they contain rather than by position, and each choice is a
judgement about which pass owns that piece of the page:

  shopfront helpers (MERCH, merch_pair, price_line) ......... take pass 13 (main has none)
  front-page product card ................................... both, merged by hand
  front-page body after the cards ........................... keep main's publication layout:
      main deliberately replaced the inline comparison table and the metric strip with a
      single CTA to compare.html, which is the same requirement this pass was working to
      (S-01 "lead with the products, not the verification process"), resolved further.
  programme flags ......................................... keep main's F83/F84 and renumber
      this pass's five rows to F85-F89, ids shifted everywhere they are named.
"""
import re

SG_MAP = {f"SG-{i:02d}": f"SG-{i + 3:02d}" for i in range(36, 46)}
Q_MAP = {f"Q-{i:02d}": f"Q-{i + 2:02d}" for i in range(27, 38)}
TP_MAP = {f"TP-{i}": f"TP-{i + 2}" for i in (22, 23, 24)}
F_MAP = {f"F{i}": f"F{i + 2}" for i in range(83, 88)}
ALL = dict(SG_MAP)
ALL.update(Q_MAP)
ALL.update(TP_MAP)
ALL.update(F_MAP)
ALL["S38"] = "S43"
ID = re.compile(r"\b(" + "|".join(sorted((re.escape(k) for k in ALL), key=len, reverse=True)) + r")\b(?![0-9])")


def shift(s):
    return ID.sub(lambda m: ALL[m.group(1)], s)


CARD = '''  <p class="publication-job"><strong>{e(job)}</strong></p>
  <p class="small">{e(detail)} {src_links(job_sources)}</p>
  <dl class="publication-facts">
    <div><dt>Documented capacity</dt><dd>{e(cap_value)} {cap_sources}</dd></div>
    <div><dt>Published dimensions</dt><dd>{e(dimension_value)} {dimension_sources}</dd></div>
  </dl>
  {price_line(p)}
  {merch_pair(p)}
  <p class="tiny muted"><span class="pill pill-warn">Amazon model match unconfirmed</span>
    Candidate product record. The matching supplied link and intended listing remain unconfirmed.</p>
  <div class="pcard-cta">
    <a class="btn" href="{e(amazon_product_url(p['asin']['v']))}" target="_blank" rel="sponsored nofollow noopener">See it on Amazon <span aria-hidden="true">↑</span></a>
    <p class="tiny muted" style="margin:.45rem 0 0"><a href="products/{e(slug)}.html">Read the sourced product guide →</a></p>
  </div>
</article>""")
'''
CARD = CARD.replace("↑", "\u2197")

path = "build.py"
src = open(path, encoding="utf-8").read()
MARK = re.compile(r"<<<<<<< ours\n(.*?)^=======\n(.*?)^>>>>>>> theirs\n", re.S | re.M)
hunks = list(MARK.finditer(src))
print("hunks found:", len(hunks))

repl = []
kinds = []
for h in hunks:
    o, t = h.group(1).strip(), h.group(2).strip()
    print("  hunk@", src[:h.start()].count("\n") + 1, "| ours:", (o[:60] or "(empty)").replace("\n", " "),
          "| theirs:", (t[:60] or "(empty)").replace("\n", " "))
for h in hunks:
    ours, theirs = h.group(1).rstrip("\n"), h.group(2).rstrip("\n")
    if "publication-job" in ours and "pcard-cta" in theirs:
        kinds.append("card")
        endtok = '</article>""")'
        keep = ours[ours.index(endtok) + len(endtok):].strip("\n")
        repl.append(CARD.rstrip("\n") + ("\n" + keep if keep else ""))
    elif "The three, side by side" in theirs:
        kinds.append("front-page layout")
        repl.append(ours)
    elif re.search(r'^\s*\("F\d+"', theirs, re.M) and re.search(r'^\s*\("F\d+"', ours, re.M):
        kinds.append("flags")
        # my patch carries the two rows that precede its insertion point, and main has those
        # rows too - take only this pass's new tuples, starting at its first one.
        mine = theirs[re.search(r'^\s*\("F83"', theirs, re.M).start():]
        repl.append(ours + "\n" + shift(mine))
    elif not ours:
        kinds.append("shopfront helpers")
        repl.append(theirs)
    else:
        raise SystemExit("unrecognised hunk:\n" + (ours or "(empty)")[:200] + "\n---\n" + theirs[:200])

out = src
for h, text in zip(reversed(hunks), reversed(repl)):
    out = out[:h.start()] + text + "\n" + out[h.end():]
open(path, "w", encoding="utf-8").write(out)
print("resolved:", kinds)
print("markers left:", out.count("<<<<<<<"), "| id refs shifted in the flag block:",
      all(x in out for x in ('("F85"', '("F89"', '"S43"')))
