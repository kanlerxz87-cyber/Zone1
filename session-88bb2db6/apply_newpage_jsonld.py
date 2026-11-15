#!/usr/bin/env python3
"""Post-merge: bring the three pages added by arena/792c279e up to the shared
SEO standard, and stop the 404 page from declaring a canonical URL.

Applied by session arena/88bb2db6 on 2026-11-15, immediately after resolving the
build.py rebase conflict against origin/main @ 8f40f04 (PR #71).

N1  picks.html, decisions.html and handover.html were added by arena/792c279e after
    this session had already wired JSON-LD into every page it knew about. They carry
    the canonical URL, the Open Graph tags and the Twitter card, but no structured
    data, so arena/792c279e's own build guard (check_seo_metadata) correctly fails
    the build. Each gets a breadcrumb block and, for picks.html, an ItemList of the
    three products it ranks. The blocks are built only from text the page already
    prints.

N2  The 404 page must not declare a canonical URL: a canonical on an error page
    tells a crawler to consolidate the URL that errored onto this one, which is the
    opposite of what should happen. The other session's guard says so explicitly.
    The 404 therefore keeps robots:noindex, drops the canonical link, and keeps a
    BreadcrumbList so the block is not empty.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

PATCHES = []


def sub(old, new, why):
    PATCHES.append((old, new, why))


# ---------------------------------------------------------------- N1
sub(
    '''    return layout("picks.html", "This week's picks \\u2014 three air fryers, three jobs", body,
                  active="picks.html",
                  description="A decision-rule picks page: which of three sourced air fryers wins which job, what one sale pays at each official commission rate, and what remains unconfirmed.")''',
    '''    purl = page_url("picks.html")
    ld = [
        {
            "@type": "ItemList",
            "@id": purl + "#picks",
            "name": "This week's picks - three air fryers, three jobs",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": pr["short_name"],
                    "url": page_url(f"products/{pr['slug']}.html"),
                }
                for i, pr in enumerate(PRODUCT_LIST, start=1)
            ],
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("This week's picks", purl),
        ]),
    ]
    return layout("picks.html", "This week's picks \\u2014 three air fryers, three jobs", body,
                  active="picks.html",
                  description="A decision-rule picks page: which of three sourced air fryers wins which job, what one sale pays at each official commission rate, and what remains unconfirmed.",
                  jsonld_blocks=ld)''',
    "N1a: picks.html gains an ItemList and a BreadcrumbList",
)

sub(
    '''    return layout("decisions.html", "Decisions \\u2014 niche, traffic, measurement and handover", body,
                  active="decisions.html",
                  description="Three decisions with scored options, a six-channel traffic plan, six metrics with their prerequisites, a pre-committed kill rule, and the five actions only the account holder can take.")''',
    '''    durl = page_url("decisions.html")
    ld = [breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Decisions", durl),
    ])]
    return layout("decisions.html", "Decisions \\u2014 niche, traffic, measurement and handover", body,
                  active="decisions.html",
                  description="Three decisions with scored options, a six-channel traffic plan, six metrics with their prerequisites, a pre-committed kill rule, and the five actions only the account holder can take.",
                  jsonld_blocks=ld)''',
    "N1b: decisions.html gains a BreadcrumbList",
)

sub(
    '''    return layout("handover.html", "Handover \\u2014 the five things only the account holder can do", body,
                  active="decisions.html",
                  description="Five owner actions totalling about an hour, each with the exact steps, the time required, the flags it closes and what to paste back.")''',
    '''    hurl = page_url("handover.html")
    ld = [breadcrumbs_jsonld([
        ("Home", SITE_URL + "/"),
        ("Decisions", page_url("decisions.html")),
        ("Handover", hurl),
    ])]
    return layout("handover.html", "Handover \\u2014 the five things only the account holder can do", body,
                  active="decisions.html",
                  description="Five owner actions totalling about an hour, each with the exact steps, the time required, the flags it closes and what to paste back.",
                  jsonld_blocks=ld)''',
    "N1c: handover.html gains a BreadcrumbList",
)

# ---------------------------------------------------------------- N2
sub(
    '''<link rel="canonical" href="{e(canonical)}">
<meta name="robots" content="{e("noindex" if page_rel == "404.html" else "index,follow,max-image-preview:large")}">''',
    '''{"" if page_rel == "404.html" else f'<link rel="canonical" href="{e(canonical)}">'}
<meta name="robots" content="{e("noindex" if page_rel == "404.html" else "index,follow,max-image-preview:large")}">''',
    "N2: the 404 page no longer declares a canonical URL",
)

for old, new, why in PATCHES:
    if s.count(old) != 1:
        raise SystemExit(f"PATCH FAILED ({s.count(old)} matches) - {why}\n{old[:160]}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print(f"applied {len(PATCHES)} patches")
for _o, _n, why in PATCHES:
    print("  -", why)
