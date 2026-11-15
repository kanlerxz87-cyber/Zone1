#!/usr/bin/env python3
"""One-shot patch: add BreadcrumbList JSON-LD to the pages that did not yet have it.

Applied by session arena/88bb2db6 on 2026-11-15. Same assertion rule as
apply_jsonld.py: every replacement must match exactly once.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

# page file -> (human label used in the breadcrumb, the exact layout(...) call tail)
PATCHES = [
    (
        '''    return layout("compliance.html", "Compliance", body, active="compliance.html",''',
        '''    return layout("compliance.html", "Compliance", body, active="compliance.html",''',
        "Compliance",
    ),
    (
        '''    return layout("data.html", "Full dataset", body, active="data.html",''',
        '''    return layout("data.html", "Full dataset", body, active="data.html",''',
        "Full dataset",
    ),
    (
        '''    return layout("executive-summary.html", "Executive summary", body, active="executive-summary.html",''',
        '''    return layout("executive-summary.html", "Executive summary", body, active="executive-summary.html",''',
        "Executive summary",
    ),
    (
        '''    return layout("flagged.html", "Flagged for review", body, active="flagged.html",''',
        '''    return layout("flagged.html", "Flagged for review", body, active="flagged.html",''',
        "Flagged for review",
    ),
    (
        '''    return layout("guides/buying-guide-air-fryers.html", "Buying guide", body,''',
        '''    return layout("guides/buying-guide-air-fryers.html", "Buying guide", body,''',
        "Buying guide",
    ),
    (
        '''    return layout("platform.html", "Platform blueprint", body, active="platform.html",''',
        '''    return layout("platform.html", "Platform blueprint", body, active="platform.html",''',
        "Platform blueprint",
    ),
    (
        '''    return layout("previous-passes.html", "Previous passes", body,''',
        '''    return layout("previous-passes.html", "Previous passes", body,''',
        "Previous passes",
    ),
    (
        '''    return layout("reverification.html", f"Re-verification {rev['pass_date']}", body,''',
        '''    return layout("reverification.html", f"Re-verification {rev['pass_date']}", body,''',
        "Re-verification",
    ),
    (
        '''    return layout("marketing-directions.html", "Suggestions", body, active="marketing-directions.html",''',
        '''    return layout("marketing-directions.html", "Suggestions", body, active="marketing-directions.html",''',
        "Suggestions (parallel pass)",
    ),
    (
        '''    return layout("decision-gate.html", "Questions and information gaps", body, active="decision-gate.html",''',
        '''    return layout("decision-gate.html", "Questions and information gaps", body, active="decision-gate.html",''',
        "Questions and gaps (parallel pass)",
    ),
]


def make_ld(page_rel, label):
    return (
        "jsonld_blocks=[breadcrumbs_jsonld([\n"
        '        ("Home", SITE_URL + "/"),\n'
        f'        ("{label}", page_url("{page_rel}")),\n'
        "    ])]"
    )


def patch_call(text, page_rel, label):
    """Append the jsonld_blocks keyword to a layout(...) call."""
    # Find the call, then insert the keyword before its closing paren.
    start = text.index("layout(" + '"' + page_rel + '"')
    # walk to the matching close paren of this call
    i = text.index("(", start)
    depth = 0
    j = i
    while True:
        ch = text[j]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    inner = text[i + 1:j]
    # The call ends with a description=... argument; add a comma and the keyword.
    if "jsonld_blocks" in inner:
        return text
    new_inner = inner.rstrip()
    if not new_inner.endswith(","):
        new_inner += ","
    new_inner += "\n                  " + make_ld(page_rel, label) + "\n              "
    return text[:i + 1] + new_inner + text[j:]


for anchor, _same, label in PATCHES:
    if s.count(anchor) != 1:
        raise SystemExit(f"PATCH FAILED — anchor matched {s.count(anchor)} times: {anchor}")
    page_rel = anchor.split('layout("')[1].split('"')[0]
    s = patch_call(s, page_rel, label)

p.write_text(s, encoding="utf-8")
print(f"added breadcrumbs to {len(PATCHES)} pages")
