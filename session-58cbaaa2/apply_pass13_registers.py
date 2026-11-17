#!/usr/bin/env python3
"""pass-13 register updates (arena/58cbaaa2-zone1, 2026-11-17).

Adds the decision rows the two new submitted links and the selected tracking ID create:
suggestions SG-36…SG-40 + path P6, questions Q-27…Q-31, topics TP-21/TP-22, and four
requirements rows. Same anchors-as-contract rule as the build patch: any ambiguous anchor
aborts the run before a byte is written.
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/user/Zone1")


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def save(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


problems = []

# --------------------------------------------------------------- suggestions.json
sug = load("data/suggestions.json")
if any(s["id"] in {"SG-36", "SG-37", "SG-38", "SG-39", "SG-40"} for s in sug["suggestions"]):
    sys.exit("suggestions SG-36..40 already present — another session got here first; aborting")

SITE = "https://kanlerxz87-cyber.github.io/Zone1"
POLICIES = "https://affiliate-program.amazon.com/help/operating/policies"
AGREEMENT = "https://affiliate-program.amazon.com/help/operating/agreement"
TAGS = "https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA"
MANAGE = "https://affiliate-program.amazon.com/home/account/tag/manage"

sug["suggestions"].extend([
 {
  "id": "SG-36",
  "title": "Settle what the site is now that five links span two product categories",
  "area": "Product set and scope",
  "problem": ("The brief that supplied this repository's products has changed the product set without saying it did. "
   "Three links submitted in November resolve to air fryers; the two submitted on 2026-11-17 resolve — as far as a "
   "fallback redirect can be said to resolve anything — to a ThermoMaven instant-read thermometer and a CHEF iQ Sense "
   "Gen3 wireless thermometer, both filed under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat. The site's "
   "masthead reads 'Air-fryer field guide', its category page is 'kitchen appliances — air fryers', and every comparison "
   "row, article and buying guide is written for that decision. This is not a data-entry task: publishing the two new "
   "items changes what the site is for, and publishing them from unconfirmed candidate destinations would build a second "
   "shallow footprint on top of the first. The register records both links with their observation fields filled and their "
   "intended-product fields blank, so the decision can be made from evidence rather than from a guess."),
  "evidence": [
   {"label": "Submitted-links register, rows PI-04 and PI-05", "url": f"{SITE}/links.html"},
   {"label": "Flag F76 — the divergence, with the observation method", "url": f"{SITE}/flagged.html#f76"},
   {"label": "CHEF iQ iQ Sense product page (official brand page)", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven official site (its own model names)", "url": "https://www.thermomaven.com/"},
   {"label": "data/product-intent-confirmations.json", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/product-intent-confirmations.json"}
  ],
  "options": [
   {"label": "A. Keep the site air-fryer-only; the two links stay in the register, unpublished",
    "what": "Nothing ships for PI-04/PI-05 beyond the register rows. The site keeps one reader intent, one internal-link graph and one set of sourced claims, and the two links remain available the moment their identity is confirmed.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Stand up a second category — after the documents, not before",
    "what": "Read the brand pages and manuals for whichever product is confirmed, add them to the source register, then write one comparison and one guide. A second category done in this order is a publication; in the other order it is two thin sites.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Follow the new links and re-plan the site around thermometers",
    "what": "Treat the two most recent submissions as the intended direction, leave the air fryers as an archive. Cheapest to justify if the owner says so in one sentence; destructive to assume from a URL.",
    "effort": "L", "risk": "high", "reversible": False}
  ],
  "recommendation": "A. Publish nothing new from an unconfirmed identity; keep the register as the visible record and decide B or C after Q-27 is answered.",
  "why": ("The site's only durable asset is that a reader can check every row. A page about a product nobody confirmed the "
   "link points at spends that asset to gain two pages."),
  "impact": 5, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Medium and rising: every new article written for 'three air fryers' deepens a frame the owner may "
   "have already outgrown, and re-framing later means rewriting the navigation, the category page and the internal links, not just adding pages."),
  "blocks": ["SG-39"],
  "blocked_by": ["Q-27"]
 },
 {
  "id": "SG-37",
  "title": "Confirm the selected tracking ID in Associates Central, then open the gate — the build already refuses to move before you do",
  "area": "Attribution",
  "problem": ("The account holder selected a tracking ID, shopnow047c-20, on 2026-11-17. Ten passes could only record that "
   "the tag inside the short links was unobservable; now there is a named ID, and the remaining unknown is much smaller and "
   "much easier: does that ID exist on the account, and does it appear in that ID's report after a click. The site cannot "
   "check either, and until it is checked every published link stays untagged — which is the correct behaviour, not an "
   "omission: a tag that does not exist attributes nothing, and a destination the publisher invented looks settled while "
   "earning nothing. What is new in this pass is that the refusal is now machinery: a field in "
   "data/product-intent-confirmations.json plus check_special_link_gate(), which fails the build if a tagged anchor appears "
   "while the gate reads closed, or if the gate is opened without a confirmation date and source."),
  "evidence": [
   {"label": "Amazon — what tracking IDs are, with the storeid-20 example (re-read 2026-11-17)", "url": TAGS},
   {"label": "Associates Central — Manage your Tracking ID", "url": MANAGE},
   {"label": "Program Policies — links must carry the Associate's tag", "url": POLICIES},
   {"label": "The register page carrying the gate state", "url": f"{SITE}/links.html"},
   {"label": "Flag F78", "url": f"{SITE}/flagged.html#f78"}
  ],
  "options": [
   {"label": "A. Five minutes in Associates Central, then open the gate for the records whose product you confirmed",
    "what": "Confirm shopnow047c-20 is listed; write the confirmation date into the register; set tagging_gate.state to open; rebuild. The build emits canonical /dp/<confirmed ASIN>?tag=… CTAs for confirmed rows only, and refuses everything else.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "B. Confirm the ID, and keep the supplied short links as-is",
    "what": "If the short links already carry this ID inside the shortener, nothing needs to change on the site — verify by clicking one and checking the report row. Cheaper than a rewrite, but the ambiguity stays: the destination is still whatever the linkener decides at click time.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "C. Leave everything as it is",
    "what": "Status quo: untagged links, no attribution, no evidence the site can ever earn. Fine for a publication whose value is its sources; not fine for an affiliate site.",
    "effort": "0", "risk": "medium", "reversible": True}
  ],
  "recommendation": "A, then test one link against the report before the other four are rebuilt on the same assumption.",
  "why": ("This is the one item on the queue where a five-minute check by the only person with account access converts a whole "
   "site from 'content that might earn' to 'content that is attributed'. The build has already done the engineering half."),
  "impact": 5, "confidence": 5, "effort": "S",
  "risk_of_not_doing": "High in the narrow sense that matters: unattributed clicks are the same as no clicks.",
  "blocks": [],
  "blocked_by": ["Q-28"]
 },
 {
  "id": "SG-38",
  "title": "Decide what the shipped click counter is allowed to become",
  "area": "Measurement",
  "problem": ("The brief asks for a privacy-preserving outbound-click counter, a self-hosted analytics endpoint and five "
   "defined events, before anything else is written. The counter and the event dictionary now ship; the endpoint cannot, "
   "because GitHub Pages runs no server code and a collector URL written into a static site with nothing behind it is a "
   "promise rather than a feature. A pass on the same day read the same instruction and shipped neither, on the ground "
   "that a per-device counter is not aggregate analytics. Both halves are right, and what remains is a decision the owner "
   "makes, not a gap an agent fills: the site today counts one device's clicks, states that plainly on every surface that "
   "shows a number, and holds an empty campaign ledger that only an authorized first-party report may fill."),
  "evidence": [
   {"label": "The measurement page: events, posture, ledger", "url": f"{SITE}/measurement.html"},
   {"label": "Flag F79 — the honest limit of this design", "url": f"{SITE}/flagged.html#f79"},
   {"label": "Program Policies §3(e) — the disclosure the counter obliges", "url": POLICIES},
   {"label": "Amazon — per-tracking-ID reports, the option that needs no code", "url": TAGS}
  ],
  "options": [
   {"label": "A. Keep the counter as a labelled diagnostic, and put per-channel tracking IDs in front of it",
    "what": "Extra tracking IDs per channel report clicks and orders inside Amazon's own numbers, with no new technology to disclose, and the local counter stays what it is: a reader-side check that the links work. Nothing new to host, nothing to breach.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Deploy a first-party collector and re-point the counter at it",
    "what": "Any endpoint the owner controls that accepts a POST — a small service on a VPS, a Worker with a queue. Then the four items in the deployment boundary have to be answered in writing: retention, IP handling, what the privacy statement says, and who reads the numbers. Only after that may the campaign ledger start with browser-derived counts, and even then the ledger's rule should stay: report figures in, device counts out.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Remove the counter and rely on Amazon's reports alone",
    "what": "One line of data plus the footer paragraph to delete. The site then measures nothing it can attribute to a page, and no article-level decision can ever be evidenced — including the one the brief asks for, whether anyone arrives at a new guide.",
    "effort": "S", "risk": "low", "reversible": True}
  ],
  "recommendation": "A now, B only when there is somewhere to put an endpoint and a person to read it.",
  "why": ("A is the option that improves the decision quality today at zero compliance cost. B is the right answer to the "
   "brief's wording and the wrong answer to its intent if nobody reads the numbers; the ledger stays empty either way, "
   "because it should."),
  "impact": 4, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Low as a breach risk — the counter sets no cookie and sends nothing — and medium as a learning risk: "
   "an unowned instrument stays an instrument."),
  "blocks": [],
  "blocked_by": ["Q-29"]
 },
 {
  "id": "SG-39",
  "title": "Write the thermometer guides from brand documents, after identity — and queue them now so the queue is honest",
  "area": "Content and traffic",
  "problem": ("The brief asks for question-shaped guides and then asks whether anyone arrives. The two new candidate products "
   "happen to sit next to this site's existing content in a way the owner may not have planned: the CHEF iQ Sense is advertised "
   "for air-fryer use, and probe-in-an-air-fryer is a genuine question a reader of this site has — how do I know when the "
   "chicken is done when the whole point of the appliance is that I do not watch it. That article is writable today from "
   "manufacturer documents. Two others are not: any guide that names a specific product needs the identity confirmed first, "
   "because a guide built on a fallback destination is a guide about the wrong appliance."),
  "evidence": [
   {"label": "Topic queue rows TP-21 and TP-22", "url": f"{SITE}/topics.html"},
   {"label": "The iQ Sense brand page, which names air-fryer use", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "data/topics.json — the register a proposal lives in", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/topics.json"}
  ],
  "options": [
   {"label": "A. Queue both topics as proposed, write neither yet",
    "what": "TP-21 (using a wireless probe in an air-fryer oven, from the manuals this site already cites) and TP-22 (instant-read versus wireless: what each measurement answers) sit in the queue with their sources named, and the build ships no page.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Write TP-21 now against the air-fryer manuals only",
    "what": "It needs no thermometer identity at all: it is a question about this site's three products and what their documents say about leaving food unattended. The second half of TP-21's title waits until a product is confirmed.",
    "effort": "M", "risk": "low", "reversible": True},
   {"label": "C. Write both now, from the candidate listings",
    "what": "Fastest page count, and it is the exact behaviour the flagged register exists to prevent: product claims derived from a redirect nobody confirmed.",
    "effort": "M", "risk": "high", "reversible": True}
  ],
  "recommendation": "A, with B as the first article to turn on once Q-27 is answered.",
  "why": "Queueing costs nothing and keeps the calendar honest; writing early spends the site's credibility on an unconfirmed product.",
  "impact": 3, "confidence": 3, "effort": "S",
  "risk_of_not_doing": "Low: the topics wait; nothing rots while they do.",
  "blocks": [],
  "blocked_by": ["Q-27"]
 },
 {
  "id": "SG-40",
  "title": "Put the submitted links on the standing re-read schedule, so a moved destination is caught before a reader is misled",
  "area": "Evidence hygiene",
  "problem": ("The redirect observations behind the register are dated snapshots. Between 2026-11-13 and 2026-11-17 the "
   "candidate ASINs for the original three links held steady while the Amazon-issued token in the landing URL changed on "
   "every request — the pattern flag F41 records. A destination can also move for reasons nobody here can see: a listing "
   "closes, a model is replaced, a short link is regenerated. Today the register would keep publishing the old observation "
   "until a pass happened to re-read it, and question Q-19 already notes that the site has no standing schedule for volatile "
   "figures, only a ledger of one-off passes."),
  "evidence": [
   {"label": "The re-verification ledger this schedule would extend", "url": f"{SITE}/reverification.html"},
   {"label": "The register rows the schedule re-reads", "url": f"{SITE}/links.html"},
   {"label": "Q-19 — how often published values should be re-read", "url": f"{SITE}/questions.html#q-19"}
  ],
  "options": [
   {"label": "A. Add the five links to the existing re-verification cadence",
    "what": "One re-read per month, or before any publishing push: fetch all five, diff the destination and title against the register, append a dated round to the ledger, and let the build's reproducibility gate carry the stamp. No new tooling — the pattern is already in the repository.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Re-read only when a decision is being made",
    "what": "Cheaper, and it means the site can publish a stale destination to a reader who never asked for a decision.",
    "effort": "0", "risk": "low", "reversible": True},
   {"label": "C. Automate it in CI",
    "what": "A scheduled workflow that fetches and files an issue when a destination moves. Real answer for a site with revenue behind it; premature while the account status is unknown, because a workflow that alerts nobody is decoration.",
    "effort": "M", "risk": "low", "reversible": True}
  ],
  "recommendation": "A now; C when there is a channel that reads alerts.",
  "why": "The register's whole claim is that its observations are dated and checkable. A date without a cadence is just an expiry date nobody set.",
  "impact": 3, "confidence": 4, "effort": "S",
  "risk_of_not_doing": "Medium: a moved destination on a page a reader trusts is the quietest way for a careful site to start lying.",
  "blocks": [],
  "blocked_by": []
 },
])

sug["paths"].append({
 "id": "P6",
 "name": "Make the money path real: five links, one tag, one ledger",
 "promise": ("Turn the two things the owner supplied on 2026-11-17 — two more product links and a selected tracking ID — into "
  "a site whose commercial links are attributable and whose product set is a decision rather than an accident."),
 "contains": ["SG-36", "SG-37", "SG-38", "SG-39", "SG-40"],
 "effort": "S (two of the five rows are a browser and five minutes; the other three are reading and choosing)",
 "must_be_true_first": ("Nothing outside the owner's own screens. The register, the gate and the measurement layer are already "
  "built and enforced by the build, so this path is answering questions, not waiting on code."),
 "delivers": ("Every submitted link either confirmed or explicitly parked; tagged canonical links for "
  "the confirmed ones, emitted by the build and not by hand; a five-event measurement dictionary with a working local counter and "
  "an empty ledger whose rules make a fabricated row impossible; and a topic queue that says what it is waiting for."),
 "does_not_fix": ("It will not produce a single conversion figure. Orders come from a report this repository cannot read, and the "
  "ledger stays empty until a human with account access writes its first row — which is the point of the design, not a shortfall."),
 "pick_this_if": "You intend to earn from this site rather than merely publish it.",
 "why_first": ("It is the only path where the owner's own action unblocks the largest number of other rows: SG-37 gates every "
  "revenue claim the site could ever make, and SG-36 decides what the other five paths are written for."),
})
sug["paths_note"] = sug["paths_note"] + (
 " | P6 was added 2026-11-17 (arena/58cbaaa2) after the same brief supplied two more product links and a tracking ID. "
 "It has no dependency on P1–P5 and can run first; if P1 has already run, P6 shrinks to SG-36, SG-38 and SG-40, because "
 "P1 closes the identity and account questions P6 opens.")
sug["pass"] = (sug.get("pass", "") +
 "; five new rows SG-36..SG-40 and path P6 by arena/58cbaaa2 (2026-11-17), after two further links and a selected "
 "tracking ID arrived in the same brief")
save("data/suggestions.json", sug)

# ----------------------------------------------------------------- questions.json
q = load("data/questions.json")
if any(x["id"] in {"Q-27", "Q-28", "Q-29", "Q-30", "Q-31"} for x in q["questions"]):
    sys.exit("questions Q-27..31 already present; aborting")
q["questions"].extend([
 {
  "id": "Q-27",
  "group": "Product identity",
  "question": "Which product were the two links submitted on 2026-11-17 created to send a reader to, and does this site publish them at all?",
  "state": "missing",
  "why_it_matters": "It decides whether the site is a three-product air-fryer guide or a kitchen-tools publication, and that decision moves the navigation, the category page, the internal-link graph and the commission-category argument. Guessing from a redirect would put unconfirmed product claims on a page that gets paid for them.",
  "what_we_know": [
   "Both links were re-read live on 2026-11-17: PI-04 lands on /dp/B0DHZTCNR5 and PI-05 on /dp/B0DZFD6R9Z, each carrying the same lv=shuf / plpRedirect=mhFallback fallback markers recorded for the original three links.",
   "The served listing titles name a ThermoMaven instant-read thermometer and a CHEF iQ Sense Gen3 wireless thermometer; Amazon files both under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat, not under Fryers > Air Fryers.",
   "The brands' own pages were read the same day: CHEF iQ states model CQ60-3C-Z3-E with five sensors and a 1,000 °F ambient rating for the iQ Sense; ThermoMaven's site names its instant-read models F1 Pro and F1 Turbo and does not use the '1 Sec' label the observed listing carries.",
   "The intended-product fields on both records are blank by design, and the observed destinations are stored in a separate field so the two can never be merged."
  ],
  "what_is_missing": "A statement from the account holder of which product each link was made for — ideally the official /dp/ URL written into the record, with the date it was checked in the account holder's own browser.",
  "how_to_discover": "Open each submitted link in the browser signed in to the Amazon account, read the listing title and the model line in Product information, and compare it with the intended product. If it matches, fill the four intended_product fields in data/product-intent-confirmations.json and rebuild; if it does not, write down what was meant and the register will show both.",
  "blocks": ["SG-36", "SG-39"],
  "sources": [
   {"label": "CHEF iQ — iQ Sense product page (brand-official)", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven — official site, instant-read line-up", "url": "https://www.thermomaven.com/"},
   {"label": "Amazon — ASIN and product URL definition", "url": "https://kdp.amazon.com/en_US/help/topic/G200652190"}
  ]
 },
 {
  "id": "Q-28",
  "group": "Attribution",
  "question": "Does the selected tracking ID shopnow047c-20 exist on the Associates account, and is it the ID attached to the published links?",
  "state": "unknowable",
  "why_it_matters": "Nothing on this site can earn until both halves are true. A tag that does not exist attributes nothing; a tag that exists but is not inside the link attributes nothing either. Everything else — content, design, measurement — is downstream of one screen in Associates Central.",
  "what_we_know": [
   "The ID was supplied by the account holder on 2026-11-17 and recorded in the register as user-provided and unvalidated.",
   "Its shape matches the only example Amazon publishes for a tracking ID — storeid-20, with sub-tag IDs of the form storeid-1-20 — read verbatim from the help node on 2026-11-17.",
   "The help node states no validation rule and publishes no list of IDs per account, so a shape match cannot confirm existence.",
   "The build now enforces the consequence: while the gate reads closed, every outbound link ships exactly as supplied and a tagged anchor fails the build."
  ],
  "what_is_missing": "Two observations only the account holder can make: the ID listed at Associates Central > Manage your Tracking ID, and a click-through appearing under that ID in the report.",
  "how_to_discover": "Open Manage your Tracking ID and check for shopnow047c-20. Then click one published product link, and confirm the click appears in that ID's report. Write the date into associates_central_confirmation_date, cite the screen as the source, and set tagging_gate.state to open.",
  "blocks": ["SG-37"],
  "sources": [
   {"label": "Amazon — what tracking IDs are, and where they are managed", "url": TAGS},
   {"label": "Program Policies — the tag requirement on Special Links", "url": POLICIES}
  ]
 },
 {
  "id": "Q-29",
  "group": "Measurement",
  "question": "Where do the five defined events' counts go, and who is allowed to read them?",
  "state": "missing",
  "why_it_matters": "The counter that ships stores its tally in the reader's own browser and sends it nowhere, which makes it a diagnostic and not analytics. Turning it into site-wide data means running an endpoint, and that act changes the site's privacy obligations in the same sentence as it changes what the site can learn.",
  "what_we_know": [
   "The event dictionary, the collector's posture and the ledger schema are in data/measurement.json and rendered on the measurement page.",
   "The collector sets no cookie, makes no request, and stores no reader identifier; the footer statement was rewritten on 2026-11-17 to say exactly that.",
   "GitHub Pages serves static files, so there is no endpoint for the browser to post to, and the register records the endpoint as null rather than inventing one.",
   "Amazon's own per-tracking-ID reports answer the channel question with no code on this site at all."
  ],
  "what_is_missing": "A hosting decision (does the owner want a first-party collector, and where), a written retention and IP-handling policy, and a named reader of the numbers.",
  "how_to_discover": "Answer Q-28 first, because a tracking-ID report answers most of what an endpoint would, for free. If an endpoint is still wanted, choose any first-party destination the owner controls, write the four items in the deployment boundary before it accepts a single event, and rebuild so the privacy statement describes what now happens.",
  "blocks": ["SG-38"],
  "sources": [
   {"label": "Program Policies §3(e) — the disclosure obligation", "url": POLICIES},
   {"label": "Amazon — tracking-ID reports per ID", "url": TAGS}
  ]
 },
 {
  "id": "Q-30",
  "group": "Measurement",
  "question": "Which authorized first-party report will fill the campaign ledger, and when does its reporting window open?",
  "state": "unknowable",
  "why_it_matters": "The ledger's rule is that eligible sessions, clicks and reported orders may be added only from a report the account holder is authorized to read. Until such a report exists the ledger must stay empty, and the site must not publish a conversion rate, an EPC or a forecast — the brief says the same, and the schema is built so that a row without a report date and a named source cannot render.",
  "what_we_know": [
   "The eight columns and their filling rules are defined in data/measurement.json and published on the measurement page.",
   "The ledger has zero rows, and the reason is published next to it rather than hidden.",
   "Reports are read in Associates Central by the account holder; no public page exposes them.",
   "The browser counter is never summed into the ledger, and the build rejects a row that tries."
  ],
  "what_is_missing": "Access to Associates Central > Reports, an approved account, and at least one reporting window with activity under a confirmed tracking ID.",
  "how_to_discover": "After Q-28 and Q-03 are answered, download the Earnings report filtered to the confirmed tracking ID and transcribe one dated row into the register: report date, report name, tracking ID, sessions, clicks, items shipped, orders, and who transcribed it.",
  "blocks": [],
  "sources": [
   {"label": "Amazon — per-tracking-ID reporting", "url": TAGS},
   {"label": "Associates Operating Agreement", "url": AGREEMENT}
  ]
 },
 {
  "id": "Q-31",
  "group": "Economics",
  "question": "Which commission category does Amazon actually apply to the two newly submitted listings, and does the site's Kitchen argument extend to them?",
  "state": "not_stated",
  "why_it_matters": "The site's economics argument rests on a published rate table read by category and on a browse path observed on three air-fryer listings. A thermometer's breadcrumb is a different path, so extending Kitchen 4.50% to the new items by analogy would turn a sourced number into an assumption in the one place a reader cannot check.",
  "what_we_know": [
   "The Standard Commission Income Statement was read in full without a login and is registered as a source; it publishes rates by category.",
   "The three air-fryer candidate destinations were observed under Small Appliances > Fryers > Air Fryers; the two new ones under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat.",
   "Amazon does not publish the category it assigns to an ASIN for commission purposes, and no public page maps a browse path to a rate line.",
   "The site therefore keeps its per-product rate cells as candidates with the table cited, and does not extend them."
  ],
  "what_is_missing": "The category named on a shipped line in the owner's own Earnings report — the only document that states, for a real transaction, which rate applied.",
  "how_to_discover": "After the first attributed sale under a confirmed tracking ID, read the category named on that report line and record it against the ASIN in the register. Until then the honest cell stays a candidate with its source, not a number.",
  "blocks": [],
  "sources": [
   {"label": "Standard Commission Income Statement", "url": "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ"},
   {"label": "Program Policies — what may be displayed and how", "url": POLICIES}
  ]
 },
])
q["compiled"] = "2026-11-17"
q["version"] = "1.2"
save("data/questions.json", q)

# --------------------------------------------------------------------- topics.json
tp = load("data/topics.json")
if any(x["id"] in {"TP-21", "TP-22"} for x in tp["topics"]):
    sys.exit("TP-21/22 already present; aborting")
tp["topics"].extend([
 {
  "id": "TP-21",
  "title": "Can you leave a probe in an air fryer? What the manuals actually say",
  "hook": "The appliance is designed to run unattended. So is a wireless probe. Whether the two go together is a document question.",
  "intent": "Informational",
  "serves": [],
  "angle": ("A reader of this site who owns any of the three products has the same follow-up question: how do I know the "
   "chicken is done without opening the door. The answer this site can give today is what the manuals and brand pages of the "
   "three air fryers say about the cavity, the rack positions and leaving the unit running — plus the fact that the CHEF iQ "
   "page names air-fryer use among its own heat environments. What the site will not do is assert a clearance, a maximum "
   "temperature rating for a probe in a specific oven, or that any brand approves the pairing, because no document read here "
   "states it."),
  "why_it_could_earn_traffic": ("Judgement, not measurement: it is the question that follows a purchase of a basket or oven-style "
   "air fryer, this site already holds the manufacturer documents on both sides of it, and nothing published here answers it yet."),
  "must_cite": [
   {"label": "CHEF iQ iQ Sense product page — the brand's own use-case list, which names the air fryer", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "Chefman 6 Qt owner's manual", "url": "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf"},
   {"label": "Emeril French Door AirFryer 360 owner's manual", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"}
  ],
  "status": "proposed",
  "blocked_by": []
 },
 {
  "id": "TP-22",
  "title": "Instant-read or wireless probe: which measurement answers the question you actually have",
  "hook": "One answers 'is this piece done right now'. The other answers 'when should I be home'.",
  "intent": "Comparison",
  "serves": [],
  "angle": ("Written only after the two newly submitted links are confirmed, and then from the brands' own documents — read "
   "accuracy and latency from the manufacturer pages, not from a listing title, and stating plainly that this site has not "
   "measured either device. The comparison a shopper needs is not which sensor is faster but which failure each design "
   "protects against: the overcooked chicken nobody watched, and the undercooked one nobody checked."),
  "why_it_could_earn_traffic": ("Judgement, not measurement: a two-way choice question with no obvious winner is the shape "
   "that survives as a durable query, and this site would be writing it from primary documents rather than from a spec scrape."),
  "must_cite": [
   {"label": "CHEF iQ iQ Sense product page", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven official site — instant-read models", "url": "https://www.thermomaven.com/"}
  ],
  "status": "proposed",
  "blocked_by": []
 },
])
tp["compiled"] = "2026-11-17"
save("data/topics.json", tp)

# ---------------------------------------------------------------- requirements.json
rq = load("data/requirements.json")
reqs = rq["requirements"]
if any(x["id"] in {"H-01", "H-02", "H-03", "H-04"} for x in reqs):
    sys.exit("requirements H-01..04 already present; aborting")
reqs.extend([
 {
  "id": "H-01",
  "scope": "Brief",
  "requirement": "Build a product-intent confirmation record for every submitted link",
  "clause": "For each submitted link, store the intended ASIN, official listing URL, confirmation date, and source. Keep observed redirect targets in a separate field. Do not merge the two fields.",
  "status": "delivered",
  "where": ["data/product-intent-confirmations.json", "links.html", "build.py"],
  "evidence": [
   {"label": "the register page", "url": "links.html"},
   {"label": "the ledger data", "url": "data/product-intent-confirmations.json"}
  ],
  "why": ("The ledger was created by arena/02b4e9c7 on 2026-11-17 with the four intended fields blank on every row and the "
   "three previously observed destinations in a separate object; this pass filled the observation fields for the two links "
   "nobody had re-read, left every intended field blank, and rendered the whole thing at links.html so the row a human must "
   "fill is a row a human can see. The two fields are never merged: on 2026-11-17 all {n_submitted_links} links were "
   "re-resolved, {n_intent_confirmed} have a confirmed intended product, and the register says so in those words."),
  "sources": ["S23", "S17", "S38"]
 },
 {
  "id": "H-02",
  "scope": "Compliance",
  "requirement": "Record the selected tracking ID and gate every tagged link behind confirmation",
  "clause": "Selected Tracking ID: shopnow047c-20 — and, from the compliance line: Replace ambiguous outbound links with validated Special Links, testing one link per product in the enrolled Associates workflow before scaling.",
  "status": "partial",
  "where": ["data/product-intent-confirmations.json", "links.html", "build.py"],
  "evidence": [
   {"label": "Amazon — what a tracking ID is, and where they are managed", "url": "https://affiliate-program.amazon.com/help/node/topic/GK5TZZ4AWML2QSLA"},
   {"label": "the gate, as published", "url": "links.html"}
  ],
  "why": ("Recorded and shape-checked against Amazon's own example (storeid-20): the ID exists on the register, its status "
   "reads 'user-provided; not independently validated', and no published link carries it. The half that can be automated is "
   "built — check_special_link_gate() fails the build if a tagged anchor appears while the gate is closed, or if the gate is "
   "opened without a confirmation date and a source — and the half that cannot is left to the account holder, with the exact "
   "screen and four edit steps written on the page. Partial is the honest status: the machinery is done, the confirmation is not."),
  "sources": ["S6", "S2"]
 },
 {
  "id": "H-03",
  "scope": "Platform",
  "requirement": "Turn on click and conversion measurement with five defined events and an empty campaign ledger",
  "clause": "Add a privacy-preserving outbound-click counter and a self-hosted analytics endpoint; record the five defined events. Start with an empty but well-defined campaign ledger… No conversion score or revenue forecast is presented here.",
  "status": "partial",
  "where": ["data/measurement.json", "measurement.html", "assets/app.js", "build.py"],
  "evidence": [
   {"label": "the measurement page", "url": "measurement.html"},
   {"label": "the register", "url": "data/measurement.json"},
   {"label": "Program Policies §3(e), the obligation the posture answers to", "url": "https://affiliate-program.amazon.com/help/operating/policies"}
  ],
  "why": ("{n_events} events are defined with properties, prohibited contents, status and the decision each one informs; a "
   "cookieless, request-free counter ships in the generated script and is disclosed in the footer's section 3(e) statement; "
   "the ledger has eight columns with a filling rule each and {n_ledger_rows} rows. The endpoint is the named gap: static "
   "Pages hosting has nowhere to receive an event, so the register records it as null and the deployment boundary says what "
   "must exist first — inventing a collector URL would have been the one way to fail this requirement honestly."),
  "sources": ["S2", "S6"]
 },
 {
  "id": "H-04",
  "scope": "Site",
  "requirement": "Mobile-first pass: type scale, tap targets, sticky comparison bar",
  "clause": "S-20 — Mobile-first pass: type scale, tap targets, sticky comparison bar.",
  "status": "delivered",
  "where": ["build.py", "assets/style.css", "compare.html"],
  "evidence": [
   {"label": "the shipped stylesheet tail", "url": "assets/style.css"},
   {"label": "the comparison page, with the bar", "url": "compare.html"}
  ],
  "why": ("Presentation only, in the stylesheet's existing vocabulary: 44px minimum tap targets on the controls a shopper "
   "actually taps below 760px, a type floor at 560px so a wide table stops being the reason a page needs pinching, and a "
   "sticky comparison bar on the comparison page that keeps the buying guide and the open-questions link within reach while "
   "a reader scrolls a matrix. No published value, source or status label is touched, and the print stylesheet hides the "
   "chrome the way it hides the rest."),
  "sources": []
 },
])
save("data/requirements.json", rq)

# ------------------------------------------------------------- decision.json wording
dpath = ROOT / "data" / "decision.json"
d = dpath.read_text(encoding="utf-8")
before = d
d = d.replace("The three supplied links show no tag in their landing URL",
              "The links submitted to this project show no tag in their landing URL (re-checked 2026-11-17, all five)")
d = d.replace("The site already covers the three supplied products.",
              "The site already covers the three supplied products (five links have now been submitted; see links.html).")
if d == before:
    problems.append("decision.json: neither stale count sentence was found")
dpath.write_text(d, encoding="utf-8")

if problems:
    sys.exit("WARNINGS (written):\n  " + "\n  ".join(problems))
print("registers updated: +5 suggestions, +1 path, +5 questions, +2 topics, +4 requirement rows, decision.json wording")
