#!/usr/bin/env python3
"""Session arena/19d92a81 — content extension, part 1: articles + topics.

Adds three seasonal, source-led articles and five topic rows.
Every {{placeholder}} in the articles is assembled from data/products.json at
runtime, so the value cannot drift from the published dataset (build guard
check_articles() re-proves this after generation).

Run from the repository root:  python3 session-19d92a81/extend_articles.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

PRODS = {p["slug"]: p for p in json.load(open(DATA / "products.json"))["products"]}


def val(slug, label):
    for s in PRODS[slug]["specs"]:
        if s["label"] == label:
            return s["value"]
    raise KeyError(f"{slug}/{label}")


def ph(slug, label, prose=None):
    v = val(slug, label)
    return "{{" + v + ("::" + prose if prose else "") + "}}"


C6, E26, C8 = "chefman-6qt-dual-basket", "emeril-26qt-french-door", "chefman-8qt-turbofry"

art1 = {
    "slug": "black-friday-model-number-switch",
    "kind": "Investigation",
    "kicker": "Seasonal / deal safety",
    "title": "The Black Friday model-number switch, and the three-minute check that catches it",
    "standfirst": (
        "Discount badges stack up in November. The listings underneath them do not always "
        "describe the same machine - including the three this site tracks. Here is the "
        "documented version, and the check to run before the deal timer wins."
    ),
    "target_query": "black friday air fryer deals",
    "intent": "Commercial investigation",
    "reading_minutes": 6,
    "products": [C8, C6, E26],
    "sections": [
        {
            "h": "One listing, two machines' features",
            "paras": [
                "The Amazon listing behind this site's 8-quart pick sells a stainless-steel air fryer whose title advertises a Hi-Fry button and a high-heat finish. Chefman documents that button on a different model: the matte-black RJ38-8T-BLACK, whose own page lists four functions and a two-minute 450F finish. The stainless unit, RJ38-SQSS-8T, is documented with a ceiling of " + ph(C8, "Temperature range") + " and no Hi-Fry mode anywhere in its own documentation.",
                "Neither machine is a fake, and the listing is not a scam. It is a hybrid: title features borrowed from one model, finish borrowed from the other. This repository has carried that conflict as an open flag through several verification rounds precisely because a rendered listing page is the only place it shows.",
            ],
            "cite": ["S29", "S26", "S12"],
        },
        {
            "h": "The same pattern one size down",
            "paras": [
                "Chefman's 6-quart drawer exists in three documented variants: the dual-window model this site tracks (RJ38-SQPF-3TDB-2W), a sibling labelled 'Dual-Basket' (RJ38-SQPF-3TDB-2), and a third 'Easy View Windows' double-basket page (RJ38-3DBW-V2). Different pages, different features, near-identical names - the exact conditions a deal carousel compresses into one thumbnail.",
                "The Emeril oven shows the softer version of the same problem: one official product page states its preset count two different ways, and the owner's manual states it a third. The manual's countable list is the one this site publishes against; the reasoning is written up in the preset-count investigation.",
            ],
            "cite": ["S10", "S18", "S27", "S25", "S14", "S15"],
        },
        {
            "h": "Why deal season makes it worse",
            "paras": [
                "**Judgement, not a sourced fact:** bundles, seller swaps and open-box stock all move faster in November, and a listing title can be edited independently of the product behind it. The discount timer is doing retail work, not verification work.",
                "A model number is the opposite. It sits in the listing's Product information table, it maps to one manufacturer page, and it cannot drift from the thing itself without changing the thing itself.",
            ],
            "cite": ["S2"],
        },
        {
            "h": "The three-minute check",
            "paras": [
                "Find the Model Number row in the listing's Product information table, and match it against the brand's own product page - not against the title. If the title's features and the model page's features disagree, the model page is describing the machine that will actually arrive.",
                "Count what the manual says is in the box against what the listing shows. The oven this site tracks records " + ph(E26, "Included accessories") + " accessories across two official statements, while its own manual cautions that not every pictured accessory ships with every unit: 'Some accessories may not be included with purchase.'",
                "**Judgement:** do the check before the timer runs out, not after. A deal that survives three minutes of reading is a deal worth taking; one that does not was selling the countdown, not the appliance.",
            ],
            "cite": ["S29", "S14", "S15", "S2"],
        },
    ],
    "closing_note": (
        "No product in this article was tested, and no listing was purchased. Model pages "
        "and listing titles were read on 2026-11-15 and 2026-11-16 and are linked per "
        "section. This site displays no Amazon prices or discount percentages."
    ),
}

art2 = {
    "slug": "air-fryer-gift-guide-2026",
    "kind": "Buying guide",
    "kicker": "Seasonal / gift guide",
    "title": "The honest 2026 air-fryer gift guide: match the format to the person",
    "standfirst": (
        "An air fryer is a wonderful gift and a terrible surprise. Three documented "
        "formats, matched to three kinds of kitchens, with the fine print that decides "
        "whether the gift is still there in February."
    ),
    "target_query": "air fryer gift ideas",
    "intent": "Commercial investigation",
    "reading_minutes": 7,
    "products": [C6, C8, E26],
    "sections": [
        {
            "h": "Give the format, not the feature list",
            "paras": [
                "Every air fryer on this page moves hot air. What separates them is shape: two drawers, one big basket, or a countertop oven with doors. The shape decides what fits the counter, what fits dinner, and what survives the return window; the feature list decides very little.",
                "This is the site's usual format map told as a gift problem. You are matching an appliance to a kitchen you may never have stood in, so the documented measurements below matter more than the adjectives.",
            ],
            "cite": ["S10", "S12", "S14"],
        },
        {
            "h": "For the person cooking for one or two, on one counter",
            "paras": [
                "The dual-basket Chefman is documented at " + ph(C6, "Capacity") + " total, divided into " + ph(C6, "Per-basket capacity", "two 3-quart baskets") + " with independent time and temperature. Its footprint is recorded at " + ph(C6, "Dimensions") + " and it weighs " + ph(C6, "Product weight") + " - the lightest of the three, which matters when the gift has to be carried up stairs.",
                "The documented gift-saver on this model is Sync Finish: the shorter cook waits so both drawers land together, per the product page and the manual. For someone whose cooking rhythm is a protein plus a side, that is the feature that gets used in week one.",
            ],
            "cite": ["S10", "S18"],
        },
        {
            "h": "For the household that cooks in batches",
            "paras": [
                "The 8-quart basket is described by its own brand page as " + ph(C8, "Stated household size", "designed for 4–6 people") + ", with four one-touch programs documented: " + ph(C8, "Presets") + ". Its recorded footprint is " + ph(C8, "Dimensions / weight") + ".",
                "One catch this site has documented at length: the Amazon listing for this size mixes features of two Chefman models. Before buying it as a gift, run the model-number check from the Black Friday piece above.",
            ],
            "cite": ["S12", "S13"],
        },
        {
            "h": "For the one who wanted an oven",
            "paras": [
                "The Emeril French-door unit is a countertop oven that air fries: " + ph(E26, "Capacity") + ", doors documented as " + ph(E26, "Door type", "french doors, single-pull opening") + ", and a rotisserie - " + ph(E26, "Rotisserie", "yes (manual documents a rotisserie preset and spit set)") + " - that no basket can offer.",
                "It is also the physically largest gift here at " + ph(E26, "Dimensions") + ", and its manual asks for five inches of clearance on the top, back and sides. Measure the recipient's cabinets before the wrapping paper goes on.",
            ],
            "cite": ["S14", "S15"],
        },
        {
            "h": "The fine print that decides whether the gift stays",
            "paras": [
                "Warranty is the gift receipt's backup. Chefman documents " + ph(C8, "Warranty", "limited 1-year warranty from date of retail purchase (non-transferable, original purchaser)") + " on the 8-quart page, and the dual-basket's warranty is recorded as " + ph(C6, "Warranty") + ".",
                "The Emeril manual documents both a 90-day money-back guarantee and a one-year replacement guarantee that, in its own words, extends only to the original purchaser and is not transferable - and it requires proof of purchase. That last line is the gift instruction: leave the receipt in the box. Everything else in this guide is a preference; that one is a rule from the manual.",
                "The gift-size traps this set has already produced: an accessory count two official documents agree on while the manual cautions 'Some accessories may not be included with purchase', and cord rules that split by brand - the Chefman manuals permit a rated extension cord with care, while the Emeril manual says never. If the recipient's outlet is across the kitchen, that difference is the gift.",
            ],
            "cite": ["S10", "S12", "S13", "S14", "S15"],
        },
    ],
    "closing_note": (
        "No product in this guide was tested, and no price is shown - Amazon prices may "
        "only be displayed when Amazon serves the link or the data comes from the official "
        "API. Warranty and guarantee wording is quoted from each manufacturer's own page "
        "or manual, linked per section."
    ),
}

art3 = {
    "slug": "how-to-clean-an-air-fryer",
    "kind": "Guide",
    "kicker": "Care and upkeep",
    "title": "How to clean an air fryer, according to the people who made it",
    "standfirst": (
        "Three manuals in this set carry cleaning sections. Quoted side by side, they "
        "agree on the big rules and split on the details. No vinegar hacks and no life "
        "tricks - just the instructions in the box."
    ),
    "target_query": "how to clean an air fryer",
    "intent": "Informational",
    "reading_minutes": 5,
    "products": [C6, C8, E26],
    "sections": [
        {
            "h": "The rules all three manuals share",
            "paras": [
                "Unplug first, cool down first. The Emeril manual's cleaning section opens with it: remove the power cord from the wall socket and be certain the appliance is thoroughly cooled before cleaning. Its instructions add a specific wait - allow at least thirty minutes to cool before attempting cleaning or storing.",
                "Never submerge the appliance body. The Chefman dual-window manual says the unit is wiped with a damp cloth and never submerged; the Emeril's before-first-use steps say the same in different words.",
            ],
            "cite": ["S15", "S18"],
        },
        {
            "h": "Where the manuals split: the dishwasher",
            "paras": [
                "The two Chefman units put their cooking parts on the top rack. The dataset's care rows read: " + ph(C6, "Basket coating / care") + ", and for the 8-quart, " + ph(C8, "Basket coating / care", "nonstick basket and rack; top-rack dishwasher safe") + ".",
                "The Emeril oven draws the line differently. Its accessories are hand-wash - caked-on food should be soaked in warm, soapy water, and hand-washing is recommended - and the appliance body may not be soaked, submerged, or washed in the dishwasher. A countertop oven is not a basket, and its manual says so.",
            ],
            "cite": ["S10", "S18", "S12", "S13", "S15"],
        },
        {
            "h": "The one rule that saves the coating",
            "paras": [
                "The dual-basket manual's caution is worth reading once in the manufacturer's own words: never spray the baskets or racks with cooking oil from an aerosol spray can. The manual offers the substitute in the same breath - fill a non-aerosol mister instead.",
                "The 8-quart manual records no aerosol rule, and this site does not extend one model's rule to another by analogy. The mister satisfies the rule that exists and breaks none that do.",
            ],
            "cite": ["S18", "S13"],
        },
        {
            "h": "The never list, in the manuals' own words",
            "paras": [
                "Metal scouring pads are banned in the Emeril manual: pieces can break off and touch electrical parts. Non-metallic pads only. Abrasive cleansers are out on the Chefman side as well.",
                "Do not scrub the heating coils - the Emeril manual calls them fragile and says they may break - and rinse the interior so no standing water is left behind.",
            ],
            "cite": ["S15", "S18"],
        },
        {
            "h": "A five-minute routine built only from the above",
            "paras": [
                "**Judgement, assembled from the instructions above:** cool, unplug, remove parts, soak anything caked, top-rack the dishwasher-safe parts and hand-wash the rest, wipe the cavity with a damp cloth and mild detergent, dry, reassemble. Nothing here is a home remedy; it is the manuals' steps in one order.",
            ],
            "cite": ["S15", "S18", "S13"],
        },
    ],
    "closing_note": (
        "No product was cleaned for this article. Every instruction above is quoted or "
        "condensed from the manufacturer manuals linked per section, read on 2026-11-16."
    ),
}

new_topics = [
    {
        "id": "TP-15",
        "title": "The Black Friday model-number switch: the deal that quietly changes the product",
        "hook": "Deal season is the season of near-identical model numbers - and this repo has already caught one.",
        "intent": "Commercial investigation",
        "serves": [C8, C6, E26],
        "angle": "The supplied Amazon listing for the 8-quart borrows features from one Chefman model and its finish from another. That documented conflict becomes the seasonal story, plus a three-minute pre-purchase check.",
        "why_it_could_earn_traffic": "Judgement: 'black friday air fryer deals' is a high-intent seasonal query, and a source-led deal-safety angle is differentiated from the price-roundup pages that dominate it. Demand is argued, not measured (see demand_note).",
        "must_cite": [
            {"label": "Amazon listing for the 8-quart (title mixes two models)", "url": "https://www.amazon.com/dp/B08DKYBTPH"},
            {"label": "Chefman RJ38-8T-BLACK product page", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-8-qt-air-fryer-w-high-fry"},
        ],
        "status": "published",
        "published_as": "articles/black-friday-model-number-switch.html",
        "blocked_by": [],
    },
    {
        "id": "TP-16",
        "title": "The honest 2026 air-fryer gift guide: match the format to the person",
        "hook": "The gift question is a counter-space question. Answer it with tape measures, not adjectives.",
        "intent": "Commercial investigation",
        "serves": [C6, C8, E26],
        "angle": "Three documented formats matched to three kinds of kitchens, with warranty, cord and accessory-count fine print taken from the manuals - including the 'keep the receipt' rule the Emeril manual actually states.",
        "why_it_could_earn_traffic": "Judgement: the gift-guide format is the classic affiliate genre for Q4, and 'air fryer gift ideas' searches arrive pre-purchase. A guide that leads with fit and fine print earns links from the care and deal pieces.",
        "must_cite": [
            {"label": "Emeril FAFO-001 owner's manual (guarantee, proof of purchase)", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"},
            {"label": "Chefman 8 Qt TurboFry Touch product page (warranty, household size)", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"},
        ],
        "status": "published",
        "published_as": "articles/air-fryer-gift-guide-2026.html",
        "blocked_by": [],
    },
    {
        "id": "TP-17",
        "title": "How to clean an air fryer, according to the people who made it",
        "hook": "The post-gift question with the biggest audience and the emptiest search results full of vinegar hacks.",
        "intent": "Informational",
        "serves": [C6, C8, E26],
        "angle": "The three manuals' cleaning sections quoted side by side: what is dishwasher-safe per model, the aerosol caution, the never list. Informational intent feeds the commercial pages through internal links.",
        "why_it_could_earn_traffic": "Judgement: care queries peak after gifting seasons and recur with every new owner; the honest-source angle fits this site's voice where recipe-blog answers do not. Demand is argued, not measured.",
        "must_cite": [
            {"label": "Chefman RJ38-SQPF-3TDB-2W owner's manual (care and cleaning)", "url": "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf"},
            {"label": "Emeril FAFO-001 owner's manual (Cleaning & Storage)", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"},
        ],
        "status": "published",
        "published_as": "articles/how-to-clean-an-air-fryer.html",
        "blocked_by": [],
    },
    {
        "id": "TP-18",
        "title": "January: the first-week setup and care checklist for a gifted air fryer",
        "hook": "Every December gift has a first week. This is the page that survives it.",
        "intent": "Informational",
        "serves": [C6, C8, E26],
        "angle": "A compilation from the manuals' before-first-use, care and safety sections: burn-in steps, clearance, cord rules, first-cook presets. Seasonal, but reusable every year.",
        "why_it_could_earn_traffic": "Judgement: compiles three already-verified source sets into one seasonal landing page; January is when gifted units get their first use and their first search.",
        "must_cite": [
            {"label": "Emeril FAFO-001 owner's manual (Before First Use)", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"},
        ],
        "status": "proposed",
        "published_as": None,
        "blocked_by": ["Q-20"],
    },
    {
        "id": "TP-19",
        "title": "Prime Day 2027: the summer version of the model-number check",
        "hook": "The July edition of the November problem, with the same three-minute fix.",
        "intent": "Commercial investigation",
        "serves": [C8, C6, E26],
        "angle": "Seasonal sequel to the Black Friday piece: refresh the model-conflict watchlist before the sale event, not during it. Blocked until the marketplace question is answered, because Prime Day is marketplace-specific.",
        "why_it_could_earn_traffic": "Judgement: seasonal events concentrate buying intent twice a year; the same verified watchlist serves both. Demand is argued, not measured.",
        "must_cite": [
            {"label": "Flag register (model-conflict rows)", "url": "https://kanlerxz87-cyber.github.io/Zone1/flagged.html"},
        ],
        "status": "proposed",
        "published_as": None,
        "blocked_by": ["Q-20"],
    },
]


def main():
    a = json.load(open(DATA / "articles.json"))
    have = {x["slug"] for x in a["articles"]}
    for art in (art1, art2, art3):
        assert art["slug"] not in have, art["slug"]
        a["articles"].append(art)
    a["updated"] = "2026-11-16"
    (DATA / "articles.json").write_text(
        json.dumps(a, indent=1, ensure_ascii=False) + "\n")

    t = json.load(open(DATA / "topics.json"))
    have_t = {x["id"] for x in t["topics"]}
    for tp in new_topics:
        assert tp["id"] not in have_t, tp["id"]
        t["topics"].append(tp)
    t["compiled"] = "2026-11-16"
    (DATA / "topics.json").write_text(
        json.dumps(t, indent=1, ensure_ascii=False) + "\n")

    print("articles:", len(a["articles"]), "topics:", len(t["topics"]))


if __name__ == "__main__":
    main()
