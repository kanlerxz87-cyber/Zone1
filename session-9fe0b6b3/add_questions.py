"""Append pass-13 open questions to data/questions.json.

Each row separates what is known from what is missing, and names the concrete
step that would discover the missing part. Nothing is inferred into an answer.
"""
import collections
import json

P = "data/questions.json"

S2 = "https://affiliate-program.amazon.com/help/operating/policies"
S36 = "https://affiliate-program.amazon.com/help/node/topic/GM6CHU93RDXZV7D8"
S1 = "https://affiliate-program.amazon.com/help/operating/agreement"
S38 = "https://www.amazon.com/dp/B0DHZTCNR5"
S39 = "https://www.amazon.com/dp/B0DZFD6R9Z"
S4 = "https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM"
FTC = "https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews"


def ev(label, url):
    return collections.OrderedDict([("label", label), ("url", url)])


ROWS = [
    collections.OrderedDict([
        ("id", "Q-27"),
        ("group", "Product set"),
        ("question", "Were the two meat-thermometer links supplied for this site, or do they belong to a different project?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "Three of the five supplied links land in the Air Fryers browse node. The two added "
         "on 2026-11-17 land in Thermometers & Timers > Meat. This site is built as a "
         "single-category publication: its tagline, buying guide, comparison narrative and "
         "chooser all assume an air fryer. If the thermometers are in scope, those pages have "
         "to be rewritten; if they are not, two supplied products never get marketed. Either "
         "answer is workable. Not deciding is the one option that wastes the links."),
        ("what_we_know", [
            "Both new links resolve reproducibly: B0c8moW59 to ASIN B0DHZTCNR5 and B0f3GKalj to ASIN B0DZFD6R9Z, confirmed twice each on 2026-11-17 by following the short link and by requesting /dp/<ASIN> directly.",
            "Both listings carry the browse path Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat.",
            "The CHEF iQ listing title contains the phrase 'Air Fryer', but as one of the appliances the thermometer is used with, not as the product type.",
            "Both products are registered in the dataset with every specification cell blank, because no brand page or owner's manual for them has been read.",
        ]),
        ("what_is_missing",
         "Any statement of intent. Nothing published by Amazon says which products a supplied "
         "short link was created to promote, and a reproducible destination is not an "
         "intention - which is why the product-link register keeps the two in separate fields."),
        ("how_to_discover",
         "Ask the account holder which products the site is meant to sell, then confirm "
         "against Associates Central: the link builder shows the ASIN each Special Link was "
         "created for. Until then the register records the observed destination only."),
        ("blocks", ["SG-31", "SG-36"]),
        ("sources", [
            ev("Amazon listing B0DHZTCNR5 - ThermoMaven thermometer (S38)", S38),
            ev("Amazon listing B0DZFD6R9Z - CHEF iQ Sense Gen3 thermometer (S39)", S39),
        ]),
        ("answer", ""),
    ]),
    collections.OrderedDict([
        ("id", "Q-28"),
        ("group", "Attribution"),
        ("question", "Does the Selected Tracking ID that was supplied belong to this account, and is it attached to the five published links?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "A tracking ID is what turns a click into a commission. If the supplied ID is not "
         "the one inside the five short links, every click the site earns is unattributed, "
         "and there is no way to discover that from outside the account. This is the single "
         "highest-value unknown on the site."),
        ("what_we_know", [
            "A Selected Tracking ID was supplied on 2026-11-17 and is recorded in the product-link register.",
            "Amazon's own help states that its software 'automatically adds \"-20\" to the end of all Associate IDs', so the supplied string has the documented shape of a US Associates Store/Tracking ID (S36).",
            "That is a statement about format only. It is not evidence of ownership, of an approved account, or of attachment to these links.",
            "No resolved link URL observed on any of the eight recorded rounds has carried a visible tag= parameter (F6).",
        ]),
        ("what_is_missing",
         "Ownership and attachment. Both live inside Associates Central, behind a sign-in "
         "this repository does not have."),
        ("how_to_discover",
         "Sign in to Associates Central, open Manage your Tracking IDs, and confirm the "
         "supplied ID appears there. Then generate one Special Link per ASIN with that ID, "
         "click it, and confirm the click lands against that ID in the tracking report "
         "before scaling to the rest. See SG-38."),
        ("blocks", ["SG-38"]),
        ("sources", [
            ev("Amazon Associates help - tracking ID format and Manage your Tracking IDs (S36)", S36),
            ev("Associates Program Policies (S2)", S2),
        ]),
        ("answer", ""),
    ]),
    collections.OrderedDict([
        ("id", "Q-29"),
        ("group", "Measurement"),
        ("question", "Where will the self-hosted analytics endpoint actually run?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "The brief asks for a self-hosted endpoint. GitHub Pages serves static files and "
         "cannot execute server-side code, so this site cannot host its own collector. Until "
         "there is somewhere for the counter to send events, the site measures nothing and "
         "the next editorial topic is chosen by instinct."),
        ("what_we_know", [
            "Five events are defined and the client counter ships on every page: page_view, guide_read, chooser_complete, outbound_click and subscribe.",
            "The endpoint contract is fixed and a reference collector is included in the repository at analytics/collect.js.",
            "No endpoint URL is configured, so events are currently counted in the page's own memory for the current visit and nothing leaves the browser. The site says so plainly rather than implying measurement that does not exist.",
            "A static host also means the endpoint cannot be a path on this domain unless a proxy is introduced, which would change the privacy posture.",
        ]),
        ("what_is_missing",
         "A host. A worker, a serverless function, or the operator's own server - any will "
         "do, and filling in one URL turns collection on with no other change."),
        ("how_to_discover",
         "Choose a host that can run the reference collector, deploy it, and set the "
         "endpoint URL in data/analytics.json. The build guard will then require the footer's "
         "privacy notice to change in the same commit, so the disclosure cannot drift."),
        ("blocks", ["SG-37", "SG-39", "SG-41"]),
        ("sources", [
            ev("Associates Program Policies - cookie and third-party technology disclosure (S2)", S2),
            ev("FTC - Endorsements, Influencers, and Reviews", FTC),
        ]),
        ("answer", ""),
    ]),
    collections.OrderedDict([
        ("id", "Q-30"),
        ("group", "Content strategy"),
        ("question", "Which of the four working titles gets written first, and what decides it?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "Four question-shaped titles were supplied as editorial hypotheses. They are "
         "working titles, not claims about popularity - nothing on this site asserts that "
         "anyone searches for them. Publishing all four at once produces four unmeasured "
         "articles; publishing them in sequence lets the second be chosen with the first's "
         "arrival data in hand."),
        ("what_we_know", [
            "The four supplied working titles are: 'Basket or oven-style air fryer: what should you compare?', 'A no-hype checklist for comparing air-fryer capacity', 'How to assess cleanup and counter-space trade-offs', and 'Questions to ask before buying a multi-function kitchen appliance.'",
            "No search-volume, trend or popularity data has been obtained for any of them, and none is claimed anywhere on this site.",
            "Amazon's own application guidance refers to a body of posts and to content being recent, so cadence matters to the account as well as to search (S4).",
        ]),
        ("what_is_missing",
         "Any measured signal. Without an analytics endpoint there is no arrival data; with "
         "Search Console registered there would be query data, but only after the pages exist "
         "and have been crawled."),
        ("how_to_discover",
         "Register the site in Search Console (SG-29), publish one guide, wait for the first "
         "impression and query data, then choose the next title from what actually arrived "
         "rather than from the order the hypotheses were listed in."),
        ("blocks", ["SG-40"]),
        ("sources", [
            ev("Amazon Associates - Application Review Process (S4)", S4),
        ]),
        ("answer", ""),
    ]),
    collections.OrderedDict([
        ("id", "Q-31"),
        ("group", "Compliance"),
        ("question", "Who is the named reviewer for the judgement half of the compliance gate?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "The mechanical half of compliance is already enforced by the build: every page "
         "carries the Associates disclosure above the fold, every outbound product link is "
         "marked rel=\"sponsored\", no page publishes an Amazon price or rating, and no "
         "article claims a test that did not happen. What a build cannot judge is whether a "
         "disclosure is clear and conspicuous in context, or whether an endorsement reads as "
         "an honest opinion. Someone has to own that, by name."),
        ("what_we_know", [
            "The FTC's guidance is that a disclosure must be clear and conspicuous, which is a contextual judgement (S24/FTC).",
            "The Operating Agreement and Program Policies are the contract the site publishes against (S1, S2).",
            "No named reviewer is recorded anywhere in this repository.",
        ]),
        ("what_is_missing", "A name, and a cadence for the review."),
        ("how_to_discover",
         "Name one person and a review cadence, and record both. Until then the mechanical "
         "gate is doing all the work and the judgement gate is unstaffed."),
        ("blocks", ["SG-43"]),
        ("sources", [
            ev("FTC - Endorsements, Influencers, and Reviews", FTC),
            ev("Associates Program Operating Agreement (S1)", S1),
            ev("Associates Program Policies (S2)", S2),
        ]),
        ("answer", ""),
    ]),
    collections.OrderedDict([
        ("id", "Q-32"),
        ("group", "Product identity"),
        ("question", "What are the model numbers and manufacturer specifications for the two thermometers?"),
        ("state", "not_stated"),
        ("why_it_matters",
         "Both thermometers are registered with every specification cell deliberately blank, "
         "because the only official document read for them is the Amazon listing. Listing "
         "titles carry claims - '3 Ultra-Thin Probes', '1000F Heat Safe', '±0.5F Accuracy' - "
         "and a title claim is not a manufacturer specification. Copying them into the "
         "verified column would be the exact inference this site exists to avoid."),
        ("what_we_know", [
            "Both ASINs and listing titles are confirmed from two independent reads on 2026-11-17.",
            "No ThermoMaven-owned or CHEF iQ-owned product page, and no owner's manual, has been located and read by this pass.",
            "The three air-fryer products show the difference a manual makes: 75 of 77 specification rows are verified because brand pages and manuals were read.",
        ]),
        ("what_is_missing",
         "Every specification. Brand product pages and owner's manuals for both models."),
        ("how_to_discover",
         "Locate each brand's own product page and the owner's manual PDF, then quote from "
         "them the way the air-fryer rows are quoted. If a brand publishes no specification "
         "sheet, the honest outcome is a permanently blank row, which the site renders and "
         "flags rather than fills in."),
        ("blocks", ["SG-31"]),
        ("sources", [
            ev("Amazon listing B0DHZTCNR5 - ThermoMaven thermometer (S38)", S38),
            ev("Amazon listing B0DZFD6R9Z - CHEF iQ Sense Gen3 thermometer (S39)", S39),
        ]),
        ("answer", ""),
    ]),
]


def main():
    with open(P, encoding="utf-8") as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    have = {q["id"] for q in d["questions"]}
    added = 0
    for row in ROWS:
        if row["id"] in have:
            print("already present:", row["id"])
            continue
        d["questions"].append(row)
        have.add(row["id"])
        added += 1
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"added {added}; questions now {len(d['questions'])}")


if __name__ == "__main__":
    main()
