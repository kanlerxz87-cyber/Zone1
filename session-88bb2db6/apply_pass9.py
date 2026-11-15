#!/usr/bin/env python3
"""One-shot patch: render pass 9 on the re-verification page.

Applied by session arena/88bb2db6 on 2026-11-15. Follows the additive pattern the
repo already uses for pass 6 and pass 7: a JSON ledger inside the session's own
folder, rendered as its own section, so no other session's file is edited and a
future session can drop the folder without touching anything else.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

# ---------------------------------------------------------------- load the ledger
old_load = '''_p7 = ROOT / "session-052f2c9f" / "pass7.json"
PASS7 = json.loads(_p7.read_text(encoding="utf-8")) if _p7.exists() else None
'''
new_load = '''_p7 = ROOT / "session-052f2c9f" / "pass7.json"
PASS7 = json.loads(_p7.read_text(encoding="utf-8")) if _p7.exists() else None
# Additive pass-9 ledger (2026-11-15, arena/88bb2db6): the final-integration re-read.
# Same additive pattern as passes 6 and 7 - owned entirely by this session's folder,
# so a later session can drop the file without touching anything else.
_p9 = ROOT / "session-88bb2db6" / "pass9.json"
PASS9 = json.loads(_p9.read_text(encoding="utf-8")) if _p9.exists() else None
'''
if s.count(old_load) != 1:
    raise SystemExit("load PATCH FAILED")
s = s.replace(old_load, new_load)

# ---------------------------------------------------------------- render the section
old_block = '''    lr = rev.get("link_resolution") or {}
    lr_html = ""'''
new_block = '''    # ---- pass-9 addendum (arena/88bb2db6): final-integration re-read, 2026-11-15 ----
    p9_html = ""
    if PASS9:
        p9 = PASS9

        def p9row(t):
            cls, label = REV_VERDICT[t["verdict"]]
            return (
                f'<tr><td><strong>{e(t["claim"])}</strong></td>'
                f'<td class="small">{e(t["published_value"])}</td>'
                f'<td class="small">{e(t["observed"])}</td>'
                f'<td><span class="pill {cls}">{e(label)}</span></td>'
                f'<td class="small"><a href="{e(t["source_url"])}" target="_blank" rel="noopener">'
                f'{e(t["source_label"])}</a></td></tr>'
            )

        p9rows = "".join(p9row(t) for t in p9["rows"])
        p9ev = "".join(
            f'<div class="callout info" style="margin:.6rem 0">'
            f'<strong>{e(x["title"])}</strong>'
            f'<p class="small">{e(x["detail"])}</p>'
            f'<p class="tiny muted">Flag {e(x["flag"])} · '
            f'<a href="{e(x["source_url"])}" target="_blank" rel="noopener">{e(x["source_label"])}</a>'
            f'</p></div>'
            for x in p9["new_evidence"]
        )
        p9_conf = sum(1 for t in p9["rows"] if t["verdict"] == "confirmed")
        p9_confl = sum(1 for t in p9["rows"] if t["verdict"] in ("conflict-live", "conflict-resolved"))
        p9_html = f"""
<h2>Pass 9 — final-integration re-read ({e(p9['pass_date'])}, arena/88bb2db6)</h2>
<p class="small">{e(p9['lede'])}</p>
<p class="tiny muted"><strong>{p9_conf}</strong> of the {len(p9['rows'])} rows below were confirmed
against the live official source on {e(p9['pass_date'])};
<strong>{p9_confl}</strong> record a disagreement between official documents that is still open.
One new conflict was found and filed rather than resolved by guesswork.</p>
<div class="tablewrap">
<table>
  <caption>Pass-9 re-reads, {e(p9['pass_date'])}</caption>
  <thead><tr><th style="width:17%">Claim</th><th style="width:17%">Published value</th>
  <th style="width:42%">What the official source says</th><th style="width:12%">Verdict</th>
  <th style="width:12%">Source</th></tr></thead>
  <tbody>{p9rows}</tbody>
</table>
</div>

<h3>What pass 9 added beyond the re-reads</h3>
{p9ev}
<p class="tiny muted">{e(p9['scope_note'])}</p>
<p class="tiny muted">Raw observations for this pass are in
<code>session-88bb2db6/EVIDENCE-2026-11-15.md</code>.</p>
"""

    lr = rev.get("link_resolution") or {}
    lr_html = ""'''
if s.count(old_block) != 1:
    raise SystemExit("block PATCH FAILED")
s = s.replace(old_block, new_block)

old_use = '''{p7_html}
'''
new_use = '''{p7_html}
{p9_html}
'''
if s.count(old_use) != 1:
    raise SystemExit(f"use PATCH FAILED ({s.count(old_use)} matches)")
s = s.replace(old_use, new_use)

p.write_text(s, encoding="utf-8")
print("build.py patched: pass 9 ledger loaded and rendered")
