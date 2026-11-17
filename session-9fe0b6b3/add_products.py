"""Add the two products supplied on 2026-11-17 to data/products.json.

Only fields read from an official source on 2026-11-17 are populated: the ASIN,
the Amazon listing title verbatim, and the browse-category path. Every specification
cell is left blank with the reason it could not be confirmed, per the site's rule.
"""
import collections
import json

P = "data/products.json"


def spec(label, unver, srcs):
    return collections.OrderedDict([
        ("label", label),
        ("value", None),
        ("source", srcs),
        ("status", "unverified"),
        ("unverified", unver),
    ])


def flag(fid, issue, why):
    return collections.OrderedDict([("id", fid), ("issue", issue), ("why", why)])


THERMOMAVEN = collections.OrderedDict([
    ("slug", "thermomaven-1-sec-thermometer"),
    ("rank", 4),
    ("brand", "ThermoMaven"),
    ("name", "1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | "
             "NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, "
             "Highly Waterproof for Grill BBQ Camping, Black"),
    ("short_name", "ThermoMaven 1 Sec Thermometer"),
    ("category", "Kitchen appliances → Meat thermometers"),
    ("link", "https://link.amazon/B0c8moW59"),
    ("asin", collections.OrderedDict([("v", "B0DHZTCNR5"), ("s", ["S38", "S40"])])),
    ("asin_evidence",
     "Supplied on 2026-11-17 and resolved twice that day: once by following "
     "https://link.amazon/B0c8moW59 and once by requesting "
     "https://www.amazon.com/dp/B0DHZTCNR5 directly. Both responses returned the same "
     "ASIN and the same <title> string. The observed listing sits in the browse path "
     "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & "
     "Timers > Meat, so it is a meat thermometer, not an air fryer (flag F77)."),
    ("amazon_listing_title", collections.OrderedDict([
        ("v", "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy "
              "| NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, "
              "Highly Waterproof for Grill BBQ Camping, Black"),
        ("s", ["S38"]),
        ("read", "2026-11-17"),
    ])),
    ("model_number", collections.OrderedDict([
        ("v", None),
        ("caveat", "No model or part number has been read for this product. The supplied "
                   "short link lands on an Amazon listing; no ThermoMaven-owned product "
                   "page or owner's manual has been located and read by this pass, so "
                   "nothing is published here. Left blank rather than inferred."),
    ])),
    ("specs", [
        spec("Probe / sensor count",
             "No official source read by this pass states how many probes or sensors this "
             "product has. The listing title and the breadcrumb path were read; a full "
             "Product information block was not. Blank by policy, not by oversight.",
             ["S38"]),
        spec("Temperature range",
             "No official source read by this pass publishes a measurable temperature "
             "range for this product. The listing title quotes an accuracy figure "
             "(±0.5 °F), which is a different specification from a range, and is not "
             "transferred into this row.",
             ["S38"]),
        spec("Accuracy as listed",
             "The listing title states '±0.5℉ Accuracy'. This pass records that the title "
             "says it; it does not verify the claim against a manufacturer datasheet or a "
             "certification document, so no value is published.",
             ["S38"]),
        spec("Connectivity",
             "The listing title describes an auto-rotate screen but names no wireless or "
             "app connectivity. No official source read by this pass states one either "
             "way, so the cell stays blank.",
             ["S38"]),
        spec("Model number",
             "Not read. See the model-number caveat on this product.",
             ["S38"]),
        spec("Warranty",
             "No official source read by this pass states a warranty term for this "
             "product.",
             ["S38"]),
    ]),
    ("pricing", collections.OrderedDict([
        ("brand_list_price", collections.OrderedDict([
            ("v", None),
            ("s", ["S38"]),
            ("note", "No manufacturer list price is published. Amazon's own price is "
                     "deliberately not displayed: Program Policies §2(b) permit price "
                     "display only where Amazon serves the link or the data comes from "
                     "the Creators/PA API, and neither applies here."),
        ])),
        ("amazon_price", None),
        ("amazon_price_reason", "Not displayed by policy (S2 §2(b))."),
    ])),
    ("reviews", collections.OrderedDict([
        ("amazon_stars", None),
        ("amazon_review_count", None),
        ("amazon_reason", "Not displayed by policy (S2 §6(t); S2 §2(b))."),
        ("brand_site_rating", None),
    ])),
    ("commission", collections.OrderedDict([
        ("rate_confirmed", None),
        ("candidate_rows", [
            collections.OrderedDict([("category", "Kitchen"), ("rate", "4.50%"),
                                     ("source", ["S3"])]),
            collections.OrderedDict([("category", "All Other Categories (fallback row)"),
                                     ("rate", "4.00%"), ("source", ["S3"])]),
        ]),
        ("why_unverified",
         "Amazon's rate table assigns a rate by the category of the item bought, and it "
         "does not publish which category it applies to a given ASIN. The observed "
         "breadcrumb for this ASIN is Home & Kitchen > Kitchen & Dining > Kitchen "
         "Utensils & Gadgets > Thermometers & Timers > Meat, a different path from the "
         "three air-fryer listings, so the settled category cannot be assumed to be the "
         "same. Only an Associates Earnings report names the category on a shipped line."),
    ])),
    ("competition", collections.OrderedDict([
        ("amazon_result_count", None),
        ("amazon_bestseller_rank", None),
        ("reason", "Not published as a stable quotable fact; aggregation is restricted by S2."),
    ])),
    ("flags", [
        flag("F77",
             "This product is a meat thermometer, not an air fryer. It was supplied "
             "alongside three air-fryer links and lands in a different Amazon browse "
             "category.",
             "The site was built around a single category — air fryers — and its tagline, "
             "buying guide, comparison narrative and chooser all assume that category. "
             "Dropping a thermometer into it silently would make those pages wrong. "
             "Recorded so the owner can decide the product set deliberately (see "
             "suggestions.html SG-31)."),
    ]),
])

CHEFIQ = collections.OrderedDict([
    ("slug", "chef-iq-sense-gen3-thermometer"),
    ("rank", 5),
    ("brand", "CHEF iQ"),
    ("name", "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | "
             "WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, "
             "Smoker, Air Fryer | Gen3"),
    ("short_name", "CHEF iQ Sense Gen3 Thermometer"),
    ("category", "Kitchen appliances → Meat thermometers"),
    ("link", "https://link.amazon/B0f3GKalj"),
    ("asin", collections.OrderedDict([("v", "B0DZFD6R9Z"), ("s", ["S39", "S40"])])),
    ("asin_evidence",
     "Supplied on 2026-11-17 and resolved twice that day: once by following "
     "https://link.amazon/B0f3GKalj and once by requesting "
     "https://www.amazon.com/dp/B0DZFD6R9Z directly. Both responses returned the same "
     "ASIN and the same <title> string. The observed listing sits in the browse path "
     "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & "
     "Timers > Meat. The listing title names 'Air Fryer' among the appliances the "
     "product is used with, but the product itself is a meat thermometer (flag F77)."),
    ("amazon_listing_title", collections.OrderedDict([
        ("v", "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | "
              "WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, "
              "Smoker, Air Fryer | Gen3"),
        ("s", ["S39"]),
        ("read", "2026-11-17"),
    ])),
    ("model_number", collections.OrderedDict([
        ("v", None),
        ("caveat", "No model or part number has been read for this product. The listing "
                   "title carries the generation marker 'Gen3'; no CHEF iQ-owned product "
                   "page or owner's manual has been located and read by this pass, so "
                   "nothing is published here."),
    ])),
    ("specs", [
        spec("Probe / sensor count",
             "The listing title states '3 Ultra-Thin Probes' and '5 Sensors'. This pass "
             "records that the title says so; it does not treat a listing title as a "
             "verified manufacturer specification, so no value is published in the "
             "verified column.",
             ["S39"]),
        spec("Temperature range",
             "The listing title states '1000°F Heat Safe'. That is a heat-safety "
             "statement, not a measurable cooking range, and no official source read by "
             "this pass publishes a range. Blank rather than reinterpreted.",
             ["S39"]),
        spec("Connectivity",
             "The listing title states 'WiFi Unlimited Range'. Recorded as a title claim "
             "only; no manufacturer datasheet has been read, so no value is published.",
             ["S39"]),
        spec("Model number",
             "Not read. See the model-number caveat on this product.",
             ["S39"]),
        spec("Warranty",
             "No official source read by this pass states a warranty term for this "
             "product.",
             ["S39"]),
    ]),
    ("pricing", collections.OrderedDict([
        ("brand_list_price", collections.OrderedDict([
            ("v", None),
            ("s", ["S39"]),
            ("note", "No manufacturer list price is published. Amazon's own price is "
                     "deliberately not displayed: Program Policies §2(b) permit price "
                     "display only where Amazon serves the link or the data comes from "
                     "the Creators/PA API, and neither applies here."),
        ])),
        ("amazon_price", None),
        ("amazon_price_reason", "Not displayed by policy (S2 §2(b))."),
    ])),
    ("reviews", collections.OrderedDict([
        ("amazon_stars", None),
        ("amazon_review_count", None),
        ("amazon_reason", "Not displayed by policy (S2 §6(t); S2 §2(b))."),
        ("brand_site_rating", None),
    ])),
    ("commission", collections.OrderedDict([
        ("rate_confirmed", None),
        ("candidate_rows", [
            collections.OrderedDict([("category", "Kitchen"), ("rate", "4.50%"),
                                     ("source", ["S3"])]),
            collections.OrderedDict([("category", "All Other Categories (fallback row)"),
                                     ("rate", "4.00%"), ("source", ["S3"])]),
        ]),
        ("why_unverified",
         "Same position as the other thermometer: the observed browse path is "
         "Thermometers & Timers > Meat, which differs from the air-fryer path, so the "
         "settled commission category cannot be assumed. Only an Associates Earnings "
         "report names the category on a shipped line."),
    ])),
    ("competition", collections.OrderedDict([
        ("amazon_result_count", None),
        ("amazon_bestseller_rank", None),
        ("reason", "Not published as a stable quotable fact; aggregation is restricted by S2."),
    ])),
    ("flags", [
        flag("F77",
             "This product is a meat thermometer, not an air fryer, although its listing "
             "title names 'Air Fryer' among the appliances it is used with.",
             "See the matching row on the ThermoMaven product and flag F77. The site's "
             "single-category model does not currently describe this product."),
    ]),
])


def main():
    with open(P, encoding="utf-8") as fh:
        d = json.load(fh, object_pairs_hook=collections.OrderedDict)
    have = {x["slug"] for x in d["products"]}
    added = 0
    for prod in (THERMOMAVEN, CHEFIQ):
        if prod["slug"] in have:
            print("already present:", prod["slug"])
            continue
        d["products"].append(prod)
        have.add(prod["slug"])
        added += 1
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"added {added}; products now {len(d['products'])}")


if __name__ == "__main__":
    main()
