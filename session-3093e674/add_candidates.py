import json

p = 'data/products.json'
d = json.load(open(p))

d['candidates_note'] = (
    "Added 2026-11-17 by arena/3093e674-zone1. The project brief of that date names five product links, not three; the two new ones "
    "point outside the air-fryer set, so they are recorded here as candidates rather than folded into the comparison, the category page or "
    "the figures. A candidate publishes only what its own listing page or the brand's own product page states, each with the source id and "
    "the date it was read. Anything the sources do not say is absent, not estimated. check_rows_have_sources() and the row-source gate apply "
    "to these rows exactly as they apply to the three products above; _published_values() includes them so article prose can only quote a "
    "value that is already in this register."
)

d['candidates'] = [
    {
        "slug": "thermomaven-f1-instant-read",
        "rank": 99,
        "brand": "ThermoMaven",
        "name": "ThermoMaven instant-read digital meat thermometer (candidate: F1 line)",
        "short_name": "ThermoMaven instant-read (candidate)",
        "category": "Kitchen appliances → Cooking thermometers",
        "link": "https://link.amazon/B0c8moW59",
        "listing_url": "https://www.amazon.com/dp/B0DHZTCNR5",
        "asin": {"v": "B0DHZTCNR5", "s": ["S36"]},
        "asin_evidence": ("Read on 2026-11-17 from the submitted short link https://link.amazon/B0c8moW59: the response's own "
                          "product-summary link is amazon.com/dp/B0DHZTCNR5. That is the destination, not a confirmation of owner "
                          "intent (see links.html LI-04)."),
        "amazon_listing_title": {
            "v": ("ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified Food Thermometer, "
                  "Auto-Rotate Bright LED Screen, Highly Waterproof for Grill BBQ Camping, Black"),
            "s": ["S36"], "read": "2026-11-17"},
        "model_number": {
            "v": None, "s": [],
            "caveat": ("Not published. The brand's own shop lists an F1, an F1 Stealth and an F1 Ace; the listing's '1 Sec' wording "
                       "does not match the F1 page's '0.7 seconds' figure, so no SKU can be attached to this ASIN without the brand or "
                       "the seller saying which one it is. Flagged as F76.")},
        "spec_label": "Candidate facts, from the brand's own F1 page — which model this ASIN is remains unconfirmed",
        "specs": [
            {"label": "Accuracy claim in the listing title", "value": "±0.5℉", "source": ["S36"], "status": "verified",
             "note": "Stated in the Amazon listing title. The brand page states the same tolerance for its F1."},
            {"label": "Brand-page reading time", "value": "0.7 seconds", "source": ["S39"], "status": "verified",
             "note": ("Published as the F1's figure, not as this listing's: the listing says '1 Sec'. Both numbers are shown because "
                       "the two sources have not been reconciled to one product.")},
            {"label": "Brand-page ingress rating", "value": "IP67 waterproof", "source": ["S39"], "status": "verified"},
            {"label": "Brand-page warranty", "value": "Lifetime warranty, no expiration, free replacements", "source": ["S39"],
             "status": "verified"},
            {"label": "Marks shown on the brand page", "value": "NIST, NSF, CE, RoHS, BPA-free", "source": ["S39"],
             "status": "verified",
             "note": "Described as the logos and calibration statement the brand page renders. This site has not seen the certificates."},
            {"label": "Brand-page list price", "value": None, "source": ["S39"], "status": "unverified",
             "unverified": ("The brand page displayed $12.99 against a struck-through $19.99 on 2026-11-17. A promotional figure on a "
                            "shop's own page is the kind of value that is untrue within a week, so it is recorded in pricing below with "
                            "its reading date and not promoted to a specification row.")},
            {"label": "Amazon price", "value": None, "source": ["S36"], "status": "unverified",
             "unverified": "Not displayed by policy (S2 §2(b)); unavailable without Associates API access."},
            {"label": "Star rating / review count", "value": None, "source": ["S36"], "status": "unverified",
             "unverified": "Not displayed by policy (S2 §6(t))."}
        ],
        "commission": {
            "rate_confirmed": None,
            "candidate_rows": [{"category": "Kitchen", "rate": "4.50%", "source": ["S3"]}],
            "why_unverified": ("Amazon's published table is keyed to categories, not ASINs. The browse node for this listing is "
                               "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat, which is "
                               "a browse path, not a commission category (see F56)."),
            "rate_source_note": "Only S3 is authoritative."},
        "pricing": {
            "brand_list_price": {"v": "$12.99 USD against a struck-through $19.99 on the brand's F1 page", "s": ["S39"],
                                 "note": "The brand's own figure on its own product page, read 2026-11-17. It is not Amazon's price and it moves; the reading date is the only warranty on it."},
            "amazon_price": None,
            "amazon_price_reason": "Not displayed by policy (S2 §2(b)).",
            "msrp_confirmed": "Not confirmed: the brand page shows a price and a struck-through figure but does not label either as an MSRP."},
        "reviews": {"amazon_stars": None, "amazon_review_count": None,
                    "amazon_reason": "Not displayed by policy (S2 §6(t); S2 §2(b)).", "brand_site_rating": None},
        "competition": {"amazon_result_count": None, "amazon_bestseller_rank": None,
                        "reason": ("Not read in this pass. This candidate is not part of the air-fryer comparison set, and no competitor "
                                   "analysis was performed on the thermometer category.")},
        "flags": [
            {"id": "F76",
             "issue": ("Which brand SKU this ASIN is cannot be pinned: the listing says '1 Sec', the brand's F1 page says 0.7 seconds, "
                       "and the brand sells three F1 variants."),
             "action": ("Read the listing's own Product information block in a logged-in browser, or take the SKU from the seller, before "
                        "any specification row is attached to B0DHZTCNR5."),
             "sources": ["S36", "S39"]}
        ],
        "identity_status": "candidate — listed, sourced, not yet marketed"
    },
    {
        "slug": "chef-iq-sense-gen3",
        "rank": 98,
        "brand": "CHEF iQ",
        "name": "CHEF iQ iQ Sense Gen 3 smart wireless meat thermometer",
        "short_name": "CHEF iQ Sense (Gen 3)",
        "category": "Kitchen appliances → Cooking thermometers",
        "link": "https://link.amazon/B0f3GKalj",
        "listing_url": "https://www.amazon.com/dp/B0DZFD6R9Z",
        "asin": {"v": "B0DZFD6R9Z", "s": ["S37"]},
        "asin_evidence": ("Read on 2026-11-17 from the submitted short link https://link.amazon/B0f3GKalj: the response's own "
                          "product-summary link is amazon.com/dp/B0DZFD6R9Z. That is the destination, not a confirmation of owner "
                          "intent (see links.html LI-05)."),
        "amazon_listing_title": {
            "v": ("CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | "
                  "5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3"),
            "s": ["S37"], "read": "2026-11-17"},
        "model_number": {
            "v": "CQ60-1C-Z1-E, printed on the brand page's 1-probe Dark Smoke variant", "s": ["S38"],
            "caveat": ("The brand sells this line in 1 to 4 probes and two colours, each with its own variant code, and the Amazon "
                       "listing sells a 3-probe bundle. Only the 1-probe code was read on the brand page, so no other bundle code is "
                       "asserted here (F76).")},
        "spec_label": "Verified specifications — from the brand's own product page",
        "specs": [
            {"label": "Sensor count", "value": "5 sensors: 4 internal temperature sensors and 1 ambient sensor", "source": ["S38"],
             "status": "verified",
             "note": "The listing title says '5 Sensors'; the brand page breaks it down as four internal plus one ambient. The two agree."},
            {"label": "Stated internal accuracy", "value": "accuracy within 1°F", "source": ["S38"], "status": "verified"},
            {"label": "Maximum ambient heat", "value": "up to 1,000°F (537°C)", "source": ["S38"], "status": "verified"},
            {"label": "Appliances the brand lists it for", "value": "oven, stovetop, gas and charcoal grills, smoker, air fryer, deep fryer, sous vide",
             "source": ["S38"], "status": "verified",
             "note": ("The row that connects this product to the rest of the site: an air fryer is on the maker's own compatibility list, "
                       "which is why the pairing guide quotes it rather than inferring it.")},
            {"label": "Connectivity", "value": "Wi-Fi and Bluetooth; unlimited range through the brand's Smart Hub", "source": ["S38"],
             "status": "verified"},
            {"label": "Battery, per the brand page", "value": "70+ hours of battery; the Smart Hub charges via USB-C", "source": ["S38"],
             "status": "verified"},
            {"label": "Probe build", "value": "stainless steel and zirconia; ultra-thin; waterproof and easy to clean", "source": ["S38"],
             "status": "verified"},
            {"label": "Amazon price", "value": None, "source": ["S37"], "status": "unverified",
             "unverified": "Not displayed by policy (S2 §2(b))."},
            {"label": "Star rating / review count", "value": None, "source": ["S37"], "status": "unverified",
             "unverified": "Not displayed by policy (S2 §6(t))."}
        ],
        "commission": {
            "rate_confirmed": None,
            "candidate_rows": [{"category": "Kitchen", "rate": "4.50%", "source": ["S3"]}],
            "why_unverified": ("The same open question as the other four products: the published table is keyed to categories and this "
                               "repository cannot read which category Amazon has assigned to an ASIN (Q-11)."),
            "rate_source_note": "Only S3 is authoritative."},
        "pricing": {
            "brand_list_price": {"v": "$129.99 USD for the 1-probe Dark Smoke variant on the brand page", "s": ["S38"],
                                 "note": "The brand's own figure for one specific variant, read 2026-11-17. The 3-probe bundle the Amazon listing sells is not priced by the row cited here."},
            "amazon_price": None,
            "amazon_price_reason": "Not displayed by policy (S2 §2(b)).",
            "msrp_confirmed": "Not confirmed: no source in this register labels any figure an MSRP."},
        "reviews": {"amazon_stars": None, "amazon_review_count": None,
                    "amazon_reason": "Not displayed by policy (S2 §6(t)).", "brand_site_rating": None},
        "competition": {"amazon_result_count": None, "amazon_bestseller_rank": None,
                        "reason": "Not read in this pass."},
        "flags": [
            {"id": "F76",
             "issue": ("The listing's 3-probe bundle could not be matched to a single brand variant code, because the brand page's codes "
                       "run per variant."),
             "action": ("Read the listing's own Product information block in a logged-in browser before publishing a model number for "
                        "this ASIN."),
             "sources": ["S37", "S38"]}
        ],
        "identity_status": "candidate — mapped to the brand line by stated features, SKU variant unsettled"
    }
]

json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
open(p, 'a').write("\n")
print("candidates:", len(d['candidates']))
