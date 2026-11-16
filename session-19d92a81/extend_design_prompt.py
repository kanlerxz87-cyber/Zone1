#!/usr/bin/env python3
"""Session arena/19d92a81 — content extension, part 3: design-prompt.json.

Extends the paste-ready design prompt with the marketing / organic-traffic layer
the brief asks for, and adds the reviewable rows behind it (D-11..D-13,
A-12..A-15, T-9..T-12, V-5..V-7, R-7..R-9). Text surgery, not a re-dump, so the
file keeps its existing hand-formatted style and the diff stays reviewable.

Run from the repository root:  python3 session-19d92a81/extend_design_prompt.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "design-prompt.json"
text = PATH.read_text()

ADDENDUM = (
    "\n\nADDENDUM - 2026-11-16 (session arena/19d92a81) - MARKETING AND ORGANIC-TRAFFIC LAYER\n"
    "The brief for this pass: make the site read like a polished marketing affiliate publication\n"
    "with catchy, trendy, product-related articles that can earn organic traffic - and never like\n"
    "AI slop. Directives below extend, and never replace, the rules above.\n"
    "\n"
    "1. READ LIKE A PUBLICATION, NOT AN ADMIN PANEL. Shopper-first navigation (Shop / Project), a\n"
    "   production-method byline on every money page, and one brand name on every surface. The\n"
    "   evidence layer stays one click away: honesty is a feature of the voice, not the layout.\n"
    "   (SG-23, SG-24, SG-27; questions Q-09, Q-23.)\n"
    "2. CATCHY, TRENDY, SOURCE-LED CONTENT. Ship seasonal and query-led pieces four to six weeks\n"
    "   before the retail moment. Three proven templates in this niche: the deal-safety\n"
    "   investigation (the model-number switch), the gift/buying guide matched to people and\n"
    "   kitchens, and the according-to-the-manuals care guide. Trendy never means unverified: the\n"
    "   sourcing rules above are unchanged. (SG-25; topic queue TP-15..TP-19.)\n"
    "3. ORGANIC TRAFFIC PROGRAM. Four clusters (format choice, care, deal safety, spec literacy)\n"
    "   with hub pages and generator-maintained internal links; one target query per article;\n"
    "   Search Console verification and sitemap submission the moment the owner can (account-only);\n"
    "   one owned channel that collects nothing (RSS first). (SG-29, SG-30; T-3 remains the\n"
    "   submission tactic.)\n"
    "4. IMAGERY. Typographic on purpose until image rights exist; NEVER AI-generated product\n"
    "   imagery; if images arrive, they are Amazon-licensed or original, with factual alt text.\n"
    "   (SG-26; question Q-25.)\n"
    "5. WHAT 'NOT AI SLOP' MEANS HERE. Specific over sweeping. Sourced over smooth. Opinion\n"
    "   labelled as judgement. Gaps shown as gaps. Freshness dated. A voice that would rather be\n"
    "   interesting than comprehensive. The banned-phrase guard in build.py is the floor, not the\n"
    "   ceiling. (V-5..V-7.)\n"
    "\n"
    "Everything in this addendum exists in reviewable form on the site: suggestions SG-23..SG-30\n"
    "with decision path P5 (suggestions.html), questions Q-22..Q-26 (questions.html), topics\n"
    "TP-15..TP-19 (topics.html), and the rows appended by this addendum to the lists below.\n"
    "Nothing in the addendum is implemented by the addendum; the owner still picks the path.\n"
)

D_ITEMS = [
    {
        "id": "D-11",
        "suggestion": "Magazine furniture on money pages: production-method byline, an 'in this guide' strip, and a visible freshness stamp",
        "why": "A reader deciding whether to trust a recommendation asks who wrote the page and when it was last checked. Both answers exist in the data layer today; neither is on the page a shopper lands on.",
        "path": "One byline line and one freshness stamp in the page templates; the strip is a short list of the page's own section headings. No new data required.",
        "status": "proposed",
        "status_note": "Suggested 2026-11-16 (session arena/19d92a81) as the design half of SG-23. Not implemented; the queue decides.",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-23", "label": "SG-23 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
    {
        "id": "D-12",
        "suggestion": "Shopping-shaped sidebar: two groups - Shop (picks, guide, articles, compare, products) and Project (summary, suggestions, questions, evidence, platform)",
        "why": "The current five-group sidebar is the owner's dashboard. A visitor with a purchase question needs four links, not twenty-five. The evidence layer stays one click away behind its own group.",
        "path": "Edit the NAV renderer in build.py only; no page content changes. Sidebar grouping is reversible in one commit.",
        "status": "proposed",
        "status_note": "Suggested 2026-11-16 (session arena/19d92a81) as the design half of SG-24. Not implemented.",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-24", "label": "SG-24 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/build.py", "label": "build.py nav renderer"}],
    },
    {
        "id": "D-13",
        "suggestion": "A seasonal design band with a strict restraint rule: type and colour only - no countdown timers, no fake urgency, no price badges",
        "why": "Countdowns and urgency badges are the slop signature of affiliate pages, and they sit badly next to a site that deliberately shows no Amazon prices. A seasonal band can say 'gift guide 2026' without theatre.",
        "path": "One accent-band component reused by seasonal pages, carrying the season name and the year.",
        "status": "proposed",
        "status_note": "Suggested 2026-11-16 (session arena/19d92a81); pairs with SG-25 and SG-26. Not implemented.",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-25", "label": "SG-25 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
]

A_ITEMS = [
    {
        "id": "A-12",
        "title": "Black Friday: the model-number switch and the three-minute check",
        "format": "Seasonal investigation",
        "hook": "Deal safety built on this repository's own documented listing conflicts.",
        "status": "published",
        "status_note": "Published 2026-11-16 by session arena/19d92a81 from registered sources only.",
        "published_as": "articles/black-friday-model-number-switch.html",
        "cites": ["S29", "S26", "S12", "S27", "S25", "S14", "S15", "S2"],
        "links": [],
    },
    {
        "id": "A-13",
        "title": "The honest 2026 air-fryer gift guide: match the format to the person",
        "format": "Seasonal buying guide",
        "hook": "Counter space and warranty fine print decide whether the gift stays.",
        "status": "published",
        "status_note": "Published 2026-11-16 by session arena/19d92a81 from registered sources only.",
        "published_as": "articles/air-fryer-gift-guide-2026.html",
        "cites": ["S10", "S18", "S12", "S13", "S14", "S15"],
        "links": [],
    },
    {
        "id": "A-14",
        "title": "How to clean an air fryer, according to the people who made it",
        "format": "Care guide",
        "hook": "The biggest care query, answered from the manuals instead of life hacks.",
        "status": "published",
        "status_note": "Published 2026-11-16 by session arena/19d92a81 from registered sources only.",
        "published_as": "articles/how-to-clean-an-air-fryer.html",
        "cites": ["S15", "S18", "S13", "S12", "S10"],
        "links": [],
    },
    {
        "id": "A-15",
        "title": "January: first-week setup and care checklist for a gifted air fryer",
        "format": "Seasonal checklist",
        "hook": "The page that survives every December gift.",
        "status": "proposed",
        "status_note": "Proposed as topic TP-18; gated on the marketplace question Q-20.",
        "published_as": None,
        "cites": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/topics.html", "label": "TP-18 in the topic queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/topics.json", "label": "Topic register on GitHub"}],
    },
]

T_ITEMS = [
    {
        "id": "T-9",
        "tactic": "Ship seasonal content four to six weeks before the retail moment, not during it",
        "how": "A four-slot yearly calendar (winter gifting, spring reset, Prime Day, back-to-school) with draft deadlines; the first three seasonal pieces shipped mid-season and are the cautionary example.",
        "status": "proposed",
        "status_note": "Needs the cadence answer (Q-24); the calendar itself is suggestion SG-25.",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-25", "label": "SG-25 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
    {
        "id": "T-10",
        "tactic": "Build four topic clusters with hubs and generator-maintained internal links",
        "how": "Format choice, care, deal safety, spec literacy - one hub each; every article links up to its hub and across to its siblings from the generator, so links cannot rot as the set grows.",
        "status": "proposed",
        "status_note": "Suggestion SG-30 carries the options and the recommendation.",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-30", "label": "SG-30 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
    {
        "id": "T-11",
        "tactic": "Refresh published seasonal pieces each year instead of publishing parallel ones",
        "how": "Re-date and re-verify the gift guide and the Black Friday piece before their season; keep one canonical page per season so links accumulate instead of splitting.",
        "status": "proposed",
        "status_note": "Complements T-8 (data refresh cadence) with an editorial one. Suggested 2026-11-16 (session arena/19d92a81).",
        "sources": [],
        "links": [{"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/articles.json", "label": "Article register on GitHub"}],
    },
    {
        "id": "T-12",
        "tactic": "Add one owned channel that collects nothing: an RSS/Atom feed surfaced in the footer",
        "how": "A feed link and the generated feed file; zero personal data, so it cannot touch the privacy disclosure. Newsletter later, only when an owner can run it (T-7 stays pending).",
        "status": "proposed",
        "status_note": "Suggestion SG-29 option B. Suggested 2026-11-16 (session arena/19d92a81).",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-29", "label": "SG-29 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
]

V_ITEMS = [
    {
        "id": "V-5",
        "rule": "Headlines name the thing and the payoff; no curiosity-gap clickbait",
        "why": "A reader arriving from search must know in one second what the page does for them. Curiosity gaps earn clicks and lose trust, and trust is this site's only product.",
        "sources": [],
        "links": [{"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/build.py", "label": "build.py voice guards"}],
    },
    {
        "id": "V-6",
        "rule": "Numbers in headlines only when the page sources them in the body",
        "why": "A headline number is a promise the body has to keep; an unsourced one is the slop tell readers notice first.",
        "sources": [],
        "links": [{"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/build.py", "label": "build.py voice guards"}],
    },
    {
        "id": "V-7",
        "rule": "Seasonal pages carry their year and their expiry, and never a countdown",
        "why": "Seasonal content must age honestly. Countdown timers are urgency theatre and contradict the site's deliberate no-Amazon-prices rule (Program Policies 2(b)).",
        "sources": ["S2"],
        "links": [],
    },
]

R_ITEMS = [
    {
        "id": "R-7",
        "suggestion": "Adopt decision path P5 (reader-facing polish) as the default direction while the account questions stay open",
        "options": "P5 as written / P5 with changes / pick rows individually",
        "recommended": "P5 as written, once Q-23 (brand) and Q-24 (cadence) have one-line answers",
        "status": "proposed",
        "status_note": "Decision row for the owner; nothing is implemented by this row. Suggested 2026-11-16 (session arena/19d92a81).",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html", "label": "P5 path on the suggestions page"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
    {
        "id": "R-8",
        "suggestion": "Name an editor, or ratify the production-method desk byline (SG-23)",
        "options": "Named editor / desk byline / neither",
        "recommended": "Desk byline now (SG-23 option B) - it is true today; upgrade to a named editor when Q-09 answers",
        "status": "proposed",
        "status_note": "Decision row for the owner. Suggested 2026-11-16 (session arena/19d92a81).",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-23", "label": "SG-23 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
    {
        "id": "R-9",
        "suggestion": "Confirm the imagery policy: typographic until licensed (SG-26)",
        "options": "Typographic / licensed Amazon imagery / original photography",
        "recommended": "Typographic now, licensed later; never AI-generated product imagery",
        "status": "proposed",
        "status_note": "Decision row for the owner. Suggested 2026-11-16 (session arena/19d92a81).",
        "sources": [],
        "links": [{"url": "https://kanlerxz87-cyber.github.io/Zone1/suggestions.html#sg-26", "label": "SG-26 in the decision queue"}, {"url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json", "label": "Decision register on GitHub"}],
    },
]


def fmt_item(item):
    """Serialize one item in the file's own style: indent-2 object re-indented by 2,
    small scalar arrays inline. Close enough to the hand format to stay reviewable."""
    body = json.dumps(item, indent=2, ensure_ascii=False)
    # inline lists of plain strings:  "key": [\n    "a",\n    "b"\n  ]  ->  "key": ["a", "b"]
    import re

    def inline_str_list(m):
        inner = m.group(2).strip()
        if "\n" not in inner:
            return m.group(0)
        parts = [p.strip() for p in inner.split(",") if p.strip()]
        return f'{m.group(1)}{", ".join(parts)}]'

    body = re.sub(
        r'("(?:sources|cites)": \[)(.*?)\]', inline_str_list, body, flags=re.S)
    indented = "\n".join(("    " + ln) if ln else ln for ln in body.splitlines())
    return indented


def splice_items(text, header, items):
    """Insert items at the end of the JSON array that starts at `header`.

    Finds the array's matching closing bracket by depth counting (nested arrays in
    some rows end at the same indent, so a line match is not enough)."""
    start = text.index(header)
    open_idx = text.index("[", start)
    depth = 0
    i = open_idx
    while i < len(text):
        ch = text[i]
        if ch == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                break
        i += 1
    close = i  # index of the matching ']'
    last_item_end = text.rfind("}", 0, close) + 1
    assert last_item_end > 0
    block = ",\n".join(fmt_item(it) for it in items)
    return text[:last_item_end] + ",\n" + block + text[last_item_end:]


def main():
    global text
    # 1. items into each list
    text = splice_items(text, '  "design": [', D_ITEMS)
    text = splice_items(text, '  "topics": [', A_ITEMS)
    text = splice_items(text, '  "tactics": [', T_ITEMS)
    text = splice_items(text, '  "voice_rules": [', V_ITEMS)
    text = splice_items(text, '  "decisions": [', R_ITEMS)

    # 2. design_prompt addendum (escaped), inserted before the value's closing quote
    anchor = '\n  "design": ['
    idx = text.index(anchor)
    assert text[idx - 2:idx] == '",', text[idx - 6:idx]
    escaped = json.dumps(ADDENDUM, ensure_ascii=False)[1:-1]
    text = text[:idx - 2] + escaped + text[idx - 2:]

    # 3. meta updates
    assert text.count('"compiled": "2026-11-15"') == 1
    text = text.replace('"compiled": "2026-11-15"', '"compiled": "2026-11-16"')
    assert text.count('"session": "arena/bf487400-zone1"') == 1
    text = text.replace(
        '"session": "arena/bf487400-zone1"',
        '"session": "arena/bf487400-zone1; extended by arena/19d92a81 (2026-11-16)"')

    # 4. stale reference fixes, logged in the session record
    #    a) "S1-S31" predates sources S32-S34
    n = text.count("S1-S31")
    text = text.replace("S1-S31", "S1-S34")
    #    b) T-1's typed article count ("12 of the queue's topics") is stale and
    #       conflates the article set with the queue; restate without a typed count.
    old_note = "12 of the queue's topics are published with target queries; A-8 to A-11 remain."
    assert old_note in text
    text = text.replace(
        old_note,
        "A-1 to A-7 of the queue are published with target queries; A-8 to A-11 remain, "
        "and A-15 is the addendum's proposed seasonal slot.")

    # validity check before writing
    d = json.loads(text)
    assert len(d["design"]) == 13 and len(d["topics"]) == 15
    assert len(d["tactics"]) == 12 and len(d["voice_rules"]) == 7
    assert len(d["decisions"]) == 9
    PATH.write_text(text)
    print("design-prompt.json extended: D13 A15 T12 V7 R9, S1-S31 fixes:", n)


if __name__ == "__main__":
    main()
