"""Pass 13, patch 4: every measurement table row carries a source link.

The site's own rule is that a table row stating something must link to where that
thing came from. These rows state what this repository defines, so the source is
the defining file in this repository on GitHub - which the row-source gate counts,
because GitHub is the official host for a fact about the repository itself.
"""
import sys

P = "build.py"
s = open(P, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit(f"expected {count} occurrence(s), found {n} of:\n{old[:300]}")
    s = s.replace(old, new)


sub(
    'def page_measurement():\n    event_rows = "".join(\n',
    'def page_measurement():\n'
    '    # These tables define this repository\'s own measurement contract, so each row\n'
    '    # cites the file that defines it. A row with no source fails the build.\n'
    '    repo_analytics = repo_link("data/analytics.json")\n'
    '    repo_ledger = repo_link("data/ledger.json")\n'
    '    event_rows = "".join(\n',
)

sub(
    '          <td class="small">{e(x["status"])}</td>\n        </tr>"""\n',
    '          <td class="small">{e(x["status"])}<div class="tiny">{repo_analytics}</div></td>\n'
    '        </tr>"""\n',
)

sub(
    '    <tr><td>URL</td><td>{endpoint_cell}</td></tr>\n'
    '    <tr><td>Method</td><td><code class="tiny">{e(ep.get("method", ""))}</code> &middot; <code class="tiny">{e(ep.get("content_type", ""))}</code></td></tr>\n'
    '    <tr><td>Kind</td><td>{e(ep.get("kind", ""))} &mdash; reference implementation at <code class="tiny">{e(ep.get("reference_implementation", ""))}</code></td></tr>\n'
    '    <tr><td>Why it is blank</td><td class="small">{e(ep.get("why_blank", ""))}</td></tr>\n',
    '    <tr><td>URL</td><td>{endpoint_cell}<div class="tiny">{repo_analytics}</div></td></tr>\n'
    '    <tr><td>Method</td><td><code class="tiny">{e(ep.get("method", ""))}</code> &middot; <code class="tiny">{e(ep.get("content_type", ""))}</code><div class="tiny">{repo_analytics}</div></td></tr>\n'
    '    <tr><td>Kind</td><td>{e(ep.get("kind", ""))} &mdash; reference implementation at <code class="tiny">{e(ep.get("reference_implementation", ""))}</code><div class="tiny">{repo_analytics}</div></td></tr>\n'
    '    <tr><td>Why it is blank</td><td class="small">{e(ep.get("why_blank", ""))}<div class="tiny">{repo_analytics}</div></td></tr>\n',
)

sub(
    "        f'<tr><td><code class=\"tiny\">{e(k)}</code></td><td class=\"small\">{e(v)}</td></tr>'\n",
    "        f'<tr><td><code class=\"tiny\">{e(k)}</code></td>'\n"
    "        f'<td class=\"small\">{e(v)}<div class=\"tiny\">{repo_analytics}</div></td></tr>'\n",
)

sub(
    '        f"""<tr><td><code class="tiny">{e(c["name"])}</code></td>\n'
    '          <td class="small">{e(c["type"])}</td>\n'
    '          <td class="small">{e(c["meaning"])}</td>\n'
    '          <td class="blank">&mdash; empty &mdash;</td></tr>"""\n',
    '        f"""<tr><td><code class="tiny">{e(c["name"])}</code></td>\n'
    '          <td class="small">{e(c["type"])}</td>\n'
    '          <td class="small">{e(c["meaning"])}</td>\n'
    '          <td class="blank">&mdash; empty &mdash;<div class="tiny">{repo_ledger}</div></td></tr>"""\n',
)

sub(
    "        f'<tr><td>{e(p[\"date\"])}</td><td class=\"small\">{e(p[\"action\"])}</td>'\n"
    "        f'<td class=\"small muted\">{e(p[\"by\"])}</td><td class=\"small muted\">{e(p.get(\"note\", \"\"))}</td></tr>'\n",
    "        f'<tr><td>{e(p[\"date\"])}</td><td class=\"small\">{e(p[\"action\"])}</td>'\n"
    "        f'<td class=\"small muted\">{e(p[\"by\"])}</td>'\n"
    "        f'<td class=\"small muted\">{e(p.get(\"note\", \"\"))}<div class=\"tiny\">{repo_ledger}</div></td></tr>'\n",
)

open(P, "w", encoding="utf-8").write(s)
print("patch 4 applied")
