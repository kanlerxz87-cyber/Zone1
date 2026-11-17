import json, pathlib, collections

p = pathlib.Path('data/articles.json')
d = json.load(open(p, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)

SEASONS = {
    "black-friday-model-number-switch": collections.OrderedDict([
        ("label", "Black Friday / Cyber Monday 2026"),
        ("window", "2026-11-17 to 2026-12-01"),
        ("expires", "2026-12-02"),
        ("scope", ("Written about the discount season as a timing problem for model numbers. It publishes no price, "
                   "no percentage off and no claim that any offer is running - and it never did, because Amazon's "
                   "Program Policies permit price and availability claims only in links that Amazon serves.")),
        ("no_price_claims", ("the retailer serves those, and this site is not permitted to restate them "
                             "(Program Policies 2(b) and 6(c))")),
        ("removal_rule", ("2026-12-02. Amazon's rule is dated and absolute: links and related references to a "
                          "limited-time promotion must come off the site as soon as the promotion ends on Amazon's "
                          "site, which for this page means the day after Cyber Monday.")),
    ]),
    "air-fryer-gift-guide-2026": collections.OrderedDict([
        ("label", "Holiday gifting 2026"),
        ("window", "2026-11-17 to 2026-12-24"),
        ("expires", "2026-12-25"),
        ("scope", ("A gift-selection guide organised by documented capacity, controls and cleaning - not by price "
                   "band, because this site publishes no prices. Nothing here says a machine is on offer or will "
                   "arrive by any date.")),
        ("no_price_claims", ("price bands and delivery promises are the retailer's, and both are exactly what "
                             "Program Policies 2(b) stops a site from asserting")),
        ("removal_rule", ("2026-12-25. The seasonal framing stops being true the day after the gift season it is "
                          "written for; the underlying product notes stay valid and live on the product pages.")),
    ]),
}

n = 0
for a in d['articles']:
    if a['slug'] in SEASONS:
        a['season'] = SEASONS[a['slug']]
        n += 1
assert n == 2, n
p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print('season blocks:', n)
