"""Pass 13: add the publishing cadence and the supplied-working-title mapping
to data/topics.json, plus register the two new guides in the topic plan."""
import collections
import json

P = "data/topics.json"


def ev(label, url):
    return collections.OrderedDict([("label", label), ("url", url)])


CADENCE = collections.OrderedDict([
    ("adopted_on", "2026-11-17"),
    ("adopted_by", "arena/9fe0b6b3-zone1 (pass 13)"),
    ("rhythm", "One sourced guide a fortnight, four then re-measure."),
    ("why_this_rhythm",
     "Sequencing is the whole point. Publishing all four working titles at once would "
     "produce four unmeasured articles; publishing them in series means the second is "
     "chosen with the first's arrival data in hand. Amazon's own application guidance "
     "refers to a body of posts and to content being recent, so cadence serves the "
     "account as well as search."),
    ("definition_of_done", [
        "The guide is registered in data/articles.json, which puts it in the sitemap and the RSS feed on the next build - no separate step exists, and none should.",
        "Every factual sentence cites a registered official source.",
        "Nothing is claimed about search volume or popularity.",
        "The disclosure is present above the fold and every outbound product link is marked rel=\"sponsored\" - both enforced by the build, not by a checklist.",
    ]),
    ("first_four_slots", [
        collections.OrderedDict([("slot", "1"), ("when", "first fortnight"),
                                 ("topic", "Questions to ask before buying a multi-function kitchen appliance"),
                                 ("state", "published 2026-11-17"),
                                 ("decided_by", "supplied working title with no existing answer on this site")]),
        collections.OrderedDict([("slot", "2"), ("when", "second fortnight"),
                                 ("topic", "Cook to temperature, not to time: does an air fryer need a thermometer?"),
                                 ("state", "published 2026-11-17"),
                                 ("decided_by", "the two products registered this pass had no content at all")]),
        collections.OrderedDict([("slot", "3"), ("when", "third fortnight"),
                                 ("topic", "not chosen"),
                                 ("state", "open"),
                                 ("decided_by", "arrival data from slots 1 and 2, plus the first Search Console query report")]),
        collections.OrderedDict([("slot", "4"), ("when", "fourth fortnight"),
                                 ("topic", "not chosen"),
                                 ("state", "open"),
                                 ("decided_by", "same as slot 3")]),
    ]),
    ("blocking_condition",
     "Slots 3 and 4 are deliberately left open. Filling them now would be choosing by "
     "instinct, which is the failure mode this cadence exists to replace. They are "
     "blocked by SG-37 (turn on measurement) and SG-29 (register the site in Search "
     "Console)."),
    ("sources", [
        ev("Amazon Associates - Application Review Process (S4)",
           "https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM"),
        ev("Google Search Central - helpful, people-first content",
           "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"),
    ]),
])

# The four working titles supplied with the brief, and what this site already has
# for each. Publishing near-duplicates would be thin content; the mapping is
# published instead so the decision is visible rather than silent.
WORKING_TITLES = [
    collections.OrderedDict([
        ("title", "Basket or oven-style air fryer: what should you compare?"),
        ("status", "already answered"),
        ("answered_by", "dual-basket-vs-oven-air-fryer"),
        ("note", "This is the one comparison the site was built around. Publishing a second "
                 "article on the same question under a different title would be duplicate "
                 "content aimed at the same query."),
    ]),
    collections.OrderedDict([
        ("title", "A no-hype checklist for comparing air fryer capacity"),
        ("status", "already answered"),
        ("answered_by", "air-fryer-capacity-guide"),
        ("note", "The existing guide covers 6, 8 and 26 quarts against manufacturer "
                 "documentation and names the unit traps. A second checklist would restate it."),
    ]),
    collections.OrderedDict([
        ("title", "How to assess cleanup and counter-space trade-offs"),
        ("status", "partly answered"),
        ("answered_by", "how-to-clean-an-air-fryer"),
        ("note", "Cleanup is covered from the manuals. The counter-space half is covered by "
                 "small-kitchen-air-fryer-dimensions, but the two are not combined into a "
                 "single trade-off piece - that combination is a candidate for slot 3 or 4 "
                 "if the arrival data supports it."),
    ]),
    collections.OrderedDict([
        ("title", "Questions to ask before buying a multi-function kitchen appliance"),
        ("status", "newly published"),
        ("answered_by", "questions-before-buying-multi-function-appliance"),
        ("note", "No existing article answered this, so it was written and published in this "
                 "pass. It is also the title that naturally covers both categories of product "
                 "the site now carries."),
    ]),
]

NEW_TOPICS = [
    collections.OrderedDict([
        ("id", "TP-21"),
        ("title", "Questions to ask before buying a multi-function kitchen appliance"),
        ("hook", "A multi-function appliance is a bundle of compromises. Eight questions expose them."),
        ("intent", "Commercial investigation"),
        ("serves", ["chefman-6qt-dual-basket", "emeril-26qt-french-door",
                    "chefman-8qt-turbofry", "thermomaven-1-sec-thermometer",
                    "chef-iq-sense-gen3-thermometer"]),
        ("angle", "Supplied as an editorial hypothesis with the brief. Answered with "
                  "documented temperature ranges, footprints, power draw and warranty terms "
                  "rather than with a feature count."),
        ("why_it_could_earn_traffic",
         "Judgement, not measurement: it is the one supplied title this site had no answer "
         "for, and it is the only one broad enough to cover both product categories."),
        ("must_cite", [
            ev("Chefman 6 Qt dual-window product page (S10)",
               "https://chefman.com/products/turbofry-touch-dual-window-air-fryer"),
            ev("Emeril French Door product page (S14)",
               "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360"),
            ev("Chefman 8 Qt product page (S12)",
               "https://chefman.com/collections/air-fryers-1/products/turbofry-touch-air-fryer-1"),
        ]),
        ("status", "published"),
        ("published_as", "questions-before-buying-multi-function-appliance"),
        ("blocked_by", []),
    ]),
    collections.OrderedDict([
        ("id", "TP-22"),
        ("title", "Cook to temperature, not to time: does an air fryer need a thermometer?"),
        ("hook", "Every air fryer here sells you a timer. A thermometer sells you the answer."),
        ("intent", "Informational, with a commercial angle"),
        ("serves", ["chefman-6qt-dual-basket", "emeril-26qt-french-door",
                    "chefman-8qt-turbofry", "thermomaven-1-sec-thermometer",
                    "chef-iq-sense-gen3-thermometer"]),
        ("angle", "Not a supplied title. Written because the two products registered on "
                  "2026-11-17 had no content at all, and because it is the question that "
                  "connects the air-fryer category to the thermometer category honestly."),
        ("why_it_could_earn_traffic",
         "Judgement, not measurement: it gives the two unmarketed products a reason to exist "
         "on the site without pretending they are air fryers."),
        ("must_cite", [
            ev("Amazon listing B0DHZTCNR5 (S38)", "https://www.amazon.com/dp/B0DHZTCNR5"),
            ev("Amazon listing B0DZFD6R9Z (S39)", "https://www.amazon.com/dp/B0DZFD6R9Z"),
            ev("Emeril French Door owner's manual (S15)",
               "https://cdn.shopify.com/s/files/1/0687/4388/8948/files/FAFO-001_VN_32451_EF_IB_T22-5004282-C_1.pdf"),
        ]),
        ("status", "published"),
        ("published_as", "cook-to-temperature-not-to-time"),
        ("blocked_by", ["Q-32"]),
    ]),
]


def main():
    with open(P, encoding="utf-8") as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    d["cadence"] = CADENCE
    d["supplied_working_titles"] = WORKING_TITLES
    have = {t["id"] for t in d["topics"]}
    added = 0
    for t in NEW_TOPICS:
        if t["id"] in have:
            print("already present:", t["id"])
            continue
        d["topics"].append(t)
        have.add(t["id"])
        added += 1
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"added {added} topics; topics now {len(d['topics'])}")


if __name__ == "__main__":
    main()
