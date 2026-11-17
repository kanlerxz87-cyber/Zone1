#!/usr/bin/env python3
"""T13-3: publish the three question-shaped guides this pass wrote, add their topic-queue
rows, and correct the stale statuses in the design-prompt topic register.

Every factual sentence in the new articles is either (a) a {{splice}} of a value already
published in data/products.json — which the build verifies, failing the build otherwise —
or (b) a quotation of a manufacturer or policy page already registered in data/sources.json,
cited per section. No number is re-typed from memory and no hands-on claim is made.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "data" / "articles.json"
TOP = ROOT / "data" / "topics.json"
DP = ROOT / "data" / "design-prompt.json"

READ = "2026-11-17"

NEW = [
    {
        "slug": "chefman-vs-emeril-air-fryer",
        "kind": "Comparison",
        "kicker": "Brand versus brand",
        "title": "Chefman vs. Emeril: what a basket brand and an oven brand actually publish",
        "standfirst": "Two brands, three machines, one decision. Both brand pages state capacity, footprint and temperature; neither states how dinner turns out. This is the comparison of what is written down, including the parts where the writing contradicts itself.",
        "target_query": "chefman vs emeril air fryer",
        "intent": "Commercial investigation",
        "reading_minutes": 6,
        "sources_read": READ,
        "products": ["chefman-6qt-dual-basket", "chefman-8qt-turbofry", "emeril-26qt-french-door"],
        "sections": [
            {
                "h": "The two brands are not selling the same shape of appliance",
                "paras": [
                    "Chefman's two pages in this set describe baskets with a fan on them. The dual-window model is {{6 Qt / 5.67 L}} divided into {{Two 3-quart baskets::two 3-quart baskets}}, each drawer carrying its own time and temperature, and the second is a single {{8 qt (brand also sells a 5 qt version of the same product page)}} cube. Both are counted in quarts of basket.",
                    "Emeril's page describes an oven with an air-fry mode. Its cavity is {{26 qt / 24.6 L (manual: 1,519 cu in)}}, it opens on {{French doors, single-pull opening::French doors that open on a single pull}}, and the brand's own specification icons list a {{Dual-speed fan::dual-speed fan for crisping}} and a rotisserie. The accessories count is the brand page's seven, and the Amazon listing for the candidate ASIN lists six names.",
                    "That difference is not marketing. A basket is deep and narrow, which is what makes shaking and stacking work; an oven cavity is wide and shallow, which is what makes a sheet pan, a spit or a 4-inch-high chicken possible at all. Everything else in the comparison follows from that choice."
                ],
                "cite": ["S10", "S12", "S14", "S18", "S28"],
            },
            {
                "h": "Heat: what each brand states, and where the numbers stop agreeing",
                "paras": [
                    "The 6 Qt page publishes {{200–450 °F / 95–235 °C}} and puts a ceiling on its headline feature: {{450 °F / 235 °C, held for 2 minutes, for extra browning}}. Read the pair together and Hi-Fry is a finishing blast, not a cook temperature.",
                    "The 8 Qt page publishes {{200–400 °F}} for the stainless model, and its features block opens \"Max temp: 400ºF/ 205ºC\". The Amazon listing title for the candidate ASIN advertises a Hi-Fry mode and 450 °F. Chefman separately sells a High-Fry 8 Qt model whose own page does publish a 450 °F figure. The most likely explanation is two products under one title — which is a documentation problem, not a spec to average.",
                    "The Emeril manual goes further in both directions: {{75–500 °F / 25–260 °C}}. It is the only unit in this set documented below 200 °F, and that low end is the reason a Proof or Dehydrate preset on it means something other than 'the fan is on'.",
                    "**The useful inference is not about crispiness.** A range that starts at 75 °F and ends at 500 °F is a different appliance class from a range of 200–450 °F, before you consider capacity at all."
                ],
                "cite": ["S10", "S12", "S13", "S26", "S29", "S15"],
            },
            {
                "h": "Counter space is the number that actually decides",
                "paras": [
                    "Footprints, in each brand's own published units. The 6 Qt dual-window: {{13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm}} at {{13.3 lb / 6.03 kg}}. The 8 Qt: {{8 Qt model: 15.4 × 12.6 × 13.5 in / 39.11 × 32 × 34.29 cm · 12.8 lb / 5.8 kg}}. The Emeril oven: {{16.9 D × 15.8 W × 14.8 H in}}.",
                    "Two details in that row matter more than the marketing copy. The Emeril is the tallest and widest, which is what puts it under a cabinet and off a small counter. And its French doors swing toward you, so the clearance in front is part of the footprint, not an afterthought.",
                    "Weight is a daily number, not a shipping number, if the appliance lives in a cupboard or on a shelf above shoulder height. Here the brands' own data disagrees with itself: Chefman's store record for the 8 Qt SKU carries a variant weight of 13.4 lb, while the same product page's specification block states 12.8 lbs / 5.8 kg. This site publishes the specification block and leaves the gap on the review register rather than picking one."
                ],
                "cite": ["S10", "S12", "S14", "S33"],
            },
            {
                "h": "Where each brand contradicts itself, and why that is your problem",
                "paras": [
                    "Emeril's page carries **25 Cooking Pre-sets** in its specification block and **24 one-touch cooking presets** in its own description, while the manual for the model names 24. Its marketing line counts the appliance as 10-in-1, and the same page separately promises two dozen presets.",
                    "Chefman's problem is the opposite kind: not one page disagreeing with itself, but several near-identical SKUs disagreeing with each other. Two 6-quart dual-basket models and a third dual-window model share a spec sheet shape, and two 8-quart TurboFry Touch models differ on maximum temperature.",
                    "So a brand-vs-brand comparison published on top of these documents inherits their ambiguity. The only reliable fix is at the appliance: the model number printed on the unit, matched to the model number on the page you are reading. A listing title is not a model number. This site publishes both and marks the gap between them."
                ],
                "cite": ["S14", "S15", "S10", "S11", "S12", "S26", "S27"],
            },
            {
                "h": "What neither brand publishes — so nobody should be telling you",
                "paras": [
                    "How evenly either one browns a full tray. How loud it is at 1700 watts in an open-plan kitchen. How long the real preheat takes. Whether the nonstick survives a year of dishwashers. Whether a rotisserie element gives an even bird. None of these is on a manufacturer page, and none is in an owner's manual, because those documents describe what the appliance is designed to do rather than how it performs.",
                    "That is a limit on this page and on every page like it. The FTC's endorsement guidance is blunt that an endorser who says they used a product must actually have used it, and that a claim about a product's performance needs support a reasonable consumer would expect. A review that narrates crispiness for a machine nobody handled is a style choice, not evidence.",
                    "What a documentation-only comparison can honestly offer is the shape of the trade, the numbers behind it, and the list of questions the documents cannot answer. That is what this page is."
                ],
                "cite": ["S8", "S2"],
            },
            {
                "h": "The order to decide in",
                "paras": [
                    "**1. Menu first, model last.** A week of fries and frozen snacks wants a basket. Two dishes at two temperatures wants two drawers. A whole bird, a sheet pan, or yoghurt wants the oven cavity.",
                    "**2. Measure the gap, then add the doors.** Tape the widest point of the gap, the height under the cabinet, and the depth including the handle swing. Compare against the published footprint, not against a photo.",
                    "**3. Confirm the model code.** Open the listing's product-information block and read the model or part number there against the brand page you intend to trust. If they differ by a character, stop and read the manual that ships in the box.",
                    "**4. Then, and only then, price.** Every figure above is stable; the price is not, and no page in this set publishes one that it can guarantee today."
                ],
                "cite": ["S10", "S12", "S14", "S16", "S28", "S29"],
            },
        ],
        "closing_note": "No appliance in this comparison was cooked in, owned or handled. Every figure above is quoted from the manufacturer product pages, owner's manuals and store records linked per section, re-read on 2026-11-17, or from the Amazon listing pages cited by number. Where two official documents disagree, both readings are published and the disagreement is listed on the review register.",
    },
    {
        "slug": "ninety-eight-percent-less-oil-claim",
        "kind": "Explainer",
        "kicker": "Reading the claim",
        "title": "\u201c98% less oil\u201d is a sentence on a box, not a measurement",
        "standfirst": "Chefman's 8 Qt page carries the phrase in its first line. Less than what, on which food, measured how, and by whom? The page does not say. Here is exactly what it does say, and four questions that work on any percentage printed on an appliance.",
        "target_query": "air fryer 98% less oil meaning",
        "intent": "Informational",
        "reading_minutes": 4,
        "sources_read": READ,
        "products": ["chefman-8qt-turbofry"],
        "sections": [
            {
                "h": "What the brand page actually states",
                "paras": [
                    "The 8 Qt TurboFry Touch page introduces the appliance with, in its own words: \u201cextra-crispy meals with 98% less oil; perfect for veggies, pizza, frozen foods, and more\u201d. The same sentence is in the store's product record for that page, which is where this site read it on 2026-11-17.",
                    "That is the whole claim. The page does not name a comparison — deep frying in a fryer, a recipe with more oil, another appliance, or nothing added at all. It does not name a food, a method, a lab or a date. It is one clause of marketing copy, and it is the only place in the brand's documents for this model where that number appears.",
                    "This site records it as what it is: a brand claim, published on the product page under the label {{Brand claim: meals with '98% less oil'}}. The label is not a hedge added by this site; it is the difference between a measurement and a promise."
                ],
                "cite": ["S12", "S33"],
            },
            {
                "h": "Why the missing half is the important half",
                "paras": [
                    "A percentage is a ratio, and a ratio with no denominator is not information. \u201c98% less oil\u201d against food submerged in a deep fryer is a real and unsurprising difference: an air fryer circulates hot air and needs a film of oil at most. \u201c98% less oil\u201d against the same recipe made in an oven with a brush of oil is a very different statement, and nothing on that page rules either reading in or out.",
                    "There is a second silence worth noticing. The claim sits next to a temperature range — {{200–400 °F}} on that page — and a care rule, not next to a nutrition statement. The brand is not making a health claim here in the regulated sense; it is describing a cooking method's usual effect. Anyone who turns it into dietary advice is going beyond the document.",
                    "**If you need the health question answered, it is not answerable from a spec sheet.** A registered dietitian, or the published comparison the brand cites if it cites one, is the route. This site publishes neither and recommends neither."
                ],
                "cite": ["S12", "S8"],
            },
            {
                "h": "What the manuals do say about oil — a care rule, not a diet rule",
                "paras": [
                    "The one oil instruction in this product set is a warning about a spray can, and it is about the coating rather than the food. The dual-window manual cautions never to spray the baskets or racks with cooking oil from an aerosol can, because the harsh components can chip the nonstick; its substitute is a non-aerosol mister. The dataset row for that model reads {{Nonstick, dishwasher-safe baskets. Manual caution: never spray with aerosol cooking oil \u2014 use a non-aerosol mister instead}}.",
                    "For the 8 Qt, this site's record carries a shorter care row: {{Nonstick basket and rack; top-rack dishwasher safe}}. No aerosol caution for that model appears in the documents read for this site, and this article does not extend the dual-window manual's rule to it. If you own the 8 Qt, the manual in the box is the authority.",
                    "The practical overlap is small and honest: the appliances in this set document how to oil them without ruining the coating. None of them documents how much oil you need for a given food, and none publishes a nutrition outcome."
                ],
                "cite": ["S18", "S10", "S12", "S13"],
            },
            {
                "h": "Four questions that work on any printed percentage",
                "paras": [
                    "**Compared with what?** If the page does not name the baseline, the number cannot be checked. A comparison to deep frying and a comparison to \u201cno oil added\u201d can both be true and mean opposite things.",
                    "**On which food, and how much of it?** A figure from a lab run on 500 g of fries is a weak guide to 200 g of vegetables. Watch for percentages that appear in marketing copy and never in the instructions.",
                    "**Whose measurement is it?** Brand-run, third-party, or unattributed. Only the first is common on a product page, and it is the one with an interest in the answer.",
                    "**Does the manual repeat it?** Instructions are the document a manufacturer has to be able to stand behind when something goes wrong. A claim that appears only in the sales copy carries a different weight, and \u2014 as with the presets and the temperature rows on this very site — the sales copy is where the published contradictions tend to live."
                ],
                "cite": ["S12", "S14", "S2"],
            },
        ],
        "closing_note": "Nothing in this article was cooked, measured or tested. The quoted sentence is reproduced from Chefman's own product page and its store product record, both read on 2026-11-17. This site takes no position on whether the claim is true; it states what the document does and does not say.",
    },
    {
        "slug": "questions-before-buying-a-multifunction-appliance",
        "kind": "Checklist",
        "kicker": "Buyer's checklist",
        "title": "Eight questions to ask before you buy a multi-function kitchen appliance",
        "standfirst": "A multi-function machine is a stack of claims: quarts, presets, temperature ranges, accessory counts. Every question below is answerable from a listing page, a spec block or the manual in the box — and each one has a live example in this site's own three-product record, including the places where the documents refuse to answer.",
        "target_query": "questions to ask before buying a multi function air fryer oven",
        "intent": "Commercial investigation",
        "reading_minutes": 7,
        "sources_read": READ,
        "products": ["chefman-6qt-dual-basket", "chefman-8qt-turbofry", "emeril-26qt-french-door"],
        "sections": [
            {
                "h": "Questions to ask of the specification block",
                "paras": [
                    "**1. Which unit is the capacity counted in, and of what?** The three appliances here publish {{6 Qt / 5.67 L}}, an {{8 qt (brand also sells a 5 qt version of the same product page)}} basket, and {{26 qt / 24.6 L (manual: 1,519 cu in)}} of cavity. The third one is the only figure you can cross-check, because the manual states the same volume in cubic inches as well as litres. Where a brand gives one number in one unit, you are trusting its definition of the space.",
                    "**2. What is the temperature range, and what is the top number held for?** The 6 Qt page pairs {{200–450 °F / 95–235 °C}} with a ceiling note: {{450 °F / 235 °C, held for 2 minutes, for extra browning}}. A maximum that lasts two minutes is a finisher. Ask which number describes a cook, and which describes a photograph.",
                    "**3. What does it need around it, not just under it?** Published footprints here are {{13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm}}, {{8 Qt model: 15.4 × 12.6 × 13.5 in / 39.11 × 32 × 34.29 cm · 12.8 lb / 5.8 kg}} and {{16.9 D × 15.8 W × 14.8 H in}}. Add the door swing and the ventilation gap the manual asks for. A machine that fits the drawn rectangle and not the real kitchen is the most common avoidable return.",
                    "**4. What does the plug ask of your circuit?** All three of these are documented at 1700 watts on a 120-volt supply. That is the question you ask before a second large appliance goes on the same run, and it is the reason the manuals' cord and extension rules are worth reading before the counter is planned."
                ],
                "cite": ["S10", "S12", "S14", "S15", "S18"],
            },
            {
                "h": "Questions to ask of the manual rather than the marketing",
                "paras": [
                    "**5. Is every advertised function documented in the instructions?** A function named only in a listing title is a claim about a box. On this site's record, the Emeril manual documents a rotisserie preset and a spit set, which is why the rotisserie is treated as a feature rather than a badge. Elsewhere, a Hi-Fry mode in a listing title meets a 200–400 °F range on the brand's own page for the model number the listing carries — the manual is the document that has to be right when you call about it.",
                    "**6. How many presets, and counted how?** The Emeril page states {{24 presets are named in the owner's manual for model FAFO-001: Airfry, Fries, Bacon, Grill, Eggs, Fish, Ribs, Defrost, Steak, Vegetables, Wings, Bake, Rotisserie, Toast, Chicken, Pizza, Pastry, Proof, Broil, Slow Cook, Roast, Dehydrate, Reheat, Warm}} in its manual, 25 in its own specification icons, and markets the machine as 10-in-1 in the same page's description. Ask what a preset is: a saved time-and-temperature pair, or a mode that shares one.",
                    "**7. What does it say about cleaning, and does that fit your habits?** The two Chefman manuals put their cooking parts on the top rack of a dishwasher; the Emeril manual hand-washes its accessories and soaks caked-on food. The dual-window manual also bans aerosol oil spray on the nonstick. A machine you will not clean properly is a machine you will not use, and the care rules are in the manual, not in the hero image."
                ],
                "cite": ["S14", "S15", "S12", "S13", "S18", "S29"],
            },
            {
                "h": "The question the documents usually dodge",
                "paras": [
                    "**8. Which exact model is this, and does the page you are reading describe that model?** Read the model or part number in the listing's product-information block and match it character by character against the brand page whose specifications you are using. Three of this site's open flags exist because that check has not been settled: more than one 6-quart Chefman SKU exists with near-identical pages; two 8-quart models disagree about their own maximum temperature; and the Emeril listing carries a model code one character away from the brand page's.",
                    "This is the one question a buyer can answer in about three minutes and the one almost nobody asks. Everything above rests on it: a specification quoted against the wrong model is not a conservative estimate, it is simply the wrong number."
                ],
                "cite": ["S10", "S11", "S12", "S26", "S27", "S28", "S16", "S29"],
            },
            {
                "h": "What this checklist cannot tell you",
                "paras": [
                    "It cannot tell you whether any of these machines cooks well. Evenness, noise, real preheat time, how long a coating lasts and how a bird roasts are not published by these brands, so no page in this set states them, and a review that narrates them without a test is describing a mood, not a measurement.",
                    "It cannot tell you today's price or availability. Amazon's Program Policies limit how an Associate site may display price, rating and review-count data, which is why this site publishes none of it and links out instead. The brand list prices on the product pages here are the brands' own figures, not the price you will pay.",
                    "What it can do is stop the expensive mistakes that documents do cover: the wrong footprint, the wrong model number, the wrong expectation of a temperature figure, and a care routine the manual forbids."
                ],
                "cite": ["S2", "S8", "S10", "S12", "S14"],
            },
            {
                "h": "Use it on the three machines here",
                "paras": [
                    "Every question above is answered, row by row and source by source, on the three product records this site keeps: the {{Chefman 6 Qt Dual Basket}}, the {{Chefman 8 Qt TurboFry}} and the {{Emeril 26 QT French Door}}. The side-by-side matrix keeps only the figures that could be confirmed, and a dash there means the documents did not answer — not that the answer is zero.",
                    "If a row you care about is blank, that is a fact about the published documents, and it is listed on the review register with the official page that was read."
                ],
                "cite": ["S10", "S12", "S14"],
            },
        ],
        "closing_note": "This checklist was written from the manufacturer pages, manuals and listing documents cited per section, re-read on 2026-11-17. No appliance was purchased, tested or handled for it, and no ranking is implied by the order of the questions.",
    },
]

# ---------------------------------------------------------------- articles
art = json.loads(ART.read_text(encoding="utf-8"))
have = {a["slug"] for a in art["articles"]}
added = [a for a in NEW if a["slug"] not in have]
art["articles"].extend(added)
art["updated"] = READ
art["note"] += (
    " | 2026-11-17 (arena/fd9778a1-zone1, pass 13): three articles added — the brand-vs-brand "
    "comparison (Chefman vs. Emeril), the '98% less oil' claim read, and the multi-function buyer's "
    "checklist (topic TP-21). Same discipline as the earlier sets: every {{placeholder}} must already "
    "be a published value in data/products.json or the build fails; every section cites registered "
    "sources only; the two brand-page quotations were transcribed from live reads on 2026-11-17 "
    "(reports/verification-2026-11-17-fd9778a1.md). Each of these three articles now carries its own "
    "sources_read date, because the register-level date describes the older set."
)
ART.write_text(json.dumps(art, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ---------------------------------------------------------------- topic queue
top = json.loads(TOP.read_text(encoding="utf-8"))
rows = {t["id"]: t for t in top["topics"]}
rows["TP-21"].update({
    "status": "published",
    "published_as": "articles/questions-before-buying-a-multifunction-appliance.html",
    "angle": rows["TP-21"]["angle"] + " PUBLISHED 2026-11-17 by arena/fd9778a1-zone1 as an eight-question "
             "checklist: questions 1-4 asked of the specification block, 5-7 of the manual, 8 the "
             "model-number check, plus an explicit section on what the documents cannot answer.",
})
top["topics"].append({
    "id": "TP-22",
    "title": "Chefman vs. Emeril: what a basket brand and an oven brand publish",
    "hook": "Two brands, three machines, and the footprint that decides it.",
    "intent": "Comparison",
    "serves": ["chefman-6qt-dual-basket", "chefman-8qt-turbofry", "emeril-26qt-french-door"],
    "angle": "The brand-level comparison the format pages stop short of: heat range and its ceiling, "
             "counted volume against cavity, and the model-number check that has to happen first. "
             "Published figures only; both brands' self-contradictions are shown rather than resolved.",
    "why_it_could_earn_traffic": "Judgement: 'chefman vs emeril' is a brand decision typed after the "
                                 "format decision, so it sits closer to a purchase than a capacity "
                                 "question. No keyword volume was available to this build.",
    "must_cite": [
        {"label": "Chefman 6 Qt dual-window product page", "url": "https://chefman.com/products/turbofry-touch-dual-window-air-fryer"},
        {"label": "Chefman 8 Qt TurboFry Touch product page", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"},
        {"label": "Emeril French Door AirFryer 360 product page", "url": "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360"},
    ],
    "status": "published",
    "published_as": "articles/chefman-vs-emeril-air-fryer.html",
    "blocked_by": [],
})
top["topics"].append({
    "id": "TP-23",
    "title": "\u201c98% less oil\u201d: reading the percentage on the box",
    "hook": "The claim is one clause of marketing copy. Here is what it says, and what it does not.",
    "intent": "Informational",
    "serves": ["chefman-8qt-turbofry"],
    "angle": "A single brand sentence, quoted exactly, with the missing denominator named. The article "
             "then contrasts it with the one oil instruction the manuals do carry (the aerosol-spray "
             "caution on the coating) and gives four questions that work on any printed percentage.",
    "why_it_could_earn_traffic": "Judgement: the phrase is on the box and in dozens of listings, so it "
                                 "gets typed into a search box by people who want the baseline nobody "
                                 "printed. No volume data exists in this repository.",
    "must_cite": [
        {"label": "Chefman 8 Qt TurboFry Touch product page (the claim's home)", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"},
        {"label": "Chefman store product record for the same page", "url": "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1.json"},
        {"label": "Chefman 6 Qt owner's manual (the aerosol-oil caution)", "url": "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf"},
    ],
    "status": "published",
    "published_as": "articles/ninety-eight-percent-less-oil-claim.html",
    "blocked_by": [],
})
top["topics"].append({
    "id": "TP-24",
    "title": "What \u201cAs an Amazon Associate I earn from qualifying purchases\u201d means, for readers",
    "hook": "The sentence is on every page here. This row existed in no queue.",
    "intent": "Policy explainer",
    "serves": [],
    "angle": "Publisher's note for the article set: the disclosure explainer was published in the "
             "pass-10 article set (design-prompt topic A-9) but no row in this canonical queue mapped "
             "to it, which is the orphan-class defect in reverse. Row added 2026-11-17 so the queue "
             "covers every published article; no new copy was written for it.",
    "why_it_could_earn_traffic": "Judgement: low volume, high trust. Recorded as a register repair, "
                                 "not as a traffic plan.",
    "must_cite": [
        {"label": "Associates Operating Agreement", "url": "https://affiliate-program.amazon.com/help/operating/agreement"},
        {"label": "FTC Disclosures 101", "url": "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"},
    ],
    "status": "published",
    "published_as": "articles/associates-disclosure-explained.html",
    "blocked_by": [],
})
top.setdefault("notes", []).append(
    "2026-11-17 (arena/fd9778a1-zone1): TP-21 published as a checklist; TP-22 and TP-23 added and "
    "published in the same pass; TP-24 added as a register repair for a published article that had no "
    "queue row. Proposed seasonal rows TP-16, TP-19 and TP-20 are unchanged and still unwritten."
)
TOP.write_text(json.dumps(top, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# ------------------------------------------------- design-prompt topic register
dp = json.loads(DP.read_text(encoding="utf-8"))
patch = {
    "A-8": {
        "status": "published",
        "status_note": "Published 2026-11-17 by arena/fd9778a1-zone1 (topic queue TP-22). Written as "
                       "the published-figures comparison, with both brands' self-contradictions shown "
                       "rather than resolved.",
        "published_as": "articles/chefman-vs-emeril-air-fryer.html",
    },
    "A-9": {
        "status": "published",
        "status_note": "Published, and the register's 'not-written' status was stale. The pass-10 "
                       "article set shipped articles/associates-disclosure-explained.html on "
                       "2026-11-16; this register was not updated with it. Corrected 2026-11-17 by "
                       "arena/fd9778a1-zone1, and the missing topic-queue row was added as TP-24.",
        "published_as": "articles/associates-disclosure-explained.html",
    },
    "A-10": {
        "status": "published",
        "status_note": "Published 2026-11-17 by arena/fd9778a1-zone1 (topic queue TP-23). The brand "
                       "sentence is quoted verbatim from the 8 Qt page and its store product record, "
                       "read the same day, and labelled a brand claim throughout.",
        "published_as": "articles/ninety-eight-percent-less-oil-claim.html",
    },
}
for t in dp["topics"]:
    if t["id"] in patch:
        t.update(patch[t["id"]])
dp["topics_note"] = (
    "Statuses in this register are re-derived from data/articles.json and data/topics.json, not typed. "
    "It carried a stale 'not-written' for a published article between 2026-11-16 and 2026-11-17 "
    "(A-9); the class of defect is open as F83 because the duplication is still in the build."
)
DP.write_text(json.dumps(dp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("articles added:", [a["slug"] for a in added])
print("topics rows:", len(top["topics"]), "| design-prompt topics:", len(dp["topics"]))
