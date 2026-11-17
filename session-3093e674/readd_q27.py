import json, pathlib, collections

OD = collections.OrderedDict
p = pathlib.Path('data/questions.json')
d = json.load(open(p, encoding='utf-8'), object_pairs_hook=OD)
if any(q['id'] == 'Q-27' for q in d['questions']):
    print('Q-27 already present'); raise SystemExit(0)

Q27 = OD([
    ("id", "Q-27"),
    ("group", "Scope"),
    ("question", "Five product links are in the brief and three products are in the site. Is the product set now five, and who says so?"),
    ("state", "missing"),
    ("why_it_matters", ("It decides whether the next content push is written for one category or two, and it is the "
                        "difference between a shop with a plan and a shop that drifted. The two new links are real and "
                        "verified as destinations - a ThermoMaven instant-read (ASIN B0DHZTCNR5) and the CHEF iQ iQ "
                        "Sense Gen 3 (ASIN B0DZFD6R9Z), both under Kitchen Utensils & Gadgets > Thermometers & Timers "
                        "> Meat - but nothing in the repository states that the site is meant to market thermometers."),),
    ("what_we_know", [
        "The brief of 2026-11-13 listed three link.amazon URLs; the brief of 2026-11-17 lists five, and the two additions had never been read by this repository before that date.",
        "Both new links resolve, on first read, to meat-thermometer listings in a Home & Kitchen sub-tree rather than to the Air Fryers node the three originals sit under.",
        "Both are recorded, sourced and disclosed as candidates in data/products.json and data/link-intent.json; neither appears in the comparison, the category table or the figures.",
    ]),
    ("what_is_missing", ("A scope statement: keep it air-fryers only and drop the two links, or widen the category. "
                         "Either answer is workable; 'both, sort of' is the one that is not, because a half-marketed "
                         "product page ranks for nothing and earns nothing."),),
    ("how_to_discover", ("Nobody needs to discover anything - the owner decides. The evidence for the decision is on "
                         "links.html (LI-04 and LI-05), which shows what each new link reaches and what is still "
                         "unknown about it. The cheapest path to a real answer: one thermometer buying guide, four "
                         "weeks, measured by Search Console (SG-29) before a second is committed."),),
    ("blocks", ["SG-37"]),
    ("sources", [
        OD([("label", "Amazon detail page for ASIN B0DHZTCNR5, read live 2026-11-17"),
            ("url", "https://www.amazon.com/dp/B0DHZTCNR5")]),
        OD([("label", "Amazon detail page for ASIN B0DZFD6R9Z, read live 2026-11-17"),
            ("url", "https://www.amazon.com/dp/B0DZFD6R9Z")]),
        OD([("label", "This repository's product-intent record"),
            ("url", "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/link-intent.json")]),
    ]),
])
idx = max(i for i, q in enumerate(d['questions']) if q['id'] == 'Q-26')
d['questions'].insert(idx + 1, Q27)
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print('Q-27 restored at index', idx + 1, '| total', len(d['questions']))
