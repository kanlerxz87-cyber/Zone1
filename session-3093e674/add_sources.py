import json

# ---------------------------------------------------------------- sources ---
p = 'data/sources.json'
d = json.load(open(p))
by = {s['id']: s for s in d['sources']}
assert 'S36' not in by, "S36 already registered - renumber before adding"

today = "2026-11-17"

d['sources'] += [
    {
        "id": "S36",
        "org": "Amazon.com (product listings)",
        "title": "Amazon detail page for ASIN B0DHZTCNR5 (ThermoMaven instant-read meat thermometer, Black)",
        "url": "https://www.amazon.com/dp/B0DHZTCNR5",
        "covers": ("The listing title, the browse-node breadcrumb and the destination of the supplied short link "
                   "https://link.amazon/B0c8moW59. Registered as a single-ASIN URL on the same rule as S16/S28/S29: a source "
                   "link must point at the page that states the value it supports. Not used for any specification claim - the "
                   "brand-model mapping for this ASIN is unresolved (F76)."),
        "kind": "Retail listing",
        "directness": "Primary for 'where does this short link land'; not used for specification claims",
        "page_version": (f"Fetched {today} from the supplied short link https://link.amazon/B0c8moW59, which resolved through "
                         "its fallback redirector (lv=shuf, plpRedirect=mhFallback, channelId=500). Document title read in full: "
                         "'Amazon.com: ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified "
                         "Food Thermometer, Auto-Rotate Bright LED Screen, Highly Waterproof for Grill BBQ Camping, Black : Home & "
                         "Kitchen'. Breadcrumb: Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & "
                         "Timers > Meat. First read of this token - there is no second read to compare stability against."),
        "verified": f"Read live {today} by session arena/3093e674-zone1 through the submitted short link; recorded in reports/verification-2026-11-17-3093e674.md."
    },
    {
        "id": "S37",
        "org": "Amazon.com (product listings)",
        "title": "Amazon detail page for ASIN B0DZFD6R9Z (CHEF iQ Sense smart wireless meat thermometer, Gen3)",
        "url": "https://www.amazon.com/dp/B0DZFD6R9Z",
        "covers": ("The listing title, the browse-node breadcrumb and the destination of the supplied short link "
                   "https://link.amazon/B0f3GKalj. Used for identity-of-destination only; the specification rows it supports are "
                   "sourced to the brand's own page (S38), which is where the numbers live."),
        "kind": "Retail listing",
        "directness": "Primary for 'where does this short link land'",
        "page_version": (f"Fetched {today} from the supplied short link https://link.amazon/B0f3GKalj, which resolved through its "
                         "fallback redirector (lv=shuf, plpRedirect=mhFallback, channelId=500). Document title read in full: "
                         "'Amazon.com: CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | "
                         "1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3: Home & Kitchen'. Breadcrumb: "
                         "Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat."),
        "verified": f"Read live {today} by session arena/3093e674-zone1 through the submitted short link; recorded in reports/verification-2026-11-17-3093e674.md."
    },
    {
        "id": "S38",
        "org": "CHEF iQ (the brand's own store)",
        "title": "iQ Sense - CHEF iQ product page (Gen 3 wireless meat thermometer)",
        "url": "https://chefiq.com/products/iq-sense",
        "covers": ("The only official source this repository holds for the iQ Sense's own published figures: five sensors (four "
                   "internal plus one ambient), accuracy within 1°F, heat resistance to 1,000°F (537°C), the appliance "
                   "compatibility list that includes 'air fryer', Wi-Fi/Bluetooth via the Smart Hub, 70+ hours of battery, USB-C "
                   "charging, probe materials, and the 1-probe Dark Smoke variant code CQ60-1C-Z1-E with its brand-page price."),
        "kind": "Brand product page",
        "directness": "Primary - the manufacturer's own page for the product",
        "page_version": (f"Fetched {today}. Variant selector offers 1 to 4 probes in Dark Smoke or Sea Salt, so the page is one "
                         "product line with several SKUs; only the displayed 1-probe Dark Smoke code and price are read from it. "
                         "Feature list read verbatim: 'Compatible with the oven, stovetop, gas and charcoal grills, smoker, air "
                         "fryer, deep fryer, and sous vide' and 'Heat resistant up to 1,000ºF (537ºC)'."),
        "verified": f"Read live {today} by session arena/3093e674-zone1; recorded in reports/verification-2026-11-17-3093e674.md."
    },
    {
        "id": "S39",
        "org": "ThermoMaven (the brand's own store)",
        "title": "ThermoMaven F1 Instant-Read Meat Thermometer - product page",
        "url": "https://www.thermomaven.com/products/f1",
        "covers": ("The F1's published figures - accuracy within ±0.5℉, a 0.7-second reading, IP67 waterproofing, lift-to-wake with "
                   "30-second auto-off, 180° rotating backlit display, magnetic storage, NIST calibration statement, NSF/CE/RoHS/"
                   "BPA-free marks, lifetime warranty with free replacements, and the brand-page price of $12.99 against a "
                   "struck-through $19.99. Also the reason the Amazon listing cannot be mapped to a SKU on the strength of its "
                   "title: the brand sells an F1, an F1 Stealth and an F1 Ace."),
        "kind": "Brand product page",
        "directness": "Primary for the F1 line; not proof that ASIN B0DHZTCNR5 is the F1 (see F76)",
        "page_version": (f"Fetched {today}. The page links its own user guide PDF (ThermoMaven_F1_User_Manual_v1_202408_Web.pdf); "
                         "the PDF was not opened by this pass, so no fact is sourced to it."),
        "verified": f"Read live {today} by session arena/3093e674-zone1; recorded in reports/verification-2026-11-17-3093e674.md."
    }
]

# S17 covers five links now, not three.
s17 = by['S17']
s17['title'] = ("link.amazon short links supplied by the account holder (B04G1MEwY, B02NbDxp3, B00hJ57DV, and from 2026-11-17 "
                "B0c8moW59 and B0f3GKalj)")
s17['covers'] = ("The five redirect links themselves and their resolved destinations. The set grew from three to five when the "
                 "project brief of 2026-11-17 listed two further links; the two new tokens had never been read by this repository "
                 "before that date.")
s17['page_version'] = (s17['page_version']
    + f" | Pass 13 ({today}, arena/3093e674-zone1): all five tokens re-read. The three originals resolved to the same destinations "
      "(B0CDY277D3, B09B7SB46R, B08DKYBTPH) with the same fallback parameters and still no visible tag=. The two new tokens resolved "
      "to B0DHZTCNR5 (ThermoMaven instant-read, Black) and B0DZFD6R9Z (CHEF iQ Sense Gen3) with the same fallback shape on "
      "channelId=500. All five tokens are 9 characters, so none is an ASIN.")
s17['verified'] = (f"Round 11 (2026-11-16, arena/b23f12f0): all three tokens re-resolved. B04G1MEwY -> /dp/B0CDY277D3, "
                   "B02NbDxp3 -> /dp/B09B7SB46R, B00hJ57DV -> /dp/B08DKYBTPH. Destinations unchanged; each landing URL still "
                   f"carries plpRedirect=mhFallback and no tag= parameter. | Pass 13 ({today}, arena/3093e674-zone1): the same "
                   "three destinations unchanged, plus B0c8moW59 -> /dp/B0DHZTCNR5 and B0f3GKalj -> /dp/B0DZFD6R9Z read for the "
                   "first time. Every landing URL still shows no tag= parameter to a fetcher.")

# Policy pages re-read today for the link/tag rules this pass implements.
by['S2']['page_version'] = by['S2']['page_version'] + (
    f" | Pass 13 ({today}, arena/3093e674-zone1): header still reads 'Updated: April 14, 2026'. Participation Requirements 2(a) "
    "and 2(b) re-read and quoted verbatim for the Special Link work: 'Special Links must use the Associates ID we have assigned to "
    "you'; 'you must include your Associates ID or \u201ctag\u201d (appearing as XXXXX-##, or such other format as we may designate) "
    "as a parameter in the URL of each link you place on your Site to an Amazon Site'; 'Special Links may be created by you or made "
    "available to you by us'; the sub-tag clause 'Upon your request but subject to our approval, we may issue you additional "
    "\u201csub-tag\u201d Associate IDs' with its prohibition on associating any sub-tag or reporting with a specific end user; "
    "\u201cSpecial Links must link to Products (as defined in the Products Statement)\u201d; and the limited-time-promotion removal "
    "duty, which is the clause the seasonal rows are held to.")
by['S6']['page_version'] = (f"Live page, re-read {today} (arena/3093e674-zone1). Confirmed verbatim: 'With tracking IDs, Associates "
    "can analyse the performance of various Web sites or merchandising strategies while accumulating earnings under a single "
    "Associates ID. For example, Associate storeid-20 might use the tracking ID storeid-1-20 to track referrals from his Web site, "
    "and storeid-2-21 to track referrals from his newsletter. Each ID would generate earnings for his Associates account "
    "storeid-20.' This is the source for the rule that a sub-tag is a separate issued ID created in the account, not a suffix an "
    "article or a build can invent. Earlier read: live page, 2026-11-13.")
by['S1']['page_version'] = by['S1']['page_version'] + (
    f" | Pass 13 ({today}, arena/3093e674-zone1): re-read live; §5 still requires the site to state clearly and prominently "
    "\u201cAs an Amazon Associate I earn from qualifying purchases.\u201d, which is the sentence the disclosure bar on every "
    "generated page carries.")
by['S23']['page_version'] = by['S23']['page_version'] + (
    f" | Pass 13 ({today}, arena/3093e674-zone1): page re-read; it remains the official Amazon-published description of linking to "
    "a detail page by ASIN in the /dp/<ASIN> form, which is the format the product-intent register checks a token against.")

d['reverified'] = today
d['reverified_2026_11_17_3093e674'] = {
    "session": "arena/3093e674-zone1",
    "date": today,
    "scope": ("S1, S2, S6, S17, S23 re-read for the link and tag rules implemented this pass; S36-S39 registered from live reads "
              "made the same day (the two new Amazon destinations, and the two brand product pages that carry their published "
              "figures)."),
    "result": ("Policies header unchanged at 'Updated: April 14, 2026'; Operating Agreement §5 wording unchanged; all five short "
               "links resolved as recorded, with the two new destinations added; no previously published value was contradicted by "
               "any read in this pass."),
    "evidence": "reports/verification-2026-11-17-3093e674.md"
}

json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
open(p, 'a').write("\n")
print('sources now:', len(d['sources']))
