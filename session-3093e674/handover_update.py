import json, pathlib, re, collections, sys

OD = collections.OrderedDict
TODAY = "2026-11-17"
SESS = "arena/3093e674-zone1"

p = pathlib.Path('data/decision.json')
d = json.load(open(p, encoding='utf-8'), object_pairs_hook=OD)
h = d['handover']

h['summary'] = ("Everything else in this repository is done as far as it can be done without your accounts. The "
                "actions below are ordered by minutes per flag closed, and each one names what to paste back so the "
                "answer lands in a register instead of a chat log. The heading on this page counts the actions, the "
                "minutes and the flags from these rows rather than typing them.")

by = {x['id']: x for x in h['items']}

by['H1']['owner_action'] = ("Open the three air-fryer listings this site markets on a desktop browser and read the "
                             "**Model number** line in each listing's \u201cProduct information\u201d section.")
by['H1']['why_now'] = ("This is the single highest-value action in the project. The site currently shows a candidate "
                       "ASIN and a \u201cbelieved\u201d manufacturer SKU; this line makes the mapping a fact instead of "
                       "a match. It cannot be done by a headless fetch, which is why it is still open after seven "
                       "sessions. The two thermometer listings the brief added on 2026-11-17 are recorded as "
                       "candidates on links.html and their model lines have not been read at all - if the product set "
                       "widens, they join this list.")

by['H2']['owner_action'] = ("In Associates Central, open **Manage your Tracking ID** and confirm that "
                            "**shopnow047c-20** is listed. Then click one published link on this site, complete a "
                            "visit, and check the Summary Report for a click against that ID in the last 24 hours.")
by['H2']['why_now'] = ("What changed on 2026-11-17: the site stopped waiting for the short links and now composes "
                       "the Special Link itself - every buy CTA is amazon.com/dp/<ASIN> with `tag=` appended from "
                       "data/config.json, and the build refuses to publish one that forgets it. So the question is "
                       "no longer 'does the short link carry the tag' (it did not: none of the five showed `tag=` "
                       "when re-read that day) but 'is this ID live in an approved account, and does Amazon credit a "
                       "link we composed rather than generated'. The single click answers both. Tagging is also a "
                       "condition of the application review, which is final once rejected (S4).")
by['H2']['what_to_paste_back'] = ("Whether the ID appears in your tracking-ID list, and whether a click showed up "
                                  "against it within 24 hours. Two words each: 'listed / not listed', 'seen / not "
                                  "seen'. If it is 'not seen', say so and the site will switch to regenerating those "
                                  "links from the Product Linking tool rather than keep guessing.")
by['H2']['source'] = ["S6", "S2", "S4", "S17"]

h['items'].append(OD([
    ("id", "H6"),
    ("owner_action", ("Create one tracking ID per money page in the same screen, and paste them in the format "
                      "`picks.html: shopnow047c-1-20` \u2014 the site reads that mapping from data/config.json and "
                      "rebuilds every link with the right ID.")),
    ("time", "10 minutes"),
    ("closes", []),
    ("why_now", ("This is the only way to learn which pages earn clicks without putting a tracker on a site whose "
                 "privacy statement says it runs none. Amazon splits reporting by tracking ID by design, and the "
                 "policy forbids tying a sub-tag to an individual visitor \u2014 a per-page constant is the version "
                 "that is allowed. Nothing in this repository can create the IDs, and nothing will invent an "
                 "identifier: the build validates the shape and refuses a tag the config never declared."),),
    ("what_to_paste_back", "The list of IDs and which page each one is for. Empty is also an answer, and it closes Q-28 as 'not in use'.",),
    ("source", ["S2", "S6"]),
]))

h['not_possible_here'] = list(h['not_possible_here']) + [
    ("Whether a hand-composed tagged /dp/ link is credited by Amazon (Q-30). One click through one published link "
     "settles it inside 24 hours; nobody outside the account can observe the result."),
    ("Which brand SKU the new thermometer ASIN is (Q-29) \u2014 the listing's Product information block is rendered "
     "client-side, and the brand sells three near-identical F1 variants, so no figure from any of them may be "
     "published as this product's until someone reads it."),
]

d['compiled'] = TODAY
d['session'] = f"{SESS} (H1/H2 reworded and H6 added {TODAY}; originally arena/ba29c641-zone1)"
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- build.py: count the heading, don't type it
b = pathlib.Path('build.py'); s = b.read_text()
old = '''    not_possible = "".join(f"<li>{e(x)}</li>" for x in d["not_possible_here"])
    body = f"""
<p class="section-eyebrow">Handover</p>
<h1>Five actions, about an hour, eighteen flags</h1>
<p class="lede">Everything in this repository is done as far as it can be done without the account holder's own logins. These five actions are the shortest path from "unverified" to "confirmed". Each shows the time it takes and the flags it closes.</p>'''
new = '''    not_possible = "".join(f"<li>{e(x)}</li>" for x in d["not_possible_here"])
    # The heading used to type its own totals ("Five actions, about an hour, eighteen flags"), which
    # is the same drift this repository keeps finding and fixing in every other register: an add or a
    # removal changes the rows and the sentence silently becomes a historical document. Counted here
    # instead, from the rows the page is about to render. Minutes are parsed out of the `time` field
    # because that field is the only place an action's cost is recorded; a row whose time is not a
    # number (none today) contributes zero rather than a guess.
    acts = d["items"]
    n_actions = len(acts)
    n_minutes = sum(int(m) for t in (a.get("time") or "" for a in acts) for m in re.findall(r"^(\\d+)", t))
    closes_flags = [f for a in acts for f in (a.get("closes") or []) if re.fullmatch(r"F\\d+", f)]
    n_flags_closed = len(set(closes_flags))
    hours = (f"{round(n_minutes / 60)} hours" if n_minutes >= 90 else
             f"{n_minutes} minutes" if n_minutes < 60 else "about an hour")
    body = f"""
<p class="section-eyebrow">Handover</p>
<h1>{n_actions} actions, {hours}, {n_flags_closed} flags</h1>
<p class="lede">Everything in this repository is done as far as it can be done without the account holder's own logins. These {n_actions} actions are the shortest path from "unverified" to "confirmed". Each shows the time it takes and the flags it closes.</p>'''
if new.split("\n")[0] in s and old not in s:
    print('build.py already patched')
else:
    assert s.count(old) == 1, s.count(old)
    b.write_text(s.replace(old, new, 1))
    import ast; ast.parse(b.read_text())
    print('build.py: handover totals computed')
print('handover items:', len(h['items']))
