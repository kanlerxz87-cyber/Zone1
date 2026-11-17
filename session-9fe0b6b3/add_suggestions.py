"""Append pass-13 decision rows to data/suggestions.json.

Each row states a problem, options with effort/risk, a recommendation, and the
official evidence the problem rests on. Nothing here is implemented by this pass
without an owner decision, except where the row says the default was taken.
"""
import collections
import json

P = "data/suggestions.json"

S2 = "https://affiliate-program.amazon.com/help/operating/policies"
S36 = "https://affiliate-program.amazon.com/help/node/topic/GM6CHU93RDXZV7D8"
S3 = "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ"
S4 = "https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM"
S1 = "https://affiliate-program.amazon.com/help/operating/agreement"
S38 = "https://www.amazon.com/dp/B0DHZTCNR5"
S39 = "https://www.amazon.com/dp/B0DZFD6R9Z"
FTC = "https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews"
FTC101 = "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers"
HELPFUL = "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"
SPAM = "https://developers.google.com/search/docs/essentials/spam-policies"
QUALIFY = "https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links"
PAGE_EXP = "https://developers.google.com/search/docs/appearance/page-experience"


def ev(label, url):
    return collections.OrderedDict([("label", label), ("url", url)])


ROWS = [
    collections.OrderedDict([
        ("id", "SG-31"),
        ("title", "Decide whether this site sells air fryers or kitchen tools — two of the five supplied links are meat thermometers"),
        ("area", "Product set"),
        ("problem",
         "Five product links have now been supplied. Three resolve into the Air Fryers browse "
         "node. The two added on 2026-11-17 resolve into a completely different node: Home & "
         "Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > "
         "Meat. One of them (CHEF iQ Sense Gen3) carries the word 'Air Fryer' inside its "
         "listing title, but only because an air fryer is among the appliances you use it with "
         "- a keyword match on titles files it in the wrong category. The site was built as a "
         "single-category publication: its tagline, buying guide, comparison narrative and "
         "three-question chooser all assume an air fryer. Both thermometers are now registered "
         "in the dataset with every specification cell blank, because no brand page or manual "
         "for them has been read. They are visible but not yet part of the story."),
        ("evidence", [
            ev("Amazon listing B0DHZTCNR5 — ThermoMaven 1 Sec thermometer, Thermometers & Timers > Meat (S38)", S38),
            ev("Amazon listing B0DZFD6R9Z — CHEF iQ Sense Gen3 thermometer, same browse node (S39)", S39),
            ev("Google Search Central — helpful, people-first content", HELPFUL),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Keep one category and retire the two thermometer links"),
                ("what", "The site stays a focused air-fryer publication. The two links stay recorded in the product-link register and on the flagged page, but are not built into product pages or guides."),
                ("effort", "S"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Run two categories and generalise the reader-facing pages"),
                ("what", "Rename the publication to something category-neutral, give each category its own pillar and chooser rules, and source real specifications for the two thermometers from brand pages and manuals."),
                ("effort", "L"), ("risk", "medium"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "C. Split the thermometers into their own site or section"),
                ("what", "Two publications, two audiences, no shared chooser. Highest cost, cleanest separation, and it doubles the domain-authority work."),
                ("effort", "L"), ("risk", "medium"), ("reversible", False),
            ]),
        ]),
        ("recommendation",
         "A for now if you want the site to rank for anything this quarter; B if the "
         "thermometers were supplied deliberately and are meant to be sold. Default taken "
         "by this pass: neither — the products are registered and flagged, and no "
         "category-facing page claims to describe them."),
        ("why",
         "A focused site with five documented products beats a general site with five thin "
         "ones, and the two thermometers currently have no manufacturer documentation behind "
         "them. Publishing them into the air-fryer comparison would make that comparison "
         "wrong, which is worse than leaving them out."),
        ("impact", 5),
        ("confidence", 5),
        ("effort", "M"),
        ("risk_of_not_doing",
         "Either the site silently mislabels two products, or two supplied products are "
         "never marketed at all."),
        ("blocks", ["SG-36", "SG-40"]),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "SG-36"),
        ("title", "Rebuild the front page as a publication front page, not a verification dashboard"),
        ("area", "Site design"),
        ("problem",
         "The landing page leads with counts: flags open, products compared, sources "
         "checked. That is the right front page for an audit and the wrong one for a shop. "
         "A reader arriving from search wants a question answered, not a methodology. The "
         "verification material is the site's proof and should stay one click away, but it "
         "should not be the first thing a buyer reads."),
        ("evidence", [
            ev("Google Search Central — helpful, people-first content", HELPFUL),
            ev("Google Search Central — page experience", PAGE_EXP),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Shop front: hero, featured guides, category tiles, picks, then the data"),
                ("what", "Editorial home page. Every dashboard surface moves behind a single navigation group and a complete footer index, so nothing becomes unreachable."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Restyle the existing dashboard"),
                ("what", "Keep the information order, improve the typography and spacing only."),
                ("effort", "S"), ("risk", "low"), ("reversible", True),
            ]),
        ]),
        ("recommendation",
         "A. The brief asks for a site that reads like a shop and like a publication; B "
         "polishes the wrong structure."),
        ("why",
         "Google's own guidance is that pages should be created for people first, and the "
         "evidence burden on an affiliate site is met by having the sources one click away, "
         "not by putting them on the front page."),
        ("impact", 4),
        ("confidence", 4),
        ("effort", "M"),
        ("risk_of_not_doing",
         "The site keeps reading like generated documentation, which is the exact complaint "
         "the brief raised."),
        ("blocks", []),
        ("blocked_by", ["SG-31"]),
    ]),
    collections.OrderedDict([
        ("id", "SG-37"),
        ("title", "Turn on measurement before writing the next guide, not after"),
        ("area", "Measurement"),
        ("problem",
         "The site counts nothing. It has no analytics, no outbound-click counter and no "
         "endpoint, while the footer correctly states that it sets no cookies and runs no "
         "analytics. That statement is true today and it is the reason the next editorial "
         "topic would be chosen by instinct. The five events are now defined and the "
         "counter ships on every page, but no endpoint is configured, so nothing is "
         "recorded yet."),
        ("evidence", [
            ev("Associates Program Policies — cookie and third-party technology disclosure (S2)", S2),
            ev("FTC — Endorsements, Influencers, and Reviews", FTC),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Self-hosted endpoint, five defined events, no cookies"),
                ("what", "Run the reference collector outside GitHub Pages and fill in one URL. Counts events, not people: no cookie, no cross-site identifier, no stored IP."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Client-side counts only, nothing leaves the browser"),
                ("what", "The counter runs and displays in-page totals for the current visit. Honest but not durable: you learn nothing about tomorrow's visitors."),
                ("effort", "S"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "C. Third-party analytics"),
                ("what", "Fastest to install, but it sets cookies or a device identifier, which changes the footer's privacy statement and adds a consent obligation."),
                ("effort", "S"), ("risk", "medium"), ("reversible", True),
            ]),
        ]),
        ("recommendation",
         "A, with B as the honest interim state. This pass shipped B and left the endpoint "
         "URL empty on purpose rather than pretending measurement is on."),
        ("why",
         "Measurement is only useful if the next topic is chosen from it, and a topic chosen "
         "from a number nobody can audit is the same as a topic chosen by instinct. Option C "
         "trades that for a cookie banner, and Program Policies require the disclosure to "
         "stay accurate."),
        ("impact", 5),
        ("confidence", 4),
        ("effort", "M"),
        ("risk_of_not_doing",
         "The publishing cadence becomes a content treadmill with no feedback loop, and the "
         "next ten articles are chosen the way the last ten were."),
        ("blocks", ["SG-40"]),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "SG-38"),
        ("title", "Test one link per product in the enrolled Associates workflow, then scale"),
        ("area", "Compliance"),
        ("problem",
         "Five link.amazon short links are published as the site's outbound calls to action, "
         "each marked rel=\"sponsored\". What cannot be seen from outside is which tracking "
         "ID sits inside them. The account holder has now supplied a Selected Tracking ID, "
         "and Amazon's own help confirms the shape of such an ID, but the shape of an ID is "
         "not proof that this one is attached to these links or that the account is approved. "
         "This pass deliberately does not assert that the supplied short links are invalid; "
         "their compliance status is unresolved, and the record keeps intended destination "
         "and observed destination as two separate fields so the two are never confused."),
        ("evidence", [
            ev("Associates Program Policies (S2)", S2),
            ev("Amazon Associates help — tracking ID format and Manage your Tracking IDs (S36)", S36),
            ev("Associates Program Operating Agreement (S1)", S1),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Generate one Special Link per product, click it, confirm the tracking report"),
                ("what", "In the enrolled account, build the link for each ASIN, open it, and confirm both the destination and that the click appears against that tracking ID before any link is published at scale."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Keep publishing the supplied short links unchanged"),
                ("what", "No change. The site keeps saying plainly that attribution is unverified."),
                ("effort", "S"), ("risk", "medium"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "C. Replace every short link with a hand-built tagged URL"),
                ("what", "Construct /dp/ASIN?tag=... links yourself. This is the option that risks breaching the way Special Links are meant to be generated, and it still cannot be verified from outside the account."),
                ("effort", "S"), ("risk", "high"), ("reversible", True),
            ]),
        ]),
        ("recommendation",
         "A, one product first. Confirm destination and the tracking report for that one "
         "link, then apply the same procedure to the rest. B is what the site ships today "
         "and is safe; C is not recommended."),
        ("why",
         "The failure mode is silent: a link that looks fine, sends the traffic, and credits "
         "nobody. A single confirmed link proves the mechanism works before five unconfirmed "
         "ones are scaled across a growing article set."),
        ("impact", 5),
        ("confidence", 5),
        ("effort", "M"),
        ("risk_of_not_doing",
         "Every click the site earns could be unattributed, and there is no way to discover "
         "that from outside Associates Central."),
        ("blocks", []),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "SG-39"),
        ("title", "Keep the campaign ledger empty until a real report fills it"),
        ("area", "Measurement"),
        ("problem",
         "The brief asks for evidence-based iteration, which invites a dashboard with a "
         "conversion rate on it. There is no conversion rate to show: the site has had no "
         "eligible sessions, and Amazon restricts how program performance data may be "
         "disclosed. The tempting move is to fill the ledger with plausible placeholders and "
         "let them harden into assumed fact."),
        ("evidence", [
            ev("Associates Program Policies (S2)", S2),
            ev("Associates Program Standard Commission Income Statement (S3)", S3),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Empty ledger, fixed column meanings, dated provenance trail"),
                ("what", "Columns are defined once and cannot be quietly redefined later. Rows are added only from an authorized first-party report. No conversion score, no revenue forecast."),
                ("effort", "S"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Model the expected performance from the published rate table"),
                ("what", "Show a projected figure from the 4.50% Kitchen rate and a guessed traffic number. It looks decisive and is a forecast dressed as data."),
                ("effort", "S"), ("risk", "high"), ("reversible", True),
            ]),
        ]),
        ("recommendation", "A. Adopted by this pass; the ledger ships with zero rows."),
        ("why",
         "An empty ledger with fixed columns is more useful than a full one with invented "
         "numbers, because the columns cannot be quietly redefined later to make a bad month "
         "look better."),
        ("impact", 3),
        ("confidence", 5),
        ("effort", "S"),
        ("risk_of_not_doing",
         "A projection published early becomes the number every later decision is measured "
         "against, and it was never real."),
        ("blocks", []),
        ("blocked_by", ["SG-37"]),
    ]),
    collections.OrderedDict([
        ("id", "SG-40"),
        ("title", "Set a publishing cadence and wire every new guide into the sitemap and feed automatically"),
        ("area", "Content and traffic"),
        ("problem",
         "Four question-shaped titles exist as working hypotheses, and the article set has "
         "grown pass by pass with no schedule. A static site can generate its sitemap and RSS "
         "feed from the same register that renders the pages, so a new guide appears in both "
         "with no extra step - but only if the cadence is a decision rather than a mood."),
        ("evidence", [
            ev("Amazon Associates — Application Review Process, content recency guidance (S4)", S4),
            ev("Google Search Central — helpful, people-first content", HELPFUL),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. One sourced guide a fortnight, four then re-measure"),
                ("what", "Publish the four working titles over eight weeks, each added to the sitemap and feed by the build, then choose the next four from measured arrivals."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Publish all four at once"),
                ("what", "Faster to a complete-looking site, but it produces four unmeasured articles instead of one measured one and three informed by it."),
                ("effort", "M"), ("risk", "medium"), ("reversible", True),
            ]),
        ]),
        ("recommendation", "A. Sequencing is the point: the second article should be chosen with the first article's numbers in hand."),
        ("why",
         "Amazon's own application guidance refers to recent content and a body of posts, so "
         "cadence matters to the account as well as to search. Publishing in series also lets "
         "each guide's arrival data inform the next topic."),
        ("impact", 4),
        ("confidence", 4),
        ("effort", "M"),
        ("risk_of_not_doing",
         "Topics keep being chosen by instinct, which is the failure mode the brief asked to "
         "replace with measurement."),
        ("blocks", []),
        ("blocked_by", ["SG-37", "SG-31"]),
    ]),
    collections.OrderedDict([
        ("id", "SG-41"),
        ("title", "Update the cookie and privacy notice in the same change that turns analytics on"),
        ("area", "Compliance"),
        ("problem",
         "The footer currently states that the site sets no cookies and runs no analytics, "
         "and that statement is true. It becomes false the moment an endpoint is configured "
         "with any storage, or a third-party script is added. Program Policies require an "
         "accurate statement of cookie and third-party technology use on Associate sites, so "
         "this is not a cosmetic line."),
        ("evidence", [
            ev("Associates Program Policies — cookie and third-party technology disclosure (S2)", S2),
            ev("FTC — Disclosures 101 for Social Media Influencers", FTC101),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Generate the notice from the analytics configuration"),
                ("what", "The footer text is produced from data/analytics.json, so turning collection on changes the sentence in the same commit. A build guard fails if the notice claims no analytics while an endpoint is set."),
                ("effort", "S"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Update the notice by hand each time"),
                ("what", "Cheaper now, and it will be forgotten exactly once - which is the one time it matters."),
                ("effort", "S"), ("risk", "medium"), ("reversible", True),
            ]),
        ]),
        ("recommendation", "A. Adopted by this pass; the guard ships with the configuration."),
        ("why",
         "A privacy statement that is true at build time and false at deploy time is the "
         "kind of defect that is invisible until someone complains."),
        ("impact", 4),
        ("confidence", 5),
        ("effort", "S"),
        ("risk_of_not_doing",
         "The site publishes an inaccurate statement of its own technology use, which the "
         "Program Policies require to be accurate."),
        ("blocks", []),
        ("blocked_by", ["SG-37"]),
    ]),
    collections.OrderedDict([
        ("id", "SG-42"),
        ("title", "Use real product photography, and never generated or copied imagery"),
        ("area", "Brand"),
        ("problem",
         "The site currently uses generated diagrams in place of photography, because image "
         "rights are unresolved. The Operating Agreement treats data, images and text as "
         "Program Content, which makes casual image reuse a contract question rather than a "
         "design one. A buying page with no photograph of the product is also a weaker page."),
        ("evidence", [
            ev("Associates Program Operating Agreement — Section 1, Program Content (S1)", S1),
            ev("Google Search Central — spam policies", SPAM),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Amazon-served product imagery only"),
                ("what", "Use imagery Amazon serves through its own permitted link tools, and nothing else. No scraping, no stock substitution."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Photograph the units yourself"),
                ("what", "Original photography, unambiguous rights, and the only option that also satisfies the 'no hands-on testing implied' caveat if captioned carefully."),
                ("effort", "L"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "C. Keep generated or stock imagery"),
                ("what", "Fast, and it misrepresents the product and may misrepresent the licence."),
                ("effort", "S"), ("risk", "high"), ("reversible", True),
            ]),
        ]),
        ("recommendation", "A now, B if the units are ever in hand. Not C."),
        ("why",
         "An affiliate page's credibility rests on the reader believing the product shown is "
         "the product sold. Generated imagery breaks that silently and is also the fastest "
         "way to make a real site look machine-made."),
        ("impact", 4),
        ("confidence", 4),
        ("effort", "M"),
        ("risk_of_not_doing",
         "Either an image-rights exposure or a page that looks exactly like the AI-generated "
         "site the brief asked to move away from."),
        ("blocks", []),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "SG-43"),
        ("title", "Put the compliance gate inside the publishing workflow, not in a checklist"),
        ("area", "Compliance"),
        ("problem",
         "Disclosure placement and endorsement language are reviewed by people reading pages. "
         "That works until a page ships without being read. The parts that can be checked "
         "mechanically - every page carries the disclosure above the fold, every outbound "
         "product link is marked sponsored, no page publishes an Amazon price or rating, no "
         "article claims a test that did not happen - are all checkable at build time and are "
         "already build failures here. What still needs a human is the judgement: whether the "
         "disclosure is clear and conspicuous in context, and whether the endorsement reads as "
         "an honest opinion."),
        ("evidence", [
            ev("Associates Program Operating Agreement (S1)", S1),
            ev("FTC — Endorsements, Influencers, and Reviews", FTC),
            ev("Google Search Central — qualify your outbound links", QUALIFY),
        ]),
        ("options", [
            collections.OrderedDict([
                ("label", "A. Build-time gate plus a named human review step"),
                ("what", "Machines enforce what is checkable; a named reviewer signs off the judgement calls before a guide is published. Both are recorded."),
                ("effort", "M"), ("risk", "low"), ("reversible", True),
            ]),
            collections.OrderedDict([
                ("label", "B. Checklist reviewed periodically"),
                ("what", "Cheapest, and it fails in exactly the case it exists for: a page that ships between reviews."),
                ("effort", "S"), ("risk", "medium"), ("reversible", True),
            ]),
        ]),
        ("recommendation", "A. The mechanical half is already implemented in this build."),
        ("why",
         "The FTC's own guidance is that a disclosure must be clear and conspicuous, which is "
         "a contextual judgement no regex can make; but the presence of the disclosure, and "
         "the sponsored marking on paid links, absolutely can be automated."),
        ("impact", 4),
        ("confidence", 5),
        ("effort", "M"),
        ("risk_of_not_doing",
         "The first page that ships without the disclosure is the only one that matters, and "
         "a periodic review finds it last."),
        ("blocks", []),
        ("blocked_by", []),
    ]),
]


def main():
    with open(P, encoding="utf-8") as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    have = {s["id"] for s in d["suggestions"]}
    added = 0
    for row in ROWS:
        if row["id"] in have:
            print("already present:", row["id"])
            continue
        d["suggestions"].append(row)
        have.add(row["id"])
        added += 1
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"added {added}; suggestions now {len(d['suggestions'])}")


if __name__ == "__main__":
    main()
