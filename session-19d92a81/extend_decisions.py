#!/usr/bin/env python3
"""Session arena/19d92a81 — content extension, part 2: suggestions + questions.

Adds eight reviewable suggestions (SG-23..SG-30) with a new decision path (P5),
and five open questions (Q-22..Q-26) with discovery steps. Nothing here is
implemented; the queue exists so the owner picks the path first.

Run from the repository root:  python3 session-19d92a81/extend_decisions.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

SITE = "https://kanlerxz87-cyber.github.io/Zone1"

new_suggestions = [
    {
        "id": "SG-23",
        "title": "Add production-method authorship to every buyer-facing page - and a named editor when there is one",
        "area": "Editorial trust",
        "problem": (
            "The buyer-facing pages carry disclosure and sourcing but no byline and no visible "
            "'how this is made' statement on the page a shopper actually lands on. A reader "
            "deciding whether to trust a purchase recommendation asks 'who wrote this?' before "
            "'is this sourced?'. Right now the honest answer is: an automated pipeline checked "
            "against manufacturer documents - which is defensible and should be stated where it "
            "will be read, not only in the article layer's help box."
        ),
        "evidence": [
            {"label": "FTC Disclosures 101 - endorsements must be disclosed clearly", "url": "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"},
            {"label": "Articles layer - 'How to read these articles' box (present, but one click away from money pages)", "url": SITE + "/articles/index.html"},
            {"label": "Question Q-09 (named author) - open", "url": SITE + "/questions.html#q-09"},
        ],
        "options": [
            {"label": "A. Name a human editor and publish an 'About our standards' page", "what": "One page describing who edits, how content is produced, how corrections work (SG-13), and the no-testing rule. Needs the owner to name a person.", "effort": "M", "risk": "none", "reversible": True},
            {"label": "B. Ship a production-method byline line now", "what": "A one-line byline on buyer-facing pages: 'Compiled from manufacturer documentation and official program policy by the Zone1 Kitchen desk. No hands-on testing is claimed.' No owner input required.", "effort": "S", "risk": "none", "reversible": True},
            {"label": "C. Status quo", "what": "Keep trust signals one click away in the article layer.", "effort": "0", "risk": "medium", "reversible": True},
        ],
        "recommendation": "B now; upgrade to A the moment Q-09 has an answer.",
        "why": (
            "A stated production method is the honest version of a byline and is publishable "
            "today; a named editor is better and cannot be invented. Doing B first means the "
            "claim on the page is always true, whatever Q-09 turns out to be."
        ),
        "impact": 4,
        "confidence": 4,
        "effort": "S",
        "risk_of_not_doing": "Medium. Anonymous recommendation pages read as automated content to readers and search quality raters alike, whatever their sourcing.",
        "blocks": ["SG-24"],
        "blocked_by": ["Q-09"],
    },
    {
        "id": "SG-24",
        "title": "Split the navigation into a shopping side and a project side",
        "area": "Site structure",
        "problem": (
            "The sidebar mixes buyer pages (picks, guides, articles, compare, products) with "
            "project pages (requirements, reverification, previous passes, platform, handover). "
            "Twenty-plus links in five groups is a dashboard for the owner, not a shop for the "
            "reader. It is the single most 'internal tool' thing a visitor sees, and the brief "
            "asks for a polished marketing affiliate site."
        ),
        "evidence": [
            {"label": "build.py sidebar groups (Start here / Products / Decide / Evidence / Platform / Archive)", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/build.py"},
            {"label": "Suggestion SG-04 (landing page around a buyer's question) - same problem at page level", "url": SITE + "/suggestions.html#sg-04"},
            {"label": "Suggestion SG-21 (uncertainty markers on money pages) - the counterweight to hiding evidence", "url": SITE + "/suggestions.html#sg-21"},
        ],
        "options": [
            {"label": "A. Two-audience nav: 'Shop' and 'Project'", "what": "Shop: picks, buying guide, articles, compare, products. Project: executive summary, suggestions, questions, evidence registers, flagged, platform. One shared top-level entry point each.", "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. Buyer-first nav with a single 'How we work' link", "what": "Everything buyer-facing in the sidebar; the whole evidence layer behind one link to an index page.", "effort": "S", "risk": "medium", "reversible": True},
            {"label": "C. Status quo", "what": "Keep the honest, owner-shaped dashboard.", "effort": "0", "risk": "low", "reversible": True},
        ],
        "recommendation": "A.",
        "why": (
            "A keeps the evidence layer one click away - which SG-21 argued for - while giving "
            "the reader a sidebar that answers their questions instead of the project's. The "
            "change is confined to the nav renderer; no page content changes."
        ),
        "impact": 4,
        "confidence": 4,
        "effort": "M",
        "risk_of_not_doing": "Medium. Every visitor who bounces from a five-group sidebar is a reader the verification work never reached.",
        "blocks": [],
        "blocked_by": [],
    },
    {
        "id": "SG-25",
        "title": "Approve a seasonal content calendar so trend pieces ship before the season, not during it",
        "area": "Content and traffic",
        "problem": (
            "The three seasonal pieces (model-number switch, gift guide, cleaning guide) shipped "
            "in the middle of the season they target. Seasonal pages earn links and rankings when "
            "they already exist when searchers arrive; the work has to precede the retail moment "
            "by four to six weeks."
        ),
        "evidence": [
            {"label": "Topic register (data/topics.json on GitHub)", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/topics.json"},
            {"label": "Topic queue TP-15..TP-19 (three published mid-season, two proposed)", "url": SITE + "/topics.html"},
            {"label": "Black Friday piece (published 2026-11-16)", "url": SITE + "/articles/black-friday-model-number-switch.html"},
            {"label": "Topics demand note - demand is argued, not measured", "url": SITE + "/topics.html"},
        ],
        "options": [
            {"label": "A. Quarterly calendar with owner sign-off six weeks ahead", "what": "Four slots a year (winter gifting, spring reset, Prime Day, back-to-school), each with a draft deadline and a one-line approval.", "effort": "S", "risk": "none", "reversible": True},
            {"label": "B. Ship-as-written, no calendar", "what": "Keep publishing when a pass produces content.", "effort": "0", "risk": "medium", "reversible": True},
            {"label": "C. Pause seasonal content until the Associates tag is live", "what": "Seasonal pages earn nothing measurable before monetization works anyway.", "effort": "0", "risk": "medium", "reversible": True},
        ],
        "recommendation": "A, with the first slot being January (TP-18) so the calendar starts with something already researched.",
        "why": (
            "The content pipeline is already proven; what is missing is timing and a one-line "
            "approval. A calendar is the cheapest lever this site has on traffic, and Q-24 is a "
            "one-message question."
        ),
        "impact": 4,
        "confidence": 3,
        "effort": "S",
        "risk_of_not_doing": "Medium. A gift guide published inside the gift season catches the tail of the searches and misses the link-building window entirely.",
        "blocks": [],
        "blocked_by": ["Q-24"],
    },
    {
        "id": "SG-26",
        "title": "Decide the image policy before any picture appears on the site",
        "area": "Design and compliance",
        "problem": (
            "Real affiliate sites carry product imagery; this one carries none, and 'add images' "
            "will be the most obvious design suggestion anyone makes. It is also the most likely "
            "compliance trap: AI-generated product pictures misrepresent the product they sell "
            "(the same deception rule that bans fake test claims), hotlinked retailer images "
            "breach terms, and Amazon's IP license covers only approved uses of Amazon Content."
        ),
        "evidence": [
            {"label": "Operating Agreement - IP License and permitted Amazon Content use", "url": "https://affiliate-program.amazon.com/help/operating/agreement"},
            {"label": "FTC Disclosures 101 - material connections and honest representation", "url": "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"},
            {"label": "Design prompt pack - D-rows on imagery", "url": SITE + "/design-prompt.html"},
        ],
        "options": [
            {"label": "A. Stay typographic on purpose, and say so", "what": "No product imagery until image rights are settled; the design leans on type, tables and spacing (the current direction).", "effort": "0", "risk": "none", "reversible": True},
            {"label": "B. Licensed Amazon imagery via SiteStripe or the API", "what": "Only once Q-25 answers and only under the license terms; images then come with the listing's own context.", "effort": "M", "risk": "low", "reversible": True},
            {"label": "C. Original photography or illustration", "what": "Expensive, slow, but fully owned; needs the physical products.", "effort": "L", "risk": "none", "reversible": True},
        ],
        "recommendation": "A now; B when Q-25 and Q-05 are answered. Never AI-generated product imagery.",
        "why": (
            "A is already built and is a defensible editorial position ('we link to the source, "
            "we do not dress it up'). B is the growth move once rights exist. AI product imagery "
            "would undo the trust the whole verification layer is built to earn."
        ),
        "impact": 3,
        "confidence": 4,
        "effort": "S",
        "risk_of_not_doing": "High if imagery arrives without a policy - one hotlinked or generated product photo is a policy breach and a trust breach at once.",
        "blocks": [],
        "blocked_by": ["Q-25"],
    },
    {
        "id": "SG-27",
        "title": "Pick one brand name for reader-facing surfaces, and label the annexes as annexes",
        "area": "Brand",
        "problem": (
            "One origin publishes at least three names: 'Zone1 Kitchen' at the root, 'Zone1 - "
            "Amazon Associates platform' under /s2, and 'Zone1 - verified Amazon affiliate "
            "product intelligence' in the README. F44 already records the parallel-builds "
            "problem; this is the naming half of it. Readers and search engines see three brands "
            "in one place."
        ),
        "evidence": [
            {"label": "Root site titles and organization schema", "url": SITE + "/"},
            {"label": "s2 annex header", "url": SITE + "/s2/"},
            {"label": "Flagged register F44 (same site published many times)", "url": SITE + "/flagged.html"},
        ],
        "options": [
            {"label": "A. Ratify 'Zone1 Kitchen' for readers; mark /s2 and other builds as internal annexes in their headers", "what": "One-line header changes; no content moves.", "effort": "S", "risk": "none", "reversible": True},
            {"label": "B. Rename the root to the platform name", "what": "Aligns with the project title but reads less like a publication.", "effort": "M", "risk": "medium", "reversible": True},
            {"label": "C. Decide the domain first (Q-07), then rename once", "what": "Avoids renaming twice.", "effort": "0", "risk": "medium", "reversible": True},
        ],
        "recommendation": "A now (it is reversible and cheap), C when the domain question lands.",
        "why": (
            "Brand consistency is the cheapest trust signal on the list, and A is true today: "
            "the annexes ARE internal builds kept for evidence."
        ),
        "impact": 3,
        "confidence": 4,
        "effort": "S",
        "risk_of_not_doing": "Medium. Fragmented branding undercuts direct traffic and makes the site look assembled rather than published.",
        "blocks": [],
        "blocked_by": ["Q-07", "Q-23"],
    },
    {
        "id": "SG-28",
        "title": "Re-plan the automation platform around the Creators API, not PA-API 5",
        "area": "Platform and automation",
        "problem": (
            "The automation blueprint plans around PA-API 5 for product research, price and "
            "availability data. Amazon has published a PA-API 5 deprecation notice pointing at "
            "the Creators API. Building the pipeline on a deprecated interface wastes the work "
            "and strands the data contracts."
        ),
        "evidence": [
            {"label": "PA-API 5 Deprecation Notice (official)", "url": "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation"},
            {"label": "New Product Advertising API registration topic (official)", "url": "https://affiliate-program.amazon.com/help/node/topic/GBRCD467W33NMWLD"},
            {"label": "Platform blueprint page", "url": SITE + "/platform.html"},
        ],
        "options": [
            {"label": "A. Re-point the pipeline at the Creators API and keep the data contracts", "what": "The research/verify/publish stages are API-agnostic; only the acquisition layer changes.", "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. Freeze automation until the account has API access", "what": "No code against an interface the account cannot call.", "effort": "0", "risk": "none", "reversible": True},
            {"label": "C. Keep the PA-API 5 assumptions", "what": "Fastest now, stranded later.", "effort": "0", "risk": "high", "reversible": False},
        ],
        "recommendation": "B immediately (nothing to build against), then A as soon as Q-05 and Q-26 answer.",
        "why": (
            "The deprecation notice is official and unambiguous. The pipeline's value is in its "
            "verification stages, which survive the swap; only the data-acquisition layer is at "
            "risk, and freezing it costs nothing."
        ),
        "impact": 4,
        "confidence": 5,
        "effort": "M",
        "risk_of_not_doing": "High for the automation roadmap: every hour spent on a deprecated API is an hour owed to the replacement.",
        "blocks": [],
        "blocked_by": ["Q-05", "Q-26"],
    },
    {
        "id": "SG-29",
        "title": "Start one owned audience channel before the algorithm owns all the traffic",
        "area": "Traffic",
        "problem": (
            "Organic search is the only channel on the plan and it is currently zero - no "
            "analytics, no Search Console verification, no inbound links. The whole business "
            "sits on one unowned channel. An owned channel (a feed, then a newsletter) is the "
            "standard hedge and needs no tracking to start."
        ),
        "evidence": [
            {"label": "Requirements register B-07/E-03 (data/requirements.json on GitHub)", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/requirements.json"},
            {"label": "Requirements register - traffic rows B-07 / E-03 (not delivered)", "url": SITE + "/requirements.html"},
            {"label": "Topics channel rows CH-1..CH-5 with their constraints", "url": SITE + "/topics.html"},
            {"label": "Question Q-08 (what may this site measure)", "url": SITE + "/questions.html#q-08"},
        ],
        "options": [
            {"label": "A. Email newsletter", "what": "Highest leverage, needs owner tooling, a sender identity, and consent design.", "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. RSS/Atom feed surfaced prominently, zero data collection", "what": "The channel exists the day the link is added; no privacy questions at all.", "effort": "S", "risk": "none", "reversible": True},
            {"label": "C. None yet", "what": "Stay search-only until traffic exists.", "effort": "0", "risk": "medium", "reversible": True},
        ],
        "recommendation": "B now, A when there is an owner to run it.",
        "why": (
            "B is a link and a feed file - it cannot breach the privacy disclosure because it "
            "collects nothing - and it gives the seasonal calendar (SG-25) somewhere to publish "
            "to while search traction builds."
        ),
        "impact": 3,
        "confidence": 3,
        "effort": "S",
        "risk_of_not_doing": "Medium over a year: single-channel sites live and die with one ranking update.",
        "blocks": [],
        "blocked_by": ["Q-08"],
    },
    {
        "id": "SG-30",
        "title": "Turn the article set into four deliberate clusters with one hub each",
        "area": "Content and traffic",
        "problem": (
            "Eighteen articles now carry target queries (as of 2026-11-16) but there is no "
            "cluster map: internal linking is whatever a reader happens to click. Small sites "
            "rank for competitive commercial queries by owning a cluster completely, not by "
            "publishing one page per idea."
        ),
        "evidence": [
            {"label": "Article set with declared target queries", "url": SITE + "/articles/index.html"},
            {"label": "Suggestion SG-09 (turn the articles into a cluster) - written when the set was smaller", "url": SITE + "/suggestions.html#sg-09"},
            {"label": "Google spam policies - scaled content abuse (the failure mode a cluster map avoids)", "url": "https://developers.google.com/search/docs/essentials/spam-policies"},
        ],
        "options": [
            {"label": "A. Four clusters with hubs and deliberate cross-links", "what": "Format choice (compare + capacity + dimensions), care (cleaning + aerosol + cords), deal safety (model switch + presets + prices), spec literacy (spec sheets + 450F + energy). Each hub links down; each article links up and across.", "effort": "M", "risk": "low", "reversible": True},
            {"label": "B. One 'start here' hub only", "what": "Cheaper, captures most of the navigation benefit.", "effort": "S", "risk": "none", "reversible": True},
            {"label": "C. Keep the flat list", "what": "Status quo.", "effort": "0", "risk": "low", "reversible": True},
        ],
        "recommendation": "A, built in the generator so the links cannot rot.",
        "why": (
            "The articles are already written around four themes; the map is the missing half. "
            "Generator-built links stay true as the set grows, unlike hand-placed ones."
        ),
        "impact": 4,
        "confidence": 3,
        "effort": "M",
        "risk_of_not_doing": "Low now, compounding: every article added without a map makes the next one worth less.",
        "blocks": [],
        "blocked_by": [],
    },
]

new_path = {
    "id": "P5",
    "name": "Make it read like a publication",
    "promise": "The reader-facing polish path: authorship, navigation, brand, imagery, seasons, and clusters - the changes that make the site feel published rather than generated.",
    "contains": ["SG-23", "SG-24", "SG-25", "SG-26", "SG-27", "SG-28", "SG-29", "SG-30"],
    "effort": "M (mostly small changes in the generator and the nav; the calendar and brand rows need one owner decision each)",
    "must_be_true_first": "P1's safety rows (SG-01, SG-02, SG-07, SG-11) should be settled, because polish on top of an unconfirmed product identity polishes the wrong thing. Nothing else blocks this path.",
    "delivers": "A site a reader can trust at a glance (bylines, one brand, a shopping-shaped nav), a seasonal content rhythm that ships before the moment, a cluster map the generator maintains, and an automation plan pointed at a live API. These are exactly the changes the brief's 'polished marketing affiliate website, not AI slop' ask describes.",
    "does_not_fix": "It does not settle product identity (Q-01/Q-02), the Associates tag (Q-04), or the domain (Q-07) - those remain owner decisions the polish cannot make.",
    "pick_this_if": "You want the site to win readers while the account questions are still open, and you are willing to answer two one-message questions (Q-23 brand, Q-24 cadence) to unblock it.",
    "why_first": "Not first - parallel. Unlike P1, nothing here can make the site wrong; it can only make it more or less convincing. It can run alongside any other path.",
}

new_questions = [
    {
        "id": "Q-22",
        "group": "Governance",
        "question": "Who signs off on the suggestion queue, and on what cadence?",
        "state": "unknowable",
        "why_it_matters": (
            "The suggestions page exists so a human picks the path before anything is built. "
            "Without a named decider and a cadence, it is a backlog - and each pass that adds "
            "well-argued rows makes the backlog longer, not the decisions better."
        ),
        "what_we_know": [
            "Every row on the suggestions page is explicitly unimplemented and carries options, a recommendation, effort and risk.",
            "Several earlier flags were dispositioned as 'the owner's call' (for example F59), which is this same gap surfacing elsewhere.",
            "Decision path P5 (session arena/19d92a81) groups the reader-facing polish suggestions so one 'yes' covers eight rows.",
        ],
        "what_is_missing": "A named decider, a review cadence, and what 'approved' means - approved to build, or approved to test?",
        "how_to_discover": (
            "One message from the owner: a cadence (for example '30 minutes monthly, I mark each "
            "row approve/reject/defer') and what approval means. The page can render an "
            "approval-state column as soon as the data carries it."
        ),
        "blocks": ["SG-23", "SG-24", "SG-25", "SG-26", "SG-27", "SG-28", "SG-29", "SG-30"],
        "sources": [
            {"label": "Suggestions register (data/suggestions.json on GitHub)", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/suggestions.json"},
            {"label": "Suggestions page - the decision queue", "url": SITE + "/suggestions.html"},
            {"label": "Flagged register - rows dispositioned to the owner", "url": SITE + "/flagged.html"},
        ],
    },
    {
        "id": "Q-23",
        "group": "Brand",
        "question": "Is 'Zone1 Kitchen' the final brand name for this site?",
        "state": "missing",
        "why_it_matters": (
            "One origin currently publishes at least three names (root, /s2 annex, README). "
            "Titles, structured data and share cards all carry a name; search engines and "
            "readers treat it as a promise about who published the page."
        ),
        "what_we_know": [
            "The root site's titles and organization schema use 'Zone1 Kitchen' with the tagline 'Air-fryer decisions, backed by sources'.",
            "The /s2 annex publishes under 'Zone1 - Amazon Associates platform'.",
            "The README titles the project 'Zone1 - verified Amazon affiliate product intelligence'.",
        ],
        "what_is_missing": "The owner's decision on the one name reader-facing surfaces should carry.",
        "how_to_discover": "The owner states the name in one line; a single commit then aligns titles, og tags, the annex header and the README. SG-27 carries the implementation options.",
        "blocks": ["SG-27"],
        "sources": [
            {"label": "Root site (titles, schema)", "url": SITE + "/"},
            {"label": "s2 annex header", "url": SITE + "/s2/"},
            {"label": "README", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/README.md"},
        ],
    },
    {
        "id": "Q-24",
        "group": "Content operations",
        "question": "What is the publishing cadence, and who approves seasonal content before it ships?",
        "state": "unknowable",
        "why_it_matters": (
            "Seasonal pages only earn their traffic if they exist four to six weeks before the "
            "retail moment. Without a cadence and a one-line approval, every seasonal piece will "
            "keep shipping mid-season, like the first three did."
        ),
        "what_we_know": [
            "The topics page carries a proposed queue with per-row status (TP-15..TP-17 published 2026-11-16, TP-18/TP-19 proposed and gated on the marketplace question Q-20).",
            "The content pipeline (research, draft, claim-check, publish) is proven by eighteen generated articles.",
        ],
        "what_is_missing": "A calendar, a sign-off owner, and a lead time. SG-25 assumes four to six weeks and offers three cadence options.",
        "how_to_discover": "One message from the owner: 'ship seasonal pieces on the calendar without asking' or 'review each draft first', plus any blackout dates. The answer sets the lead time in the calendar.",
        "blocks": ["SG-25"],
        "sources": [
            {"label": "Topic register (data/topics.json on GitHub)", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/topics.json"},
            {"label": "Topics and traffic plan", "url": SITE + "/topics.html"},
            {"label": "Articles index", "url": SITE + "/articles/index.html"},
        ],
    },
    {
        "id": "Q-25",
        "group": "Imagery and IP",
        "question": "May the site use Amazon product images, and under what terms?",
        "state": "unknowable",
        "why_it_matters": (
            "Product imagery is the most requested design upgrade and the most likely "
            "compliance trap. The Operating Agreement licenses Amazon Content only for "
            "approved uses; hotlinking or generating look-alike product photos is not that."
        ),
        "what_we_know": [
            "The Operating Agreement contains an IP License governing use of Amazon Content in connection with properly formatted Special Links.",
            "Program Policies restrict price and rating display to Amazon-served links or official API data (section 2(b) and section 6(t) as cited on the compliance page).",
            "The site publishes no imagery today, deliberately - see SG-26.",
        ],
        "what_is_missing": "Whether the account is approved, whether SiteStripe image sourcing is enabled for it, and which image sources the owner wants used.",
        "how_to_discover": "Associates Central, SiteStripe settings and the IP License section of the Operating Agreement - five minutes once the account is accessible. Record the answer on SG-26.",
        "blocks": ["SG-26"],
        "sources": [
            {"label": "Associates Program Operating Agreement (IP License)", "url": "https://affiliate-program.amazon.com/help/operating/agreement"},
            {"label": "Associates Program Policies (2(b), 6(t))", "url": "https://affiliate-program.amazon.com/help/operating/policies"},
        ],
    },
    {
        "id": "Q-26",
        "group": "Automation",
        "question": "Which API will the automation platform call, now that PA-API 5 has a deprecation notice?",
        "state": "missing",
        "why_it_matters": (
            "The brief's platform automates product research, pricing and availability - all of "
            "which depend on an official data interface. Amazon has published a PA-API 5 "
            "deprecation notice; planning the pipeline against a deprecated interface strands "
            "the work."
        ),
        "what_we_know": [
            "Amazon publishes a PA-API 5 Deprecation Notice and a Product Advertising API registration topic (both linked on this row).",
            "The platform blueprint's verification stages are API-agnostic; only the acquisition layer is interface-specific (SG-28).",
        ],
        "what_is_missing": "The replacement interface's eligibility terms, rate limits and timeline as they apply to this account - and which interface the owner wants the platform built against.",
        "how_to_discover": "Read the deprecation notice's replacement guidance (linked), check the account's eligibility for the successor API, then record the decision in data/platform.json and update the blueprint page.",
        "blocks": ["SG-28"],
        "sources": [
            {"label": "PA-API 5 Deprecation Notice (official)", "url": "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation"},
            {"label": "New Product Advertising API registration (official)", "url": "https://affiliate-program.amazon.com/help/node/topic/GBRCD467W33NMWLD"},
        ],
    },
]


def main():
    s = json.load(open(DATA / "suggestions.json"))
    have = {x["id"] for x in s["suggestions"]}
    for sg in new_suggestions:
        assert sg["id"] not in have, sg["id"]
        s["suggestions"].append(sg)
    have_p = {x["id"] for x in s["paths"]}
    assert new_path["id"] not in have_p
    s["paths"].append(new_path)
    s["compiled"] = "2026-11-16"
    s["pass"] = (
        "Verification pass 9 (arena/42ca97ad-zone1), extended from integration pass 8; "
        "marketing and decision-support extension SG-23..SG-30 + path P5 by session "
        "arena/19d92a81 (2026-11-16)"
    )
    s["paths_note"] = (
        s["paths_note"].rstrip()
        + " P5 is independent: it is the reader-facing polish path and can run in parallel "
        "with any of the four above."
    )
    (DATA / "suggestions.json").write_text(
        json.dumps(s, indent=1, ensure_ascii=False) + "\n")

    q = json.load(open(DATA / "questions.json"))
    have_q = {x["id"] for x in q["questions"]}
    for item in new_questions:
        assert item["id"] not in have_q, item["id"]
        q["questions"].append(item)
    q["compiled"] = "2026-11-16"
    (DATA / "questions.json").write_text(
        json.dumps(q, indent=1, ensure_ascii=False) + "\n")

    print("suggestions:", len(s["suggestions"]), "paths:", len(s["paths"]),
          "questions:", len(q["questions"]))


if __name__ == "__main__":
    main()
