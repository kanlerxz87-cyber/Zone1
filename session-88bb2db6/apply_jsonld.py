#!/usr/bin/env python3
"""One-shot patch: wire JSON-LD, canonical and social cards into build.py.

Applied by session arena/88bb2db6 on 2026-11-15. Every replacement asserts the
exact original text, so the script fails loudly rather than silently mis-patching.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

PATCHES = []


def sub(old, new):
    PATCHES.append((old, new))


# ---------------------------------------------------------------- landing page
sub(
    '''    return layout("index.html", "Air fryer buying guide", body, active="index.html",
                  description="A source-led comparison of three air-fryer formats, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.")''',
    '''    ld = [
        PUBLISHER,
        {
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "url": SITE_URL + "/",
            "name": SITE_NAME,
            "description": SITE_TAGLINE,
            "inLanguage": "en-US",
            "publisher": {"@id": SITE_URL + "/#organization"},
        },
        breadcrumbs_jsonld([("Home", SITE_URL + "/")]),
        {
            "@type": "ItemList",
            "@id": SITE_URL + "/#formats",
            "name": "Three air-fryer formats compared",
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
    ]
    return layout("index.html", "Air fryer buying guide", body, active="index.html",
                  description="A source-led comparison of three air-fryer formats, with manufacturer specifications, visible gaps and the status of the supplied Amazon links.",
                  jsonld_blocks=ld)''')

# ---------------------------------------------------------------- product page
sub(
    '''    return layout(f"products/{tag}.html", p["short_name"], body,
                  active=f"products/{tag}.html",
                  description=f"Documentation-based review of the {p['name']} — verified specifications with official source links.")''',
    '''    purl = page_url(f"products/{tag}.html")
    ld = [
        {
            "@type": "ItemPage",
            "@id": purl + "#webpage",
            "url": purl,
            "name": p["name"],
            "description": f"Documentation-based review of the {p['name']} — verified specifications with official source links.",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Kitchen appliances", page_url("categories/kitchen-appliances.html")),
            (p["short_name"], purl),
        ]),
    ]
    return layout(f"products/{tag}.html", p["short_name"], body,
                  active=f"products/{tag}.html",
                  description=f"Documentation-based review of the {p['name']} — verified specifications with official source links.",
                  jsonld_blocks=ld)''')

# ---------------------------------------------------------------- category page
sub(
    '''    return layout("categories/kitchen-appliances.html", "Category: Kitchen", body,
                  active="categories/kitchen-appliances.html",
                  description="Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.")''',
    '''    curl = page_url("categories/kitchen-appliances.html")
    ld = [
        {
            "@type": "CollectionPage",
            "@id": curl + "#webpage",
            "url": curl,
            "name": "Category: Kitchen",
            "description": "Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Kitchen appliances", curl),
        ]),
        {
            "@type": "ItemList",
            "@id": curl + "#products",
            "name": "Tracked air fryers",
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
    ]
    return layout("categories/kitchen-appliances.html", "Category: Kitchen", body,
                  active="categories/kitchen-appliances.html",
                  description="Kitchen appliance category page: three tracked air fryers with verified capacity, manufacturer list price and open flags.",
                  jsonld_blocks=ld)''')

# --------------------------------------------------------------- compare page
sub(
    '''    return layout("compare.html", "Comparison", body, active="compare.html",
                  description="Verified-only comparison of three air fryers, with gaps left visible and every value linked to an official source.")''',
    '''    curl = page_url("compare.html")
    ld = [
        {
            "@type": "ItemList",
            "@id": curl + "#products",
            "name": "Three air fryers compared",
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
            ("Comparison", curl),
        ]),
    ]
    return layout("compare.html", "Comparison", body, active="compare.html",
                  description="Verified-only comparison of three air fryers, with gaps left visible and every value linked to an official source.",
                  jsonld_blocks=ld)''')

# -------------------------------------------------------------- article index
sub(
    '''    return layout("articles/index.html", "Articles", body, active="articles/index.html",
                  description="Eight sourced articles on dual-basket vs oven air fryers, what a 450 F badge means, preset-count conflicts, capacity from published numbers, and why this site publishes no Amazon prices.")''',
    '''    aurl = page_url("articles/index.html")
    ld = [
        {
            "@type": "CollectionPage",
            "@id": aurl + "#webpage",
            "url": aurl,
            "name": "Articles",
            "isPartOf": {"@id": SITE_URL + "/#website"},
            "about": {"@id": SITE_URL + "/#organization"},
            "inLanguage": "en-US",
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Articles", aurl),
        ]),
        {
            "@type": "ItemList",
            "@id": aurl + "#articles",
            "name": "Sourced air-fryer articles",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": art["title"],
                    "url": page_url(f"articles/{art['slug']}.html"),
                }
                for i, art in enumerate(ARTICLES["articles"], start=1)
            ],
        },
    ]
    return layout("articles/index.html", "Articles", body, active="articles/index.html",
                  description="Eight sourced articles on dual-basket vs oven air fryers, what a 450 F badge means, preset-count conflicts, capacity from published numbers, and why this site publishes no Amazon prices.",
                  jsonld_blocks=ld)''')

# --------------------------------------------------------------- article page
sub(
    '''    return layout(f"articles/{a['slug']}.html", a["title"], body,
                  active="articles/index.html", description=a["standfirst"])''',
    '''    aurl = page_url(f"articles/{a['slug']}.html")
    ld = [
        article_jsonld(a, aurl),
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Articles", page_url("articles/index.html")),
            (a["title"], aurl),
        ]),
    ]
    return layout(f"articles/{a['slug']}.html", a["title"], body,
                  active="articles/index.html", description=a["standfirst"],
                  og_type="article", jsonld_blocks=ld,
                  og_image_alt=f"{a['title']} — {SITE_NAME}")''')

# -------------------------------------------------------------- questions page
sub(
    '''    return layout("questions.html", "Open questions", body, active="questions.html",
                  description="The questions, information and answers that must be settled before a decision on this site is reasonable, separated into known, discoverable, not-stated and account-only.")''',
    '''    qurl = page_url("questions.html")
    # FAQPage. Every answer below is assembled only from fields that the page above
    # already prints in full — what_we_know, what_is_missing and how_to_discover —
    # so the structured data restates visible content and adds nothing.
    faq = []
    for item in q["questions"]:
        answer = []
        if item.get("what_we_know"):
            answer.append("What we know: " + " ".join(item["what_we_know"]))
        if item.get("what_is_missing"):
            answer.append("What is missing: " + item["what_is_missing"])
        if item.get("how_to_discover"):
            answer.append("How to find it out: " + item["how_to_discover"])
        if not answer:
            continue
        faq.append({
            "@type": "Question",
            "name": item["question"],
            "acceptedAnswer": {"@type": "Answer", "text": " ".join(answer)},
        })
    ld = [
        {
            "@type": "FAQPage",
            "@id": qurl + "#faq",
            "url": qurl,
            "mainEntity": faq,
        },
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Questions and gaps", qurl),
        ]),
    ]
    return layout("questions.html", "Open questions", body, active="questions.html",
                  description="The questions, information and answers that must be settled before a decision on this site is reasonable, separated into known, discoverable, not-stated and account-only.",
                  jsonld_blocks=ld)''')

# --------------------------------------------------------------------- 404
sub(
    '''    return layout("404.html", "Page not found", body)''',
    '''    return layout("404.html", "Page not found", body,
                  description="That page does not exist on this site. Start from the air-fryer buying guide, the articles, or the flagged-for-review register.",
                  jsonld_blocks=[breadcrumbs_jsonld([
                      ("Home", SITE_URL + "/"),
                      ("Page not found", page_url("404.html")),
                  ])])''')

for old, new in PATCHES:
    if s.count(old) != 1:
        raise SystemExit(
            f"PATCH FAILED — expected exactly 1 occurrence, found {s.count(old)}:\n{old[:120]}")
    s = s.replace(old, new)

p.write_text(s, encoding="utf-8")
print(f"applied {len(PATCHES)} patches to build.py")
