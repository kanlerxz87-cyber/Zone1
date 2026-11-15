#!/usr/bin/env python3
"""Resolve the build.py rebase conflicts, keeping both sessions' work.

Applied by session arena/88bb2db6 on 2026-11-15, rebasing onto origin/main @ 8f40f04
(PR #71, session arena/792c279e; also PRs #70 and #72 from sessions 22f43836 and
94a562a1).

Three conflicts, all in code that both sessions changed independently:

Hunk 1+2  the <head> of layout(). Both sessions added canonical URLs, Open Graph and
    Twitter card tags and JSON-LD. The merged version takes this session's richer
    per-page implementation and adopts two things the other session got right and
    this session had missed:
      * a 404 page must not be indexed - `robots: noindex`, not `index,follow`;
      * the JSON-LD must carry `"@context": "https://schema.org"`. Without a context
        the nodes are not interpreted as schema.org types. This session's first
        version emitted a bare array, which is the defect the other session's
        `@context` + `@graph` form avoids.
    The merged version also keeps the other session's Organization
    `disambiguatingDescription`, which states the non-affiliation and the disclosure
    inside the structured data itself.

Hunk 3  page_article(). Both sessions added Article structured data. The other
    session also added a share row and previous/next navigation, which are kept
    verbatim. Its Article block is not duplicated: the merged version emits one
    Article block in <head>, from the same fields plus the ones this session added
    (dates, image, author/publisher references), instead of a second copy in the
    body.
"""
import re
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

MARK = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", re.S | re.M)

blocks = MARK.findall(s)
if len(blocks) != 3:
    raise SystemExit(f"expected 3 conflict hunks, found {len(blocks)}")

(ours1, theirs1), (ours2, theirs2), (ours3, theirs3) = blocks

# ---------------------------------------------------------------- hunk 1
HUNK1_MERGED = '''
    # Absolute URL of this page. The landing page canonicalises to the directory form
    # so that https://…/Zone1/ and https://…/Zone1/index.html are one URL, not two.
    canonical = SITE_URL + "/" if page_rel == "index.html" else page_url(page_rel)
    full_title = f"{title} · {SITE_NAME}"
    # Fall back to the page's own description for the social card; a link shared with
    # no text still gets a readable preview rather than an empty one.
    social_desc = description or f"{SITE_NAME} — {SITE_TAGLINE}."
    social_alt = og_image_alt or f"{SITE_NAME} — {SITE_TAGLINE}"
    ld = jsonld(jsonld_blocks)
'''

# ---------------------------------------------------------------- hunk 2
HUNK2_MERGED = '''
<link rel="canonical" href="{e(canonical)}">
<meta name="robots" content="{e("noindex" if page_rel == "404.html" else "index,follow,max-image-preview:large")}">
<meta property="og:type" content="{e(og_type)}">
<meta property="og:site_name" content="{e(SITE_NAME)}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(social_desc)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(OG_IMAGE)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(social_alt)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(full_title)}">
<meta name="twitter:description" content="{e(social_desc)}">
<meta name="twitter:image" content="{e(OG_IMAGE)}">
<meta name="twitter:image:alt" content="{e(social_alt)}">
{ld}
<link rel="stylesheet" href="{prefix}assets/style.css">
'''

# ---------------------------------------------------------------- hunk 3
# Keep the other session's share row and prev/next navigation verbatim; replace its
# body-level Article JSON-LD with a single head-level Article block.
share_part = theirs3.split("    _ld = json.dumps({", 1)[0]
share_part = share_part.replace(
    "    # --- 2026-11-15 (arena/792c279e): reader-facing polish on the editorial layer.",
    "    # --- 2026-11-15 (arena/792c279e): reader-facing polish on the editorial layer.",
)
HUNK3_MERGED = share_part + '''    # Structured data for this article is emitted once, in <head>, by layout(), with
    # the same @context and @graph wrapper as every other block. (arena/792c279e
    # appended a second, body-level Article block; merged here into one so a crawler
    # never sees two conflicting Article nodes for the same URL.)
    aurl = page_url(f"articles/{a['slug']}.html")
    ld = [
        article_jsonld(a, aurl),
        breadcrumbs_jsonld([
            ("Home", SITE_URL + "/"),
            ("Articles", page_url("articles/index.html")),
            (a["title"], aurl),
        ]),
    ]
'''

merged = [HUNK1_MERGED, HUNK2_MERGED, HUNK3_MERGED]
it = iter(merged)


def replace(m):
    return next(it)


s = MARK.sub(replace, s)
p.write_text(s, encoding="utf-8")
print("build.py: 3 hunks merged (hunk 1 + hunk 2 = head, hunk 3 = share row + Article)")
