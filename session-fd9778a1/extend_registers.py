#!/usr/bin/env python3
"""T13-2 (decision desk) + T13-4 (source stamps) for pass 13, session arena/fd9778a1-zone1.

Everything added here is one of two things:
  * a suggestion, phrased as a decision with paths, an effort and a cost of doing nothing; or
  * a question, phrased with what this repository can already prove, what it cannot, and the
    exact step that would settle it.
No row asserts a market fact, a traffic figure, a revenue figure or a product superiority claim,
because no such figure exists in this repository.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = "2026-11-17"
SITE = "https://kanlerxz87-cyber.github.io/Zone1/"
REPO = "https://github.com/kanlerxz87-cyber/Zone1/blob/main/"

SOURCES = ROOT / "data" / "sources.json"
SUG = ROOT / "data" / "suggestions.json"
Q = ROOT / "data" / "questions.json"
DP = ROOT / "data" / "design-prompt.json"
REQ = ROOT / "data" / "requirements.json"
LOG = ROOT / "data" / "decision-log.json"


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p, d):
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ev(label, url):
    return {"label": label, "url": url}


# --------------------------------------------------------------------------- #
# 1. sources: register the page-experience guidance this pass read, and stamp the
#    four manufacturer pages re-read on 2026-11-17.
# --------------------------------------------------------------------------- #
src = load(SOURCES)
srcs = src["sources"]
if not any(s["id"] == "S38" for s in srcs):
    srcs.append({
        "id": "S38",
        "org": "Google Search Central",
        "title": "Understanding page experience in Google Search results",
        "url": "https://developers.google.com/search/docs/appearance/page-experience",
        "covers": ("The published self-assessment questions this site holds its mobile pass to: content "
                   "displays well on mobile, main content distinguishable from other content, no excessive "
                   "ads, no intrusive interstitials or dialogs. Verifies nothing about a product."),
        "kind": "Search guidance",
        "directness": "Primary - the search engine's own published guidance for site owners",
        "page_version": ("Fetched live " + TODAY + " (arena/fd9778a1-zone1). Page heading 'Understanding "
                         "page experience in Google Search results'; self-assessment list and FAQ present as "
                         "quoted on this row. Registered by this pass, first read."),
        "verified": ("Read " + TODAY + " by arena/fd9778a1-zone1 while deciding the sticky-bar scope: the "
                     "guidance warns against intrusive interstitials and dialogs, which is why the comparison "
                     "bar is bottom-anchored, non-blocking, hidden from print and hidden above 880 px."),
    })
stamp = (" | Re-read live " + TODAY + " (arena/fd9778a1-zone1): ")
re_read = {
    "S10": ("specification block verbatim - Capacity 6 Qt / 5.67 L, 200-450 F / 95-235 C, Dimensions 13.38 x "
            "11.81 x 10.63 in / 33.98 x 30 x 27 cm, Weight 13.3 lbs / 6.03 kg, Power 1700W/120V, Model Number "
            "RJ38-SQPF-3TDB-2W, cETL + 1-year assurance; features block 'Max temp: 450F/ 235C with Hi-Fry "
            "function' and 'Sync Function so both baskets finish cooking at the same time'; brand review widget "
            "4.6 from 1310 total reviews (5*930 4*259 3*85 2*12 1*24); price block $119.99 with promotional "
            "prices displayed alongside. Every figure matches the register; the review count is unchanged from "
            "2026-11-17T earlier read by arena/4618f77b (1,310)."),
    "S12": ("features and specification blocks verbatim - 'Max temp: 400F/ 205C', '4 cooking presets', "
            "'5-quart or 8-quart nonstick basket', '200-400F / 95-205C temperature range', 'Power: 1700W/120V', "
            "'Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 cm x 32 cm x 34.29 cm', 'Weight: "
            "(8 Qt Model) 12.8 lbs / 5.8 kg', 'Model Number: RJ38-SQSS-8T', cETL + 1-year assurance; brand "
            "review widget 4.6 from 717 total reviews. Unchanged from the register. No Hi-Fry or 450 F figure "
            "appears anywhere on this page, which is the half of flag F3 that the brand controls."),
    "S14": ("specification icons verbatim - '26-Quart Capacity / preparing food for 4-6 people', '24.6 Liters', "
            "'16.9\"D x 15.8\"W x 14.8\"H', '120 volts', 'Dual-Speed Fan', '25 Cooking Pre-sets'; product code "
            "4-00675-02A-VN; price $199.99; brand widget rating 2.6 from 25 reviews; description says '10-in-1' "
            "and '26-quart extra-large capacity'. Every figure matches the register, and the 25-vs-24 preset "
            "conflict (F4) is still live on the page, as is the 11-in-1 label carried by a marketing image asset."),
    "S33": ("store product record for the same page - updated_at 2026-11-17T11:41:54-05:00; 8 Quart variant "
            "price 119.99 with compare_at_price 119.99 (so no discount displayed on that variant), SKU "
            "RJ38-SQSS-8T, barcode 816458024518, variant weight 13.4 lb; 5 Quart variant price 79.99 vs "
            "compare_at 99.99, SKU RJ38-SQSS-5T. Body copy carries the '98% less oil' sentence quoted by "
            "articles/ninety-eight-percent-less-oil-claim.html. NEW IRREGULARITY: the variant weight (13.4 lb) "
            "and the page's own specification block (12.8 lbs / 5.8 kg) are 0.6 lb apart on the same date - "
            "recorded as F84, not averaged."),
}
for s in srcs:
    if s["id"] in re_read:
        s["page_version"] = s["page_version"] + stamp + re_read[s["id"]]
dump(SOURCES, src)

# --------------------------------------------------------------------------- #
# 2. suggestions: the design-and-decision rows this pass was asked for.
# --------------------------------------------------------------------------- #
sug = load(SUG)
existing = {x["id"] for x in sug["suggestions"]}
NEW_SUG = [
    {
        "id": "SG-36",
        "title": "Put the three machines above the trust metrics on the front page",
        "area": "Design and layout",
        "problem": ("The landing page opened with a hero, then a five-tile metrics row in which two tiles "
                    "count flags and sources, then a compliance caution, before a reader met a product. That "
                    "is the order of an audit file. A shop puts the goods first and the receipts underneath, "
                    "which changes what a first-time visitor does in the first ten seconds without changing a "
                    "single published value."),
        "evidence": [ev("build.py - page_index body order", REPO + "build.py"),
                     ev("The published front page as it now stands", SITE),
                     ev("Suggestion SG-04 (make it read like a shop), the row this one continues",
                        SITE + "suggestions.html#sg-04")],
        "options": [
            {"label": "A. Product rail first, metrics row after the comparison table",
             "what": ("Hero, then the three product cards with their brand list price, best-for and "
                      "check-first rows; the metrics strip moves below the table as a trust footer. The "
                      "disclosure band and the paid-link fact stay where they are: the disclosure above the "
                      "header on every page, the label on every purchase link."),
             "effort": "S", "risk": "none", "reversible": True},
            {"label": "B. Product rail first, metrics to the footer only",
             "what": "Stricter version: the counts stop being a section and become one footer line.",
             "effort": "S", "risk": "low", "reversible": True},
            {"label": "C. Leave the order alone",
             "what": "Status quo: the reader sees the verification process before the products.",
             "effort": "0", "risk": "low", "reversible": True}],
        "recommendation": ("A, shipped by this pass on 2026-11-17: the product rail now leads and the metrics "
                           "row follows the comparison table. Pick B if you want the audit layer off the first "
                           "screen entirely."),
        "why": ("Every number in the metrics row stays on the site either way - this is about order, not about "
                "hiding. A reader who has not yet seen a product has no reason to care how many sources it took."),
        "impact": 4, "confidence": 4, "effort": "shipped",
        "risk_of_not_doing": ("First impressions keep forming on the wrong screen: a buyer arrives, sees a "
                             "count of open flags, and reads the site as a compliance document about someone "
                             "else's project."),
        "blocks": ["S-20-mobile-first-follow-through"],
        "blocked_by": [],
        "resolved_on": TODAY,
    },
    {
        "id": "SG-37",
        "title": "Give every product page the same three-line buying block: what it is for, what to check, what the brand charges",
        "area": "Design and layout",
        "problem": ("A product page here carried a stat row, a specification table and a caution, and no answer "
                    "to the two questions a buyer asks in order: 'what is this machine for' and 'what would I be "
                    "walking into'. Both are answerable from rows already on the page; neither was assembled "
                    "into a decision block."),
        "evidence": [ev("MERCH register in build.py", REPO + "build.py"),
                     ev("Published example - the 6 Qt page", SITE + "products/chefman-6qt-dual-basket.html"),
                     ev("Google on what makes affiliate content worth reading rather than thin affiliation",
                        "https://developers.google.com/search/docs/essentials/spam-policies")],
        "options": [
            {"label": "A. Two merchandising rows plus a labelled brand list price",
             "what": ("'Best for' quotes a documented feature; 'Check first' quotes the open conflict on that "
                      "product; the price line is the brand's own list price with the policy reason no Amazon "
                      "price appears beside it. Implemented 2026-11-17 on the product pages and the front-page "
                      "cards."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. Add a third row: 'who should not buy this'",
             "what": ("The negative case is the most trusted line on a review page and it is writable from the "
                      "same documents (a 26-quart oven is not for a rented kitchen you must leave unmarked). "
                      "Needs one decision per product from you before it can be phrased, because 'who should "
                      "not' is advice, not a quotation."),
             "effort": "S", "risk": "medium", "reversible": True},
            {"label": "C. Show no price at all, as until 2026-11-17",
             "what": ("Defensible - a list price on a page nobody re-reads daily is a claim about yesterday. "
                      "The current build keeps the date-stamped read trail on the dataset page, which is why A "
                      "was chosen over C."),
             "effort": "0", "risk": "low", "reversible": True}],
        "recommendation": ("A is shipped. Decide B on its merits: it is the row that makes the site read as "
                           "advice rather than transcription, and it is the one row that cannot be generated "
                           "from the register alone."),
        "why": ("The generator reads both cells from data/products.json and from the product's own flag rows, so "
                "the block cannot drift away from the table beneath it. The price line carries the reason Amazon "
                "prices are absent, which is the one question an affiliate site's pricing normally dodges."),
        "impact": 5, "confidence": 4, "effort": "M",
        "risk_of_not_doing": ("Product pages stay reference pages: useful to a reader who is already "
                              "convinced, useless to the one deciding."),
        "blocks": [], "blocked_by": [], "resolved_on": TODAY,
    },
    {
        "id": "SG-38",
        "title": "Keep the sticky comparison bar, and decide whether it may carry a purchase button",
        "area": "Measurement and mobile",
        "problem": ("On a phone the reader either scrolls back to the header or leaves. The site had no "
                    "persistent route to the comparison, and adding one raises a policy question worth deciding "
                    "explicitly rather than absorbing silently: a purchase button that follows the reader down "
                    "the page is the most persuasive element on the page, and it is also the element Amazon's "
                    "participation requirements care most about."),
        "evidence": [ev("Amazon Associates Program Policies - participation requirements, link clarity",
                        "https://affiliate-program.amazon.com/help/operating/policies"),
                     ev("Google page-experience guidance: avoid intrusive interstitials and dialogs",
                        "https://developers.google.com/search/docs/appearance/page-experience"),
                     ev("The bar as shipped (mobile and tablet only, hidden in print)", REPO + "build.py")],
        "options": [
            {"label": "A. Two internal routes, no purchase button",
             "what": ("What shipped 2026-11-17: 'Which one fits' and 'Compare all 3', plus the paid-link fact "
                      "in its own line. Bottom-anchored, never covers the footer, hidden on desktop and in "
                      "print."),
             "effort": "S", "risk": "none", "reversible": True},
            {"label": "B. Add 'See it on Amazon' to the bar on product pages",
             "what": ("Highest expected click-through of anything on this list. Each product page already runs "
                      "the same tagged, sponsored link in its own CTA block, so B is a placement choice, not a "
                      "new mechanism. Say yes and it is one line in build.py."),
             "effort": "S", "risk": "medium", "reversible": True},
            {"label": "C. Remove the bar",
             "what": "Keep the page static; rely on the header nav and the in-body links.",
             "effort": "S", "risk": "low", "reversible": True}],
        "recommendation": ("Keep A now. Decide B only alongside the click measurement (SG-44 / Q-27): a "
                           "placement change without a click counter is a guess about what persuades."),
        "why": ("A keeps the sticky surface informational, which is the safest reading of the rule against "
                "obscuring where a link goes, and it is the version that cannot be mistaken for an interstitial "
                "by the search engine's own guidance."),
        "impact": 3, "confidence": 4, "effort": "S",
        "risk_of_not_doing": ("Nothing breaks; the mobile reader simply keeps leaving mid-comparison, and the "
                              "site never learns how often."),
        "blocks": [], "blocked_by": [], "resolved_on": TODAY,
    },
    {
        "id": "SG-39",
        "title": "Settle the photography question - it is the single largest reason the site still reads as generated",
        "area": "Media rights",
        "problem": ("There is no product image anywhere on this site except a generated social card and four "
                    "SVG diagrams. A shopper deciding between two baskets and an oven cavity reads six tables "
                    "with no picture of either. The gap is not a styling failure: Amazon's Program Content "
                    "includes its images, and manufacturer images are the brand's property, so no agent may "
                    "close it by copying a photo or generating a likeness."),
        "evidence": [ev("Associates Operating Agreement, section 1 (Program Content includes images)",
                        "https://affiliate-program.amazon.com/help/operating/agreement"),
                     ev("The figures-only substitute currently published", SITE + "figures.html"),
                     ev("The recorded decision and its open question", SITE + "questions.html#q-22")],
        "options": [
            {"label": "A. You photograph the three units",
             "what": ("Phone photographs of each machine on a counter, doors open and closed, plus the model "
                      "plate. Original, right-free, and the only option that also produces the 'what it is like "
                      "to live with' layer S-06 deferred - because you would have held the thing. Say yes and "
                      "this pass's successor puts the files in assets/products/ with a caption naming who took "
                      "them and when."),
             "effort": "S", "risk": "none", "reversible": True},
            {"label": "B. Ask each brand for a licensed press pack",
             "what": ("Chefman and Emeril both run press/retail asset sets. Needs written permission naming this "
                      "site, and the permission has to be recorded in the source register like any other fact."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "C. Generated imagery",
             "what": ("Rejected, and recorded as rejected so it is not proposed again by a later pass: an "
                      "invented picture of a specific commercial product is a misrepresentation of the thing a "
                      "reader is being paid to send them to buy."),
             "effort": "S", "risk": "high", "reversible": False},
            {"label": "D. Stay illustration-only",
             "what": "Keep the diagrams, accept that the pages read as documentation.",
             "effort": "0", "risk": "medium", "reversible": True}],
        "recommendation": ("A. It is one afternoon, it is unambiguously yours to publish, and it is the only "
                           "path that lets the site say something about handling the appliance without inventing "
                           "an experience."),
        "why": ("Every alternative either needs somebody else's permission or produces an image that misrepresents "
                "the product. Option A also closes the 'thin affiliate' criticism Google's spam policy makes by "
                "adding content no listing page contains."),
        "impact": 5, "confidence": 5, "effort": "S",
        "risk_of_not_doing": ("The design ceiling stays where it is: no amount of typography fixes a shop window "
                              "with no goods in it."),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-40",
        "title": "Pick a publishing cadence and a kill rule before the next article is written",
        "area": "Content and traffic",
        "problem": ("Twenty-four articles in twelve days is a burst, not a cadence, and bursts do not compound. "
                    "The queue has four proposed topics (TP-16, TP-19, TP-20 and the seasonal slots) and no rule "
                    "for which one becomes next, so the next pick defaults to whoever is writing."),
        "evidence": [ev("The topic queue, with its proposed rows", SITE + "topics.html"),
                     ev("This pass's three additions, each tied to a queue row", REPO + "data/topics.json"),
                     ev("Google's spam policies: scaled content abuse is the failure mode of volume-first publishing",
                        "https://developers.google.com/search/docs/essentials/spam-policies")],
        "options": [
            {"label": "A. One article a week, only if it answers a documented gap",
             "what": ("A ceiling, not a target: a week passes without a post if no topic has an official source "
                      "to answer it. This is the only cadence this repository's own evidence rule can honour."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. Two a month, seasonal dates first",
             "what": ("Black Friday, January gift returns, Prime Day. Fewer pieces, each with a real date window "
                      "and a scheduled re-read of the sources it quotes."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "C. Let measured queries decide, once Search Console has data",
             "what": ("Zero new articles until the property has 4-8 weeks of query data, then write to the "
                      "queries that already show the site. Requires the owner action in Q-28."),
             "effort": "S", "risk": "low", "reversible": True},
            {"label": "D. No cadence; publish when an agent pass has something to add",
             "what": "Status quo, which is how the queue got four proposed rows with no order.",
             "effort": "0", "risk": "medium", "reversible": True}],
        "recommendation": ("A now, switching to C the week the Search Console property has data. Both are honest "
                           "about the constraint: this site will not publish a sentence it cannot cite."),
        "why": ("Cadence is what turns a set of articles into a publication; the kill rule is what stops cadence "
                "becoming volume. Suggested kill rule, pre-committed: after eight weeks on path A or B, if the "
                "property shows no impressions growth for the cluster's target queries, stop writing and fix "
                "findability instead."),
        "impact": 4, "confidence": 3, "effort": "M",
        "risk_of_not_doing": ("Either the burst decays and nothing is published for a month, or the queue is "
                              "filled on volume - and volume without a source is the exact pattern the spam "
                              "policies name."),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-41",
        "title": "Decide whether the shopfront applies to the canonical build only, or to every build on the domain",
        "area": "Repository integrity",
        "problem": ("This repository publishes seven parallel builds on one origin, each with its own "
                    "stylesheet and its own copy of the data. The design work in this pass - product rail, "
                    "merchandising rows, the sticky bar, the mobile type scale - lands in the root build only. "
                    "A reader who arrives at s2/, dashboard/, research/, docs/ or an annex sees the old look, "
                    "and no amount of polish on the root build changes that."),
        "evidence": [ev("The catalogue of parallel builds kept in this repo", SITE + "previous-passes.html"),
                     ev("Flag F20 (one site, one index) and suggestion SG-05", SITE + "flagged.html"),
                     ev("Google on site structure and canonical URLs for one site",
                        "https://developers.google.com/search/docs/crawling-indexing/site-structure-overview")],
        "options": [
            {"label": "A. Declare the root build canonical; annexes keep their own look and are no-indexed",
             "what": ("Search engines get one site, readers get one brand, and the verification annexes stay "
                      "publicly readable as evidence with a visible banner naming them as archives. Cheapest "
                      "option that ends the two-looks problem."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. Port the design system into every build",
             "what": ("Uniform, and it means editing five generators that each have their own reproducibility "
                      "gate - the work multiplies every time the tokens change."),
             "effort": "L", "risk": "medium", "reversible": True},
            {"label": "C. Move the annexes out of the published site entirely",
             "what": ("Keep them in the repository, serve only the buying guide. Cleanest for indexing, and it "
                      "removes the reader-facing evidence trail the brief asked to keep published."),
             "effort": "M", "risk": "medium", "reversible": False}],
        "recommendation": ("A. It is the only option that makes 'the site' a single thing to design, without "
                           "destroying the audit trail that is this project's actual differentiator."),
        "why": ("Every design decision made from now on has to answer this question first, or it is made seven "
                "times. That is why it sits above the visual work, not beside it."),
        "impact": 4, "confidence": 5, "effort": "M",
        "risk_of_not_doing": ("Polish decays at the edges of the domain, and a crawler or a reader with a "
                              "search-result bookmark keeps finding the older, less trustworthy-looking version."),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-42",
        "title": "Decide how this site may show social proof at all, given the policy it obeys",
        "area": "Trust and compliance",
        "problem": ("No Amazon star rating, review count or price appears anywhere on the site, because the "
                    "program policies restrict how an Associate may display them. The site therefore shows "
                    "nothing that looks like popularity - which is compliant, and also reads as a wall of "
                    "tables to a shopper. Manufacturer-hosted ratings are the current compromise: they are the "
                    "brand's own figures, labelled as such."),
        "evidence": [ev("Program Policies 2(b) and 6(t) - price, availability and rating display",
                        "https://affiliate-program.amazon.com/help/operating/policies"),
                     ev("The article that already explains the rule to readers",
                        SITE + "articles/no-amazon-prices.html"),
                     ev("Why the Creators/PA API is the only compliant route to Amazon figures",
                        "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation")],
        "options": [
            {"label": "A. Status quo: brand-hosted ratings, labelled, with the read date",
             "what": ("What ships today on the product pages ('brand-site rating, not Amazon'). It gives the "
                      "reader a number and tells them whose number it is."),
             "effort": "0", "risk": "low", "reversible": True},
            {"label": "B. Get Creators/PA API access and serve Amazon data the way the policy intends",
             "what": ("Prices and ratings shown only when the API serves them through your link. Requires the "
                      "account, credentials and the qualifying-sales threshold - the three things no agent can "
                      "supply. Until then this row is a plan, not an option."),
             "effort": "L", "risk": "low", "reversible": True},
            {"label": "C. Replace ratings with verifiable trust signals",
             "what": ("The read date on every figure, the count of official sources behind a claim, and the "
                      "list of what the documents do not answer. Less persuasive to a browsing shopper, more "
                      "durable than any rating, and it is the angle this site can actually own."),
             "effort": "S", "risk": "low", "reversible": True}],
        "recommendation": ("C now, A kept as it is, and B the moment credentials exist. The marketing case for "
                           "this site is not 'we have more reviews than the other list'; it is 'we are the only "
                           "page that shows its working'."),
        "why": ("Ratings are borrowed credibility that can be taken away by a policy change or a stale read. "
                "Provenance is owned."),
        "impact": 3, "confidence": 4, "effort": "M",
        "risk_of_not_doing": ("The site keeps losing the comparison on the other pages' terms - star counts - "
                              "instead of winning on the one axis no aggregator competes on."),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-43",
        "title": "Give the front page one designed moment a season, not a redesign",
        "area": "Design and layout",
        "problem": ("The visual identity is coherent now (paper, ink, brand green, serif display) and the shop "
                    "layer exists, but the front page is the same object in November and in July. A publication "
                    "signals liveness: one seasonal surface, changed on a schedule, is what makes a returning "
                    "reader feel the site is run rather than generated."),
        "evidence": [ev("The seasonal topics already queued", SITE + "topics.html"),
                     ev("The generated front page today", SITE),
                     ev("Google's page-experience guidance on main content and interstitials",
                        "https://developers.google.com/search/docs/appearance/page-experience")],
        "options": [
            {"label": "A. One seasonal band above the product rail, generated from the topic queue",
             "what": ("A single line: the date window, the article that serves it, and the fact that the prices "
                      "below are list prices, not deal prices. Rendered only when a queued seasonal row is in "
                      "window, so off-season the page is exactly what it is today."),
             "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. A per-season hero treatment (colour and copy only)",
             "what": ("Stronger signal, more moving parts, and it invites a reader to expect deals the site is "
                      "not allowed to promise."),
             "effort": "M", "risk": "medium", "reversible": True},
            {"label": "C. Nothing until traffic justifies it",
             "what": "Defensible: a seasonal band on a site with zero measured visitors is decoration.",
             "effort": "0", "risk": "low", "reversible": True}],
        "recommendation": ("C until the analytics question (Q-27) is settled, then A. The band is worth building "
                           "when there is someone to notice it."),
        "why": ("Seasonality is the one marketing lever this site can pull without touching a claim: it changes "
                "what is surfaced, never what is asserted."),
        "impact": 2, "confidence": 3, "effort": "M",
        "risk_of_not_doing": "The site reads as evergreen, which is safe but forgettable.",
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-44",
        "title": "Instrument the click before optimising the design, and pick who hosts the endpoint",
        "area": "Measurement and mobile",
        "problem": ("This pass changed placement, ordering and prominence on the assumption that a product rail "
                    "and a comparison bar help a buyer decide. The assumption is reasoned, not measured, and the "
                    "site has no way to learn otherwise: GitHub Pages serves static files, so there is nowhere "
                    "for a click event to arrive. Five events are defined on measurement.html and none can fire."),
        "evidence": [ev("The five event definitions and their prerequisites", SITE + "measurement.html"),
                     ev("GitHub Pages serves static files only",
                        "https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site"),
                     ev("Program Policies: link clarity and the ban on misleading placement",
                        "https://affiliate-program.amazon.com/help/operating/policies")],
        "options": [
            {"label": "A. Self-host a counter endpoint alongside Pages",
             "what": ("One route, one append-only table, no cookies and no fingerprinting: click, outbound "
                      "destination host, page, timestamp. Needs a small host, a privacy line in the footer, and "
                      "the disclosure that a counter now exists."),
             "effort": "M", "risk": "medium", "reversible": True},
            {"label": "B. A privacy-first hosted analytics product",
             "what": ("Fewer moving parts to run, and the number of third parties on the page changes - which "
                      "the cookie and third-party disclosure (F11) must then reflect."),
             "effort": "S", "risk": "medium", "reversible": True},
            {"label": "C. Amazon's own earnings report as the only measurement",
             "what": ("Zero new code and zero new disclosure. It answers 'did anything earn', never 'what did the "
                      "reader click', so design changes stay unmeasured."),
             "effort": "0", "risk": "low", "reversible": True},
            {"label": "D. Ship no measurement and stop claiming optimisation",
             "what": ("Honest, and what the site does today. The campaign ledger stays empty by design and the "
                      "brief's 'continuously optimise' line stays blocked rather than faked."),
             "effort": "0", "risk": "low", "reversible": True}],
        "recommendation": ("A, with the ledger schema already drafted in data/campaign-ledger.json. It is the "
                           "only option that measures the click, which is the one number the design decisions on "
                           "this page need. B only if you would rather not run a service."),
        "why": ("Every row in this queue ends at the same wall: without a click counter, the difference between "
                "path A and path C is a matter of taste, and taste cannot be reviewed later."),
        "impact": 5, "confidence": 5, "effort": "M",
        "risk_of_not_doing": ("The site keeps being optimised by judgement, and the campaign ledger stays empty "
                              "for the fourth pass running - which means the brief's central automation claim "
                              "stays unverifiable."),
        "blocks": [], "blocked_by": [],
    },
]
sug["suggestions"].extend([x for x in NEW_SUG if x["id"] not in existing])
# SG-36's "blocks" slot is meant for register ids; keep the graph clean by not inventing one.
for x in sug["suggestions"]:
    if x["id"] == "SG-36":
        x["blocks"] = []
sug["paths"].append({
    "id": "P6",
    "name": "Make the shop look bought-in",
    "promise": ("The presentation layer a buyer judges the site by: products before process, a decision block "
                "on every product page, a mobile route that survives scrolling, and the two things that have "
                "to be decided by a human before the look can finish - photography and hosting."),
    "contains": ["SG-36", "SG-37", "SG-38", "SG-39", "SG-41", "SG-42", "SG-43", "SG-44", "SG-40"],
    "effort": ("Three quarters of it shipped on 2026-11-17 (SG-36, SG-37, SG-38, and SG-41/SG-42/SG-44 as "
               "decisions). What is left is two owner actions: the photography route (SG-39) and the "
               "measurement host (SG-44)."),
    "must_be_true_first": ("You accept that no picture, no price guarantee and no popularity claim appears on "
                           "this site unless its source is on the page. That is the constraint the design has to "
                           "live inside; it is why SG-39 is the highest-leverage row in the path."),
    "delivers": ("A front page that opens with goods, product pages that answer the two buyer questions in order, "
                 "a mobile reader who is never stuck, and a design record an owner can review without reading "
                 "the build."),
    "does_not_fix": ("Traffic, indexing of the parallel builds, and the fact that the site cannot yet see a "
                     "single click. SG-41, SG-44 and Q-28 are the rows that fix those."),
    "pick_this_if": "You want the site to look like a publication someone runs, and you will supply one of the two decisions.",
    "why_first": ("It sits last in the order on purpose: the compliance floor (P1) and findability (P3) are what "
                  "make a polished page worth polishing. If you want the visual change before the indexing work, "
                  "swap P6 ahead of P3 - nothing in P6 depends on P3."),
})
sug["paths_note"] = (sug.get("paths_note", "") +
                     " P6 was added by arena/fd9778a1-zone1 on " + TODAY + " for the shopfront pass; its "
                     "implemented half is recorded in data/decision-log.json rather than asserted here.")
sug["pass"] = (sug["pass"] + "; shopfront and decision-desk rows SG-36..SG-44 + path P6 by "
               "arena/fd9778a1-zone1 (" + TODAY + ")")
dump(SUG, sug)

# --------------------------------------------------------------------------- #
# 3. questions: what must be true before a design or traffic decision is reasonable.
# --------------------------------------------------------------------------- #
q = load(Q)
have_q = {x["id"] for x in q["questions"]}
NEW_Q = [
    {
        "id": "Q-27",
        "group": "Measurement",
        "question": "Is there any host on this project that can receive a click event, and who operates it?",
        "state": "missing",
        "why_it_matters": ("Three of the four decisions in the shopfront path (SG-38, SG-43, SG-44) are "
                           "placement decisions. Placement can only be judged with a click counter, and a "
                           "static GitHub Pages site has no server to count on. Until this is answered, every "
                           "'this will convert better' claim about the design - including the ones on this "
                           "repository's own pages - is unfalsifiable."),
        "what_we_know": [
            "The site ships no analytics, sets no cookies, and states that in the footer's cookie notice, which is the disclosure Program Policies 3(e) asks for.",
            "measurement.html defines five events with their fields and explicitly records that none of them can fire from a static host.",
            "data/campaign-ledger.json is committed empty by design, with a dated provenance rule for the day a real figure arrives."],
        "what_is_missing": "A decision: self-host a minimal counter, adopt a privacy-first hosted product, or accept Amazon's earnings report as the only measurement. Each changes what the footer must disclose.",
        "how_to_discover": ("Answer the three sub-questions in writing: (1) who runs a server here; (2) is a "
                            "first-party counter acceptable to you if it stores page, timestamp and destination "
                            "host with no cookie and no fingerprint; (3) does the choice get written into the "
                            "cookie notice the same day it ships. Nothing in this repository can answer them, "
                            "and nothing public will."),
        "blocks": ["SG-44", "SG-38", "SG-43"],
        "sources": [ev("The five event definitions and their prerequisites", SITE + "measurement.html"),
                    ev("Amazon Program Policies, participation requirements (disclosure of third-party technology)",
                       "https://affiliate-program.amazon.com/help/operating/policies"),
                    ev("The empty campaign ledger", REPO + "data/campaign-ledger.json")],
        "answer": None,
    },
    {
        "id": "Q-28",
        "group": "Content strategy",
        "question": "Which search queries does the site already appear for, and at what position?",
        "state": "missing",
        "why_it_matters": ("The topic queue picks its next four articles by judgement, labelled as judgement "
                           "because nobody has a query report. Search Console gives the site's own real queries "
                           "for free, and it is the only input that turns 'a no-hype capacity checklist' from an "
                           "editorial guess into a measured decision."),
        "what_we_know": [
            "sitemap.xml publishes the canonical URL list and feed.xml publishes the article set; both are regenerated by build.py on every commit.",
            "The site is one origin, one path prefix (/Zone1/), with canonical URLs emitted per page since pass 9.",
            "No pass in this repository has evidence of a verified Search Console property, and none can have: verification is an account action."],
        "what_is_missing": ("Ownership of the property, the submitted sitemap, and 4-8 weeks of query data. "
                             "Then the two numbers that decide the next topic: impressions by query, and "
                             "average position for queries where an existing article already answers the intent."),
        "how_to_discover": ("Verify the property for kanlerxz87-cyber.github.io/Zone1/ (a DNS TXT record you "
                            "control, or an HTML meta tag committed by an agent - the second is one line in "
                            "layout() and no agent may pick the domain for you), submit sitemap.xml, then export "
                            "the query report after four weeks and paste it into data/campaign-ledger.json with "
                            "a date and a source note."),
        "blocks": ["SG-40", "SG-43"],
        "sources": [ev("What the sitemap currently publishes", SITE + "sitemap.xml"),
                    ev("Search Console basics (Google's own documentation)",
                       "https://developers.google.com/search/docs/fundamentals/search-console-basics"),
                    ev("Google's guidance on building and submitting a sitemap",
                       "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap")],
        "answer": None,
    },
    {
        "id": "Q-29",
        "group": "Authorship",
        "question": "Whose name is on this publication, and what does that person actually have?",
        "state": "missing",
        "why_it_matters": ("A byline is the cheapest trust signal a buying guide can carry, and the most "
                           "dangerous to fake. The FTC's endorsement rules make the endorser's actual "
                           "experience the test for describing a product, so a name with no hands-on basis "
                           "behind it is worse than no name - and an invented one is a misrepresentation this "
                           "site could not defend in front of a regulator or a reader."),
        "what_we_know": [
            "No author identity exists in the repository: the structured data names the site as publisher, and every article page says documentation-based, no hands-on testing.",
            "Suggestion SG-32 proposes a production-method authorship line, which the site could ship today because it is a description of how the page was made.",
            "The only person who can hold the appliances is the owner; SG-39 option A is the same decision viewed from the media side."],
        "what_is_missing": ("Three things: a name or handle to publish, one sentence about why that person is "
                             "qualified to compare published documents (not to cook), and a decision on whether "
                             "they will ever handle a unit - because if they do, the 'no hands-on testing' "
                             "sentence has to come off, and a review of the tested machine becomes possible."),
        "how_to_discover": "Owner answer, ten minutes. Then an agent pass updates data/site.json, the Organization and Article structured data, and the footer's 'who runs this' block.",
        "blocks": ["SG-41"],
        "sources": [ev("FTC Disclosures 101 for influencers (the experience requirement)",
                       "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"),
                    ev("16 CFR Part 255 - Endorsements and Testimonials in Advertising",
                       "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255"),
                    ev("The authorship row in the queue", SITE + "suggestions.html#sg-32")],
        "answer": None,
    },
    {
        "id": "Q-30",
        "group": "Site ownership",
        "question": "Is this a subpath of a GitHub Pages domain, or a domain of its own?",
        "state": "missing",
        "why_it_matters": ("The brand, the social preview, the canonical URLs and the entire look of the site are "
                           "currently built around a repository name ('Zone1') that no shop would print on a "
                           "window. A real domain changes the masthead, the memory of the site, and what a "
                           "verification pass costs; keeping the subpath is also a legitimate choice, but it "
                           "should be chosen, not inherited."),
        "what_we_know": [
            "Every page canonicalises under https://kanlerxz87-cyber.github.io/Zone1/, and the landing page canonicalises to the directory form so index.html and / are one URL.",
            "GitHub Pages supports a custom domain with a DNS record and a settings change, documented by GitHub.",
            "The site name shown to readers is 'Zone1 Kitchen', which is a repository label adapted rather than a brand."],
        "what_is_missing": "A decision on the domain, and the brand name that goes with it. Then a mechanical change: SITE_URL in data/config.json, the footer masthead, the og:image card and the Search Console property in Q-28.",
        "how_to_discover": ("Pick a name, buy or point a domain, set it in Pages settings, then have an agent "
                            "pass change base_url in data/config.json and re-run the build: the guard that "
                            "compares committed HTML to a rebuild will surface every place the old URL was "
                            "hardcoded."),
        "blocks": ["SG-41", "SG-43"],
        "sources": [ev("GitHub Pages custom-domain documentation",
                       "https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site"),
                    ev("The canonical URLs as built today", SITE),
                    ev("The brand row in the queue", SITE + "suggestions.html#sg-33")],
        "answer": None,
    },
    {
        "id": "Q-31",
        "group": "Product photography",
        "question": "Who owns the rights to any image of these three products, and is a photo of your own kitchen allowed to appear?",
        "state": "not_stated",
        "why_it_matters": ("This is the row that decides whether the site can ever look like a shop. The design "
                           "work in this pass is the ceiling of what typography alone can do; every remaining "
                           "visual improvement wants an image, and images are the one asset class this repository "
                           "has deliberately published none of."),
        "what_we_know": [
            "Amazon's Operating Agreement section 1 defines Program Content to include the data, images and text available through the program, and the site publishes no Amazon image for that reason.",
            "The manufacturer pages carry their own photography on Shopify's CDN; nothing in this repository records a licence from Chefman or Emeril to reuse it.",
            "The site's only current imagery is four generated SVG diagrams and a generated social card, both described as such on figures.html.",
            "Generated or copied pictures of a specific product would misrepresent the item a reader is being paid to send to a retailer, which is why that option is recorded as rejected, not deferred."],
        "what_is_missing": ("Either a photograph you took (with a sentence saying who took it and when), or "
                             "written permission from a brand naming this site, or an explicit decision to stay "
                             "text-and-diagrams. All three are answers; only the first two need doing."),
        "how_to_discover": ("Option one is an afternoon with a phone: three units, front, open, and the model "
                            "plate, plus a line of caption. Option two is one email each to Chefman and Emeril "
                            "press asking for permission to use product imagery on this site specifically, with "
                            "the reply filed in data/sources.json like any other fact."),
        "blocks": ["SG-39"],
        "sources": [ev("Associates Operating Agreement, section 1 (Program Content)",
                       "https://affiliate-program.amazon.com/help/operating/agreement"),
                    ev("The figures page, as the current substitute", SITE + "figures.html"),
                    ev("Google on thin affiliation and original content",
                       "https://developers.google.com/search/docs/essentials/spam-policies")],
        "answer": None,
    },
    {
        "id": "Q-32",
        "group": "Brand",
        "question": "What is this site for, in one sentence a shopper would repeat: a buying guide, a deals page, or a verification service?",
        "state": "missing",
        "why_it_matters": ("The brief asks simultaneously for a marketing affiliate site, a dashboard of every "
                           "finding, and a compliance-grade source register. Those three products want different "
                           "front pages, different vocabulary and different evidence. Every design row in the "
                           "queue is downstream of this answer, which is why the site keeps oscillating between "
                           "a shop and an audit."),
        "what_we_know": [
            "The repository's own positioning row says the niche was dictated by the product set, not chosen by research (data/marketing.json).",
            "The front page now leads with the three machines and puts the metrics under the comparison table, which is the buying-guide reading of the brief.",
            "A deals page is not available to this site as configured: it may not display Amazon prices or ratings without the API, and it runs no paid placements."],
        "what_is_missing": ("One sentence, owned by you, and consistency with it. If the answer is 'a buying "
                             "guide', the register pages move to the footer permanently and the article set gets "
                             "the front page. If it is 'a verification service for people who buy appliances', "
                             "the flags and the read dates move up, and the site should stop imitating a shop."),
        "how_to_discover": ("No research step exists. Write the sentence, then have a pass test every page "
                            "against it: any surface that does not serve the sentence becomes an annex. "
                            "Decisions R-9 to R-12 on design-prompt.html are where it gets recorded."),
        "blocks": ["SG-36", "SG-41", "SG-43"],
        "sources": [ev("The positioning row as it stands", REPO + "data/marketing.json"),
                    ev("The front page after this pass", SITE),
                    ev("Why a deals page is not currently available", SITE + "articles/no-amazon-prices.html")],
        "answer": None,
    },
    {
        "id": "Q-33",
        "group": "Content operations",
        "question": "Who writes the next article, on what schedule, and who checks it before it publishes?",
        "state": "missing",
        "why_it_matters": ("Twenty-four articles exist because agent passes wrote them under an evidence rule and "
                           "a build guard. That is a pipeline with no owner, no cadence and no editor, which is "
                           "exactly how a publication becomes a content farm with good footnotes. The topic queue "
                           "has four proposed rows and no order."),
        "what_we_know": [
            "Every article is machine-checked: a value quoted in prose must already be a published value in the dataset, an unregistered source citation fails the build, and banned stock phrases fail it too.",
            "The voice rules on design-prompt.html are the editorial standard currently enforced, and they were adopted on 2026-11-16.",
            "The kill rule proposed in SG-40 is the only published performance commitment in the content plan."],
        "what_is_missing": ("A cadence (SG-40), an editor - is a human reading each piece before it ships, or is "
                             "the guard the only check? - and a byline policy, which is Q-29. Answering the "
                             "editor question alone changes what 'published' means on this site."),
        "how_to_discover": "Owner decision, then recorded in data/topics.json as a cadence field and on the decisions register as a status change.",
        "blocks": ["SG-40"],
        "sources": [ev("The article guards in the generator", REPO + "build.py"),
                    ev("The voice rules enforced by the build", SITE + "design-prompt.html"),
                    ev("Google on helpful content and mass-produced pages",
                       "https://developers.google.com/search/docs/essentials/spam-policies")],
        "answer": None,
    },
    {
        "id": "Q-34",
        "group": "Attribution",
        "question": "Did the one-link test produce a tracked click in the Associates earnings report?",
        "state": "unknowable",
        "why_it_matters": ("The site now attaches your tracking ID to every outbound product link and fails the "
                           "build if one ships without it. That makes the links correct in form. Whether Amazon "
                           "credits a click through them - which is the whole point of a tracking ID - can only "
                           "be read in your account."),
        "what_we_know": [
            "The owner-supplied ID shopnow047c-20 is recorded in data/config.json with its provenance and applied by the build to every /dp/ link.",
            "Flags F76 and F82 record what remains open: attribution untested, and none of the five supplied short links carried a tag when read on 2026-11-17.",
            "The brief's own instruction is a single test link, confirmed destination and confirmed tracking, before scaling to the rest."],
        "what_is_missing": "One click, one day, one screenshot of the earnings or tracking report showing that click attributed to the ID.",
        "how_to_discover": ("In Associates Central: build one link for the 6 Qt ASIN with tracking ID "
                            "shopnow047c-20, open it in a private window, confirm the destination is "
                            "amazon.com/dp/B0CDY277D3 with the tag in the URL, then check the report the next "
                            "day. Paste the observation into data/product-intent.json and this row's answer "
                            "field; an agent pass will then close F76."),
        "blocks": ["SG-38", "SG-44"],
        "sources": [ev("What the site currently records about the tag", SITE + "product-intent.html"),
                    ev("Program Policies 2(a) - Special Links must carry the assigned ID",
                       "https://affiliate-program.amazon.com/help/operating/policies"),
                    ev("Flag F76, open", SITE + "flagged.html#f76")],
        "answer": None,
    },
    {
        "id": "Q-35",
        "group": "Evidence base",
        "question": "Which figure is the appliance's weight, and which is the boxed figure, for the 8 Qt?",
        "state": "not_stated",
        "why_it_matters": ("Found by this pass on the brand's own page, on the same date, from two fields of the "
                           "same product record: the specification block says 12.8 lbs / 5.8 kg and the store "
                           "variant carries 13.4 lb. A reader who is deciding whether a shelf or a cupboard can "
                           "take it gets a different answer depending on which field they find, and neither "
                           "document says which one is the product and which is the package. Recorded as F84."),
        "what_we_know": [
            "Both numbers are on chefman.com for RJ38-SQSS-8T as read on " + TODAY + ".",
            "The site publishes the specification-block figure, because that block is where the brand states the appliance's dimensions and weight together.",
            "Nothing was averaged, and no weight claim appears in any article on this site."],
        "what_is_missing": "A statement from Chefman of which figure is the appliance, or a third document that says so (the manual's specification page is the likeliest place and does not carry a weight for this model).",
        "how_to_discover": "Ask Chefman support for the net weight of RJ38-SQSS-8T, or photograph the scale readout if a unit is on hand. Either answer closes F84 and lets the small-kitchen article state a weight.",
        "blocks": [],
        "sources": [ev("Chefman 8 Qt product page (specification block)", "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"),
                    ev("Chefman store product record for the same page (variant weight)",
                       "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1.json"),
                    ev("Flag F84", SITE + "flagged.html#f84")],
        "answer": None,
    },
    {
        "id": "Q-36",
        "group": "Platform compliance",
        "question": "May the site use a brand's own marketing sentence as content, and with what framing?",
        "state": "not_stated",
        "why_it_matters": ("This pass published an article about the '98% less oil' line on the 8 Qt page. "
                           "Quoting a brand's claim and naming the missing baseline is more useful than the "
                           "claim, and less risky than repeating it - but no registered document states the "
                           "boundary, and a later pass that paraphrases instead of quoting will cross it. "
                           "Operating Agreement 6(a) restricts altering Program Content; a brand's own site is "
                           "not Program Content, and that distinction is exactly what needs writing down."),
        "what_we_know": [
            "The site quotes manufacturer pages and manuals with the page linked and the read date stated; that is the pattern the article set follows.",
            "The oil article quotes the sentence, labels it a brand claim, and states what the page does not say. It makes no health claim of its own.",
            "No decision row exists for the general rule, and the register carries no policy citation for brand-site copy as such."],
        "what_is_missing": ("A one-line editorial rule, recorded as a decision, on quoting brand marketing copy: "
                             "verbatim quotation with the page cited, or silence. Then the same rule for listing "
                             "titles, which are Amazon content rather than brand content."),
        "how_to_discover": "It is a policy read, not a lookup: the Operating Agreement's Content sections and the Program Policies, applied to non-Amazon brand copy, then recorded on the decisions register as a status change.",
        "blocks": [],
        "sources": [ev("Associates Operating Agreement (Content and Program Content)",
                       "https://affiliate-program.amazon.com/help/operating/agreement"),
                    ev("Program Policies (content on your site)",
                       "https://affiliate-program.amazon.com/help/operating/policies"),
                    ev("The article this question arose from", SITE + "articles/ninety-eight-percent-less-oil-claim.html")],
        "answer": None,
    },
    {
        "id": "Q-37",
        "group": "Governance",
        "question": "Which accessibility and mobile standard is the design required to meet, and can this site cite it?",
        "state": "missing",
        "why_it_matters": ("This pass widened tap targets to a 44 px minimum and added a fluid type scale. Both "
                           "are usability choices the build enforces and no page claims they satisfy a standard, "
                           "because the site cannot cite one: the verifier's official-host list contains no "
                           "accessibility body, so a WCAG reference could not be linked as a source without "
                           "weakening every other citation on the page. Recorded as F86."),
        "what_we_know": [
            "The site's own checks confirm contrast pairs and disclosure presence, not conformance to an external standard.",
            "Google's page-experience guidance asks whether content displays well on mobile and whether intrusive interstitials are avoided - both satisfied by the current build and quotable from a registered source (S38).",
            "No accessibility standard is registered in data/sources.json, so no page on this site may assert conformance."],
        "what_is_missing": ("A decision on whether to hold the design to a named standard. If yes, an owner or "
                            "agent pass must register the standard's own publisher page as a source - and the "
                            "verifier's host list is the gate, which is a one-line change with a reason attached."),
        "how_to_discover": ("Decide the standard, then have a pass add its official page to data/sources.json and "
                            "to verify.py's allow list in the same commit, so the claim and the citation arrive "
                            "together. Do not add the claim first."),
        "blocks": ["SG-38"],
        "sources": [ev("Google page-experience guidance, the standard this site can currently cite",
                       "https://developers.google.com/search/docs/appearance/page-experience"),
                    ev("The verifier's official-host list", REPO + "verify.py"),
                    ev("Flag F86", SITE + "flagged.html#f86")],
        "answer": None,
    },
]
q["questions"].extend([x for x in NEW_Q if x["id"] not in have_q])
q["compiled"] = TODAY + " (extended by arena/fd9778a1-zone1; original register compiled 2026-11-16)"
dump(Q, q)

# --------------------------------------------------------------------------- #
# 4. design-prompt: the shopfront block of the paste-ready brief + status rows.
# --------------------------------------------------------------------------- #
dp = load(DP)
dp["design_prompt"] += """

SHOPFRONT PASS 2026-11-17 — WHAT THE BUILD NOW DOES, AND WHAT STILL NEEDS A HUMAN
Implemented, so do not propose it twice:
- The front page opens with the three machines (capacity, the brand's own list price labelled as such, a
  "Best for" row and a "Check first" row per card), and the metric tiles sit under the comparison table.
- Product pages carry the same two merchandising rows as a decision block above the fold, sourced from the
  rows already on the page, and a compact sponsored CTA.
- Mobile: one clamp() type scale per heading level, a 44 px minimum hit area on every interactive control,
  a bottom-anchored comparison bar on reader pages only (hidden on desktop, in print and over the footer),
  and a one-line hint under any table that is wider than the screen.
- Merchandising copy is generated from a single MERCH register in build.py. Both cells are quotations of
  published rows; no cell may assert performance, comfort, durability or taste, because no test was run.

Still the designer's to decide, and blocked on a human, not on skill:
- Photography (SG-39, Q-31). Nothing above the fold can look like a shop until there is an image nobody has
  to licence from Amazon. Owner photographs are the recommended route; copied brand images and generated
  product likenesses are both rejected in writing.
- One site, one look (SG-41, Q-30). Seven parallel builds share an origin; design decisions apply to the
  canonical root build unless the annexes are declared archives.
- Placement proof (SG-44, Q-27). Sticky bar, price line and merchandising order are reasoned changes; no
  click data exists, so no change may be described as an improvement in conversion anywhere on this site.
- Voice ceiling (Q-29, Q-33). A byline and a cadence are what separate a publication from a generated
  archive. Both are owner answers, and a byline naming a person who has not used the products is prohibited
  by the same rule that bans a fake "we tested" line.
"""
dp["design"].extend([
    {"id": "D-13",
     "suggestion": "Lead the front page with the product rail; move the metric tiles below the comparison table",
     "why": "A buyer needs to see the goods before the paperwork. The tiles stay on the page, one screen later.",
     "path": "Reorder page_index(); keep the disclosure band, the paid-link fact and the caution callout untouched in position.",
     "status": "implemented",
     "status_note": "Shipped 2026-11-17 by arena/fd9778a1-zone1. Every figure in the rail is read from data/products.json by the same loop that renders the table, so it cannot disagree with it.",
     "sources": [], "links": [{"url": REPO + "build.py", "label": "page_index product rail"}]},
    {"id": "D-14",
     "suggestion": "Add the two merchandising rows — 'Best for' and 'Check first' — to the cards and the product pages",
     "why": "Those are the two questions a buyer asks in order, and both are answerable from rows this site already publishes.",
     "path": "One MERCH register in build.py, rendered by merch_pair(); cells cite the same source chips as the table below them.",
     "status": "implemented",
     "status_note": "Shipped 2026-11-17. The copy names documented features and open conflicts only; the 'who should not buy this' row (SG-37 option B) stays out until an owner writes it.",
     "sources": [], "links": [{"url": REPO + "build.py", "label": "MERCH and merch_pair()"}]},
    {"id": "D-15",
     "suggestion": "Show the brand's own list price, with the policy reason no Amazon price appears beside it",
     "why": "A shop without a price looks unlike a shop; an affiliate site without the reason looks like it is hiding something.",
     "path": "price_line() reads the registered brand list price and states that Program Policies 2(b) and 6(t) keep Amazon's figure off the page.",
     "status": "implemented",
     "status_note": "Shipped 2026-11-17. The dated read trail lives on the dataset page and the verification ledgers; the card deliberately does not print a read date, because a price block can change between reads (flag F84 exists for exactly that class of drift).",
     "sources": ["S2"], "links": [{"url": REPO + "build.py", "label": "price_line()"}]},
    {"id": "D-16",
     "suggestion": "Mobile-first pass: fluid type scale, 44 px hit areas, sticky comparison bar, wide-table hint",
     "why": "The comparison table is the site's product. On a phone it was the hardest thing to reach and the easiest thing to lose.",
     "path": "Clamp() per heading level, min-height on interactive chrome only, a bottom-anchored bar on reader surfaces, and a JS-revealed hint that appears only when a table is genuinely clipped.",
     "status": "implemented",
     "status_note": "Shipped 2026-11-17. Progressive: with scripts disabled the tables still scroll, the bar stays put and no content is hidden. The bar is hidden on desktop, in print and while the footer is visible; no interstitial, per the page-experience guidance (S38). The 44 px figure is a usability choice, not a standards claim — see F86 and Q-37.",
     "sources": ["S38"], "links": [{"url": REPO + "build.py", "label": "shopfront CSS block and shopbar in layout()"}]},
    {"id": "D-17",
     "suggestion": "One designed seasonal moment on the front page, generated from the topic queue's own windows",
     "why": "Liveness is what a reader notices between visits, and it is the one marketing lever that does not touch a claim.",
     "path": "A band above the product rail, rendered only when a queued seasonal row is in window.",
     "status": "pending",
     "status_note": "Deliberately not built in this pass: SG-43 recommends waiting for the measurement answer (Q-27). A seasonal band on a site with no visitors is decoration.",
     "sources": [], "links": [{"url": SITE + "suggestions.html#sg-43", "label": "SG-43"}]},
])
dp["tactics"].extend([
    {"id": "T-12",
     "tactic": "Publish one question-shaped guide per queue row the moment the row has an official source to answer it",
     "how": "Three shipped on 2026-11-17 (TP-21 buyer's checklist, TP-22 brand-vs-brand, TP-23 the '98% less oil' read), each added to data/articles.json so the sitemap, the RSS feed, the article index and the internal links regenerate from the register rather than by hand.",
     "status": "partial",
     "status_note": "The cadence itself is undecided — SG-40 and Q-33. What is proven is that the machinery costs nothing per article: one register row and a rebuild.",
     "sources": ["S30"], "links": [{"url": SITE + "articles/index.html", "label": "The article index as published"}]},
    {"id": "T-13",
     "tactic": "Choose the next topic from measured queries, not from instinct",
     "how": "Verify the Search Console property, submit the generated sitemap, read the query report after four weeks, and put the two numbers that decide the next piece (impressions by query, average position where an article already answers the intent) into the campaign ledger with a date and a source note.",
     "status": "pending",
     "status_note": "Blocked on the owner action in Q-28. Nothing on this site has changed hands on a query number yet, and the queue says so out loud.",
     "sources": ["S30"], "links": [{"url": SITE + "sitemap.xml", "label": "sitemap.xml as generated today"}]},
    {"id": "T-14",
     "tactic": "Make one URL set findable: canonical root build, annexes labelled archives",
     "how": "SG-41 option A: the root build carries the design and the index; s2/, site/, research/, docs/, dashboard/ and the annexes keep their evidence role and stop competing for the same reader and the same crawler.",
     "status": "pending",
     "status_note": "Unchanged by this pass and unfixable by it: those builds are other sessions' generators with their own reproducibility gates. Requested on the coordination board rather than edited.",
     "sources": ["S31"], "links": [{"url": SITE + "previous-passes.html", "label": "Parallel-build catalogue"}]},
])
dp["voice_rules"].extend([
    {"id": "V-8",
     "rule": "A product page may say what a machine is for and what to check before buying. It may not say what it is like to live with.",
     "why": "The first is a reading of published documents; the second is an experience nobody here has had, and FTC guidance makes having used the product the test for describing it.",
     "sources": ["S8"], "links": []},
    {"id": "V-9",
     "rule": "A price on this site is a brand's own list price, labelled as such, with the reason Amazon's figure is absent in the same breath.",
     "why": "Silence about price reads as an omission; an unlabelled price reads as today's price. Naming both the figure and the policy that keeps the other one off the page is the version a reader can check.",
     "sources": ["S2"], "links": []},
])
dp["decisions"].extend([
    {"id": "R-9",
     "suggestion": "Which surface is the site's first screen: the buying guide's product rail, or the verification dashboard's metrics?",
     "options": "Product rail first (shipped) / metrics first (previous) / metrics to footer only",
     "recommended": "Product rail first, metrics under the comparison table — SG-36 option A",
     "status": "implemented",
     "status_note": "Implemented 2026-11-17 by arena/fd9778a1-zone1 and published as SG-36's own default. Ratify, or pick SG-36 option B to move the tiles to the footer entirely.",
     "sources": [], "links": [{"url": SITE, "label": "The front page as shipped"}]},
    {"id": "R-10",
     "suggestion": "Photography route for the shopfront",
     "options": "Owner photographs / brand press-licence request / stay diagram-only / generated images (rejected)",
     "recommended": "Owner photographs (SG-39 option A)",
     "status": "needs-owner",
     "status_note": "Open, and it is the row that caps how far the visual work can go. Q-31 states the rights position; no agent pass will fill this by choosing for you.",
     "sources": ["S1"], "links": [{"url": SITE + "questions.html#q-31", "label": "Q-31"}]},
    {"id": "R-11",
     "suggestion": "Cadence, byline and editorial check for the next article set",
     "options": "One a week with a source test / two a month, seasonal first / wait for query data / status quo",
     "recommended": "One a week now, switch to measured queries when Search Console has 4-8 weeks of data (SG-40 A then C)",
     "status": "needs-owner",
     "status_note": "Three linked questions: Q-28 (queries), Q-29 (byline), Q-33 (who writes and who checks). None of them can be answered from inside this repository.",
     "sources": ["S30"], "links": [{"url": SITE + "topics.html", "label": "The queue the cadence would govern"}]},
    {"id": "R-12",
     "suggestion": "Who hosts the click counter, and what the footer says the day it goes live",
     "options": "Self-hosted minimal endpoint / privacy-first hosted tool / Amazon earnings report only / no measurement",
     "recommended": "Self-hosted counter with no cookie and no fingerprint, footer notice updated in the same commit (SG-44 option A)",
     "status": "needs-owner",
     "status_note": "Q-27. Until it is answered, no page here may claim a design change improved conversion, and this pass does not.",
     "sources": ["S2"], "links": [{"url": SITE + "measurement.html", "label": "measurement.html"}]},
])
dp["compiled"] = TODAY + " (pass 13 shopfront additions by arena/fd9778a1-zone1; base compiled 2026-11-16)"
dump(DP, dp)

# --------------------------------------------------------------------------- #
# 5. requirements register: honest status moves for the rows this pass touched.
# --------------------------------------------------------------------------- #
req = load(REQ)
R = {r["id"]: r for r in req["requirements"]}
moves = {
    "B-01": ("partial", ["assets/style.css", "data/articles.json", "build.py"],
             ("The build fails on {n_banned} banned stock-phrase entries and on machine-spliced sentences, and "
              "pass 13 (2026-11-17) added the shop layer a buyer judges a storefront by: the front page opens "
              "with the three machines (capacity, the brand's own list price, a 'Best for' row and a 'Check "
              "first' row each), the product pages lead with the same decision block, and mobile got a fluid "
              "type scale, a 44 px minimum hit area and a sticky comparison route. What still keeps this row at "
              "partial is one fact, not one effort: there is no product image anywhere on the site, because "
              "Amazon's Program Content may not be copied and no brand licence is recorded (Q-31, SG-39). A "
              "shop window with no goods in it reads as generated, whatever the typography does."),
             ["S1", "S38"]),
    "B-08": ("delivered", ["articles/index.html", "data/topics.json", "data/articles.json"],
             ("24 articles now, three of them added by pass 13 on 2026-11-17 with the shapes a shopper "
              "actually types: 'Chefman vs. Emeril: what a basket brand and an oven brand actually publish', "
              "'\u201c98% less oil\u201d is a sentence on a box, not a measurement', and 'Eight questions to ask "
              "before you buy a multi-function kitchen appliance'. Trendy in the durable sense — a question "
              "with a documented answer and a visible gap where there is none — and deliberately not "
              "trend-chasing: a trending claim with no official source is the one thing this build will not "
              "publish. What is still missing is not titles, it is cadence and query data (Q-28, Q-33, SG-40)."),
             ["S30"]),
    "D-01": ("partial", ["data/articles.json", "build.py", "data/topics.json"],
             ("Every article row declares its target query, its intent and a reading time, and each new piece "
              "is regenerated into the index, the sitemap, the feed and the prev/next strip from one register "
              "row — the pipeline is mechanical and its output is checked. It stays partial because the "
              "optimisation half is absent: no query report and no click counter, so nothing in the pipeline "
              "learns which article earned anything. F12 still states what a real loop requires."),
             ["S2", "S30"]),
    "A-02": ("delivered", ["data/design-prompt.json", "data/suggestions.json", "suggestions.html"],
             ("Pass 13 added the shopfront half of the brief-facing prompt: the paste-ready design prompt now "
              "carries a 'what the build does since 2026-11-17 and what still needs a human' block, nine new "
              "suggestion rows with paths and effort, five design rows with live status, three traffic tactics "
              "and two voice rules the generator enforces."), []),
    "A-03": ("delivered", ["suggestions.html", "design-prompt.html", "decision-log.html", "data/suggestions.json"],
             ("Three review surfaces, one mechanism: suggestions.html is the queue with paths, design-prompt.html "
              "is the status view with a blank Decision column, and decision-log.html is where a path is picked "
              "and exported back as JSON. Pass 13 added path P6 ('make the shop look bought-in') and a computed "
              "decision desk at the top of the queue — open rows, rows blocked on an unanswered question, the "
              "questions that unblock the most, and the highest-scoring row with no recorded choice — all of it "
              "counted from the registers at build time, so it cannot go stale the way a typed summary does."), []),
    "A-04": ("delivered", ["questions.html", "data/questions.json"],
             ("Eleven rows added on 2026-11-17 (Q-27 to Q-37), each stating the answer's owner: the account "
              "holder alone can settle the click-test question (Q-34) and the photography rights question "
              "(Q-31); Search Console ownership settles the next topic (Q-28); two rows record what an official "
              "source was read and does not state (Q-35's weight conflict, Q-36's quotation rule). Nothing here "
              "was filled by inference, and the four states — known, missing, unknowable, not_stated — are the "
              "legend, not decoration."), []),
    "A-05": ("delivered", ["questions.html", "data/questions.json", "data/sources.json"],
             ("Every new row ends in a discovery step concrete enough to hand to someone: which Associates "
              "Central screen answers Q-34, which email answers Q-31, which four weeks of data answers Q-28, and "
              "which single line of build.py answers Q-30. Where the answer would need a source this verifier "
              "cannot cite, the row says so instead of inventing the citation (Q-37, F86)."), []),
}
for rid, (status, where, why, sources) in moves.items():
    row = R[rid]
    row["status"] = status
    row["where"] = where
    row["why"] = why
    if sources:
        row["sources"] = sources
    row.setdefault("evidence", [])
    row["evidence"] = [e_ for e_ in row["evidence"] if not e_["url"].startswith(("http", "#"))] + [
        {"label": "pass 13 record", "url": "reports/verification-2026-11-17-fd9778a1.md"}]
req["counts_note"] = ("Counts are computed from the rows at build time rather than typed, so this page cannot "
                      "claim a total the register does not contain. Statuses last moved 2026-11-17 by "
                      "arena/fd9778a1-zone1 (pass 13 shopfront): B-08 and A-02 to A-05 delivered, B-01 and D-01 "
                      "still partial with the reason named.")
dump(REQ, req)

# --------------------------------------------------------------------------- #
# 6. decision log: record what this pass implemented under the standing rule.
# --------------------------------------------------------------------------- #
log = load(LOG)
SHOPFRONT_IMPL = [
    ("SG-36",
     "The front page now opens with the three product cards — capacity, the brand's own list price with the "
     "policy reason no Amazon price appears beside it, a 'Best for' row and a 'Check first' row — and the "
     "metric tiles moved under the comparison table. Order only: no value changed, and the disclosure band "
     "and the paid-link labels stayed where the compliance guards expect them."),
    ("SG-37",
     "Every product page gained the same two merchandising rows as a decision block above the fold, generated "
     "by merch_pair() from the product's own sourced spec and flag rows, plus a compact sponsored CTA on the "
     "front-page card. Option B of that row ('who should not buy this') is deliberately NOT implemented: it is "
     "advice rather than a quotation, so it waits for you."),
    ("SG-38",
     "Mobile-first chrome: one clamp() type scale per heading level, a 44 px minimum hit area on every "
     "interactive control, a bottom-anchored comparison bar on reader pages only (hidden on desktop, in print "
     "and while the footer is on screen), and a hint under any table genuinely wider than the viewport. The "
     "bar carries no purchase button — option B of that row stays open until a click counter exists."),
]
for _sid, _what in SHOPFRONT_IMPL:
    log["implemented"].append({
        "id": _sid,
        "session": "arena/fd9778a1-zone1",
        "date": TODAY,
        "path": "A",
        "what": _what,
        "why_allowed": ("The row's own recommendation is option A: effort S-M, risk low or none, reversible, "
                        "and blocked by nothing in state 'unknowable'. The standing rule on this page "
                        "authorises implementing that and recording it here. No claim about conversion is made "
                        "anywhere in the change, because no click data exists (Q-27)."),
        "evidence": ["build.py", "assets/style.css", "data/suggestions.json",
                     "reports/verification-2026-11-17-fd9778a1.md"],
    })
log["choices_note"] = (log.get("choices_note", "") +
                       " 2026-11-17: path P6 added to the queue (SG-36..SG-44) with three rows implemented under "
                       "the standing rule and six left for the owner — session arena/fd9778a1-zone1.").strip()
dump(LOG, log)
print("suggestions:", len(sug["suggestions"]), "| questions:", len(q["questions"]),
      "| paths:", len(sug["paths"]), "| sources:", len(srcs))
