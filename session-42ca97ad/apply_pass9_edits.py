#!/usr/bin/env python3
"""One-shot editor for data/suggestions.json and data/questions.json (session 42ca97ad).

Kept in the repository so the edit is reproducible and reviewable. It is idempotent:
running it twice does not duplicate the rows it adds.
"""
import json
import collections

SUG = "data/suggestions.json"
Q = "data/questions.json"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, object_pairs_hook=collections.OrderedDict)


def save(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


POLICIES = "https://affiliate-program.amazon.com/help/operating/policies"
RATE_TABLE = "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ"
APP_REVIEW = "https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM"
CFR_465 = "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465/section-465.6"
CHEFMAN_6QT = "https://chefman.com/products/turbofry-touch-dual-window-air-fryer"
CHEFMAN_8QT = "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"
EMERIL = "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360"
MANUAL_6QT = "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf"
MANUAL_8QT = "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQSS-8T-UG-US.pdf"
MANUAL_EMERIL = "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"
LIST_6QT = "https://link.amazon/B04G1MEwY"
LIST_EMERIL = "https://link.amazon/B02NbDxp3"
LIST_8QT = "https://link.amazon/B00hJ57DV"

# --------------------------------------------------------------------------- #
# New suggestions
# --------------------------------------------------------------------------- #

NEW_SUGGESTIONS = [
    {
        "id": "SG-18",
        "title": "Decide what the AI agent in the brief is allowed to read, before the pipeline is written",
        "area": "Platform and compliance",
        "problem": (
            "The brief asks for an AI platform that \"automates product research, identifies trending and "
            "high-converting products, analyses pricing, reviews, competition, and commission potential\". "
            "Read against Amazon's IP License, most of the automatic half of that is contractually closed. "
            "Section 1 states that Amazon \"will not allow any third party to use Program Content to, "
            "directly or indirectly, develop or improve large language or multimodal models, machine learning "
            "models or related technology\". Section 2(e) forbids accessing Creators API, PA API or Data Feeds "
            "\"for the purpose of aggregating, analyzing, extracting, or repurposing any Product Advertising "
            "Content ... or in the direct training or fine-tuning of a machine learning and/or foundational "
            "model\" without Amazon's express prior written approval. An Amazon listing's title, price, rating "
            "and review count are Program Content. An agent that reads Amazon listings to learn what sells is "
            "therefore the exact use the licence names; an agent that reads manufacturers' own product pages "
            "and owner's manuals is not. This is a constraint on design, and it is cheapest to honour before "
            "the pipeline is written."
        ),
        "evidence": [
            {"label": "Associates Program IP License, section 1 - Program Content and large language models",
             "url": POLICIES},
            {"label": "Associates Program IP License, section 2(e) - aggregating, analysing, repurposing, and model training",
             "url": POLICIES},
        ],
        "options": [
            {
                "label": "A. Build the platform on manufacturer and first-party data only",
                "what": (
                    "Research the manufacturers' own product pages and owner's manuals, keep the verified "
                    "dataset as the single source of truth, and let the generator write only what that dataset "
                    "contains. This repository already implements the pattern: build.py refuses to publish an "
                    "article whose numbers are not in data/products.json, and every value on the site carries "
                    "the official page it came from. Trend and niche signals then come from your own click and "
                    "earnings data rather than from Amazon's listings."
                ),
                "effort": "L", "risk": "low", "reversible": True,
            },
            {
                "label": "B. Apply for Creators API or PA API and operate inside the API licence",
                "what": (
                    "The APIs are the sanctioned route to Amazon data, and their output may be displayed under "
                    "sections 2(b) and 6(t) with the required display rules. Credentials are tied to the primary "
                    "account holder and request volume scales with account sales, so this path depends on Q-05 "
                    "and Q-03 being answered first."
                ),
                "effort": "L", "risk": "medium", "reversible": False,
            },
            {
                "label": "C. Ask Amazon for prior written approval to use listing content",
                "what": (
                    "Section 2(e) allows the use with Amazon's express prior written approval. Until that "
                    "approval exists in writing, any version of option A that reads listing text is the "
                    "prohibited use."
                ),
                "effort": "M", "risk": "low", "reversible": True,
            },
        ],
        "recommendation": "A, treating B as the later upgrade rather than the starting point.",
        "why": (
            "The headline capability in the brief is the part the licence most clearly constrains, and knowing "
            "that before the research pipeline is designed costs nothing, while discovering it afterwards "
            "costs the pipeline. Option A is not a reduced version of the brief: it is the version of it that "
            "is lawful, and this repository already demonstrates that it can be built - the whole site is a "
            "working example of manufacturer-sourced, machine-written, claim-checked content."
        ),
        "impact": 5, "confidence": 5, "effort": "L",
        "risk_of_not_doing": (
            "High. A pipeline built on scraped listing content that later turns out to be the prohibited use "
            "means discarding the pipeline, and potentially the account, at the point where the most has been spent."
        ),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-19",
        "title": "Give every published value a refresh date, and let the build report what has gone stale",
        "area": "Content operations",
        "problem": (
            "Every published figure on this site carries the date it was read, but nothing tells the owner "
            "when it should be read again. The dataset already contains a measured case of drift: Chefman's "
            "own review counter moved from 1,302 to 1,305 within twenty-four hours while the average held at "
            "4.6. The Associates application-review criteria recorded in this repository also include a "
            "requirement that site content be recent - a requirement that was not re-read on 2026-11-15 "
            "(flag F46), so the exact window must be confirmed before it is used as a schedule. A page that is "
            "silently three months stale still looks authoritative, and the site has no mechanism to say so."
        ),
        "evidence": [
            {"label": "Chefman 6 Qt brand page - 1,305 brand-hosted reviews at the 2026-11-15 read",
             "url": CHEFMAN_6QT},
            {"label": "Application Review Process - site content recency criterion (not re-read 2026-11-15; see flag F46)",
             "url": APP_REVIEW},
        ],
        "options": [
            {
                "label": "A. Publish a stale-value report driven by the read dates the dataset already carries",
                "what": (
                    "A dated read already exists for most rows. Add one build report that lists every value "
                    "whose read date is older than a per-class interval you set - 30 days for ratings and "
                    "review counts, 180 days for physical specifications - and link it from the flag page so "
                    "staleness is visible rather than silent."
                ),
                "effort": "M", "risk": "low", "reversible": True,
            },
            {
                "label": "B. Automate the re-fetch",
                "what": (
                    "Schedule the same fetches this pass made and rewrite the dataset. It works, but a script "
                    "that writes into the verified dataset can silently overwrite a human correction, so it "
                    "needs the same no-inference guard the article gate uses."
                ),
                "effort": "L", "risk": "medium", "reversible": True,
            },
            {
                "label": "C. Freeze the values as a dated snapshot",
                "what": (
                    "Leave the dataset as it is and treat it as a snapshot. Simplest and safest, but a stale "
                    "specification is a wrong specification the moment a manufacturer changes it."
                ),
                "effort": "none", "risk": "medium", "reversible": False,
            },
        ],
        "recommendation": (
            "A now, and B only once the corrections log in SG-13 exists, so an automated re-fetch can never "
            "silently overwrite a human decision."
        ),
        "why": (
            "The site's credibility rests on values being right on the day they were read, and it already says "
            "so on every page. What it does not yet do is warn when they stop being right. A stale-value report "
            "turns a slow, invisible risk into a visible one, and it reuses the read-date discipline the "
            "dataset already carries rather than adding a new process."
        ),
        "impact": 4, "confidence": 4, "effort": "M",
        "risk_of_not_doing": (
            "Medium. The failure is slow and invisible: a manufacturer revises a specification, the site keeps "
            "publishing the old one, and the first person to notice is a reader."
        ),
        "blocks": [], "blocked_by": [],
    },
    {
        "id": "SG-20",
        "title": "Decide the product set before the next content push",
        "area": "Catalogue",
        "problem": (
            "The site covers three air fryers, two of them from the same brand and two of them in the same "
            "form factor, so the comparison a reader can make here today is narrow. The category is much wider "
            "than that: the Amazon listing pages the site's own links open carry Amazon's own related-listing "
            "carousels, and those name the competing French-door ovens and dual-basket fryers a shopper in this "
            "niche is actually choosing between - each with a manufacturer's product page and manual that this "
            "project already knows how to verify to the standard the site holds. Adding the direct competitors "
            "is the largest single lever on both organic traffic and commission, and also the largest block of "
            "new verification work."
        ),
        "evidence": [
            {"label": "Amazon listing for B09B7SB46R - related-listing carousel naming competing French-door ovens",
             "url": LIST_EMERIL},
            {"label": "Amazon listing for B0CDY277D3 - related-listing carousel naming competing dual-basket fryers",
             "url": LIST_6QT},
        ],
        "options": [
            {
                "label": "A. Add the competing listings the site's own Amazon pages already name",
                "what": (
                    "Take each carousel entry that is a genuine competitor for the same buyer - not a sponsored "
                    "slot - and bring it to the same standard as the three current products: manufacturer page, "
                    "owner's manual, verified dataset rows, and a sourced line in the comparison matrix."
                ),
                "effort": "L", "risk": "low", "reversible": True,
            },
            {
                "label": "B. Keep three products and widen by format instead",
                "what": (
                    "Add one product per form factor the site already explains, so the comparison is about air "
                    "fryer types rather than about these three particular units."
                ),
                "effort": "M", "risk": "low", "reversible": True,
            },
            {
                "label": "C. Stay at three products",
                "what": (
                    "The narrowest option and the cheapest to keep verified. It caps traffic at whatever a few "
                    "exact-match queries can bring."
                ),
                "effort": "none", "risk": "medium", "reversible": False,
            },
        ],
        "recommendation": (
            "A, but only after SG-01 settles which model each supplied link points to. Adding products to a "
            "catalogue whose existing entries are mis-identified multiplies the error instead of fixing it."
        ),
        "why": (
            "Organic traffic in this niche is won by covering the comparison a buyer is making, not by covering "
            "one product deeply. Two of the three current products share a brand and a form factor, so the set "
            "cannot answer the two questions its own articles say are most common: air fryer or oven, and which "
            "dual basket."
        ),
        "impact": 5, "confidence": 4, "effort": "L",
        "risk_of_not_doing": (
            "High. Every week spent deepening three pages is a week not spent on the pages a comparison search "
            "lands on."
        ),
        "blocks": [], "blocked_by": ["Q-01"],
    },
    {
        "id": "SG-21",
        "title": "Put the \"we could not confirm this\" markers on the money pages, not only on the register",
        "area": "Trust and conversion",
        "problem": (
            "The most distinctive thing this site does - refusing to guess, and publishing what it could not "
            "confirm - lives on a separate Flagged page that a reader has to go and find. On the buying guide "
            "that reads as thoroughness. On a product page, next to the price and the buy button, it would read "
            "as rigour, and it would answer the question a sceptical buyer actually has: why does this page not "
            "show the price, and why does it say the model is unconfirmed? The site's decision to show no "
            "price, no rating and no review count is correct under Program Policies sections 2(b) and 6(t), and "
            "it is also the thing most likely to look like an omission to a reader who never sees the reason."
        ),
        "evidence": [
            {"label": "16 CFR 465.6 - a company-controlled site must not misrepresent its reviews as independent",
             "url": CFR_465},
            {"label": "Program Policies 2(b) - when prices and availability may be shown",
             "url": POLICIES},
        ],
        "options": [
            {
                "label": "A. Put an inline marker next to each unconfirmed value on the product pages",
                "what": (
                    "Where a specification row is blank or in conflict, show a short marker in place - \"not "
                    "confirmed by the manufacturer\" - that links to the register row and its source. The value "
                    "stays blank; the reason becomes visible exactly where the reader is looking."
                ),
                "effort": "M", "risk": "low", "reversible": True,
            },
            {
                "label": "B. Add a short trust strip under each buy button",
                "what": (
                    "One line plus a link: what this page is based on, what was not tested, and where the open "
                    "items are. Cheaper than A and it does the same job for most readers."
                ),
                "effort": "S", "risk": "low", "reversible": True,
            },
            {
                "label": "C. Leave the register where it is",
                "what": (
                    "Keeps the buying pages clean. The cost is that the site's best differentiator is invisible "
                    "to exactly the reader who needs it most."
                ),
                "effort": "none", "risk": "low", "reversible": True,
            },
        ],
        "recommendation": "B first, then A on the product pages once the wording is settled.",
        "why": (
            "The reason a document-based site converts at all is that it is visibly different from a site that "
            "invents a star rating. Right now the evidence of that difference sits three clicks away. This is the "
            "cheapest conversion improvement available, and it needs no new facts - only the reasons already "
            "published on the flag page, moved next to the values they qualify."
        ),
        "impact": 4, "confidence": 4, "effort": "S",
        "risk_of_not_doing": (
            "Medium. Nothing breaks and no rule is breached; the site simply fails to get credit for the thing "
            "it does better than a typical affiliate page."
        ),
        "blocks": [], "blocked_by": [],
    },
]

# --------------------------------------------------------------------------- #
# New questions
# --------------------------------------------------------------------------- #

NEW_QUESTIONS = [
    {
        "id": "Q-15",
        "group": "Economics",
        "question": "What commission rate does Amazon's published table give for kitchen appliances, and does that rate apply to these three listings?",
        "state": "known",
        "why_it_matters": (
            "The rate is the single number that converts traffic into money, and it is the number an affiliate "
            "page most often asserts without checking. Kitchen pays 4.50% and the fallback row pays 4.00%, so "
            "the difference between the two is worth roughly a twelfth of the modelled revenue."
        ),
        "answer": (
            "The published Table 1 row reads \"Physical Books, Kitchen, Automotive - 4.50%\". All three listings "
            "render the browse-node path \"Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air "
            "Fryers\", read directly on 2026-11-15 by following the three supplied short links, so 4.50% is the "
            "well-evidenced working rate. The one thing still missing is the category Amazon applies when it "
            "settles a commission: that name appears only on a shipped line in the Associates Earnings report. "
            "Until one exists, the site publishes both candidate rows and labels which is which."
        ),
        "what_we_know": [
            "The published Table 1 lists Physical Books, Kitchen and Automotive at 4.50%, and All Other Categories at 4.00%.",
            "Amazon does not publish an ASIN-to-category mapping, which is why the site shows both candidate rows.",
            "All three listings display the same breadcrumb: Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers.",
            "Re-read 2026-11-15: the breadcrumb was read directly on all three ASINs - B0CDY277D3, B09B7SB46R and B08DKYBTPH - not only on the Emeril listing, which was the limit of the earlier observation recorded in the annex register's F-06.",
        ],
        "what_is_missing": (
            "Confirmation of the category Amazon applies at commission time. No public source states it for an "
            "ASIN; the Earnings report names it only on a shipped line."
        ),
        "how_to_discover": (
            "Associates Central > Reports > Earnings shows the category applied to each shipped item. Before any "
            "sale exists, the breadcrumb is the best available evidence and is recorded as evidence rather than "
            "as confirmation."
        ),
        "blocks": ["SG-10"],
        "sources": [
            {"label": "Standard Commission Income Statement, Table 1", "url": RATE_TABLE},
            {"label": "Chefman 6 Qt listing - browse-node path read 2026-11-15", "url": LIST_6QT},
            {"label": "Emeril 26 Qt listing - browse-node path read 2026-11-15", "url": LIST_EMERIL},
            {"label": "Chefman 8 Qt listing - browse-node path read 2026-11-15", "url": LIST_8QT},
        ],
    },
    {
        "id": "Q-16",
        "group": "Programme compliance",
        "question": "May this site display Amazon prices, star ratings or review counts?",
        "state": "known",
        "why_it_matters": (
            "These are the three fields a reader expects on an affiliate page and the three an Associate site "
            "usually cannot show. Getting this wrong is the fastest route to a policy breach, so the answer has "
            "to be a rule rather than a preference."
        ),
        "answer": (
            "No, unless the account holds Creators API or PA API access. Program Policies section 2(b) allows a "
            "site to show prices and availability only when Amazon serves the link or the data comes from "
            "Creators API or PA API; section 6(t) allows customer reviews and star ratings only when obtained "
            "through those same APIs. This build holds neither, so every Amazon price, rating and review count on "
            "the site is left blank and flagged. The one rating that does appear is each manufacturer's own "
            "review widget on the manufacturer's own page, shown with the date it was read - that is the "
            "brand's content, not Program Content, and it is not an Amazon rating."
        ),
        "what_we_know": [
            "Program Policies 2(b), read verbatim 2026-11-15: \"Product prices and availability may vary from time to time. ... your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API and you comply with the requirements regarding use of Creators API or PA API in the License.\"",
            "Program Policies 6(t), read verbatim 2026-11-15: \"You will not display or otherwise use any of our customer reviews or star ratings, in part or in whole, on your Site unless you have obtained a link to that customer review or star rating through Creators API or PA API and you comply with the requirements for Creators API and PA API described in the License.\"",
            "The build has an executable guard for this: a build check refuses to emit any price tracking or price alerting element, and the site carries no price or rating values at all.",
        ],
        "what_is_missing": (
            "Nothing about the rule itself - it is a settled reading of the current policy text. What is missing "
            "is whether the account will ever hold the API access that would unlock the display."
        ),
        "how_to_discover": (
            "Not applicable to the rule. If the account later obtains Creators API or PA API access, sections "
            "2(b) and 6(t) must be re-read against that API's own licence terms before any value is displayed."
        ),
        "blocks": ["SG-06"],
        "sources": [
            {"label": "Associates Program Policies - Participation Requirements 2(b) and 6(t)", "url": POLICIES},
        ],
    },
    {
        "id": "Q-17",
        "group": "Evidence base",
        "question": "What is this site's product coverage actually based on?",
        "state": "known",
        "why_it_matters": (
            "A reader who assumes the site tested these appliances will read its comparisons wrongly, and 16 CFR "
            "465.6 makes it deceptive for a business to misrepresent a site it controls as providing independent "
            "review. The basis of the coverage therefore has to be stated plainly, not implied."
        ),
        "answer": (
            "Manufacturer documentation only. Every specification on this site comes from the manufacturer's own "
            "product page or the owner's manual for that exact model, read on the date recorded alongside it. "
            "No appliance was bought, unboxed, cooked in, weighed or photographed, so no page here claims a "
            "cooking result, a measured time, a noise level or a hands-on comparison. The three product pages "
            "are document reviews and say so in their titles and their ledes; the articles carry the same "
            "statement at the top. Where the official record contradicts itself - the 8-quart 450 F ceiling, the "
            "Emeril preset count - the site publishes the conflict instead of resolving it by guesswork."
        ),
        "what_we_know": [
            "Every populated specification row in data/products.json names at least one official source, and build.py fails the build if a row carries a value with no source.",
            "All three owner's manuals were read end to end on 2026-11-15 and every value attributed to them was found in them.",
            "The site's own footer, every article header and the three product pages each state that nothing was tested.",
        ],
        "what_is_missing": (
            "Nothing about the coverage. What the site cannot answer is how any of these machines actually cooks, "
            "because nobody here has used one - and that gap is the honest limit of every comparison on the site."
        ),
        "how_to_discover": (
            "Only by buying and testing each unit and recording the test. The conflicts that a reader is most "
            "likely to hit - which Chefman 8-quart model the listing actually is, what the Emeril's preset count "
            "really says - can only be settled by reading the model plate on the unit, or by the owner's own test."
        ),
        "blocks": ["SG-15"],
        "sources": [
            {"label": "Chefman RJ38-SQPF-3TDB-2W owner's manual - the 6 Qt document source", "url": MANUAL_6QT},
            {"label": "Chefman RJ38-SQSS-8T owner's manual - the 8 Qt document source", "url": MANUAL_8QT},
            {"label": "Emeril FAFO-001 owner's manual - the 26 Qt document source", "url": MANUAL_EMERIL},
            {"label": "16 CFR 465.6 - company-controlled review sites", "url": CFR_465},
        ],
    },
    {
        "id": "Q-18",
        "group": "Platform and compliance",
        "question": "Can the brief's AI agent read and analyse Amazon's own product data?",
        "state": "known",
        "why_it_matters": (
            "The brief's central instruction is to build an AI platform that \"automates product research, "
            "identifies trending and high-converting products, analyses pricing, reviews, competition and "
            "commission potential\". If that platform is designed to read Amazon listing content, the design is "
            "either unlawful under the licence or needs written approval, and the difference decides the whole "
            "architecture."
        ),
        "answer": (
            "Not under the standard licence, and this project does not attempt it. IP License section 1 says "
            "Amazon \"will not allow any third party to use Program Content to, directly or indirectly, develop "
            "or improve large language or multimodal models, machine learning models or related technology\". "
            "Section 2(e) forbids accessing Creators API, PA API or Data Feeds \"for the purpose of aggregating, "
            "analyzing, extracting, or repurposing any Product Advertising Content ... or in the direct training "
            "or fine-tuning of a machine learning and/or foundational model\" without Amazon's express prior "
            "written approval. Listing titles, prices, ratings and review counts are Program Content. The "
            "automation that remains available is exactly what this repository already does: read manufacturers' "
            "own published pages, hold a verified dataset, and generate prose that may only state values present "
            "in that dataset. That is a design constraint on the platform, not an open question."
        ),
        "what_we_know": [
            "IP License section 1, read verbatim 2026-11-15: \"This license does not include any downloading, copying or other use of Program Content for the benefit of any third party, or any use of data mining, robots, or similar data gathering and extraction tools.\"",
            "IP License section 1, final paragraph, read verbatim 2026-11-15: \"will not allow any third party to, use Program Content to, directly or indirectly, develop or improve large language or multimodal models, machine learning models or related technology.\"",
            "IP License section 2(e), read verbatim 2026-11-15: \"You will not, without our express prior written approval, access or use Creators API, PA API or Data Feeds for the purpose of aggregating, analyzing, extracting, or repurposing any Product Advertising Content or in connection with any software or other application intended for use by persons or entities that offer products on an Amazon Site, or in the direct training or fine-tuning of a machine learning and/or foundational model.\"",
            "The repository already runs its automation on first-party and manufacturer data only; flag F8 records the same constraint as a platform guardrail.",
        ],
        "what_is_missing": (
            "Nothing in the rule. What is missing is Amazon's prior written approval, which section 2(e) names "
            "as the only route to the restricted use and which does not exist today."
        ),
        "how_to_discover": (
            "Only Amazon can grant it. Until approval exists in writing, the constraint stands and the platform "
            "must run on manufacturer and first-party data."
        ),
        "blocks": ["SG-18"],
        "sources": [
            {"label": "Associates Program IP License, sections 1 and 2(e)", "url": POLICIES},
        ],
    },
    {
        "id": "Q-19",
        "group": "Content operations",
        "question": "How often should this site's published values be re-read?",
        "state": "missing",
        "why_it_matters": (
            "The Associates application-review criteria recorded in this repository include a requirement that "
            "site content be recent, and that requirement governs whether a review of this site succeeds. The "
            "exact window was not re-read on 2026-11-15 (flag F46), so it must be confirmed before it is used as "
            "a schedule. Meanwhile the drift is demonstrably real: a manufacturer's own review counter moved "
            "within twenty-four hours."
        ),
        "what_we_know": [
            "Every rating figure the site publishes already carries its read date, and flag F19 records why.",
            "Re-read 2026-11-15: the Chefman 6 Qt counter still read 1,305 and the 8 Qt still read 716, unchanged from the 2026-11-14 read, while the averages held at 4.6.",
            "The 2026-11-15 pass re-read every manufacturer page and every owner's manual and found no published value to be wrong.",
        ],
        "what_is_missing": (
            "The recency criterion itself, read from the Application Review Process page rather than carried "
            "forward, and the owner's chosen refresh interval for each class of value."
        ),
        "how_to_discover": (
            "Re-read the Application Review Process page and record the exact wording with its date. Then set an "
            "interval per value class and let the build report anything past it - which is SG-18."
        ),
        "blocks": ["SG-19"],
        "sources": [
            {"label": "Application Review Process - content recency criterion (not re-read 2026-11-15; see flag F46)",
             "url": APP_REVIEW},
            {"label": "Chefman 6 Qt brand page - review count at the 2026-11-15 read", "url": CHEFMAN_6QT},
        ],
    },
    {
        "id": "Q-20",
        "group": "Site ownership",
        "question": "Which country and marketplace is this site actually promoting, and who states it?",
        "state": "missing",
        "why_it_matters": (
            "All three supplied links resolve to amazon.com, the US marketplace. Whether the operator can hold a "
            "US Associates account, and on what terms, is not a detail: it decides the tax form, the payment "
            "method, the disclosure wording and which marketplace's commission table applies. The repository "
            "currently holds two different statements about where the operator is - Japan in the 2026-11-15 pages "
            "and Norway in the s2 annex register - and neither came from the operator (flag F42)."
        ),
        "what_we_know": [
            "All three supplied link.amazon short links resolve to amazon.com, the US marketplace, and all three listings sit under the same US browse-node path.",
            "Participation Requirements 1, read verbatim 2026-11-15: \"If you are a non-US person participating in the Associates Program, you agree that unless you have otherwise notified us in your tax information you will perform all services under the Agreement outside the United States.\"",
            "The commission table the site publishes is the US Standard Commission Income Statement.",
        ],
        "what_is_missing": (
            "The operator's actual country of residence, stated once by the operator, and the marketplace the site "
            "is intended to promote. The two statements already in the repository are agent-session observations, "
            "not owner statements."
        ),
        "how_to_discover": (
            "The owner states their country once, one register row cites it, and the other wording is corrected to "
            "match. The Associates application itself, which asks for tax information and a bank account, is the "
            "authority on whether a non-US applicant is accepted."
        ),
        "blocks": [],
        "sources": [
            {"label": "Associates Program Policies - Participation Requirements 1 (enrollment and eligibility)",
             "url": POLICIES},
            {"label": "Standard Commission Income Statement (US)", "url": RATE_TABLE},
        ],
    },
]


def main():
    # ---- suggestions -------------------------------------------------------
    s = load(SUG)
    have = {x["id"] for x in s["suggestions"]}
    for row in NEW_SUGGESTIONS:
        if row["id"] in have:
            print(f"{row['id']}: already present, not duplicated")
            continue
        s["suggestions"].append(collections.OrderedDict(row))
        print(f"{row['id']}: added")
    s["version"] = "1.1"
    s["pass"] = "Verification pass 9 (arena/42ca97ad-zone1), extended from integration pass 8"
    s["compiled"] = "2026-11-15"
    save(SUG, s)

    # ---- questions ---------------------------------------------------------
    q = load(Q)
    have = {x["id"] for x in q["questions"]}
    for row in NEW_QUESTIONS:
        if row["id"] in have:
            print(f"{row['id']}: already present, not duplicated")
            continue
        q["questions"].append(collections.OrderedDict(row))
        print(f"{row['id']}: added")
    q["version"] = "1.1"
    q["compiled"] = "2026-11-15"
    # Idempotent: append the note only if it is not already there.
    _ADD = ("Questions in the 'known and sourced' state carry their answer on the row: an "
            "official source already settles them, and the answer is what the source says. "
            "Every other row states plainly that no answer is published, and names the step "
            "that would produce one.")
    if _ADD not in q["preamble"]:
        q["preamble"] = q["preamble"] + " " + _ADD
    save(Q, q)


if __name__ == "__main__":
    main()
