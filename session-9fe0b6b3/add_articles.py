"""Pass 13: publish two question-shaped guides.

The brief supplied four working titles. Two of them are already answered by
articles this site has published ('basket or oven-style' and 'capacity
checklist'), and a third is largely covered by two existing pieces. Publishing
near-duplicates of them would be thin affiliate content, which is both bad
for readers and the exact failure mode Google's spam policies call out. So
this pass publishes the one supplied title with no existing answer, plus one
new guide that serves the two products registered on 2026-11-17, which
currently have no content at all. The mapping for all four titles is recorded
on topics.html rather than left implicit.
"""
import collections
import json

P = "data/articles.json"

ARTICLES = [
    collections.OrderedDict([
        ("slug", "questions-before-buying-multi-function-appliance"),
        ("kind", "Buying guide"),
        ("kicker", "Supplied question"),
        ("title", "Questions to ask before buying a multi-function kitchen appliance"),
        ("standfirst",
         "A multi-function appliance is a bundle of compromises. Here are the eight "
         "questions that expose them, answered with numbers taken from manufacturer "
         "pages and owner's manuals rather than from a marketing box."),
        ("target_query", "questions to ask before buying a multi-function kitchen appliance"),
        ("intent", "Commercial investigation"),
        ("reading_minutes", 7),
        ("products", [
            "chefman-6qt-dual-basket",
            "emeril-26qt-french-door",
            "chefman-8qt-turbofry",
            "thermomaven-1-sec-thermometer",
            "chef-iq-sense-gen3-thermometer",
        ]),
        ("sections", [
            collections.OrderedDict([
                ("h", "Start with the job, not the feature list"),
                ("paras", [
                    "A feature list tells you what a machine can do. It does not tell you "
                    "what it will be doing in your kitchen on a Tuesday. The three "
                    "appliances tracked here solve different jobs: the {{6 Qt / 5.67 L}} "
                    "dual-basket unit is built around cooking two things at once, the "
                    "{{26 qt / 24.6 L (manual: 1,519 cu in)}} countertop oven is built "
                    "around replacing more than one appliance, and the single-basket unit "
                    "is built around volume.",
                    "So the first question is not 'how many functions does it have'. It is "
                    "'which job do I do most weeks, and does this machine's shape suit "
                    "that job?' A rotisserie you use twice is not a feature; it is counter "
                    "space you paid for and cannot get back.",
                ]),
                ("cite", ["S10", "S14"]),
            ]),
            collections.OrderedDict([
                ("h", "Where does the thermometer fit?"),
                ("paras", [
                    "Two of the five products supplied for this site are not appliances at "
                    "all. The {{ThermoMaven 1 Sec Thermometer}} and the "
                    "{{CHEF iQ Sense Gen3 Thermometer}} are thermometers, and they land in "
                    "a different Amazon browse category from the air fryers: "
                    "{{Kitchen appliances → Meat thermometers}}.",
                    "That is not a mismatch to hide, because it answers a real question "
                    "about appliance buying. A multi-function appliance promises to hit a "
                    "temperature for a set time. A thermometer tells you whether it "
                    "actually did. If you have ever taken chicken out of an air fryer on "
                    "time and found it dry in one spot and underdone in another, the "
                    "problem was never the timer.",
                    "Every specification cell for both thermometers is currently blank on "
                    "this site. No brand page or owner's manual for them has been read yet, "
                    "so nothing is published about them — and nothing is invented either.",
                ]),
                ("cite", ["S38", "S39", "S40"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 1: what is the real temperature range, and do I need the ends of it?"),
                ("paras", [
                    "Range is not a bragging number; the ends are where the useful modes "
                    "live. The countertop oven is documented at {{75–500 °F / 25–260 °C}}, "
                    "which is why it can dehydrate and proof — both are low-temperature "
                    "jobs. The dual-basket unit is documented at "
                    "{{200–450 °F / 95–235 °C}}, and its {{450 °F / 235 °C, held for 2 minutes, "
                    "for extra browning}} ceiling is what makes a final crisp possible.",
                    "If you never cook below 200 °F, half of the oven's advantage is "
                    "invisible to you. If you never need to finish a cook hard, the "
                    "Hi-Fry ceiling is a number on a box.",
                ]),
                ("cite", ["S15", "S10"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 2: what does it ask of my kitchen?"),
                ("paras", [
                    "Power and footprint are the two constraints nobody regrets checking "
                    "early. All three air fryers here draw {{1700 W}}, which is close to "
                    "the practical ceiling for a US kitchen counter circuit shared with "
                    "anything else.",
                    "Footprint is where they genuinely differ. The dual-basket unit is "
                    "{{13.38 × 11.81 × 10.63 in / 33.98 × 30 × 27 cm}}; the countertop oven "
                    "is {{16.9 D × 15.8 W × 14.8 H in}} and needs door clearance in front "
                    "of it as well. Measure the gap, not the appliance: the oven's French "
                    "doors, {{French doors, single-pull opening::French doors with a "
                    "single-pull opening}}, swing outward, and that swing is easy to "
                    "forget until the first time it hits a wall.",
                ]),
                ("cite", ["S10", "S14", "S13"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 3: how many of the functions will I actually use?"),
                ("paras", [
                    "Counting functions is the easiest number to inflate and the hardest "
                    "to value. The dual-basket unit's worth rests on one function: "
                    "finishing two cooks together. The oven's worth rests on whether you "
                    "will use it as an oven at all.",
                    "A useful test is to name the last four meals you cooked and ask which "
                    "functions each needed. If the answer is 'air fry' four times, you are "
                    "being sold a bundle, not a solution.",
                ]),
                ("cite", ["S10", "S14"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 4: what happens when it needs cleaning?"),
                ("paras", [
                    "Cleanup is the most under-specified part of any appliance listing and "
                    "the part most likely to decide whether you keep using the thing. Look "
                    "for a documented statement, not a promise: dishwasher-safe baskets, a "
                    "nonstick coating, and — importantly — the care instructions. One "
                    "manual here carries an explicit caution against aerosol cooking oil "
                    "on a nonstick basket, which is the kind of detail that only appears "
                    "in the documentation.",
                    "The dual-basket unit's baskets are described as nonstick and "
                    "dishwasher-safe. Treat that as a claim to verify on the page for the "
                    "exact model you are buying, because coatings and care instructions "
                    "vary between SKUs that look identical.",
                ]),
                ("cite", ["S18", "S10"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 5: what is the warranty, in writing?"),
                ("paras", [
                    "Warranty length is usually a single line and it is worth reading "
                    "before you buy rather than after. The countertop oven is documented "
                    "at {{1-year warranty}}, and the Chefman units carry their own stated "
                    "terms. A one-year term on a {{1700 W}} appliance that runs hot is not "
                    "generous, but it is the market norm, and knowing that is more useful "
                    "than discovering it in month thirteen.",
                ]),
                ("cite", ["S14", "S12"]),
            ]),
            collections.OrderedDict([
                ("h", "Question 6: can I verify the claims before I pay?"),
                ("paras", [
                    "Every number above is quoted from a manufacturer page or an owner's "
                    "manual, and every one of them can be checked in a click. That is the "
                    "point. An appliance listing that will not state its temperature "
                    "range, its dimensions or its warranty is telling you something, and "
                    "it is not that the numbers are impressive.",
                    "Where a manufacturer states two different figures on two of its own "
                    "pages, this site publishes the conflict rather than picking a side. "
                    "You will meet that on the 8-quart Chefman, whose listing and manual "
                    "disagree about its maximum temperature.",
                ]),
                ("cite", ["S12", "S13"]),
            ]),
            collections.OrderedDict([
                ("h", "The short version"),
                ("paras", [
                    "Ask what job you do most weeks, what the ends of the temperature "
                    "range buy you, what the machine asks of your counter and your circuit, "
                    "which functions you will genuinely use, how it cleans, what the "
                    "warranty says in writing, and whether you can verify all of it before "
                    "you pay.",
                    "If you can answer those eight from the documentation, you do not need "
                    "a review to tell you what to buy. You need a link.",
                ]),
                ("cite", ["S10", "S14", "S12"]),
            ]),
        ]),
        ("closing_note",
         "No appliance here was tested, handled or owned by this site. Every figure is "
         "quoted from a manufacturer product page or an owner's manual, and every gap is "
         "published instead of filled in. The two thermometers named in this article have "
         "no confirmed specification on this site yet."),
    ]),
    collections.OrderedDict([
        ("slug", "cook-to-temperature-not-to-time"),
        ("kind", "Explainer"),
        ("kicker", "New category"),
        ("title", "Cook to temperature, not to time: does an air fryer need a thermometer?"),
        ("standfirst",
         "Every air fryer here sells you a timer. A thermometer sells you the answer. "
         "Here is the case for measuring, the limits of doing it with the appliances "
         "themselves, and what is still unknown about the two units on this site."),
        ("target_query", "do you need a meat thermometer for an air fryer"),
        ("intent", "Informational, with a commercial angle"),
        ("reading_minutes", 6),
        ("products", [
            "chefman-6qt-dual-basket",
            "emeril-26qt-french-door",
            "chefman-8qt-turbofry",
            "thermomaven-1-sec-thermometer",
            "chef-iq-sense-gen3-thermometer",
        ]),
        ("sections", [
            collections.OrderedDict([
                ("h", "A timer measures your patience, not your food"),
                ("paras", [
                    "An air fryer timer counts minutes. Food does not cook by the clock; "
                    "it cooks by the heat that actually reaches the middle. Two chicken "
                    "breasts of different thickness, straight from the fridge, in a basket "
                    "that was not preheated, will not finish together no matter what the "
                    "dial says.",
                    "That is the whole argument for a thermometer, and it has nothing to "
                    "do with being fussy. It is the difference between 'the timer went "
                    "off' and 'it is done'.",
                ]),
                ("cite", []),
            ]),
            collections.OrderedDict([
                ("h", "What the appliances themselves document"),
                ("paras", [
                    "The three air fryers tracked here document temperature ranges, not "
                    "internal food temperature. The countertop oven is documented at "
                    "{{75–500 °F / 25–260 °C}} and the dual-basket unit at "
                    "{{200–450 °F / 95–235 °C}}. Those are air temperatures inside a "
                    "cavity.",
                    "None of the three publishes a probe, a food-temperature sensor or an "
                    "internal thermometer. The countertop oven does document a rotisserie, "
                    "and it is the one mode where a probe earns its keep immediately: a "
                    "whole bird is the hardest thing to judge by eye and the easiest to "
                    "ruin by opening the door to check.",
                ]),
                ("cite", ["S15", "S10"]),
            ]),
            collections.OrderedDict([
                ("h", "So what are the two thermometers doing on this site?"),
                ("paras", [
                    "Two of the five product links supplied for this site are "
                    "thermometers: the {{ThermoMaven 1 Sec Thermometer}} and the "
                    "{{CHEF iQ Sense Gen3 Thermometer}}. Both resolve to the Amazon browse "
                    "path {{Kitchen appliances → Meat thermometers}}, not to the air-fryer "
                    "path the other three land in.",
                    "They are not air fryers and this site does not pretend otherwise. "
                    "They are here because the question this article asks — did the food "
                    "actually reach temperature? — is the question those two products "
                    "answer, and because they were supplied alongside the air fryers.",
                    "The two work differently. An instant-read thermometer answers at a "
                    "moment in time: you open the basket, measure, decide. A wireless "
                    "probe thermometer answers continuously: it sits in the food while the "
                    "door stays shut. That difference matters more than any specification, "
                    "because it decides whether you lose heat every time you check.",
                ]),
                ("cite", ["S38", "S39", "S40"]),
            ]),
            collections.OrderedDict([
                ("h", "The honest state of the evidence"),
                ("paras", [
                    "Every specification cell for both thermometers is blank on this site. "
                    "The listing titles carry claims — a one-second read, three probes, "
                    "five sensors, a heat-safe rating — but a listing title is not a "
                    "manufacturer specification sheet, and this site does not copy title "
                    "claims into a verified column.",
                    "So this article tells you why you might want one and which of the two "
                    "approaches suits which cook. It does not tell you which is more "
                    "accurate, how fast either really reads, or how long a battery lasts, "
                    "because none of that has been confirmed from an official source yet. "
                    "Those cells will be filled from brand pages and manuals, or left "
                    "blank, and nothing in between.",
                ]),
                ("cite", ["S38", "S39"]),
            ]),
            collections.OrderedDict([
                ("h", "Where a thermometer does not help"),
                ("paras", [
                    "A thermometer will not fix a crowded basket. Air has to move; if the "
                    "food is packed, the outside overcooks before the middle catches up, "
                    "and a probe will simply tell you that in more detail.",
                    "It also will not tell you about browning. Colour is still a visual "
                    "judgement, and the dual-basket unit's "
                    "{{450 °F / 235 °C, held for 2 minutes, for extra browning}} function "
                    "exists precisely because crispness is a separate problem from "
                    "doneness.",
                ]),
                ("cite", ["S10"]),
            ]),
        ]),
        ("closing_note",
         "Nothing here was tested or handled. Temperature ranges are quoted from "
         "manufacturer documentation; the two thermometers have no confirmed "
         "specification on this site, and this article does not supply one."),
    ]),
]


def main():
    with open(P, encoding="utf-8") as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    have = {a["slug"] for a in d["articles"]}
    added = 0
    for a in ARTICLES:
        if a["slug"] in have:
            print("already present:", a["slug"])
            continue
        d["articles"].append(a)
        have.add(a["slug"])
        added += 1
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"added {added}; articles now {len(d['articles'])}")


if __name__ == "__main__":
    main()
