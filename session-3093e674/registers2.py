import json, sys, pathlib, collections

D = pathlib.Path('data')
TODAY = "2026-11-17"


def load(name):
    return json.load(open(D / name, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)


def save(name, d):
    json.dump(d, open(D / name, 'w'), indent=2, ensure_ascii=False)
    open(D / name, 'a').write("\n")


def od(**kw):
    return collections.OrderedDict(kw)


# ================================================================ questions
q = load('questions.json')
by = {x['id']: x for x in q['questions']}

q4 = by['Q-04']
q4['question'] = ("Which Associates tag do the supplied short links carry, and is it an ID that exists in this account? "
                  "(Partly answered on 2026-11-17: the owner has named the tracking ID this site should publish with.)")
q4['what_we_know'] = q4['what_we_know'] + [
    ("Stated by the project owner on 2026-11-17: 'Selected Tracking ID:shopnow047c-20'. That is a first-party "
     "instruction about which ID the site should publish with, recorded in data/config.json with that provenance - not a "
     "verification that the ID is active, and not evidence about what the five short links already carry."),
    ("Since 2026-11-17 the root build no longer depends on the short links to earn: every product CTA is composed as a "
     "canonical /dp/<ASIN> URL carrying that tag, and check_special_links() fails the build if a CTA forgets it. The "
     "unknown has narrowed from 'we cannot monetise at all' to 'the tag is published but unproven'."),
    ("A tag is required on every link to Amazon (Program Policies 2(a)/(b), re-read 2026-11-17), and Amazon states it has "
     "no obligation to pay where links are not properly formatted (Operating Agreement 3)."),
]
q4['what_is_missing'] = ("Two things, both inside the account. First, whether shopnow047c-20 is a live tracking ID in an "
                         "enrolled Associates account - the shape matches Amazon's published XXXXX-## pattern, and shape is "
                         "not existence. Second, whether any of the five supplied short links already carries it, which is "
                         "unreadable from outside because the shortener hides its own parameters.")
q4['how_to_discover'] = ("One test, five minutes, before anything else is written: publish a single tagged link for one "
                         "product, click it from an incognito browser, complete a dummy visit, then read Associates Central > "
                         "Reports for a click recorded against that tracking ID for the last 24 hours. If it appears, scale "
                         "the pattern to every page (the build already does). If it does not, the tag or the account state "
                         "is wrong and no further content should be written until it is fixed. The step-by-step is on "
                         "handover.html.")
q4['sources'] = q4['sources'] + [
    {"label": "Associates Operating Agreement, section 3 (Special Links and fees)",
     "url": "https://affiliate-program.amazon.com/help/operating/agreement"}]

q8 = by['Q-08']
q8['question'] = ("What may this site measure, and whose consent does that require? (Partly settled on 2026-11-17: "
                  "an on-device counter is shipped; anything that transmits is not.)")
q8['what_we_know'] = q8.get('what_we_know', []) + [
    ("Shipped 2026-11-17: five events defined in data/measurement.json, counted in the visitor's own browser, sent "
     "nowhere. The footer's statement that the site runs no analytics and sets no cookies stays true, which is the "
     "constraint that decided the design (Program Policies 3(e))."),
    ("check_measurement_contract() fails the build if the shipped script ever makes a network call, sets a cookie, or "
     "if an analytics endpoint is configured while any page still claims the site runs no analytics."),
]
q8['what_is_missing'] = ("The decision the counter cannot make for the owner: whether to host a collector at all. The "
                         "endpoint contract is specified and switched off; turning it on needs a privacy rewrite, a "
                         "retention answer and a country decision (Q-20).")

q['questions'] += [
    od(id="Q-27", group="Scope",
       question="Five product links are in the brief and three products are in the site. Is the product set now five, and who says so?",
       state="missing",
       why_it_matters=("It decides whether the next content push is written for one category or two, and it is the "
                       "difference between a shop with a plan and a shop that drifted. The two new links are real and "
                       "verified as destinations - a ThermoMaven instant-read (ASIN B0DHZTCNR5) and the CHEF iQ iQ Sense "
                       "Gen 3 (ASIN B0DZFD6R9Z), both under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat - "
                       "but nothing in the repository states that the site is meant to market thermometers."),
       what_is_missing=("A scope statement: keep it air-fryers only and drop the two links, or widen the category. "
                        "Either answer is workable; 'both, sort of' is the one that is not, because a half-marketed "
                        "product page ranks for nothing and earns nothing."),
       how_to_discover=("Nobody needs to discover anything - the owner decides. The evidence for the decision is on "
                        "links.html (LI-04 and LI-05), which shows what each new link reaches and what is still unknown "
                        "about it. The cheapest path to a real answer: one thermometer buying guide, four weeks, "
                        "measured by Search Console (SG-29) before a second is committed."),
       blocks=["SG-37"], sources=[
           {"label": "Amazon detail page for ASIN B0DHZTCNR5, read live 2026-11-17", "url": "https://www.amazon.com/dp/B0DHZTCNR5"},
           {"label": "Amazon detail page for ASIN B0DZFD6R9Z, read live 2026-11-17", "url": "https://www.amazon.com/dp/B0DZFD6R9Z"},
           {"label": "This repository's product-intent record", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/link-intent.json"}]),
    od(id="Q-28", group="Attribution",
       question="Does the Associates account hold any sub-tag tracking IDs, and which one belongs to this site?",
       state="unknowable",
       why_it_matters=("This is the only mechanism that answers 'which page gets clicks' without putting a third-party "
                       "tracker on a site whose trust claim is that it watches nobody. Amazon's own model: an associate "
                       "with storeid-20 issues storeid-1-20 for a site and storeid-2-21 for a newsletter, and reports "
                       "each separately. Re-read live 2026-11-17."),
       what_is_missing=("The list of tracking IDs in the account. The build supports per-page sub-tags through "
                        "data/config.json → sub_tags.assigned and will validate their shape, but it will not invent an "
                        "ID: a sub-tag is an ID Amazon issues 'upon your request but subject to our approval', so "
                        "guessing one produces a link that silently earns nothing."),
       how_to_discover=("Associates Central → Manage your Tracking ID. Create one ID per money page if you want "
                        "attribution, paste the IDs in the format 'picks.html': 'shopnow047c-1-20', rebuild, and the "
                        "links change themselves. One constraint to respect: no sub-tag may be associated with a "
                        "specific end user, so never derive one from a visitor."),
       blocks=["SG-38"], sources=[
           {"label": "What are tracking IDs, and how does the new site help Associates use them?",
            "url": "https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA"},
           {"label": "Program Policies, section 2(b) - sub-tags, issued on request and subject to approval",
            "url": "https://affiliate-program.amazon.com/help/operating/policies"}]),
    od(id="Q-29", group="Products",
       question="Which brand SKU is ASIN B0DHZTCNR5 - the F1, the F1 Stealth or the F1 Ace?",
       state="not_stated",
       why_it_matters=("It is the difference between publishing a specification and publishing somebody else's product. "
                       "The listing's own title claims '1 Sec'; the brand's F1 page states 0.7 seconds; the brand sells "
                       "three near-identical F1 variants. Nothing in the sources links the ASIN to one of them, so no "
                       "figure from any of them may be published as this product's."),
       what_is_missing="A statement from the listing's Product information block, read in a logged-in browser, or the seller's own answer.",
       how_to_discover=("Open the listing and read the Product information table for the model number - the same "
                        "operation that closed F49/F68 for two of the three air fryers on 2026-11-16 - or ask the brand "
                        "which SKU carries that ASIN. Until then the candidate row stays mostly blank by design."),
       blocks=["TP-22"], sources=[
           {"label": "Amazon listing for B0DHZTCNR5, read 2026-11-17", "url": "https://www.amazon.com/dp/B0DHZTCNR5"},
           {"label": "ThermoMaven F1 product page (states 0.7 seconds), read 2026-11-17", "url": "https://www.thermomaven.com/products/f1"}]),
    od(id="Q-30", group="Compliance",
       question="Is a hand-composed tagged /dp/ URL accepted as a Special Link, or must every link come from the Product Linking tool?",
       state="missing",
       why_it_matters=("The entire build change of 2026-11-17 rests on this. Program Policies 2(b) says Special Links "
                       "'may be created by you or made available to you by us', and requires the tag as a URL parameter, "
                       "which reads as permission to compose the link yourself. But the Operating Agreement also warns "
                       "that Amazon has no obligation to pay where links are not properly formatted, and 'properly' is "
                       "Amazon's word to define, not this repository's."),
       what_is_missing="Proof that a click through a composed link is reported. One click, one report row - the same test as Q-04.",
       how_to_discover=("Do not scale before it passes: publish one composed link, click it, check the Associates report "
                        "for that tracking ID inside 24 hours. If it does not appear, regenerate the same link from the "
                        "Product Linking tool in Associates Central and use the tool's output verbatim - the build "
                        "reads the link from data/config.json and data/products.json, so swapping the destination is a "
                        "data edit, not a rewrite."),
       blocks=[], sources=[
           {"label": "Program Policies, section 2(b) - 'Special Links may be created by you or made available to you by us'",
            "url": "https://affiliate-program.amazon.com/help/operating/policies"},
           {"label": "Operating Agreement, section 3 - no fee obligation where links are not properly formatted",
            "url": "https://affiliate-program.amazon.com/help/operating/agreement"}]),
]
save('questions.json', q)
print('questions:', len(q['questions']))

# ================================================================ suggestions
sg = load('suggestions.json')
ids = {s['id'] for s in sg['suggestions']}
assert 'SG-36' not in ids


def S(**kw):
    return collections.OrderedDict(kw)


sg['suggestions'] += [
    S(id="SG-36", title="Stop publishing untagged product links: compose the Special Link once, in the build",
      area="Links and attribution",
      problem=("For sixteen passes every product CTA on this site pointed at the raw link.amazon short link, because no "
               "Associates tag existed in the repository and none could be invented. On 2026-11-17 the owner named one "
               "(Selected Tracking ID:shopnow047c-20), which turned the problem from unknown into configurable - and an "
               "unmonetised link is not a conservative choice, it is a broken one: 2(b) requires the tag as a URL "
               "parameter and the Operating Agreement releases Amazon from paying where links are not properly formatted."),
      evidence=[S(label="Program Policies, Participation Requirements 2(a) and 2(b) — read live 2026-11-17",
                  url="https://affiliate-program.amazon.com/help/operating/policies"),
                S(label="Operating Agreement section 3 — Special Links and the fee obligation",
                  url="https://affiliate-program.amazon.com/help/operating/agreement"),
                S(label="This site's link record, showing every composed destination and its status",
                  url="https://kanlerxz87-cyber.github.io/Zone1/links.html")],
      options=[S(label="A. Compose the canonical /dp/<ASIN>?tag=… link in the build, from config",
                 what=("Implemented 2026-11-17. One function builds every outbound product link from data/config.json; "
                       "the supplied short link stays visible underneath as the artefact being checked; a guard fails "
                       "the build if a CTA forgets the tag, points at the redirector, or carries a tag the config never "
                       "declared."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Generate each link in the Product Linking tool and paste the results",
                 what=("Amazon's own tool, so formatting is unquestionably accepted - and the output is opaque to a "
                       "build: a long URL with generated parameters that no gate can validate and that rot when an "
                       "account changes. Suited to a few links, not to a site regenerated from data every pass."),
                 effort="M", risk="low", reversible=True),
               S(label="C. Leave the links untagged until the account is confirmed",
                 what=("What the site did until today. Compliant and honest, and it means the site's entire output "
                       "earns nothing while the question sits unanswered."),
                 effort="S", risk="none", reversible=True)],
      recommendation=("A, with one test before scaling: one tagged link, one click, one row in the Associates report. If "
                      "the report shows nothing, switch to B for that product rather than assuming the composed format "
                      "works everywhere."),
      why=("A is the only option that is simultaneously checkable by a machine and reversible by a human: the value "
           "lives in one config file, the rule lives in one guard, and if the tag turns out to be wrong no page has to "
           "be re-edited. B is the fallback with the best compliance certainty and the worst maintainability; keep it "
           "for the product where A fails its test."),
      impact=5, confidence=4, effort="S",
      risk_of_not_doing=("High. Every day of traffic sent through an untagged link is unpaid work, and the correction "
                         "is a config value, not a project."),
      blocks=[], blocked_by=["Q-30"]),
    S(id="SG-37", title="Decide the product set before the next content push: three air fryers, or five products in two categories",
      area="Scope",
      problem=("The brief now names five links; the site is an air-fryer guide with three marketed products. Two of the "
               "five resolve to meat thermometers, which no page on this site recommends - they are recorded, sourced "
               "and disclosed as candidates only. A shop is judged by whether it covers its category, and a half-"
               "covered category reads worse than a narrow one."),
      evidence=[S(label="Where the five links actually go, row by row",
                  url="https://kanlerxz87-cyber.github.io/Zone1/links.html"),
                S(label="Amazon listing for the new ThermoMaven ASIN, read 2026-11-17",
                  url="https://www.amazon.com/dp/B0DHZTCNR5")],
      options=[S(label="A. Stay air-fryers; say so on the front page and retire the two links",
                 what=("Narrow and defensible. The two links stay in the intent record as 'received, not marketed' so "
                       "the trail survives, and the site stops growing sideways."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Add a second category properly: two product pages, one category hub, one cluster",
                 what=("Real work: brand-page verification per row, its own comparison, its own disclosure and its own "
                       "internal links. The bridge article (meat probe in an air fryer) is already written and gives "
                       "the new category an audience on day one."),
                 effort="L", risk="medium", reversible=True),
               S(label="C. Keep publishing candidates without building pages",
                 what=("Where the repository sits tonight. It is honest, but it is a holding position, not a plan - and "
                       "a reader who wants a thermometer gets a record, not a recommendation."),
                 effort="S", risk="medium", reversible=True)],
      recommendation=("B, but staged: one category hub and two product pages only after each brand's own page has been "
                      "read row by row, and only after Q-29 is settled for the ThermoMaven ASIN. If the owner's answer "
                      "is that the brief's five links were a mistake, A costs nothing."),
      why=("Scoping decisions are cheap before content exists and expensive after. The site's advantage is that it "
           "publishes less than it knows; that advantage survives a second category only if the second category is "
           "held to the same evidence rule."),
      impact=4, confidence=3, effort="M",
      risk_of_not_doing=("Medium. Time gets spent on a third air-fryer article nobody needed instead of the category "
                         "the owner actually asked for."),
      blocks=[], blocked_by=["Q-27"]),
    S(id="SG-38", title="Buy page-level attribution from Amazon with sub-tag IDs instead of buying an analytics script",
      area="Measurement",
      problem=("The site can now count outbound clicks, but only on each reader's own device - there is no aggregate, "
               "because there is no collector, and adding one collides with the footer's 'no analytics' statement and "
               "with Program Policies 3(e). Amazon already provides the aggregate that matters, in the one report this "
               "site is allowed to trust."),
      evidence=[S(label="What tracking IDs are, and how one account reports them separately",
                  url="https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA"),
                S(label="Program Policies 2(b) - sub-tags are issued on request, subject to approval, and never per user",
                  url="https://affiliate-program.amazon.com/help/operating/policies"),
                S(label="This site's measurement page, including the endpoint that is specified and switched off",
                  url="https://kanlerxz87-cyber.github.io/Zone1/measurement.html")],
      options=[S(label="A. One tracking ID per money page, created in Associates Central",
                 what=("Owner action, ten minutes. Record them in data/config.json → sub_tags.assigned keyed by page "
                       "path; the build composes each page's links with that ID and validates the shape. Then the "
                       "Tracking ID Summary answers 'which page gets clicks' with no script on the site at all."),
                 effort="S", risk="none", reversible=True),
               S(label="B. Host Plausible or GoatCounter and rewrite the privacy statement",
                 what=("Aggregate on-site behaviour, at the cost of a disclosure rewrite, a retention policy and a "
                       "consent question for EU and UK visitors (Q-20 is unanswered)."),
                 effort="M", risk="medium", reversible=True),
               S(label="C. Nothing",
                 what=("Content decisions keep being made on instinct, which is exactly what the brief's priority 4 "
                       "objects to."),
                 effort="S", risk="high", reversible=True)],
      recommendation=("A first, on its own, for a full quarter. Only if the report cannot answer a question you need "
                      "answered should B be considered."),
      why=("A uses the mechanism Amazon built for this purpose and explicitly permits, it needs no new disclosure, and "
           "it preserves the sentence the site is staking its credibility on. It also respects the rule that a sub-tag "
           "may never be tied to an individual visitor, which any per-user scheme would break."),
      impact=4, confidence=4, effort="S",
      risk_of_not_doing=("Medium-high. Without a denominator the next eight articles are an unfalsifiable guess about "
                         "what shoppers want."),
      blocks=[], blocked_by=["Q-28"]),
    S(id="SG-39", title="Put the buy block where the decision is made, not only on the product page",
      area="Design and conversion",
      problem=("Until today the only outbound link on the whole site sat on three product pages. A reader who decides "
               "at the comparison table, on the category page or in a 'this week's picks' card had to navigate back to "
               "find something to click, which is a funnel with a step nobody intended. SG-25 designed the pattern; "
               "this row ships it."),
      evidence=[S(label="Program Policies 6(v)/6(w) - a link must be clear about where it goes, which a labelled button satisfies",
                  url="https://affiliate-program.amazon.com/help/operating/policies"),
                S(label="Google: qualify outbound commercial links",
                  url="https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links")],
      options=[S(label="A. One compact CTA cell, same builder, everywhere a product row appears",
                 what=("Implemented 2026-11-17 on the category table, the comparison matrix and the picks cards: same "
                       "tagged URL, same rel='nofollow sponsored noopener', same 'Affiliate link' chip, no duplicated "
                       "disclosure paragraph because the page-level statement is already above the fold."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Leave the tables editorial and link only from prose",
                 what=("The current site's actual behaviour before this pass. Reads purist; converts nobody."),
                 effort="S", risk="medium", reversible=True)],
      recommendation=("A, and keep the full disclosure block on the product pages themselves - a buyer who lands "
                      "directly from a search result must see the sentence, not a chip."),
      why=("A CTA that is built by the same function as every other CTA cannot drift out of compliance: if the "
           "disclosure or the tag is wrong somewhere, the build fails everywhere. That is the only way a sitewide "
           "pattern survives the next twelve passes."),
      impact=4, confidence=4, effort="S",
      risk_of_not_doing="Medium. The site's best traffic is on pages that make a decision easy and then send nowhere.",
      blocks=[], blocked_by=[]),
    S(id="SG-40", title="Give every seasonal page an expiry date, and let the build enforce it",
      area="Compliance and operations",
      problem=("The site publishes a Black Friday guide and a holiday gift guide. Amazon's rule for promotions is "
               "absolute and dated: 'You must remove from your Site any links and related references to limited time "
               "promotions as soon as that promotion on the relevant Amazon Site ends.' Nothing in this repository "
               "enforces a deadline, so the obligation currently depends on someone remembering a calendar."),
      evidence=[S(label="Program Policies, section 2(b) - the limited-time promotion removal duty, read live 2026-11-17",
                  url="https://affiliate-program.amazon.com/help/operating/policies"),
                S(label="The seasonal pages themselves",
                  url="https://kanlerxz87-cyber.github.io/Zone1/articles/black-friday-model-number-switch.html")],
      options=[S(label="A. A season block in the article register, with a build guard on the date",
                 what=("Implemented 2026-11-17: each seasonal article carries a scope note and an expiry date in "
                       "data/articles.json; the article page renders it, and check_seasonal_expiry() fails the build "
                       "the day after it passes, forcing an explicit decision - re-date with a fresh read, or retire "
                       "the page from the sitemap and the feed."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Take the seasonal pages down automatically when they expire",
                 what=("Automating the compliance obligation is tempting and wrong on its own: silently deleting a "
                       "published URL produces a 404 for anyone who linked to it and hides the decision from the "
                       "corrections log. If chosen, it needs a redirect target."),
                 effort="M", risk="medium", reversible=True),
               S(label="C. Rely on the next agent pass noticing",
                 what=("What the site does today. It has survived because the seasons have not turned yet."),
                 effort="S", risk="high", reversible=True)],
      recommendation=("A now, and B only as an explicit owner-approved retirement with a redirect to the evergreen "
                      "version of the same advice."),
      why=("The failure mode of a seasonal affiliate page is not that it stops being useful - it is that it keeps "
           "asserting a promotion that ended. A date in the data plus a gate that reads it turns a memory task into "
           "a build step, which is the whole point of this project's compliance gate."),
      impact=4, confidence=5, effort="S",
      risk_of_not_doing=("High if the account is approved and growing: a stale promotion reference is a named breach "
                         "in the policy text, and the remedy Amazon states is removal."),
      blocks=[], blocked_by=[]),
    S(id="SG-41", title="Lead the front page with the four buyer questions, before the products",
      area="Design and content",
      problem=("The brief names four editorial hypotheses in a shopper's own words. Three were already covered by "
               "articles; the fourth was not, and the front page's first move was a format guide rather than a "
               "question. A search visitor arrives with a sentence in their head, and a page that opens with a product "
               "grid asks them to translate."),
      evidence=[S(label="Google's own standard for helpful, people-first content",
                  url="https://developers.google.com/search/docs/fundamentals/creating-helpful-content"),
                S(label="The new guide answering the fourth question",
                  url="https://kanlerxz87-cyber.github.io/Zone1/articles/questions-before-a-multi-function-appliance.html")],
      options=[S(label="A. A 'start with your question' band above the format guide",
                 what=("Implemented 2026-11-17: four cards, each a question a person types, each linking the guide "
                       "that answers it - basket-or-oven, capacity without hype, cleanup and counter space, and the "
                       "multi-function checklist published by this pass."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Rewrite the hero itself as a question",
                 what=("A bigger design change to a hero that four passes have already tuned; it would collide with "
                       "the shipped masthead system for a marginal gain."),
                 effort="M", risk="medium", reversible=True)],
      recommendation=("A. Keep the product cards - they carry the buying path - and let the questions be the entry."),
      why=("It costs one band of markup, it matches the brief's own words rather than an invented content strategy, "
           "and every card links to an article that already cites its sources, so nothing new has to be verified."),
      impact=3, confidence=4, effort="S", risk_of_not_doing="Low-medium.", blocks=[], blocked_by=[]),
    S(id="SG-42", title="Decide what the parallel annexes do with product links now that the root build tags theirs",
      area="Repository",
      problem=("The s2 annex is a published build with its own pages and its own untagged /dp/ links. Since this pass "
               "changed the root build's link builder, the two disagree about what a buy link looks like, and both are "
               "crawled. Flag F77 records it."),
      evidence=[S(label="The annex's own index",
                  url="https://kanlerxz87-cyber.github.io/Zone1/s2/index.html"),
                S(label="This repository's generator for the annex",
                  url="https://github.com/kanlerxz87-cyber/Zone1/blob/main/scripts/build_s2_site.py")],
      options=[S(label="A. Point the annex at the same link builder",
                 what=("One function, one config value, both builds. Keeps the whole repository consistent and is the "
                       "smallest edit that ends the divergence."),
                 effort="S", risk="low", reversible=True),
               S(label="B. Label the annex dated evidence and strip its CTAs",
                 what=("Honest, and it stops two builds competing for the same query - but it means the annex's 393 "
                       "assertions keep running over a site that no longer sells anything."),
                 effort="M", risk="low", reversible=True),
               S(label="C. Leave it",
                 what=("Every later pass inherits the question again."), effort="S", risk="medium", reversible=True)],
      recommendation=("A on the next pass that touches scripts/build_s2_site.py, or B if the annex is meant as a "
                      "frozen verification artefact. The choice is the owner's; this pass did not edit another "
                      "session's build."),
      why=("A site with two answers to 'what is a buy link' is a maintenance trap, and the divergence was created by "
           "this pass's change, so it would be dishonest to leave it unrecorded."),
      impact=3, confidence=4, effort="S", risk_of_not_doing="Medium.", blocks=[], blocked_by=[]),
]

paths = {p['id']: p for p in sg['paths']}
for pid, new in (("P4", ["SG-36", "SG-38", "SG-40", "SG-42"]), ("P2", ["SG-39", "SG-41"]), ("P1", ["SG-37"])):
    for n in new:
        if n not in paths[pid]['contains']:
            paths[pid]['contains'].append(n)
paths['P4']['delivers'] = (paths['P4']['delivers'] +
    " Also, since 2026-11-17: tagged Special Links composed from one config value and enforced by a guard; five "
    "measurement events counted on the reader's own device and nowhere else; a campaign ledger that cannot accept a "
    "row without a dated provenance line; and an expiry gate on seasonal claims.")
sg['paths_note'] = ("Suggested order: P1, then P3, then P2, then P4. P3 is placed second because the traffic question "
                    "is decided before the writing, not after. Updated 2026-11-17: the four rows added by pass 13 sit "
                    "in P1, P2 and P4, and SG-36 is the only row on this board that changes whether the site earns "
                    "anything, so if P4 is picked, SG-36 is its first commit.")
sg['version'] = "1.2"
sg['compiled'] = TODAY
sg['pass'] = ("Pass 13 (arena/3093e674-zone1), 2026-11-17: SG-36 to SG-42 added on top of the 34-row register from "
              "passes 8 to 12; the register is still the review surface, and nothing in it is implemented before an "
              "owner reads it except under the adopt-after-silence rule recorded on decision-log.html.")
save('suggestions.json', sg)
print('suggestions:', len(sg['suggestions']))
