import json, sys, pathlib, collections

D = pathlib.Path('data')


def load(name):
    return json.load(open(D / name, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)


def save(name, d):
    json.dump(d, open(D / name, 'w'), indent=2, ensure_ascii=False)
    open(D / name, 'a').write("\n")


TODAY = "2026-11-17"

# ============================================================ sources: S40 (CHEF iQ FAQ)
src = load('sources.json')
assert 'S40' not in {s['id'] for s in src['sources']}
src['sources'].append(collections.OrderedDict([
    ("id", "S40"),
    ("org", "CHEF iQ (the brand's own support page)"),
    ("title", "iQ Sense FAQ — CHEF iQ (probe temperature limits, app requirement, cleaning)"),
    ("url", "https://chefiq.com/pages/new-iq-sense-faq"),
    ("covers", ("The limits that the product page does not break down: the portion of the probe inserted into food is rated "
                "to 212˚F, the ambient sensor at the ceramic end to 752˚F, and Gen 3's maximum ambient limit to 1,000ºF; the "
                "probe is waterproof and 'technically top-rack dishwasher safe' though the brand advises against it; the hub "
                "is not waterproof; the app is required to see any data; up to 4 probes pair to a Gen 3 hub; the hub holds a "
                "charge for 20 hours and a Gen 3 probe for up to 60.")),
    ("kind", "Brand support page"),
    ("directness", "Primary — the manufacturer's own answers about its own product"),
    ("page_version", (f"Fetched {TODAY}. Quoted verbatim where this register or an article uses the wording. The page is dated "
                      "in no visible way, so every value taken from it is labelled with this reading date rather than a "
                      "publication date.")),
    ("verified", f"Read live {TODAY} by session arena/3093e674-zone1; see reports/verification-2026-11-17-3093e674.md."),
]))
save('sources.json', src)
print('sources:', len(src['sources']))

# ============================================================ products: candidate spec rows
prod = load('products.json')
cands = {c['slug']: c for c in prod['candidates']}
chefiq = cands['chef-iq-sense-gen3']
chefiq['specs'] = [s for s in chefiq['specs'] if s['label'] not in ('Amazon price', 'Star rating / review count')]
chefiq['specs'] += [
    {"label": "Probe limit, food end", "value": "212˚F for the portion inserted into the food", "source": ["S40"],
     "status": "verified",
     "note": ("The figure the marketing headline does not carry. The product page's 1,000°F is the ambient end; this is the "
              "part that sits inside the dinner, and the two are different numbers by design (S38 vs S40).")},
    {"label": "Probe limit, ambient end", "value": "752˚F at the ceramic end; Gen 3 maximum ambient limit 1,000ºF",
     "source": ["S40"], "status": "verified"},
    {"label": "App requirement", "value": "a smart device and the free brand app are required to see any data",
     "source": ["S40"], "status": "verified"},
    {"label": "Cleaning, per the brand", "value": "probe waterproof and 'technically top-rack dishwasher safe' (not advised); hub not waterproof",
     "source": ["S40"], "status": "verified"},
    {"label": "Amazon price", "value": None, "source": ["S37"], "status": "unverified",
     "unverified": "Not displayed by policy (S2 §2(b))."},
    {"label": "Star rating / review count", "value": None, "source": ["S37"], "status": "unverified",
     "unverified": "Not displayed by policy (S2 §6(t))."},
]
prod['candidates'] = list(cands.values())
save('products.json', prod)
print('candidate specs:', {c['slug']: len(c['specs']) for c in prod['candidates']})

# ============================================================ articles: TP-21 and TP-22
art = load('articles.json')
existing = {a['slug'] for a in art['articles']}
assert 'questions-before-a-multi-function-appliance' not in existing
art['articles'] += [
    collections.OrderedDict([
        ("slug", "questions-before-a-multi-function-appliance"),
        ("kind", "Buying guide"),
        ("kicker", "Before you buy"),
        ("title", "Questions to ask before buying a multi-function kitchen appliance"),
        ("standfirst", "A box that claims eleven jobs is selling you a decision you have to make on seven "
                       "separate questions. Ask them in this order and most of the market sorts itself out "
                       "before a price is involved — and none of them needs a review, a tester or a video.",),
        ("target_query", "questions to ask before buying a multi function air fryer oven"),
        ("intent", "Commercial investigation"),
        ("reading_minutes", 8),
        ("products", ["emeril-26qt-french-door", "chefman-6qt-dual-basket", "chefman-8qt-turbofry"]),
        ("sections", [
            {"h": "1. What is the second function, and what replaces it?",
             "paras": [
                 "A multi-function appliance earns its counter space by standing in for something you would otherwise "
                 "own. The question is not how many functions are listed but which one you would genuinely stop using. "
                 "The largest machine in this guide documents a {{75–500 °F / 25–260 °C}} range, which is a dehydrator, "
                 "an oven and a proofing box in one envelope; the two basket machines start at {{200–400 °F}} and "
                 "{{200–450 °F / 95–235 °C}} and do not pretend otherwise.",
                 "The trade you are not told about: an appliance that can do eleven things usually does the eleventh "
                 "through the same fan, the same cavity and the same rack position. Read the function list as a claim "
                 "about the temperature range, because that is the only part of it a specification can settle."
             ],
             "cite": ["S15", "S12", "S10"]},
            {"h": "2. Does the quoted maximum apply to every mode?",
             "paras": [
                 "This is the question that separates a documented product from a marketed one. The 8-quart basket "
                 "model is sold with a high-temperature option and its brand page gives one upper bound while its "
                 "collection page gives a lower one — the disagreement is published on this site as a conflict rather "
                 "than resolved, because both pages are the manufacturer's.",
                 "Ask the same question of any mode you intend to use daily. If the answer is a marketing badge rather "
                 "than a number in the manual, you are buying the badge."
             ],
             "cite": ["S12", "S26", "S2"]},
            {"h": "3. How many of the claimed presets are documented anywhere?",
             "paras": [
                 "Preset counts are the loudest number on the box and the least stable. The large French-door oven's "
                 "own brand page carries '25 Cooking Pre-sets' in one block, an '10-in-1' functions line in its "
                 "copy and an asset named for eleven, while the retail listing that sells it says 24. Three numbers, "
                 "one product, one page.",
                 "Treat the count as a hint about the interface, not a capability. If you will cook six things in it, "
                 "six presets you understand beat nineteen you will never press."
             ],
             "cite": ["S14", "S28", "S35"]},
            {"h": "4. Will it fit where you actually cook?",
             "paras": [
                 "Measure three things before you decide: the counter depth, the height to the cabinet above, and the "
                 "clearance the manual demands. The published footprints are {{16.9 D × 15.8 W × 14.8 H in}} for the "
                 "oven-style machine and {{13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm}} for the dual basket.",
                 "The clearance line is the one people skip, and it is in the manual rather than the listing because "
                 "it is a safety instruction, not a specification. A machine that fits against the wall on paper is "
                 "not a machine that can be used against the wall."
             ],
             "cite": ["S14", "S10", "S18"]},
            {"h": "5. What has to be washed, and by hand?",
             "paras": [
                 "Multi-function means multi-part: racks, trays, a rotisserie spit, a crumb tray, and a cavity that "
                 "cannot be submerged. The basket machines get the dishwasher-safe claim on their baskets; the oven "
                 "format spreads its accessories across several pieces, and the brand's own box contents are what you "
                 "should count — this listing's title claims six accessories while the manual contents run to seven, "
                 "which is published as a discrepancy rather than averaged.",
                 "Ask which parts touch food and which touch the heating element. The second group is where a "
                 "cleanup regret lives."
             ],
             "cite": ["S28", "S15", "S10"]},
            {"h": "6. What does it ask of your circuit?",
             "paras": [
                 "All three appliances in this guide draw 1700 watts. That is the number that decides whether the "
                 "machine shares an outlet with a kettle or a microwave, and whether an extension cord is allowed at "
                 "all — the manuals answer the cord question differently for different models, which is documented "
                 "on this site with the sentences quoted.",
                 "If your kitchen has one 20-amp circuit for every counter outlet, an eleven-function appliance can "
                 "be a two-function appliance at dinnertime."
             ],
             "cite": ["S13", "S18", "S15"]},
            {"h": "7. Who stands behind it, in writing?",
             "paras": [
                 "Warranty terms for these products are published by the brands, not by the marketplace: a "
                 "one-year assurance on one, a lifetime statement on an accessory from a different category, a "
                 "third-party protection plan offered at checkout on the retail page. Read the brand's sentence, "
                 "because the listing is a storefront and the guarantee is a manufacturer's.",
                 "This is also where this site stops. It publishes what the documents say and the date each one was "
                 "read; it does not own a machine, has not cooked in one, and will not tell you how it feels."
             ],
             "cite": ["S10", "S14", "S2"]},
            {"h": "The one-question version",
             "paras": [
                 "If you only ask one question, ask this: which of these claims is in the manual rather than the "
                 "listing? Everything else is decoration around that answer."
             ],
             "cite": ["S2"]},
        ]),
        ("closing_note", "Every figure above is quoted from a manufacturer page, an owner's manual or a listing that "
                         "this site read on a date it publishes. No product was tested for this article, and nothing "
                         "here is a recommendation to buy a specific model."),
    ]),
    collections.OrderedDict([
        ("slug", "meat-thermometer-in-an-air-fryer"),
        ("kind", "Explainer"),
        ("kicker", "Two appliances, one question"),
        ("title", "Can you put a wireless meat thermometer in an air fryer? What the makers write"),
        ("standfirst", "The probe brand publishes a compatibility list, the air fryer maker publishes a temperature "
                       "range, and the two numbers do not describe the same part of the probe. That gap is the whole "
                       "answer, and it is in the documents.",),
        ("target_query", "can i use a wireless meat thermometer in an air fryer"),
        ("intent", "Informational"),
        ("reading_minutes", 6),
        ("products", ["chefman-6qt-dual-basket", "chefman-8qt-turbofry", "emeril-26qt-french-door"]),
        ("sections", [
            {"h": "What the probe maker says first",
             "paras": [
                 "The brand page for the wireless probe lists the appliances it is compatible with, and an air fryer is "
                 "on the list: oven, stovetop, gas and charcoal grills, smoker, air fryer, deep fryer, and sous vide. "
                 "It also states heat resistance up to {{up to 1,000°F (537°C)}} and five sensors — four internal, one "
                 "ambient.",
                 "So the manufacturer-facing answer to 'can it go in an air fryer' is yes, in the same sentence that "
                 "lists a deep fryer. What that list does not say is which part of the probe survives which temperature "
                 "for how long, and the FAQ has to be read for that."
             ],
             "cite": ["S38"]},
            {"h": "The two limits, which are not the same number",
             "paras": [
                 "The brand's own FAQ splits the probe into two zones: {{212˚F for the portion inserted into the food}} "
                 "and {{752˚F at the ceramic end; Gen 3 maximum ambient limit 1,000ºF}} at the ambient sensor. A single "
                 "'1,000°F' headline is true of the end that reads your oven, not of the shaft inside the dinner.",
                 "That distinction is why a probe can survive a 450-degree cavity and still be a poor fit for a small "
                 "one: in an air fryer the food, the fan and the element are centimetres apart, and the manual for the "
                 "appliance, not the thermometer, governs what may sit in the airflow."
             ],
             "cite": ["S40", "S38"]},
            {"h": "What the air fryer side documents",
             "paras": [
                 "The oven-style appliance in our set documents {{75–500 °F / 25–260 °C}}; the basket models document "
                 "{{200–400 °F}} and {{200–450 °F / 95–235 °C}}. None of the three manuals we read contains a sentence "
                 "about leaving a probe or its cable in the cavity — which is worth stating plainly, because 'the "
                 "manual does not forbid it' is not the same fact as 'the manual permits it'.",
                 "The manuals do carry instructions that change the shape of the question: the vents must stay clear, "
                 "and non-stick aerosol sprays are cautioned against on the basket coatings. A cable routed through a "
                 "door seal and sitting in an airflow touches both of those rules at once."
             ],
             "cite": ["S15", "S12", "S10", "S18", "S13"]},
            {"h": "The practical difference the listings blur",
             "paras": [
                 "An instant-read thermometer is a different object from a wireless probe: you take the first out, "
                 "which is why the brand can quote ±0.5℉ accuracy and a sub-second reading without any temperature "
                 "rating for leaving it in. The second stays in the food for the whole cook, so its cable, its handle "
                 "and its battery are all inside the hot space.",
                 "If the reason you want a probe in an air fryer is to stop opening the door, an instant-read on the "
                 "counter beside it answers that too — and it is the option with fewer things left in the heat."
             ],
             "cite": ["S39", "S40"]},
            {"h": "What nobody has answered, including this page",
             "paras": [
                 "Nothing we read states a maximum air-fryer temperature for a probe cable, and nothing states whether "
                 "a hub or its charging case may sit next to a running appliance. Those are the two questions a buyer "
                 "should send to the probe brand's support line, and we would rather print the gap than fill it with a "
                 "guess that sounds like advice.",
                 "This site has not put a probe in an air fryer. It has read what both manufacturers publish, on the "
                 "dates recorded in the source list, and it says so here rather than in a footnote."
             ],
             "cite": ["S2", "S8"]},
        ]),
        ("closing_note", "Two manufacturers' pages and three manuals, quoted; no testing, and no claim that either "
                         "combination is safe or unsafe — the numbers are published so the question can be asked of "
                         "the brand directly."),
    ]),
]
art['updated'] = TODAY
save('articles.json', art)
print('articles:', len(art['articles']))

# ============================================================ topics: register the two new rows
top = load('topics.json')
top['topics'] += [
    collections.OrderedDict([
        ("id", "TP-21"),
        ("title", "Questions to ask before buying a multi-function kitchen appliance"),
        ("hook", "Eleven functions, seven questions. Only the questions can be answered from a document."),
        ("intent", "Commercial investigation"),
        ("serves", ["emeril-26qt-french-door", "chefman-6qt-dual-basket", "chefman-8qt-turbofry"]),
        ("angle", ("The fourth of the four editorial hypotheses the project brief named, and the only one not already "
                   "covered by the article set. Written as a checklist a reader can carry into any listing, using the "
                   "conflicts this repository has already documented as worked examples rather than as evidence about "
                   "one product.")),
        ("why_it_could_earn_traffic", ("Judgement: a question-shaped guide at the consideration stage, aimed at the "
                                       "phrase a shopper types before they narrow to a model. No search-volume claim is "
                                       "made — this repository has no keyword tool.")),
        ("status", "published"),
        ("published_as", "articles/questions-before-a-multi-function-appliance.html"),
        ("must_cite", [
            {"label": "Emeril French Door AirFryer 360 owner's manual", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB.pdf"},
            {"label": "Chefman 8 Qt TurboFry Touch product page", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"},
            {"label": "Chefman 6 Qt Dual-Window product page", "url": "https://chefman.com/products/turbofry-touch-dual-window-air-fryer"}]),
        ("caveat", "The brief lists this as a working title, not as a measured demand signal. Whether anyone arrives is a Search Console question (SG-29), not a claim this row can make."),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "TP-22"),
        ("title", "Can you put a wireless meat thermometer in an air fryer?"),
        ("hook", "The probe is rated to 1,000°F. So is not the part you think."),
        ("intent", "Informational"),
        ("serves", ["chefman-6qt-dual-basket", "chefman-8qt-turbofry", "emeril-26qt-french-door"]),
        ("angle", ("The bridge between the three products this site has marketed for four days and the two added by "
                   "the brief of 2026-11-17: the probe maker's own compatibility list names an air fryer, its FAQ "
                   "splits the probe into a 212°F food end and a 1,000°F ambient end, and the air fryer manuals say "
                   "nothing either way. Publishing that gap is the article.")),
        ("why_it_could_earn_traffic", ("Judgement: a long-tail question with two manufacturers' numbers in tension is "
                                       "the kind of query an AI answer engine cannot resolve without reading both "
                                       "pages, which is the position this site is built to hold.")),
        ("status", "published"),
        ("published_as", "articles/meat-thermometer-in-an-air-fryer.html"),
        ("must_cite", [
            {"label": "iQ Sense — CHEF iQ product page", "url": "https://chefiq.com/products/iq-sense"},
            {"label": "iQ Sense FAQ — CHEF iQ", "url": "https://chefiq.com/pages/new-iq-sense-faq"},
            {"label": "ThermoMaven F1 product page", "url": "https://www.thermomaven.com/products/f1"}]),
        ("caveat", ("Nothing here is a safety verdict. The site has not put a probe in an air fryer; it publishes what "
                    "each manufacturer states and names the two questions neither answers.")),
        ("blocked_by", ["Q-29"]),
    ]),
]
top['version'] = "2"
top['compiled'] = TODAY
top['compiled_by'] = "arena/3093e674-zone1 (pass 13); originally arena/63a2c638 (integration pass 9)"
save('topics.json', top)
pub = sum(1 for t in top['topics'] if t['status'] == 'published')
print('topics:', len(top['topics']), 'published', pub)
