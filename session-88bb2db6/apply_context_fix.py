#!/usr/bin/env python3
"""Post-merge hardening of the combined SEO layer.

Applied by session arena/88bb2db6 on 2026-11-15, immediately after resolving the
build.py rebase conflict against origin/main @ 8f40f04 (PR #71, arena/792c279e).

Two defects in this session's original JSON-LD implementation, both caught by
comparing against the other session's independent implementation:

C1  The JSON-LD was emitted as a bare JSON array with no "@context". A consumer
    that requires an explicit context cannot tell the nodes are schema.org types.
    Correct form is {"@context": "https://schema.org", "@graph": [...]}. Fixed.

C2  The Organization node carried a description but no "disambiguatingDescription".
    The other session's version states the non-affiliation and the Amazon Associate
    disclosure *inside* the structured data, which is the right place for it: the
    disclosure then travels with the data rather than only appearing on the page.
    Adopted.

Both changes were confirmed by reading the other session's build.py at
origin/main:8f40f04.
"""
from pathlib import Path

p = Path("build.py")
s = p.read_text(encoding="utf-8")

# ---------------------------------------------------------------- C1
OLD_JSONLD = '''def jsonld(blocks):
    """Render one or more JSON-LD blocks for the <head>.

    A list is emitted as one @graph so the blocks can reference each other by @id.
    `</` is escaped so a string containing it can never close the script element.
    """
    if not blocks:
        return ""
    payload = json.dumps(blocks, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\\\/")
    return f'<script type="application/ld+json">{payload}</script>'
'''

NEW_JSONLD = '''def jsonld(blocks):
    """Render JSON-LD blocks for the <head>.

    The blocks are emitted as one @graph inside an object carrying an explicit
    "@context". Both parts matter:

      * @context tells a consumer that the node types are schema.org types. Without
        it, a bare array of nodes is ambiguous.
      * @graph lets the blocks reference each other by @id, so an Article can point
        at the publisher node instead of duplicating the publisher's details.

    `</` is escaped so a string containing it can never close the script element.
    """
    if not blocks:
        return ""
    payload = json.dumps({"@context": "https://schema.org", "@graph": blocks},
                         ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\\\/")
    return f'<script type="application/ld+json">{payload}</script>'
'''

if s.count(OLD_JSONLD) != 1:
    raise SystemExit(f"C1 PATCH FAILED ({s.count(OLD_JSONLD)} matches)")
s = s.replace(OLD_JSONLD, NEW_JSONLD)

# ---------------------------------------------------------------- C2
OLD_PUB = '''    "description": (
        "An independent, documentation-based air-fryer buying guide. Every specification "
        "links to the manufacturer's own page or owner's manual; nothing is inferred and "
        "no hands-on testing is claimed."
    ),
}'''

NEW_PUB = '''    "description": (
        "An independent, documentation-based air-fryer buying guide. Every specification "
        "links to the manufacturer's own page or owner's manual; nothing is inferred and "
        "no hands-on testing is claimed."
    ),
    # The disclosure and the non-affiliation statement travel inside the structured
    # data, not only in the page body, so a consumer that reads the data alone still
    # sees them. Adopted from arena/792c279e's implementation.
    "disambiguatingDescription": (
        "Not owned by, endorsed by or sponsored by Amazon.com, Inc. or any brand named "
        "on the site. " + DISCLOSURE
    ),
}'''

if s.count(OLD_PUB) != 1:
    raise SystemExit(f"C2 PATCH FAILED ({s.count(OLD_PUB)} matches)")
s = s.replace(OLD_PUB, NEW_PUB)

p.write_text(s, encoding="utf-8")
print("applied 2 patches:")
print("  - C1: JSON-LD now carries an explicit @context inside an @graph object")
print("  - C2: Organization now carries disambiguatingDescription (non-affiliation + disclosure)")
