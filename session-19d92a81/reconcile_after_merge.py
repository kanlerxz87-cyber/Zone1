#!/usr/bin/env python3
"""Session arena/19d92a81 — reconcile with parallel sessions after merging origin/main.

Upstream sessions landed overlapping work while this session worked (gift guide,
imagery/seasonal suggestions, nav redesign, Q-22/Q-23, TP-15..TP-17, SG-23..SG-26).
This script keeps their rows, keeps only this session's UNIQUE content, renumbers
ids to the next free slots, and rewrites internal cross-references.

Dropped as superseded (recorded in COORDINATION.md):
  - article air-fryer-gift-guide-2026 (theirs, TP-15, already published)
  - SG nav-split (their pass 12 shipped it), SG seasonal-calendar (their SG-24),
    SG imagery-policy (their SG-23)
  - Q publishing-cadence (their Q-23), Q images (their Q-22)
  - design rows D-12 (implemented by pass 12), A-13 (their gift guide), R-9 (their SG-23)

Run from the repository root:  python3 session-19d92a81/reconcile_after_merge.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "session-19d92a81"))

import extend_articles as EA          # noqa: E402  (ph() re-reads current products.json)
import extend_decisions as ED         # noqa: E402
import extend_design_prompt as EDP    # noqa: E402

SITE = "https://kanlerxz87-cyber.github.io/Zone1"
GH = "https://github.com/kanlerxz87-cyber/Zone1/blob/main/"


def fix(text, pairs):
    for old, new in pairs:
        text = text.replace(old, new)
    return text


# ---------------------------------------------------------------- articles --
def do_articles():
    a = json.load(open(DATA / "articles.json"))
    have = {x["slug"] for x in a["articles"]}
    for art in (EA.art1, EA.art3):          # art2 (gift guide) dropped: theirs is published
        assert art["slug"] not in have, art["slug"]
        a["articles"].append(art)
    a["updated"] = "2026-11-16"
    (DATA / "articles.json").write_text(json.dumps(a, indent=1, ensure_ascii=False) + "\n")
    return len(a["articles"])


# ------------------------------------------------------------------ topics --
def do_topics():
    t = json.load(open(DATA / "topics.json"))
    # their TP-17 = the Black Friday direction; this session shipped the article
    tp17 = next(x for x in t["topics"] if x["id"] == "TP-17")
    tp17["status"] = "published"
    tp17["published_as"] = "articles/black-friday-model-number-switch.html"
    tp17["angle"] += (" Realized 2026-11-16 by session arena/19d92a81 as the "
                      "model-number-switch investigation - deal safety built on this "
                      "repository's own documented listing conflicts.")
    mine = {}
    for tp in EA.new_topics:
        mine[tp["id"]] = tp
    # TP-15 (BF) and TP-16 (gift) dropped; TP-17 (cleaning) -> TP-18; TP-18 -> TP-19; TP-19 -> TP-20
    cleaning = dict(mine["TP-17"]); cleaning["id"] = "TP-18"
    january = dict(mine["TP-18"]); january["id"] = "TP-19"
    primeday = dict(mine["TP-19"]); primeday["id"] = "TP-20"
    have = {x["id"] for x in t["topics"]}
    for tp in (cleaning, january, primeday):
        assert tp["id"] not in have, tp["id"]
        t["topics"].append(tp)
    t["compiled"] = "2026-11-16"
    (DATA / "topics.json").write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
    return len(t["topics"])


# ------------------------------------------------------------- suggestions --
def do_suggestions():
    s = json.load(open(DATA / "suggestions.json"))
    by = {x["id"]: x for x in ED.new_suggestions}
    rows = []

    sg27 = dict(by["SG-23"])   # production-method authorship -> SG-27
    sg27["id"] = "SG-27"
    sg27["blocks"] = []

    sg28 = dict(by["SG-27"])   # brand consolidation -> SG-28
    sg28["id"] = "SG-28"
    sg28["blocked_by"] = ["Q-07", "Q-25"]

    sg29 = dict(by["SG-28"])   # Creators API roadmap -> SG-29
    sg29["id"] = "SG-29"

    sg30 = dict(by["SG-29"])   # owned audience / RSS -> SG-30
    sg30["id"] = "SG-30"
    sg30["why"] = fix(sg30["why"], [("the seasonal calendar (SG-25)",
                                     "the seasonal calendar (SG-24)")])

    sg31 = dict(by["SG-30"])   # cluster map -> SG-31
    sg31["id"] = "SG-31"
    sg31["problem"] = fix(sg31["problem"], [
        ("Eighteen articles now carry target queries (as of 2026-11-16)",
         "Twenty-one articles carry target queries after this merge (2026-11-16)")])

    rows = [sg27, sg28, sg29, sg30, sg31]
    have = {x["id"] for x in s["suggestions"]}
    for r in rows:
        assert r["id"] not in have, r["id"]
        s["suggestions"].append(r)

    path = ED.new_path
    path["contains"] = ["SG-23", "SG-24", "SG-25", "SG-27", "SG-28", "SG-29", "SG-30", "SG-31"]
    path["delivers"] = fix(path["delivers"], [
        ("These are exactly the changes the brief's",
         "P5 now also carries the parallel pass's rows (SG-23..SG-25: imagery licensing, "
         "seasonal shipping, one compliant call-to-action). These are exactly the changes the brief's")])
    path["pick_this_if"] = fix(path["pick_this_if"], [
        ("(Q-23 brand, Q-24 cadence)", "(Q-25 brand, Q-23 publishing decisions)")])
    have_p = {x["id"] for x in s["paths"]}
    assert path["id"] not in have_p
    s["paths"].append(path)
    s["paths_note"] = (
        s["paths_note"].rstrip()
        + " P5 is independent: it is the reader-facing polish path and can run in "
        "parallel with any of the four above."
    )
    s["pass"] = (s["pass"] + "; marketing and decision-support rows SG-27..SG-31 + "
                 "path P5 by session arena/19d92a81 (2026-11-16), reconciled after "
                 "merging the parallel pass's SG-23..SG-26")
    (DATA / "suggestions.json").write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n")
    return len(s["suggestions"]), len(s["paths"])


# --------------------------------------------------------------- questions --
def do_questions():
    q = json.load(open(DATA / "questions.json"))
    by = {x["id"]: x for x in ED.new_questions}

    q24 = by["Q-22"]   # governance -> Q-24
    q24["id"] = "Q-24"
    q24["blocks"] = ["SG-27", "SG-28", "SG-29", "SG-30", "SG-31"]

    q25 = by["Q-23"]   # brand -> Q-25
    q25["id"] = "Q-25"
    q25["blocks"] = ["SG-28"]
    q25["how_to_discover"] = fix(q25["how_to_discover"],
                                 [("SG-27 carries the implementation options",
                                   "SG-28 carries the implementation options")])

    q26 = by["Q-26"]   # automation API -> Q-26 (id unchanged)
    q26["blocks"] = ["SG-29"]
    q26["what_we_know"] = [fix(w, [("(SG-28)", "(SG-29)")]) for w in q26["what_we_know"]]

    rows = [q24, q25, q26]
    have = {x["id"] for x in q["questions"]}
    for r in rows:
        assert r["id"] not in have, r["id"]
        q["questions"].append(r)
    q["compiled"] = "2026-11-16"
    (DATA / "questions.json").write_text(json.dumps(q, indent=1, ensure_ascii=False) + "\n")
    return len(q["questions"])


# ----------------------------------------------------------- design prompt --
ADDENDUM = (
    "\n\nADDENDUM - 2026-11-16 (session arena/19d92a81) - MARKETING AND ORGANIC-TRAFFIC LAYER\n"
    "The brief for this pass: make the site read like a polished marketing affiliate publication\n"
    "with catchy, trendy, product-related articles that can earn organic traffic - and never like\n"
    "AI slop. Directives below extend, and never replace, the rules above.\n"
    "\n"
    "1. READ LIKE A PUBLICATION, NOT AN ADMIN PANEL. Pass 12 grouped the sidebar into\n"
    "   Shop smart / Products / Trust & evidence / Owner workspace and set the visual system;\n"
    "   what remains is a production-method byline on every money page (SG-27) and one brand\n"
    "   name on every surface (SG-28, question Q-25). The evidence layer stays one click away:\n"
    "   honesty is a feature of the voice, not the layout.\n"
    "2. CATCHY, TRENDY, SOURCE-LED CONTENT. Ship seasonal and query-led pieces four to six\n"
    "   weeks before the retail moment (T-9; the parallel pass's SG-24 says the same from the\n"
    "   other side: ship while the season is live). Three proven templates in this niche: the\n"
    "   deal-safety investigation (the model-number switch, published), the gift/buying guide\n"
    "   matched to people and kitchens (published), and the according-to-the-manuals care guide\n"
    "   (published). Trendy never means unverified: the sourcing rules above are unchanged.\n"
    "3. ORGANIC TRAFFIC PROGRAM. Four clusters with hub pages and generator-maintained\n"
    "   internal links (SG-31); one target query per article; Search Console verification and\n"
    "   sitemap submission the moment the owner can (account-only, T-3); one owned channel that\n"
    "   collects nothing - RSS first (SG-30).\n"
    "4. IMAGERY. Typographic on purpose until image rights exist - the parallel pass's SG-23\n"
    "   and Q-22 settle the licensing question; NEVER AI-generated product imagery; if images\n"
    "   arrive, they are Amazon-licensed or original, with factual alt text.\n"
    "5. WHAT 'NOT AI SLOP' MEANS HERE. Specific over sweeping. Sourced over smooth. Opinion\n"
    "   labelled as judgement. Gaps shown as gaps. Freshness dated. A voice that would rather\n"
    "   be interesting than comprehensive. The banned-phrase guard in build.py is the floor,\n"
    "   not the ceiling. (V-5..V-7.)\n"
    "\n"
    "Everything in this addendum exists in reviewable form on the site: suggestions SG-27..SG-31\n"
    "with decision path P5 (suggestions.html), questions Q-24..Q-26 (questions.html), topics\n"
    "TP-18..TP-20 (topics.html), and the rows appended by this addendum to the lists below.\n"
    "Nothing in the addendum is implemented by the addendum; the owner still picks the path.\n"
)


def do_design_prompt():
    d = json.load(open(DATA / "design-prompt.json"))
    by_id = {}
    for lst in (EDP.D_ITEMS, EDP.A_ITEMS, EDP.T_ITEMS, EDP.V_ITEMS, EDP.R_ITEMS):
        for it in lst:
            by_id[it["id"]] = it

    # ordered remap of internal cross-references to the post-merge ids
    REMAP = [
        ("Needs the cadence answer (Q-24); the calendar itself is suggestion SG-25.",
         "Needs the publishing-decision answer (Q-23); complements SG-24's "
         "ship-while-live rule with a lead-time target."),
        ("Q-23 (brand)", "Q-25 (brand)"),
        ("Q-24 (cadence)", "Q-23 (publishing decisions)"),
        ("(Q-24)", "(Q-23)"),
        ("Suggestion SG-30 carries", "Suggestion SG-31 carries"),
        ("Suggestion SG-29 option B", "Suggestion SG-30 option B"),
        ("SG-23 option B", "SG-27 option B"),
        ("design half of SG-23", "design half of SG-27"),
        ("#sg-30", "#sg-31"),
        ("#sg-29", "#sg-30"),
        ("#sg-25", "#sg-24"),
        ("#sg-23", "#sg-27"),
        ("SG-23", "SG-27"),
        ("SG-25", "SG-24"),
    ]

    def remap(item):
        return json.loads(fix(json.dumps(item, ensure_ascii=False), REMAP))

    kept = [remap(by_id[i]) for i in (
        "D-11", "D-13",                       # D-12 dropped: pass 12 shipped the nav regroup
        "A-12", "A-14", "A-15",               # A-13 dropped: their gift guide is published
        "T-9", "T-10", "T-11", "T-12",
        "V-5", "V-6", "V-7",
        "R-7", "R-8",                         # R-9 dropped: covered by their SG-23 / Q-22
    )]
    for it in kept:
        if it["id"] in ("D-11", "D-13"):
            d["design"].append(it)
        elif it["id"].startswith("A-"):
            d["topics"].append(it)
        elif it["id"].startswith("T-"):
            d["tactics"].append(it)
        elif it["id"].startswith("V-"):
            d["voice_rules"].append(it)
        else:
            d["decisions"].append(it)

    d["design_prompt"] += ADDENDUM
    d["session"] = (d.get("session", "") + "; extended by arena/19d92a81 (2026-11-16)")
    d["compiled"] = "2026-11-16"
    (DATA / "design-prompt.json").write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    return len(d["design"]), len(d["topics"]), len(d["tactics"]), len(d["voice_rules"]), len(d["decisions"])


def main():
    print("articles:", do_articles())
    print("topics:", do_topics())
    print("suggestions:", do_suggestions())
    print("questions:", do_questions())
    print("design-prompt D/A/T/V/R:", do_design_prompt())


if __name__ == "__main__":
    main()
