#!/usr/bin/env python3
"""pass 13 (re-scoped onto main e5fc007) — data, sources, gate and register layer.

Additive on purpose: main's measurement register, intent register and flag numbering are the
canonical ones, so this script extends them with the four official pages read on 2026-11-17 that
main had not read, the brand-catalogue check for the two newly submitted links, the wiring state of
the local collector, and the decision rows. Nothing here replaces a merged decision; the drop list is
in session-58cbaaa2/artifacts/README.md.
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/user/Zone1")
HELPS = "https://affiliate-program.amazon.com/help/node/topic/"
SITE = "https://kanlerxz87-cyber.github.io/Zone1"
problems = []


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def save(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def save2(name, data):
    # files main serialises at indent=2 keep that style, so the diff stays purely additive
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# ─────────────────────────────────────────────────────────────────── sources.json
s = load("data/sources.json")
have = {x["id"] for x in s["sources"]}
new_sources = [
 {"id": "S38", "org": "CHEF iQ (brand)",
  "url": "https://chefiq.com/products/iq-sense",
  "title": "CHEF iQ iQ Sense wireless meat thermometer — official product page",
  "covers": "The brand's own model designation and ratings for the iQ Sense, checked against the listing observed at /dp/B0DZFD6R9Z",
  "kind": "Brand product page", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1). The brand page names model CQ60-3C-Z3-E, describes the "
   "Gen3 kit and its probes, and gives an ambient rating the observed Amazon listing does not repeat; it does not "
   "mention an Amazon ASIN. Recorded because it is what the manufacturer states, not because it confirms a listing "
   "identity — see flag F83. Evidence: reports/verification-2026-11-17-58cbaaa2.md.")},
 {"id": "S39", "org": "ThermoMaven (brand)",
  "url": "https://www.thermomaven.com/",
  "title": "ThermoMaven official site — instant-read and wireless thermometer line-up",
  "covers": "The brand's own instant-read model names, checked against the '1 Sec' title on the listing observed at /dp/B0DHZTCNR5",
  "kind": "Brand site", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1). The brand's instant-read line is named F1 Pro / F1 Turbo "
   "with a sub-second read; the site does not use the '1 Sec' label the observed Amazon listing carries as a model "
   "name. Recorded as a divergence, not resolved: this site does not claim which product the submitted short code was "
   "created to promote (flag F83, Q-27). Evidence: reports/verification-2026-11-17-58cbaaa2.md.")},
 {"id": "S40", "org": "Amazon.com Associates Central",
  "url": HELPS + "GF4RJEQNXSMR7SP3",
  "title": "Why doesn't my tracking ID appear in your URL after a visitor clicks through to Amazon from my Web site?",
  "covers": "Whether an absent tag= parameter on a landing URL can be read as evidence about attribution",
  "kind": "Help article", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1) from the linked-topic list on S6. Full answer, verbatim: "
   "\u201cWe understand your concern, but rest assured that it is not necessary for your unique ID to appear in order "
   "for us to track sales made after the initial click through. The individual shopping session will be tagged in a "
   "way that allows us to track the items purchased and credit you with the appropriate commission.\u201d This is the "
   "official statement that a landing URL without a visible tag is not evidence either way; it says nothing about "
   "whether any particular link carries any particular ID. Flag F84.")},
 {"id": "S41", "org": "Amazon.com Associates Central",
  "url": HELPS + "GJDYPQZK6E37RLPU",
  "title": "How do I request multiple tracking IDs?",
  "covers": "Creating additional tracking IDs, the 100-per-account limit, and the report where each ID's data is read",
  "kind": "Help article", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1) from the linked-topic list on S6. Verbatim: to create "
   "multiple IDs, \u201cvisit your account and click on \u2018Manage your Tracking ID\u2019\u201d (linked as "
   "https://affiliate-program.amazon.com/home/account/tag/manage); \u201cOnce they have been created, you will be able "
   "to see data on each ID in your Tracking ID Summary Report\u201d; \u201cthere is a limit of 100 Tracking IDs per "
   "associate account\u201d. This is where the confirmation this site cannot perform lives, and the second official page "
   "naming that screen.")},
]
for x in new_sources:
    if x["id"] not in have:
        s["sources"].append(x)
for x in s["sources"]:
    if x["id"] == "S6" and "2026-11-17" not in x.get("page_version", ""):
        x["page_version"] += (" Re-read verbatim 2026-11-17 (arena/58cbaaa2-zone1) because the account holder supplied "
                              "a tracking ID that day: the worked example remains 'storeid-20' with sub-tag "
                              "'storeid-1-20', each ID reportable individually, new IDs created at Associates Central > "
                              "'Manage your Tracking ID'. The node states no validation rule and publishes no per-account "
                              "list, so it can confirm the shape of an ID and nothing more.")
save("data/sources.json", s)

# ────────────────────────────────────────────────────────────────────── verify.py
v = ROOT / "verify.py"
vt = v.read_text(encoding="utf-8")
if "chefiq.com" not in vt:
    anchor = 'OFFICIAL_HOSTS = {'
    idx = vt.index(anchor) + len(anchor)
    vt = (vt[:idx] + "\n    # Brand pages read 2026-11-17 for the two links submitted that day (sources S38/S39). Registered\n"
          "    # as official brand sites — which is not the same as confirming a listing identity; see flag F83.\n"
          '    "chefiq.com",\n    "www.thermomaven.com",' + vt[idx:])
    v.write_text(vt, encoding="utf-8")
    print("verify.py allow-list extended")

# ──────────────────────────────────────────────────────────── product-intent.json
pi = load("data/product-intent.json")
brand = {
 "PI-04": {
  "listing_says": "Title as served on 2026-11-17: 'ThermoMaven 1 Sec Professional Digital Meat Thermometer, "
                  "\u00b10.5\u2109 Accuracy | NIST&NSF Certified Food Thermometer \u2026 Black'. No model number in the "
                  "fetched portion of the page.",
  "brand_page_says": "ThermoMaven's own site names its instant-read line F1 Pro and F1 Turbo and states a "
                     "sub-second read; '1 Sec' is not used there as a model name.",
  "verdict": "Not reconciled. The brand's catalogue and the listing title use different kinds of identifier, and "
             "neither names the ASIN, so the intended product stays null and no product page is written.",
  "source_ids": ["S39", "S36", "S23"],
 },
 "PI-05": {
  "listing_says": "Title as served on 2026-11-17: 'CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin "
                  "Probes | Gen3'. No model number in the fetched portion of the page.",
  "brand_page_says": "CHEF iQ's iQ Sense product page states model CQ60-3C-Z3-E, its Gen3 probe configuration and an "
                     "ambient rating the listing does not repeat, and lists air-fryer use among its heat environments.",
  "verdict": "Consistent with, not confirmed by. A brand model designation that the listing does not carry cannot be "
              "transcribed into the intended-ASIN field, so the row stays open (Q-27).",
  "source_ids": ["S38", "S37", "S23"],
 },
}
for r in pi["rows"]:
    if r["id"] in brand and not r.get("brand_catalogue_check"):
        r["brand_catalogue_check"] = brand[r["id"]]
        ids = r.setdefault("observed_source_ids", [])
        for sid in brand[r["id"]]["source_ids"]:
            if sid not in ids:
                ids.append(sid)
        r["note"] = (r.get("note", "") + " Brand catalogue read against this listing on 2026-11-17 (S38/S39): "
                     "reconciles with, but does not confirm, the candidate destination — flag F83.").strip()
pi["observation_method_correction"] = {
 "date": "2026-11-17",
 "what_changed": (
  "Two official help nodes read on this date narrow what a landing URL can be said to show. Amazon states that a "
  "tracking ID 'is not necessary … to appear in order for us to track sales made after the initial click through', "
  "because the session is tagged on Amazon's side (S40). So the absence of a tag= parameter on an observed URL is a "
  "null observation, not evidence that a link failed to attribute, and this record does not use it as evidence."),
 "what_still_cannot_be_seen": (
  "The positive: whether the selected ID is listed on the account, and whether a click through a published link "
  "appears under it. That is read in the Tracking ID Summary Report, which S41 names as the per-ID report, and it "
  "requires the account holder's login. Until then the tag on this site's links is verified as attached and "
  "well-formed, and is described exactly that way."),
 "historical_rows": (
  "Left as written. F82 and the dated observations above record what a fetch returned on the date shown; rewriting "
  "them would remove the audit trail. The correction is applied where the inference is made in the present tense — "
  "the landing-page note and this page."),
 "sources": ["S40", "S41", "S6"],
}
pi["sub_tag_plan"] = {
 "what": ("S41 records that additional tracking IDs are created at Associates Central > Manage your Tracking ID, that "
          "each one is reported in the Tracking ID Summary Report, and that an account may hold up to 100. One ID per "
          "channel — site, newsletter, social, per-article — separates traffic sources inside Amazon's own reporting, "
          "with no script on this site and nothing new to disclose."),
 "limit": ("It attributes a channel, not a page: clicks and orders arrive per tracking ID, not per URL, so a sub-tag "
           "plan answers 'which channel' while page-level questions stay with the local tally and the guide-depth "
           "event until an endpoint exists."),
 "status": "proposed; needs the account holder to create the IDs",
 "sources": ["S41", "S6"],
}
save2("data/product-intent.json", pi)

# ─────────────────────────────────────────────────────────────── measurement.json
me = load("data/measurement.json")
wired = {
 "EV-01": ("not_wired", "A page arrival could be counted locally, but with no endpoint a local arrival count answers "
                       "nothing about an audience, so this pass left it out rather than imply an aggregate."),
 "EV-02": ("wired_local_only", "Outbound clicks to amazon.com/dp/ and to link.amazon are counted in this browser "
                                "against the page they came from and the 10-character ASIN in the href. No cookie, no "
                                "request, no reader identifier, no destination query string stored."),
 "EV-03": ("not_wired", "Guide completion needs a scroll or last-heading signal nobody has asked for yet; the topic "
                        "queue is the current answer to 'did anyone read this'."),
 "EV-04": ("wired_local_only", "A captioned <table> that reaches 35% of the viewport is flagged once per page per "
                                "device. That is the comparison-viewed signal this register asked for."),
 "EV-05": ("manual_only", "Entered by hand from an authorized first-party report into data/campaign-ledger.json; the "
                           "ledger has 0 rows and nothing in the script writes to it."),
}
for ev in me["events"]:
    st, detail = wired.get(ev["id"], ("not_wired", ""))
    ev["wired"] = {"state": st, "detail": detail, "checked_on": "2026-11-17"}
me["status"] = "defined_and_wired_locally; nothing transmits"
me["collector"] = {
 "state": "wired_local_only",
 "added_on": "2026-11-17",
 "added_by": "arena/58cbaaa2-zone1",
 "what": ("A cookieless tally kept in the reader's own browser: outbound product clicks (EV-02) and captioned "
          "comparison tables actually seen (EV-04), plus which page they came from. It is wired to satisfy the "
          "specification in this file, and it is not analytics — no server receives anything, so no site-wide number "
          "exists or is published."),
 "storage": ("window.localStorage under one key, holding page slugs, ASINs and counts. No cookie is set, no "
             "first-party storage identifier is generated, and nothing is read from the destination's query string."),
 "transmitted": "No. The script issues no fetch, beacon or XHR, and the register holds no collector URL to send to.",
 "endpoint": ("None, and deliberately unwritten: GitHub Pages serves static files, so a collector URL in the code "
              "with nothing behind it would be a promise rather than a feature. prerequisites step 1 is what changes "
              "this."),
 "ceiling": "Forty entries per bucket, oldest dropped. A diagnostic on one device, not an archive.",
 "disclosure": ("The footer's Program Policies \u00a73(e) statement was rewritten in the same commit that shipped the "
                "counter, as this register's own privacy rule requires, and it describes the tally and the erase "
                "control rather than claiming no script runs."),
 "erasure": ("Erase and export controls sit on this page; clearing the browser's storage for this site removes the "
             "tally completely, and nothing else holds a copy."),
 "sub_tag_alternative": ("Amazon's own per-tracking-ID reporting answers the channel question with no code on this "
                         "site at all, and S41 records a limit of 100 IDs per account, so room exists for one ID per "
                         "channel. It attributes a channel rather than a page."),
 "honest_limit": ("Counts describe one device. They cannot be summed into the campaign ledger, and the build rules "
                  "keep it that way: ledger rows come only from an authorized first-party report."),
}
me["why_nothing_is_sending"].append(
 "Still true after 2026-11-17, when two of these events became wired: nothing is *sent*. The tally that now runs "
 "lives in each reader's own browser and has no destination, which is why no page on this site reports a count.")
me["privacy_rules"].append(
 "The collector added 2026-11-17 (EV-02, EV-04) keeps its tally in the reader's own browser, sets no cookie, records "
 "no reader identifier and makes no request; if it ever gains an endpoint, this rule and the footer statement are "
 "rewritten in the same commit.")
me["status_note"] = ("Recorded 2026-11-17 by arena/58cbaaa2-zone1, which re-scoped itself against main's merged "
                     "register instead of publishing a second one: this file is the canonical specification, and the "
                     "collector row above is the increment.")
save("data/measurement.json", me)

# ──────────────────────────────────────────────────────────────────── suggestions
sg = load("data/suggestions.json")
if {x["id"] for x in sg["suggestions"]} & {"SG-36", "SG-37", "SG-38"}:
    sys.exit("SG-36..38 already present; aborting")
sg["suggestions"].extend([
 {
  "id": "SG-36",
  "title": "Decide what happens to the two links that are not air fryers — with the options in front of you",
  "area": "Product set and scope",
  "problem": ("main's F76 records the fact — two of the five submitted links land on cooking thermometers, outside "
   "the category every article, table and navigation label on this site is built for — and asks the owner to say "
   "what they were meant to promote or drop them. What it does not do is lay out the paths, because an unmerged "
   "observation and a decision are different documents. This row is the decision half, and it is deliberately "
   "written after the brand-catalogue check (F83) rather than before it: neither candidate listing reconciles with "
   "the manufacturer's own model names, so any page written now would be about a product nobody confirmed."),
  "evidence": [
   {"label": "Product-intent record, rows PI-04 and PI-05 with the brand-catalogue check", "url": f"{SITE}/product-intent.html"},
   {"label": "Flag F76 (main) — the divergence, as observed", "url": f"{SITE}/flagged.html#f76"},
   {"label": "Flag F83 — what the two brand pages do and do not settle", "url": f"{SITE}/flagged.html#f83"},
   {"label": "CHEF iQ iQ Sense page (brand-official)", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven official site (its own model names)", "url": "https://www.thermomaven.com/"}
  ],
  "options": [
   {"label": "A. Park both rows: the register keeps them, the site publishes neither",
    "what": "Zero new pages. The site keeps one reader intent, one internal-link graph and one set of sourced claims, and the two links stay available the moment their identity is confirmed.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Stand up a thermometer category — after the documents, in this order",
    "what": "Confirm the intended product (Q-27), read the brand pages and manuals into the source register, then write one comparison and one guide. In this order a second category is a publication; in the reverse order it is two shallow sites sharing a domain.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Follow the newest links and re-plan the site around thermometers",
    "what": "Treat the two most recent submissions as the direction, archive the air-fryer set. Cheapest to justify if the owner says so in one sentence; destructive to infer from a URL.",
    "effort": "L", "risk": "high", "reversible": False}
  ],
  "recommendation": "A. Publish nothing new from an unconfirmed identity; keep the register as the visible record and choose B or C only after Q-27 is answered.",
  "why": ("The site's only durable asset is that a reader can check every row. A page about a product nobody confirmed "
   "the link points at spends that asset to gain two pages."),
  "impact": 5, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Medium and rising: every article written for 'three air fryers' deepens a frame the owner may "
   "have outgrown, and re-framing later means rewriting navigation, the category page and the internal links — not "
   "just adding pages."),
  "blocks": ["SG-39" if False else "SG-36"],
  "blocked_by": ["Q-27"]
 },
 {
  "id": "SG-37",
  "title": "Close the attribution question where it can actually be closed: a click test read in the Tracking ID Summary Report",
  "area": "Attribution",
  "problem": ("Main wired the selected tracking ID into every outbound link and check_associate_tagging() now fails "
   "the build if a tag or rel=sponsored is missing — so the mechanical half is proven and was proven before this "
   "pass ran. The remaining half is not a build problem at all: that shopnow047c-20 is listed on the account, and "
   "that a click shows up under it. S40 also removes a false indicator the repository had been weighing — a landing "
   "URL with no visible tag proves nothing — which means the only evidence that settles this is a report row, and "
   "only one person can read that row."),
  "evidence": [
   {"label": "Amazon — how multiple tracking IDs are created and reported (S41, read 2026-11-17)", "url": HELPS + "GJDYPQZK6E37RLPU"},
   {"label": "Amazon — a tag need not appear in the click-through URL (S40, read 2026-11-17)", "url": HELPS + "GF4RJEQNXSMR7SP3"},
   {"label": "Amazon — what tracking IDs are, and the storeid-20 example (S6)", "url": HELPS + "GK5TZZ4AWML2QSLA"},
   {"label": "The record carrying the correction and the gate history", "url": f"{SITE}/product-intent.html"},
   {"label": "Flag F84 — the over-reading, corrected on the record", "url": f"{SITE}/flagged.html#f84"}
  ],
  "options": [
   {"label": "A. One click, one report row, one sentence back",
    "what": "Open Manage your Tracking ID, confirm shopnow047c-20 is listed, click one published product link, and confirm the click appears in that ID's report. Then write the date and the report name into the register; a later pass records the answer against Q-28 and closes F82's open half.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "B. Create one ID per channel while you are in there",
    "what": "Same screen, a few more minutes: per-channel IDs give clicks and orders per channel inside Amazon's reporting, with nothing new to host or disclose — S41 records 100 IDs per account, so there is room.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "C. Leave it",
    "what": "The site keeps publishing tagged links whose attribution has never been observed once. If the ID is not on the account, every click on this site is unattributed and no page here would ever know.",
    "effort": "0", "risk": "medium", "reversible": True}
  ],
  "recommendation": "A, then B in the same sitting.",
  "why": ("It is the one queue item where a five-minute check by the only person with access converts a whole site from "
   "'content that might earn' to 'content that is attributed' — and B costs one more screen while the tab is open."),
  "impact": 5, "confidence": 5, "effort": "S",
  "risk_of_not_doing": "High in the narrow sense that matters: an unattributed click is the same as no click.",
  "blocks": [],
  "blocked_by": ["Q-28"]
 },
 {
  "id": "SG-38",
  "title": "Say what the shipped local tally is allowed to become",
  "area": "Measurement",
  "problem": ("Main's register defined five events with status defined_not_shipped, and a pass the same day argued a "
   "browser-stored tally 'would not give the publisher usable aggregate analytics' and shipped neither. The tally now "
   "ships for EV-02 and EV-04 — cookieless, request-free, erasable, with the §3(e) statement rewritten in the same "
   "commit as the register's own privacy rule demands — which makes the criticism and the feature both true and leaves "
   "one open question: is a per-device diagnostic the end state, or the placeholder for a collector? An answer is now "
   "required rather than optional, because code that reads storage on every page is a live surface, not a proposal."),
  "evidence": [
   {"label": "The measurement page: per-event wiring state and the collector block", "url": f"{SITE}/measurement.html"},
   {"label": "Flag F85 — the honest limit of what shipped", "url": f"{SITE}/flagged.html#f85"},
   {"label": "The specification the collector implements", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/measurement.json"},
   {"label": "Program Policies §3(e), the disclosure the counter obliges", "url": "https://affiliate-program.amazon.com/help/operating/policies"}
  ],
  "options": [
   {"label": "A. Keep it as a labelled diagnostic; put per-channel tracking IDs in front of it",
    "what": "Amazon's own per-ID reports (S41) answer 'which channel' inside numbers the publisher is authorized to read, and the local tally stays what it is: a reader-side check that the links work. Nothing new to host, nothing new to disclose.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Deploy a first-party endpoint and re-point the tally at it",
    "what": "prerequisites step 1: any host the owner controls that can accept an event. The four items in the register's privacy rules then have to be answered in writing before the first write — retention, IP handling, what the footer says, who reads it — and the campaign ledger's rule stays: report figures in, device counts out.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Remove the counter",
    "what": "Delete the tally block from the emitted script, the collector section from the register and the footer sentence about it. Reverts to main's defined_not_shipped state and loses the only signal that distinguishes 'the link was clicked' from 'the table was read'.",
    "effort": "S", "risk": "low", "reversible": True}
  ],
  "recommendation": "A now; B only when somebody will read the numbers, because an endpoint nobody reads is decoration with a privacy cost.",
  "why": ("A improves decision quality today at zero compliance cost. B answers the brief's wording and not its intent. "
   "The ledger stays empty in all three cases, because nothing authorised has been recorded — that is the design, not "
   "a shortfall."),
  "impact": 4, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Low as a breach risk — no cookie, no request — and non-zero as a trust risk: an unowned "
   "instrument on every page is the kind of thing a later pass forgets is there and starts quoting."),
  "blocks": [],
  "blocked_by": []
 },
])
sg["pass"] = (sg.get("pass", "") +
 "; SG-36..SG-38 and path P6 by arena/58cbaaa2 (2026-11-17), written after re-scoping this session's "
 "draft against the merged intent register and measurement layer rather than publishing parallel ones")
if not any(p.get("id") == "P6" for p in sg.get("paths", [])):
    sg.setdefault("paths", []).append({
     "id": "P6",
     "name": "Make the money path real: five links, one tag, one ledger",
     "promise": ("Turn what the owner supplied on 2026-11-17 — two more links and a tracking ID — into a site whose "
                 "commercial links are provably attributed and whose product set is a decision rather than an accident."),
     "contains": ["SG-36", "SG-37", "SG-38"],
     "effort": "S (two of the three rows are a browser and five minutes; the third is a reading-and-choosing task)",
     "must_be_true_first": ("Nothing outside the owner's screens. The intent register, the tagging gate and the "
                            "measurement specification are merged and enforced by the build, so this path is answering "
                            "questions, not waiting on code."),
     "delivers": ("Every submitted link either confirmed or explicitly parked; a tracking ID whose attribution has been "
                  "observed in a report rather than assumed from markup; a per-channel sub-tag scheme that needs no "
                  "infrastructure; and a measurement layer whose wiring state is published per event, with a ledger "
                  "whose rules make a fabricated row impossible."),
     "does_not_fix": ("It will not produce a conversion figure. Orders come from a report this repository cannot read, "
                      "and the ledger's first row will be transcribed by a human or will not exist."),
     "pick_this_if": "You intend to earn from this site rather than merely publish it.",
     "why_first": ("It is the only path where the owner's own action unblocks the largest number of other rows, and it "
                   "is the only one whose bottleneck is a login this project will never have."),
    })
save("data/suggestions.json", sg)

# ────────────────────────────────────────────────────────────────────── questions
q = load("data/questions.json")
if {x["id"] for x in q["questions"]} & {"Q-27", "Q-28"}:
    sys.exit("Q-27/Q-28 already present; aborting")
q["questions"].extend([
 {
  "id": "Q-27",
  "group": "Product identity",
  "question": ("Which product were the two links submitted on 2026-11-17 created to send a reader to — and does this "
               "site publish them at all?"),
  "state": "missing",
  "why_it_matters": ("It decides whether this is a three-product air-fryer guide or a kitchen-tools publication, and "
   "that moves the navigation, the category page, the internal-link graph and the commission-category argument. "
   "Reading it off a fallback redirect would put unconfirmed product claims on a page that gets paid for them, and "
   "main's F76 already records that neither candidate reconciles with its manufacturer's own catalogue."),
  "what_we_know": [
   "Both links were re-read live on 2026-11-17: PI-04 lands on /dp/B0DHZTCNR5 and PI-05 on /dp/B0DZFD6R9Z, each with the same lv=shuf / plpRedirect=mhFallback fallback markers recorded for the original three, and neither landing URL carrying an asin= parameter.",
   "Amazon files both candidates under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat — a different browse path from the air-fryer listings this site is built around.",
   "The brands' own pages were read the same day: ThermoMaven names its instant-read line F1 Pro / F1 Turbo and does not use the '1 Sec' label the listing carries; CHEF iQ states model CQ60-3C-Z3-E for the iQ Sense, a designation the listing does not repeat.",
   "intended_asin, official_listing_url, confirmation_date and confirmation_source are null on both rows by construction, and the observed destinations live in separate observed_* fields."
  ],
  "what_is_missing": ("A statement from the account holder of which product each link was created to promote — ideally "
                      "the official /dp/ URL they wrote in the Link Building tool, with the date it was checked in "
                      "their own browser."),
  "how_to_discover": ("Open each submitted link in the browser signed in to the Amazon account and read the listing "
   "title plus the model line in Product information; compare it with what you meant to promote, and with the brand "
   "pages registered as S38/S39. If it matches, fill the four intended fields on that row of "
   "data/product-intent.json; if it does not, write down what was meant. A third option is legitimate: say the link was "
   "submitted in error, and the row closes as dropped rather than unresolved."),
  "blocks": ["SG-36"],
  "sources": [
   {"label": "CHEF iQ — iQ Sense product page (brand-official)", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven — official site, instant-read line-up", "url": "https://www.thermomaven.com/"},
   {"label": "Amazon — ASIN and product URL definition", "url": "https://kdp.amazon.com/en_US/help/topic/G200652190"}
  ]
 },
 {
  "id": "Q-28",
  "group": "Attribution",
  "question": ("Is shopnow047c-20 listed on the Associates account, and does a click through a published link appear "
               "under it in the Tracking ID Summary Report?"),
  "state": "unknowable",
  "why_it_matters": ("Main attaches the tag to every outbound link and a build guard enforces that it is attached and "
   "well-formed. That is a statement about this site's markup, not about Amazon's books. If the ID is not the one on "
   "the account, every click here is unattributed and nothing on this site would ever reveal it."),
  "what_we_know": [
   "The ID was supplied by the account holder on 2026-11-17 and is recorded as user-provided; its shape matches the only example Amazon publishes (storeid-20, sub-tags storeid-1-20), read verbatim from S6 the same day.",
   "No official page states a validation rule or lists which IDs exist for which account, so a shape match cannot confirm existence.",
   "S40 states that a tracking ID need not appear in the click-through URL for a sale to be attributed, so the clean landing URLs observed for the five supplied links neither support nor undermine anything.",
   "check_associate_tagging() fails the build if a rendered Amazon link lacks the tag or lacks rel=sponsored, which is why 'attached' is not the open part of this question."
  ],
  "what_is_missing": ("Two observations only the account holder can make: the ID present at Associates Central > Manage "
                      "your Tracking ID, and a click-through appearing in that ID's summary report."),
  "how_to_discover": ("Open Manage your Tracking ID and check for shopnow047c-20. Click one published product link. "
   "Read the Tracking ID Summary Report — the destination S41 names — for that click. Write the date and the report "
   "name into data/product-intent.json's tracking_id_status so the claim becomes an observation, then a later pass "
   "updates F82 and this row together."),
  "blocks": ["SG-37"],
  "sources": [
   {"label": "Amazon — how IDs are created and reported, and the 100-per-account limit", "url": HELPS + "GJDYPQZK6E37RLPU"},
   {"label": "Amazon — a tag need not appear in the URL to attribute the sale", "url": HELPS + "GF4RJEQNXSMR7SP3"},
   {"label": "Amazon — what a tracking ID is (re-read verbatim 2026-11-17)", "url": HELPS + "GK5TZZ4AWML2QSLA"}
  ]
 },
])
q["compiled"] = "2026-11-17"
q["version"] = "1.2"
save("data/questions.json", q)

# ────────────────────────────────────────────────────────────────────── topics.json
tp = load("data/topics.json")
tp["topics"].extend([
 {
  "id": "TP-21",
  "title": "Can you leave a probe in an air fryer? What the manuals actually say",
  "hook": ("The appliance is designed to run unattended. A wireless probe is designed to be left in. Whether the two "
           "go together is a question the documents can answer."),
  "intent": "Informational",
  "serves": [],
  "angle": ("A reader who owns any of the three products has the same follow-up question: how do I know the chicken is "
   "done without opening the door. What this site can answer today is what the manuals and brand pages of the three air "
   "fryers say about the cavity, rack positions and leaving the unit running — and the fact that CHEF iQ lists "
   "air-fryer use among the iQ Sense's own heat environments (S38). What it will not do is assert a clearance, a "
   "maximum probe temperature inside a specific oven, or that any brand approves the pairing: no document read here "
   "states any of those, so those cells stay unwritten and the article says why."),
  "why_it_could_earn_traffic": ("Judgement, not measurement: it is the question that follows a purchase of a basket or "
   "oven-style air fryer, this site already holds the manufacturer documents on both sides of it, and nothing published "
   "here answers it yet."),
  "must_cite": [
   {"label": "CHEF iQ iQ Sense product page — the brand's own use-case list, which names the air fryer", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "Chefman 6 Qt owner's manual", "url": "https://cdn.shopify.com/s/files/1/0576/5755/7158/files/RJ38-SQPF-3TDB-2W-UG-US.pdf"},
   {"label": "Emeril French Door AirFryer 360 owner's manual", "url": "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"}
  ],
  "status": "proposed",
  "blocked_by": [],
  "status_note": ("Queued 2026-11-17 by arena/58cbaaa2. Writable from documents this site already cites; the half of "
   "the title that names a specific probe waits for Q-27.")
 },
 {
  "id": "TP-22",
  "title": "Instant-read or wireless probe: which measurement answers the question you actually have",
  "hook": "One answers 'is this piece done right now'. The other answers 'when should I be home'.",
  "intent": "Comparison",
  "serves": [],
  "angle": ("Written only after the two newly submitted links are confirmed, and then from the brands' own documents: "
   "stated accuracy and read time from the manufacturer pages, never from a listing title, and an explicit statement "
   "that this site has not measured either device. The comparison a shopper needs is not which sensor is faster but "
   "which failure each design protects against — the overcooked chicken nobody watched, and the undercooked one nobody "
   "checked."),
  "why_it_could_earn_traffic": ("Judgement, not measurement: a two-way question with no obvious winner is a durable "
   "query, and this site would write it from primary documents rather than from a spec scrape."),
  "must_cite": [
   {"label": "CHEF iQ iQ Sense product page", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven official site — instant-read models", "url": "https://www.thermomaven.com/"}
  ],
  "status": "proposed",
  "blocked_by": ["Q-27"],
  "status_note": "Queued 2026-11-17 and blocked by the owner's answer to Q-27; blocked_by is a register field, not a build gate."
 },
])
tp["compiled"] = "2026-11-17"
save("data/topics.json", tp)

# ─────────────────────────────────────────────────────────────────── requirements
rq = load("data/requirements.json")
rq["requirements"].extend([
 {
  "id": "H-01",
  "scope": "Brief",
  "requirement": "Record every submitted link with its intended product, official listing URL, confirmation date and source, kept separate from the observed redirect target",
  "clause": "Create a product-intent confirmation record for each submitted product link: intended ASIN, official listing URL, confirmation date, and source. Keep observed redirect targets in a separate field. Do not merge the two fields.",
  "status": "partial",
  "where": ["data/product-intent.json", "product-intent.html", "build.py", "reports/verification-2026-11-17-58cbaaa2.md"],
  "evidence": [
   {"label": "the rendered record", "url": "product-intent.html"},
   {"label": "the register", "url": "data/product-intent.json"},
   {"label": "this pass's evidence file", "url": "reports/verification-2026-11-17-58cbaaa2.md"}
  ],
  "why": ("Delivered by the merged register (arena/5b17c077 consolidated three parallel records into this one file and "
   "retired the others), and this pass adds the two things it found rather than a competing register: a brand-catalogue "
   "check on each of the two newly submitted rows, and a dated correction of the reasoning that read a missing tag= "
   "parameter as evidence about attribution (S40, S41). Partial rather than delivered because the intended half is still "
   "null on all {n_submitted_links} rows — {n_intent_confirmed} confirmed — and only the account holder can fill them. "
   "This pass also wrote, then withdrew, a parallel schema-v2 file at "
   "data/product-intent-confirmations.json once it found main had retired that path; the draft and the reason are kept "
   "under session-58cbaaa2/artifacts/."),
  "sources": ["S23", "S17", "S38", "S39", "S40", "S41"]
 },
 {
  "id": "H-02",
  "scope": "Platform",
  "requirement": "Wire the defined measurement events and keep the campaign ledger empty but well-defined",
  "clause": "Add a privacy-preserving outbound-click counter and a self-hosted analytics endpoint; record the five defined events. Start with an empty but well-defined campaign ledger. No conversion score or revenue forecast is presented here.",
  "status": "partial",
  "where": ["data/measurement.json", "measurement.html", "assets/app.js", "data/campaign-ledger.json"],
  "evidence": [
   {"label": "the measurement page, with the per-event wiring state", "url": "measurement.html"},
   {"label": "the specification and collector block", "url": "data/measurement.json"},
   {"label": "Program Policies \u00a73(e), the disclosure the posture answers to", "url": "https://affiliate-program.amazon.com/help/operating/policies"}
  ],
  "why": ("{n_events} events are specified in main's register; this pass moved two of them from defined to wired by "
   "shipping a cookieless, request-free local tally (EV-02, EV-04) into the generated script, recorded the wiring state "
   "per event so nobody has to read the source to learn what runs, and rewrote the footer's §3(e) statement in the same "
   "commit exactly as the register's own privacy rule demands. The ledger holds {n_ledger_rows} rows and its rule — "
   "authorized first-party report in, device counts out — is what keeps it that way. Partial names the gap that "
   "cannot be closed inside a static repository: there is no endpoint, the register records it as unwritten rather than "
   "inventing a URL, and prerequisites step 1 is an owner decision."),
  "sources": ["S2", "S41", "S6"]
 },
 {
  "id": "H-03",
  "scope": "Site",
  "requirement": "Mobile-first presentation pass: type floor, tap targets, sticky comparison affordance",
  "clause": "S-20 — Mobile-first pass: type scale, tap targets, sticky comparison bar.",
  "status": "delivered",
  "where": ["build.py", "assets/style.css"],
  "evidence": [{"label": "the emitted stylesheet tail", "url": "assets/style.css"}],
  "why": ("Presentation only, inside the stylesheet's existing vocabulary and variables, so no published value, source "
   "badge or status label moved. Deliberately re-cut after the rebase onto main: the earlier draft of this work had "
   "restructured the comparison bar, main had meanwhile shipped its own responsive pass, and two sticky bars on one "
   "page is a defect, not an integration — so this row carries the remainder that does not collide (tap-target and "
   "type floors on the shopper surfaces, plus the tally controls styled from the same tokens) and names the collision "
   "rather than hiding it."),
  "sources": []
 },
])
save2("data/requirements.json", rq)
d = json.dumps(rq["requirements"][-1], ensure_ascii=False)

# ────────────────────────────────────────────────────────────────── decision.json
dp = ROOT / "data" / "decision.json"
dt = dp.read_text(encoding="utf-8")
n0 = dt
dt = dt.replace(
 "The three supplied links show no tag in their landing URL, so as supplied they are evidence of a destination, not of an attribution path.",
 "The three supplied links show no tag in their landing URL, so as supplied they are evidence of a destination, not of an attribution path. "
 "[Corrected 2026-11-17, arena/58cbaaa2: five links have been submitted, and per S40 a missing tag= parameter on a landing URL is a null "
 "observation — Amazon states the ID need not appear in the URL for a sale to be attributed. This sentence is kept as what that pass recorded; "
 "the inference it drew is narrowed on product-intent.html and in flag F84.]")
dt = dt.replace(
 "In Associates Central, open **Manage Tracking IDs** and read the tracking ID, then confirm that the three supplied links carry it. If they do not, rebuild each link from the Product Linking tool.",
 "In Associates Central, open **Manage Tracking IDs** and read the tracking ID, then confirm that the three supplied links carry it. If they do not, rebuild each link from the Product Linking tool. "
 "[Updated 2026-11-17: the site no longer sends readers through the supplied short links — every outbound link is now a tagged canonical /dp/ URL "
 "(main, F82), so the check that remains is a report row, not a link inspection: read the Tracking ID Summary Report (S41) after a click. "
 "Register note: this repository holds {n_submitted_links} submitted links.]")
if dt == n0:
    problems.append("decision.json: neither stale sentence was found to annotate")
dp.write_text(dt, encoding="utf-8")

print("data layer applied:",
      "+4 sources;", "+2 product-intent corrections;", "+1 collector block;",
      "+3 suggestions +P6;", "+2 questions;", "+2 topics;", "+3 requirement rows;", "2 decision.json annotations")
if problems:
    print("WARNINGS:", problems)
