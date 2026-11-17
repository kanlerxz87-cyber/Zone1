#!/usr/bin/env python3
"""pass 13, final scope — data layer (session 58cbaaa2, 2026-11-17, applied onto main 4609ff3).

Additive only: main's registers are canonical, so this script extends them with the four official
pages this pass read that were not registered, the brand-catalogue check for the two newly submitted
links, the dated correction about what a landing URL can show, and the decision rows those create.
Each file is rewritten in its own existing indentation style so the diff stays purely additive.
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/user/Zone1")
HELPS = "https://affiliate-program.amazon.com/help/node/topic/"
SITE = "https://kanlerxz87-cyber.github.io/Zone1"
notes = []


def style_of(path):
    """(indent, ensure_ascii) that reproduces the file's current serialisation, best effort."""
    raw = path.read_text(encoding="utf-8")
    d = json.loads(raw)
    for indent in (1, 2, 4, None):
        for ea in (False, True):
            probe = json.dumps(d, indent=indent, ensure_ascii=ea) + "\n"
            if probe == raw:
                return indent, ea
    # fall back to matching the first line's leading whitespace
    lead = len(raw.splitlines()[1]) - len(raw.splitlines()[1].lstrip()) if len(raw.splitlines()) > 1 else 1
    return (lead or 1), False


def load(name):
    p = ROOT / name
    return json.loads(p.read_text(encoding="utf-8"))


def save(name, data):
    p = ROOT / name
    indent, ea = style_of(p)
    p.write_text(json.dumps(data, indent=indent, ensure_ascii=ea) + "\n", encoding="utf-8")
    notes.append(f"{name}: indent={indent}")


# ───────────────────────────────────────────────────────────────────────── sources
s = load("data/sources.json")
have = {x["id"] for x in s["sources"]}
new = [
 {"id": "S39", "org": "CHEF iQ (brand)", "url": "https://chefiq.com/products/iq-sense",
  "title": "CHEF iQ iQ Sense wireless meat thermometer — official product page",
  "covers": "The brand's own model designation, probe configuration and ambient rating for the iQ Sense, checked against the listing observed at /dp/B0DZFD6R9Z",
  "kind": "Brand product page", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1). The brand page states model CQ60-3C-Z3-E, the Gen3 probe "
   "configuration and an ambient rating the observed Amazon listing does not repeat, and lists air-fryer use among the "
   "product's heat environments. It does not mention an Amazon ASIN. Registered because it is what the manufacturer "
   "states, not because it confirms a listing identity — see flag F80. Evidence: "
   "reports/verification-2026-11-17-58cbaaa2.md.")},
 {"id": "S40", "org": "ThermoMaven (brand)", "url": "https://www.thermomaven.com/",
  "title": "ThermoMaven official site — instant-read and wireless thermometer line-up",
  "covers": "The brand's own instant-read model names, checked against the '1 Sec' title on the listing observed at /dp/B0DHZTCNR5",
  "kind": "Brand site", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1). The brand's instant-read line is named F1 Pro / F1 Turbo "
   "with a sub-second read; the site does not use '1 Sec' as a model name. Recorded as a divergence, not resolved: "
   "this site makes no claim about which product the submitted short code was created to promote (flag F80, Q-27). "
   "Evidence: reports/verification-2026-11-17-58cbaaa2.md.")},
 {"id": "S41", "org": "Amazon.com Associates Central", "url": HELPS + "GF4RJEQNXSMR7SP3",
  "title": "Why doesn't my tracking ID appear in your URL after a visitor clicks through to Amazon from my Web site?",
  "covers": "Whether an absent tag= parameter on a landing URL can be read as evidence about attribution",
  "kind": "Help article", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1), from the linked-topic list on S6. Full answer, verbatim: "
   "\u201cWe understand your concern, but rest assured that it is not necessary for your unique ID to appear in order "
   "for us to track sales made after the initial click through. The individual shopping session will be tagged in a way "
   "that allows us to track the items purchased and credit you with the appropriate commission.\u201d This is the "
   "official statement that a landing URL without a visible tag is not evidence either way; it says nothing about "
   "whether a particular link carries a particular ID. Flag F81.")},
 {"id": "S42", "org": "Amazon.com Associates Central", "url": HELPS + "GJDYPQZK6E37RLPU",
  "title": "How do I request multiple tracking IDs?",
  "covers": "Where additional tracking IDs are created, the 100-per-account limit, and the report where each ID's data is read",
  "kind": "Help article", "directness": "Primary",
  "page_version": ("Read 2026-11-17 (arena/58cbaaa2-zone1), from the linked-topic list on S6. Verbatim: to create "
   "multiple IDs, \u201cvisit your account and click on \u2018Manage your Tracking ID\u2019\u201d (linked as "
   "https://affiliate-program.amazon.com/home/account/tag/manage); \u201cOnce they have been created, you will be able "
   "to see data on each ID in your Tracking ID Summary Report\u201d; \u201cthere is a limit of 100 Tracking IDs per "
   "associate account\u201d, with Associates Customer Service named for further requirements. This is where the "
   "enrolled-Associates test result this site waits for is actually read, and it is the second official page naming "
   "that screen.")},
]
for x in new:
    if x["id"] not in have:
        s["sources"].append(x)
for x in s["sources"]:
    if x["id"] == "S6" and "2026-11-17" not in str(x.get("page_version", "")):
        x["page_version"] = (str(x.get("page_version", "")) + " Re-read verbatim 2026-11-17 (arena/58cbaaa2-zone1) "
                             "because the account holder supplied a tracking ID that day: the worked example remains "
                             "'storeid-20' with sub-tag 'storeid-1-20'; each ID can be reported individually; new IDs "
                             "are created at Associates Central > 'Manage your Tracking ID'. The node states no "
                             "validation rule and publishes no per-account list, so it can confirm the shape of an ID "
                             "and nothing more.")
save("data/sources.json", s)

# ────────────────────────────────────────────────────────────────────────── verify.py
v = ROOT / "verify.py"
vt = v.read_text(encoding="utf-8")
if "chefiq.com" not in vt:
    anchor = 'OFFICIAL_HOSTS = {'
    i = vt.index(anchor) + len(anchor)
    vt = (vt[:i] + "\n    # Brand pages read 2026-11-17 against the two links submitted that day (sources S39/S40).\n"
          "    # Registered as official brand sites, which is not the same as confirming a listing identity: F80.\n"
          '    "chefiq.com",\n    "www.thermomaven.com",' + vt[i:])
    v.write_text(vt, encoding="utf-8")
    notes.append("verify.py: two brand hosts allow-listed")

# ───────────────────────────────────────────────────────────────── product-intent.json
pi = load("data/product-intent.json")
brand = {
 "PI-04": {
  "listing_says": ("Title as served on 2026-11-17: 'ThermoMaven 1 Sec Professional Digital Meat Thermometer, "
                   "\u00b10.5\u2109 Accuracy | NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, "
                   "Highly Waterproof for Grill BBQ Camping, Black'. No model number in the fetched portion of the page."),
  "brand_page_says": ("ThermoMaven's own site names its instant-read line F1 Pro and F1 Turbo and states a "
                      "sub-second read; '1 Sec' is not used there as a model name."),
  "verdict": ("Not reconciled. The brand catalogue and the listing title use different kinds of identifier and "
              "neither names the ASIN, so the intended product stays null and no product page is written."),
  "source_ids": ["S40", "S36", "S23"],
 },
 "PI-05": {
  "listing_says": ("Title as served on 2026-11-17: 'CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin "
                   "Probes | Gen3'. No model number in the fetched portion of the page."),
  "brand_page_says": ("CHEF iQ's iQ Sense product page states model CQ60-3C-Z3-E, the Gen3 probe configuration and an "
                      "ambient rating the listing does not repeat, and names air-fryer use among the heat environments "
                      "the product is sold for."),
  "verdict": ("Consistent with, not confirmed by. A brand model designation the listing does not carry cannot be "
              "transcribed into an intended-ASIN field, so the row stays open pending Q-27."),
  "source_ids": ["S39", "S37", "S23"],
 },
}
for r in pi["rows"]:
    bc = brand.get(r["id"])
    if bc and not r.get("brand_catalogue_check"):
        r["brand_catalogue_check"] = bc
        ids = r.setdefault("observed_source_ids", [])
        for sid in bc["source_ids"]:
            if sid not in ids:
                ids.append(sid)
        r["note"] = ((r.get("note") or "") + " Brand catalogue read against this listing on 2026-11-17 (S39/S40): "
                     "reconciles with, but does not confirm, the candidate destination — flag F80; the "
                     "associates_link_test fields stay empty because a URL inspection is not a link test (S41).").strip()
if "observation_method_correction" not in pi:
    pi["observation_method_correction"] = {
     "date": "2026-11-17",
     "read_by": "arena/58cbaaa2-zone1",
     "what_changed": (
      "Two official help nodes read on this date narrow what a landing URL can be said to show. Amazon states that a "
      "tracking ID 'is not necessary … to appear in order for us to track sales made after the initial click through', "
      "because the session is tagged on Amazon's side (S41). So the absence of a tag= parameter on an observed URL is "
      "a null observation, not evidence that a link failed to attribute, and no row on this record may be read that "
      "way in either direction."),
     "what_still_cannot_be_seen": (
      "The positive: whether the selected ID is listed on the account, and whether a click through a published link "
      "appears under it. That is read in the Tracking ID Summary Report named by S42, and it requires the account "
      "holder's login. Until it is, the correct statement is the one this file already makes — the tag is recorded, "
      "not validated, and not applied to links."),
     "where_it_applies": (
      "The inference is corrected where it is drawn in the present tense: the link-intent page carries this note "
      "next to the per-row test fields, and flag F81 records it. Historical rows, including the F76 observation and "
      "the dated flag prose about no tag appearing, are left exactly as written — they are records of what those "
      "passes observed, and rewriting them would remove the audit trail that makes them evidence."),
     "sources": ["S41", "S42", "S6"],
    }
if "sub_tag_plan" not in pi:
    pi["sub_tag_plan"] = {
     "what": ("S42 records that additional tracking IDs are created at Associates Central > Manage your Tracking ID, "
              "that each one is reported in the Tracking ID Summary Report, and that an account may hold up to 100. "
              "One ID per channel — site, newsletter, social — separates traffic sources inside Amazon's own "
              "reporting, with no script on this site, nothing new to host and no new technology to disclose."),
     "limit": ("It attributes a channel, not a page: clicks and orders arrive per tracking ID, not per URL. Page-level "
               "questions stay with the five event definitions on measurement.html, which remain disabled until the "
               "endpoint contract there is satisfied."),
     "status": "proposed; needs the account holder to create the IDs in Associates Central",
     "sources": ["S42", "S6"],
    }
save("data/product-intent.json", pi)

# ────────────────────────────────────────────────────────────────────── suggestions
sg = load("data/suggestions.json")
clash = {x["id"] for x in sg["suggestions"]} & {"SG-36", "SG-37", "SG-38"}
if clash:
    sys.exit(f"suggestions already present: {sorted(clash)}; aborting")
sg["suggestions"].extend([
 {
  "id": "SG-36",
  "title": "Decide what happens to the two links that are not air fryers — with the paths in front of you",
  "area": "Product set and scope",
  "problem": ("main's F77 records the observation and asks the owner to say what the two links submitted on 2026-11-17 "
   "were meant to promote, or drop them. What a register cannot do is present the choice, and this is now a choice "
   "with a cost attached to delay: the brand-catalogue check (F80) shows the two candidate listings do not reconcile "
   "with either manufacturer's own model names, so the rows cannot be closed by reading harder, while every new "
   "article written for 'three air fryers' deepens a frame the owner may already have outgrown. Publishing the two "
   "thermometers from a fallback destination would build a second shallow footprint on top of the first."),
  "evidence": [
   {"label": "Link-intent record, PI-04 and PI-05 with the brand-catalogue check", "url": f"{SITE}/product-intent.html"},
   {"label": "Flag F80 — what the two brand pages do and do not settle", "url": f"{SITE}/flagged.html#f80"},
   {"label": "CHEF iQ iQ Sense page (brand-official)", "url": "https://chefiq.com/products/iq-sense"},
   {"label": "ThermoMaven official site (its own model names)", "url": "https://www.thermomaven.com/"},
   {"label": "data/product-intent.json", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/data/product-intent.json"}
  ],
  "options": [
   {"label": "A. Park both rows: the register keeps them, the site publishes neither",
    "what": "Zero new pages. The site keeps one reader intent, one internal-link graph and one set of sourced claims, and both links stay available the moment their identity is confirmed.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Stand up a thermometer category — after the documents, in that order",
    "what": "Confirm the intended product (Q-27), read the brand pages and manuals into the source register, then write one comparison and one guide. In this order a second category is a publication; in the reverse order it is two thin sites sharing a domain.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Follow the newest links and re-plan the site around thermometers",
    "what": "Treat the two most recent submissions as the direction and archive the air-fryer set. Cheapest to justify if the owner says so in one sentence; destructive to infer from a URL.",
    "effort": "L", "risk": "high", "reversible": False}
  ],
  "recommendation": "A. Publish nothing new from an unconfirmed identity; keep the register as the visible record and choose B or C only after Q-27 is answered.",
  "why": ("The site's only durable asset is that a reader can check every row. A page about a product nobody confirmed "
   "the link points at spends that asset to gain two pages."),
  "impact": 5, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Medium and rising: re-framing later means rewriting the navigation, the category page and the "
   "internal-link graph, not just adding pages — and the category lede has already had to be repaired once because "
   "the count was typed rather than read (F82)."),
  "blocks": [],
  "blocked_by": ["Q-27"]
 },
 {
  "id": "SG-37",
  "title": "Close the attribution question where it can actually be closed: one click, read in the Tracking ID Summary Report",
  "area": "Attribution",
  "problem": ("The repository now holds the right machinery and the right blank fields: the tracking ID is recorded as "
   "user-provided and unvalidated, associate_tag is deliberately blank, F76 states that no link is confirmed to carry "
   "it, and every row has associates_link_test_passed/date/source fields waiting for a result that only the account "
   "holder can produce. What was missing is the statement of *where* the result is read — and a caution: reading a "
   "landing URL is not a test. Amazon's own help node (S41) says the ID need not appear in the URL at all, so the "
   "observations this project has accumulated about clean landing URLs cannot fill those fields. S42 names the "
   "screen that creates IDs, the Tracking ID Summary Report where per-ID data appears, and the limit of 100 IDs per "
   "account, which is what makes a per-channel scheme cheap enough to do in the same sitting."),
  "evidence": [
   {"label": "Amazon — where IDs are created, the 100-per-account limit, the report that reads them", "url": HELPS + "GJDYPQZK6E37RLPU"},
   {"label": "Amazon — a tag need not appear in the click-through URL", "url": HELPS + "GF4RJEQNXSMR7SP3"},
   {"label": "Amazon — what tracking IDs are, and the storeid-20 example (re-read verbatim 2026-11-17)", "url": HELPS + "GK5TZZ4AWML2QSLA"},
   {"label": "Flag F81 — the over-reading, corrected on the record", "url": f"{SITE}/flagged.html#f81"},
   {"label": "The record carrying the per-row test fields", "url": f"{SITE}/product-intent.html"}
  ],
  "options": [
   {"label": "A. Confirm the ID, click one published link, read the report, write the result back",
    "what": "Check shopnow047c-20 is listed at Manage your Tracking ID; click one published product link; confirm the click appears in that ID's report. Then fill associates_central_confirmation_date/source and the per-row test fields in data/product-intent.json — a later pass can then set associate_tag with the contract in tests/test_build_contract.py satisfied, and nothing else needs to change.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "B. A, plus one ID per channel while you are in there",
    "what": "Same screen, a few more minutes. Per-channel IDs give clicks and orders per channel inside Amazon's reporting with no code on this site; S42 records 100 per account, so there is room for site, newsletter and social.",
    "effort": "S", "risk": "low", "reversible": True},
   {"label": "C. Leave the fields empty",
    "what": "Status quo, which is the correct default and is worth naming: unvalidated tag, untagged links, no attribution, no earnings. It is defensible for a publication whose value is its sources and indefensible for an affiliate site.",
    "effort": "0", "risk": "medium", "reversible": True}
  ],
  "recommendation": "A, then B in the same sitting — and never a URL inspection as a substitute for the report row.",
  "why": ("It is the one queue item where a five-minute check by the only person with account access converts a whole "
   "site from 'content that might earn' to 'content that is attributed', and it is the only item that closes F76, "
   "F81 and the per-row test fields at once."),
  "impact": 5, "confidence": 5, "effort": "S",
  "risk_of_not_doing": "High in the narrow sense that matters: an unattributed click is the same as no click.",
  "blocks": [],
  "blocked_by": ["Q-28"]
 },
 {
  "id": "SG-38",
  "title": "Settle what the measurement layer is allowed to become, so the disabled collector stops being an open question in three files at once",
  "area": "Measurement",
  "problem": ("Three places currently describe one decision in different tenses: data/measurement.json holds five events "
   "with status defined_not_shipped, analytics/collector.py is a working fail-closed service that GitHub Pages does not "
   "run and that refuses events until four operator-set conditions are met, and the footer tells readers that browser "
   "collection is disabled and nothing is sent. All three are true today. None of them says what the project intends, "
   "which is the condition under which a 'proposed' page turns into an unowned surface a later pass quotes. This "
   "session built a cookieless, request-free browser tally for EV-02/EV-04 while working on an older base, found main "
   "carrying the opposite posture behind a test (tests/test_build_contract.py), and withdrew it rather than merge "
   "around a decision — the option set below is that withdrawn work, offered as a choice instead of a fait accompli."),
  "evidence": [
   {"label": "The event definitions and the deployment gate", "url": f"{SITE}/measurement.html"},
   {"label": "The collector the repository already ships, and its fail-closed contract", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/analytics/collector.py"},
   {"label": "The test that enforces collection staying off", "url": "https://github.com/kanlerxz87-cyber/Zone1/blob/main/tests/test_build_contract.py"},
   {"label": "Program Policies §3(e), the disclosure any collection triggers", "url": "https://affiliate-program.amazon.com/help/operating/policies"},
   {"label": "Amazon — per-ID reporting, the option needing no code on this site", "url": HELPS + "GJDYPQZK6E37RLPU"}
  ],
  "options": [
   {"label": "A. Keep collection off; run per-channel tracking IDs instead, and re-point the page at Amazon's numbers",
    "what": "SG-37 path B does the measuring with no new technology to host or disclose. measurement.html gains one line saying which channel question the report answers and which it does not, and the footer statement stays accurate without amendment.",
    "effort": "S", "risk": "none", "reversible": True},
   {"label": "B. Deploy the collector the repository already contains, then wire EV-01 to EV-04 to it",
    "what": "Host analytics/collector.py on any origin the owner controls, set the four environment conditions, approve the privacy and retention notice, test the event flow, and only then change the footer in the same commit — the sequence the collector's own docstring and the build contract both require. The campaign ledger still fills only from an authorized report (report_import.py), never from the event stream.",
    "effort": "L", "risk": "medium", "reversible": True},
   {"label": "C. Ship the local-only tally as a labelled diagnostic, endpoint still absent",
    "what": "What this session had built: counts kept in the reader's own browser, no cookie, no request, no identifier, export and erase on the measurement page, and an honest label that a single device cannot say anything about an audience. Cheapest instrument that tests whether the links work. Rejected as a unilateral move on purpose: it makes the footer's 'browser collection remains disabled' sentence false, and a decision that flips a tested, merged posture belongs to the owner, not to a pass.",
    "effort": "M", "risk": "medium", "reversible": True}
  ],
  "recommendation": "A now, B when there is somebody to read the numbers, C only as an explicit amendment to the footer statement in the same commit.",
  "why": ("A improves decision quality today at zero compliance cost and is the only option that needs nothing the "
   "account holder has not already been asked for in SG-37. The ledger stays empty in all three cases, because nothing "
   "authorized has been recorded — that is the design, not a shortfall."),
  "impact": 4, "confidence": 4, "effort": "S",
  "risk_of_not_doing": ("Low as a breach risk while collection stays off, and rising as a documentation risk: an event "
   "specification nobody owns and a service nobody deploys is how a later pass ends up quoting a number that was never "
   "measured."),
  "blocks": [],
  "blocked_by": []
 },
])
sg["pass"] = (sg.get("pass", "") +
 "; SG-36..SG-38 and path P6 by arena/58cbaaa2 (2026-11-17) — written twice, and shortened the second time: "
 "the first draft's parallel intent register, measurement register and flags were dropped when main's merged "
 "registers and collection-disabled contract were found. The withdrawn draft is published at "
 "session-58cbaaa2/artifacts/.")
if not any(p.get("id") == "P6" for p in sg.get("paths", [])):
    sg.setdefault("paths", []).append({
     "id": "P6",
     "name": "Make the money path real: five links, one tag, one report row",
     "promise": ("Turn what the owner supplied on 2026-11-17 — two more links and a tracking ID — into a site whose "
                 "commercial links are attributed on evidence rather than on assumption, and whose product set is a "
                 "decision instead of an accident."),
     "contains": ["SG-36", "SG-37", "SG-38"],
     "effort": "S (two of the three rows are a browser, a report and five minutes; the third is a reading-and-choosing task)",
     "must_be_true_first": ("Nothing outside the owner's screens. The intent register, the link-test fields, the "
                            "tagging contract and the five event definitions are merged and enforced by the build, so "
                            "this path answers questions rather than waiting on code."),
     "delivers": ("Every submitted link confirmed or explicitly parked; a tracking ID whose attribution has been "
                  "observed in the Tracking ID Summary Report rather than inferred from markup; a per-channel sub-tag "
                  "scheme that needs no infrastructure; and a measurement layer whose status, service and disclosure "
                  "say the same thing in the same tense."),
     "does_not_fix": ("It will not produce a conversion figure. Orders come from an authorized first-party report, and "
                      "the campaign ledger's first row is transcribed by a human or does not exist."),
     "pick_this_if": "You intend to earn from this site rather than merely publish it.",
     "why_first": ("It is the only path where the owner's own action unblocks the largest number of other rows, and the "
                   "only one whose entire bottleneck is a login this repository will never have."),
    })
save("data/suggestions.json", sg)

# ──────────────────────────────────────────────────────────────────────── questions
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
   "F80 shows the two candidates do not reconcile with either manufacturer's own model names — so this cannot be "
   "settled by a pass reading harder."),
  "what_we_know": [
   "Both links were re-read live on 2026-11-17: PI-04 lands on /dp/B0DHZTCNR5 and PI-05 on /dp/B0DZFD6R9Z, each with the same lv=shuf / plpRedirect=mhFallback fallback form recorded for the original three, and neither landing URL carrying an asin= parameter.",
   "Amazon files both candidates under Kitchen Utensils & Gadgets > Thermometers & Timers > Meat — a different browse path from the air-fryer listings this site is built around (F77).",
   "The brands' own pages were read the same day: ThermoMaven names its instant-read line F1 Pro / F1 Turbo and does not use the '1 Sec' label the listing carries; CHEF iQ states model CQ60-3C-Z3-E for the iQ Sense, a designation the listing does not repeat, and names air-fryer use among that product's heat environments.",
   "intended_asin, official_listing_url, confirmation_date and confirmation_source are null on both rows by construction, and the observed destinations live only in the observed_* fields."
  ],
  "what_is_missing": ("A statement from the account holder of which product each link was created to promote — ideally "
                      "the official /dp/ URL they entered in the Link Building tool, with the date it was checked in "
                      "their own browser. 'The link was sent in error' is a complete answer and closes the row."),
  "how_to_discover": ("Open each submitted link in the browser signed in to the Amazon account and read the listing "
   "title plus the model line in Product information; compare it with what you meant to promote and with the brand "
   "pages registered as S39/S40. If it matches, fill the four intended fields on that row of data/product-intent.json; "
   "the build's contract then permits the tagging question to be taken up in order (Q-28)."),
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
  "why_it_matters": ("Until both halves are true the site cannot earn, and no page on it could tell you. A tag that "
   "does not exist attributes nothing; a tag that exists but is not the one attached attributes nothing either. "
   "Everything else in the queue — content, measurement, the category question — is downstream of one screen inside "
   "the account."),
  "what_we_know": [
   "The value was supplied by the account holder on 2026-11-17 and is recorded as user-provided; its shape matches the only example Amazon publishes (storeid-20, sub-tag storeid-1-20), re-read verbatim from S6 the same day.",
   "No official page states a validation rule or lists which IDs exist for which account, so a shape match cannot confirm existence, and the repository keeps associate_tag blank by contract rather than filling it.",
   "S41 states that a tracking ID need not appear in the click-through URL for a sale to be attributed, so the clean landing URLs observed for the submitted links neither support nor undermine anything: a URL inspection cannot fill the per-row associates_link_test fields.",
   "S42 names where the result is read — the Tracking ID Summary Report — and records the 100-IDs-per-account limit that makes a per-channel scheme practical (F81)."
  ],
  "what_is_missing": ("Two observations only the account holder can make: the ID present at Associates Central > Manage "
                      "your Tracking ID, and a click-through appearing in that ID's summary report."),
  "how_to_discover": ("Open Manage your Tracking ID and check for shopnow047c-20. Click one published product link. "
   "Read the Tracking ID Summary Report for that click. Write the date and the report name into "
   "data/product-intent.json's per-row associates_link_test_* fields and the associates_central_confirmation fields — "
   "the build contract in tests/test_build_contract.py then governs when the tag may be applied, and a later pass can "
   "close F76 and this row together."),
  "blocks": ["SG-37"],
  "sources": [
   {"label": "Amazon — how IDs are created and reported, and the limit per account", "url": HELPS + "GJDYPQZK6E37RLPU"},
   {"label": "Amazon — a tag need not appear in the URL to attribute the sale", "url": HELPS + "GF4RJEQNXSMR7SP3"},
   {"label": "Amazon — what a tracking ID is (re-read verbatim 2026-11-17)", "url": HELPS + "GK5TZZ4AWML2QSLA"}
  ]
 },
])
q["compiled"] = "2026-11-17"
q["version"] = str(q.get("version", "1.1"))
save("data/questions.json", q)

# ─────────────────────────────────────────────────────────────────────────── topics
tp = load("data/topics.json")
if any(x["id"] in {"TP-22", "TP-23"} for x in tp["topics"]):
    sys.exit("TP-22/TP-23 already present; aborting")
tp["topics"].extend([
 {
  "id": "TP-22",
  "title": "Can you leave a probe in an air fryer? What the manuals actually say",
  "hook": ("The appliance is built to run unattended. A wireless probe is built to be left in. Whether the two go "
           "together is a question the documents can answer."),
  "intent": "Informational",
  "serves": [],
  "angle": ("A reader who owns any of the three products has the same follow-up question: how do I know the chicken is "
   "done without opening the door. What this site can answer today is what the manuals and brand pages of the three air "
   "fryers say about the cavity, the rack positions and leaving the unit running — plus the fact that CHEF iQ lists "
   "air-fryer use among the iQ Sense's own heat environments (S39). What it will not do is assert a clearance, a "
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
  "status_note": ("Queued 2026-11-17 by arena/58cbaaa2 and deliberately not written. Writable from documents this site "
   "already cites; the half of the title that names a specific probe waits for Q-27. Numbered after 66c32067's TP-21, "
   "which this pass found already merged and did not renumber.")
 },
 {
  "id": "TP-23",
  "title": "Instant-read or wireless probe: which measurement answers the question you actually have",
  "hook": "One answers 'is this piece done right now'. The other answers 'when should I be home'.",
  "intent": "Comparison",
  "serves": [],
  "angle": ("Written only after the two newly submitted links are confirmed, and then from the brands' own documents: "
   "stated accuracy and read time from the manufacturer pages, never from a listing title, with an explicit statement "
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
  "status_note": ("Queued 2026-11-17 and waiting on Q-27. blocked_by is a register field for the reader's benefit, not "
   "a build gate; nothing here will write the piece early.")
 },
])
tp["compiled"] = "2026-11-17"
save("data/topics.json", tp)

# ───────────────────────────────────────────────────────────────────── requirements
rq = load("data/requirements.json")
rq["requirements"].extend([
 {
  "id": "H-01",
  "scope": "Brief",
  "requirement": "Record each submitted link with intended ASIN, official listing URL, confirmation date and source, kept separate from the observed redirect target",
  "clause": "Create a product-intent confirmation record for every submitted product link: intended ASIN, official listing URL, confirmation date, and source. Keep observed redirect targets in a separate field. Do not merge the two fields. Validate the supplied short links by testing one per product in the enrolled Associates workflow before scaling.",
  "status": "partial",
  "where": ["data/product-intent.json", "product-intent.html", "build.py", "tests/test_build_contract.py"],
  "evidence": [
   {"label": "the rendered record, with the brand-catalogue table and the method correction", "url": "product-intent.html"},
   {"label": "this pass's evidence file", "url": "reports/verification-2026-11-17-58cbaaa2.md"},
   {"label": "Amazon — where an enrolled link test is actually read", "url": HELPS + "GJDYPQZK6E37RLPU"}
  ],
  "why": ("The register, the field separation and the build contract were merged by other sessions; this pass added "
   "what they lacked — the brand-catalogue check on the two links submitted on 2026-11-17, which shows a listing "
   "marketing phrase and a manufacturer model number are different kinds of identifier and closes neither row (F80), "
   "and a dated correction of the inference that a landing URL without a visible tag says anything about attribution "
   "(F81, S41). Partial by arithmetic rather than by judgement: {n_submitted_links} rows, {n_intent_confirmed} with a "
   "confirmed intended product, {n_link_tests_passed} enrolled-Associates link tests recorded. Only the account holder "
   "can move those two numbers, which is Q-27 and Q-28."),
  "sources": ["S23", "S36", "S37", "S39", "S40", "S41", "S42"]
 },
 {
  "id": "H-02",
  "scope": "Site",
  "requirement": "Keep narrative counts in prose derived from the registers rather than typed into sentences",
  "clause": "Flag irregularities found during review; never let a published page assert something the data contradicts.",
  "status": "delivered",
  "where": ["build.py", "categories/kitchen-appliances.html", "data/product-intent.json"],
  "evidence": [
   {"label": "the guard", "url": "build.py"},
   {"label": "the category page whose lede was repaired", "url": "categories/kitchen-appliances.html"}
  ],
  "why": ("The category lede still described the submitted set as three links, present tense, two days after the "
   "register grew to five — every value inside the sentence correct, the sentence false, and no gate reading "
   "narrative. Repaired where the tense is present (the lede now reads len(rows) and the register's own "
   "observed_listing_category field, spelled by _num_word) and guarded by check_submitted_link_count(), scoped to the "
   "shopper surfaces and the two registers so a dated row that truthfully records 2026-11-14 cannot be 'fixed' by "
   "rewriting it. Recorded as F82 with the process note: when the owner submits another link, add a row, never a "
   "sentence."),
  "sources": ["S17"]
 },
])
save("data/requirements.json", rq)

# ─────────────────────────────────────────────────────────────────── decision.json
dp = ROOT / "data" / "decision.json"
dt = dp.read_text(encoding="utf-8")
n0 = dt
dt = dt.replace(
 "The three supplied links show no tag in their landing URL, so as supplied they are evidence of a destination, not of an attribution path.",
 "The three supplied links show no tag in their landing URL, so as supplied they are evidence of a destination, not of an attribution path. "
 "[Narrowed 2026-11-17 by arena/58cbaaa2: per S41 a tracking ID need not appear in the click-through URL for a sale to be "
 "attributed, so the absence of a tag= parameter is a null observation, not evidence about attribution. The five submitted "
 "links are recorded on product-intent.html; flag F81.]")
dt = dt.replace(
 "In Associates Central, open **Manage Tracking IDs** and read the tracking ID, then confirm that the three supplied links carry it. If they do not, rebuild each link from the Product Linking tool.",
 "In Associates Central, open **Manage Tracking IDs** and read the tracking ID, then confirm that the three supplied links carry it. If they do not, rebuild each link from the Product Linking tool. "
 "[Updated 2026-11-17: the confirmation that counts is a row in the Tracking ID Summary Report (S42), not a look at a link's "
 "destination — see Q-28 and SG-37 for the exact five minutes, and F76 for why the tag stays unapplied until they pass.]")
if dt == n0:
    notes.append("decision.json: neither sentence was found to annotate (left as is)")
dp.write_text(dt, encoding="utf-8")

print("data layer applied:", "; ".join(notes))
