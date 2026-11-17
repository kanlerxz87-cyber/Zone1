import re, sys, pathlib

p = pathlib.Path('build.py')
s = p.read_text(encoding='utf-8')
orig = s


def sub(old, new, label, count=1):
    global s
    if s.count(old) != count:
        print(f'!! MISS [{label}] expected {count} got {s.count(old)}: {old[:70]!r}')
        sys.exit(1)
    s = s.replace(old, new, count)
    print(f'ok [{label}]')


GUARDS = '''

# --------------------------------------------------------------------------- #
# pass 13 guards (2026-11-17, arena/3093e674-zone1): the link builder, the intent
# register and the measurement layer each get one executable rule, so the promises
# those pages make are properties of the build rather than sentences in a document.
# --------------------------------------------------------------------------- #

def check_special_links(pages):
    """Build guard: every money-page CTA to Amazon carries the configured Associates tag.

    Why this is a build failure and not a note: Participation Requirements 2(b) requires the tag
    "as a parameter in the URL of each link you place on your Site to an Amazon Site", and the
    Operating Agreement releases Amazon from any obligation to pay where links are not properly
    formatted (S2, S1 - both re-read 2026-11-17). For a site whose whole output is these links, a
    forgotten tag is not a style defect; it is the site working for nothing. Before 2026-11-17 the
    CTAs were the raw short links and the tag was unknown, so nothing could be checked. Now the tag
    is a build input, which makes both the link and its absence checkable.

    Four things are asserted, on the rendered HTML rather than on the templates:
      1. a CTA (data-z1k="outlink") points at a /dp/<ASIN> and carries the configured tag;
      2. no CTA still points at the short-link redirector, which cannot be audited from here;
      3. the tag, if any, matches the declared shape and comes from config - never from a template;
      4. citation links keep their own identity: they are excluded by class="src", so a source
         badge is never silently turned into a monetised link.
    """
    problems = []
    anchor = re.compile(r'<a\\b[^>]*data-z1k="outlink"[^>]*>', re.I)
    for rel, html_text in pages.items():
        for tag in anchor.findall(html_text):
            href = re.search(r'href="([^"]+)"', tag)
            href = href.group(1) if href else ""
            if "link.amazon" in href:
                problems.append(f"{rel}: a product CTA still points at the supplied short link ({href[:80]})")
                continue
            if not re.search(r"amazon\\.com/dp/[A-Z0-9]{10}$", href) and not re.search(
                    r"amazon\\.com/dp/[A-Z0-9]{10}\\?", href):
                problems.append(f"{rel}: CTA is not a canonical /dp/<ASIN> URL: {href[:90]}")
            if ASSOCIATE_TAG:
                allowed = [ASSOCIATE_TAG] + list(SUB_TAGS.values())
                m = re.search(r"[?&]tag=([^&]+)", href)
                if not m:
                    problems.append(f"{rel}: CTA carries no Associates tag although data/config.json declares one: {href[:90]}")
                elif m.group(1) not in allowed:
                    problems.append(f"{rel}: CTA tag {m.group(1)!r} is not the configured tag or an assigned sub-tag")
            elif "tag=" in href:
                problems.append(f"{rel}: a tag appeared in a CTA while data/config.json declares none - "
                                f"links and configuration have diverged")
    if ASSOCIATE_TAG and not tag_is_wellformed(ASSOCIATE_TAG):
        problems.append(f"data/config.json: associate_tag {ASSOCIATE_TAG!r} does not match the published "
                        f"XXXXX-## shape (Program Policies 2(b))")
    for key, val in SUB_TAGS.items():
        if not tag_is_wellformed(val):
            problems.append(f"data/config.json: sub-tag {key!r} = {val!r} does not match the published tag shape")
    return problems


def check_link_intent():
    """Build guard: the intent register keeps intended and observed apart, and covers every link.

    The brief's instruction was structural - "Keep observed redirect targets in a separate field.
    Do not merge the two fields." - and a rule that only exists in prose is a rule an impatient
    later pass can merge in one edit. So the merge is what this checks for: an `intended.asin`
    filled from an `observed.final_asin` is the exact shape of the mistake, and it is a failure.
    """
    problems = []
    recs = LINK_INTENT.get("records") or []
    seen = set()
    for r in recs:
        rid = r.get("id", "?")
        if rid in seen:
            problems.append(f"{rid}: duplicate row id in data/link-intent.json (the F67 defect class)")
        seen.add(rid)
        for key in ("submitted_link", "intended", "observed", "identity_status", "site_treats_it_as"):
            if key not in r:
                problems.append(f"{rid}: missing required field {key!r}")
        it, ob = r.get("intended", {}), r.get("observed", {})
        if not ob.get("final_asin") or not re.fullmatch(r"[A-Z0-9]{10}", str(ob.get("final_asin", ""))):
            problems.append(f"{rid}: observed.final_asin is absent or is not a 10-character ASIN, so it is not an observation of a listing")
        if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", str(ob.get("observed_on", ""))):
            problems.append(f"{rid}: observed.observed_on must be the date the fetch happened")
        if it.get("asin"):
            if not re.fullmatch(r"[A-Z0-9]{10}", str(it["asin"])):
                problems.append(f"{rid}: intended.asin {it['asin']!r} is not an ASIN")
            if it["asin"] == ob.get("final_asin") and not str(it.get("status", "")).lower().startswith("confirmed by the account holder"):
                problems.append(
                    f"{rid}: intended.asin equals the observed destination without an owner statement behind it. "
                    f"An intent may only be recorded from the account holder; copying the fetch result is the merge this register exists to prevent.")
        if it.get("asin") is None and it.get("confirmed_on"):
            problems.append(f"{rid}: intended.confirmed_on is set with no intended ASIN - nothing was confirmed")
        for fid in r.get("open_items", []):
            if fid.startswith("F"):
                num = int(fid[1:])
                known = {f[0] for f in PROGRAMME_FLAGS} | {f"F{n:02d}" for n in range(1, 40)}
                if fid not in known:
                    problems.append(f"{rid}: open_items points at {fid}, which no flag register carries")
            elif fid.startswith("Q"):
                if fid not in {q["id"] for q in QUESTIONS["questions"]}:
                    problems.append(f"{rid}: open_items points at {fid}, which is not in the questions register")
    # Coverage: every link this site markets must have a row. The reverse (a row with no product)
    # is allowed and expected - those are the links that are recorded but not yet marketed.
    for prod in list(PRODUCT_LIST) + list(CANDIDATE_LIST):
        link = prod.get("link")
        if link and not any(r.get("submitted_link") == link for r in recs):
            problems.append(f'{prod["slug"]}: marketed through {link} with no intent row in data/link-intent.json')
        asin = (prod.get("asin") or {}).get("v")
        if asin and not any(r.get("observed", {}).get("final_asin") == asin for r in recs):
            problems.append(f'{prod["slug"]}: marketed as {asin} but no intent row records that destination being read live')
    return problems


def check_campaign_ledger():
    """Build guard: a ledger row may only exist with a dated, attributable provenance trail.

    The brief asked for "an empty but well-defined campaign ledger" with each field added "only when
    obtained from authorized first-party reports". An empty register is easy to publish; the part
    that has to be built now is the thing that refuses a bad row later, before there is a number to
    argue about. This also blocks the two fields the brief explicitly excludes - a conversion score
    and a revenue forecast - because they are arithmetic a reader will mistake for measurement.
    """
    problems = []
    rows = LEDGER.get("rows") or []
    allowed = {c["key"] for c in LEDGER["columns"]}
    for n, row in enumerate(rows):
        rid = row.get("id", f"row {n + 1}")
        for req in ("period_start", "period_end", "source", "obtained_on"):
            if not row.get(req):
                problems.append(f"campaign ledger {rid}: {req} is required on every row")
        for key in row:
            if key not in allowed and key != "id":
                problems.append(f"campaign ledger {rid}: field {key!r} is not in the declared column set")
            if key in ("revenue", "forecast", "conversion_rate", "expected_earnings"):
                problems.append(f"campaign ledger {rid}: {key} may not be stored; the brief excludes a "
                                f"conversion score and a revenue forecast, and it is derived arithmetic anyway")
        for f in ("period_start", "period_end", "obtained_on"):
            if row.get(f) and not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", str(row[f])):
                problems.append(f"campaign ledger {rid}: {f} must be an ISO date")
        src = str(row.get("source", ""))
        if src and not (">" in src or "Search Console" in src or "Associates" in src):
            problems.append(f"campaign ledger {rid}: source {src!r} does not name a report this site is allowed to quote")
        for url in re.findall(r"https?://([^\\s\"'<>]+)", src):
            host = url.split("/")[0].lower()
            if host not in REGISTERED_HOSTS:
                problems.append(f"campaign ledger {rid}: source cites {host}, which is not a registered official host")
    starts = [r.get("period_start") for r in rows if r.get("period_start")]
    if starts != sorted(starts):
        problems.append("campaign ledger: rows must stay in period order so a reader sees the trail, not a pile")
    return problems


def check_measurement_contract(pages):
    """Build guard: the privacy promise on measurement.html is a property of the shipped script.

    The site's whole disclosure position is that it watches nothing. That made adding the brief's
    click counter a real decision rather than a free one: a sentence saying "runs no analytics" in
    the footer and a script posting to a collector cannot both be true on the same commit. So the
    boundary is asserted in code - the shipped JS makes no network call and sets no cookie, the
    endpoint stays switched off while no endpoint URL is configured, and the moment an endpoint is
    configured the footer's sentence is required to stop claiming there is no analytics.
    """
    problems = []
    for bad in ("fetch(", "XMLHttpRequest", "sendBeacon", "document.cookie =", "import(", "@import"):
        if bad in JS:
            problems.append(f"assets/app.js: {bad!r} breaks the no-network promise measurement.html makes")
    endpoint = (CONFIG.get("analytics_endpoint") or "").strip()
    status = str(MEASUREMENT.get("endpoint_contract", {}).get("status", ""))
    if not endpoint and status.strip().lower().startswith("enabled"):
        problems.append("data/measurement.json says the endpoint is enabled while data/config.json has no URL to send to")
    if endpoint and status.strip().lower().startswith("not built"):
        problems.append("data/config.json sets an analytics endpoint but data/measurement.json still says it is not built")
    if endpoint:
        for rel in ("index.html", "measurement.html"):
            text = pages.get(rel, "")
            if "runs no analytics" in text:
                problems.append(f"{rel}: the footer still states that the site runs no analytics while an endpoint is configured")
    if not endpoint and '"z1k.ledger.v1"' not in JS:
        problems.append("the on-device ledger key disappeared from assets/app.js while measurement.html still documents it")
    # The five events the page promises must be the five events the script can emit.
    spec_names = {e["name"] for e in MEASUREMENT.get("events", [])}
    if len(spec_names) != 5:
        problems.append(f"data/measurement.json defines {len(spec_names)} events; the brief asked for five defined events")
    for name in spec_names:
        if f"'{name}'" not in JS:
            problems.append(f"measurement.html documents event {name!r} but assets/app.js never records it")
    return problems


'''

sub('''def check_no_orphan_pages(pages):''', GUARDS.lstrip('\n') + '''def check_no_orphan_pages(pages):''', 'guards-defs')

sub('''    orphan_pages = check_no_orphan_pages(pages)''',
    '''    link_problems = check_special_links(pages)
    if link_problems:
        raise SystemExit("BUILD FAILED - outbound links are not Special Links as Amazon defines them "
                         "(Program Policies 2(b), Operating Agreement 3):\\n  " + "\\n  ".join(link_problems))
    intent_problems = check_link_intent()
    if intent_problems:
        raise SystemExit("BUILD FAILED - the product-intent record is incomplete or has merged its two fields:\\n  "
                         + "\\n  ".join(intent_problems))
    ledger_problems = check_campaign_ledger()
    if ledger_problems:
        raise SystemExit("BUILD FAILED - campaign ledger row without a dated provenance trail:\\n  "
                         + "\\n  ".join(ledger_problems))
    measure_problems = check_measurement_contract(pages)
    if measure_problems:
        raise SystemExit("BUILD FAILED - measurement layer contradicts its own privacy contract:\\n  "
                         + "\\n  ".join(measure_problems))

    orphan_pages = check_no_orphan_pages(pages)''', 'guards-wired')

# ---------------------------------------------------------------- PROGRAMME_FLAGS: F76 / F77
NEW_FLAGS = '''
    # ---- arena/3093e674, pass 13, 2026-11-17 -------------------------------------------- #
    ("F76", "The brief names five product links; the site has only ever been built for three, and two of the five cannot be mapped to a model at all.",
     "data/products.json (new candidates[]), data/link-intent.json rows LI-04 and LI-05, links.html",
     "Recorded 2026-11-17 by arena/3093e674-zone1. The project brief of that date lists link.amazon/B0c8moW59 and link.amazon/B0f3GKalj alongside the three original tokens; sixteen passes resolved and published against three only. Both new tokens resolve - on the first read ever taken of them - to ThermoMaven instant-read ASIN B0DHZTCNR5 and CHEF iQ iQ Sense Gen 3 ASIN B0DZFD6R9Z, both under Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat, i.e. outside the air-fryer set the site's comparison, category page and figures were built around. They are published as candidates, not folded into that set: a three-way air-fryer comparison that silently gained two thermometers would be a worse buying guide than an incomplete one. The ThermoMaven row is deliberately almost empty. Its listing title claims \\"1 Sec\\" while the brand's own F1 page states 0.7 seconds for the F1, and the brand sells an F1, an F1 Stealth and an F1 Ace - so the listing cannot be attached to any one of them, and no accuracy, ingress or warranty figure is published as \\"this product's\\" (the brand figures are shown attributed to the F1 page, with the mismatch named). The CHEF iQ row can carry more because the brand page states the sensor count, the 1,000°F limit and the appliance list, and the listing agrees with all three; its variant code stays partial because the codes run per probe count and colour while the Amazon listing sells a 3-probe bundle. Decision needed from the owner: confirm which product each new link is meant to promote, then either build the thermometer category properly (product pages, verification rows, cluster) or drop the two links from the brief's scope. Until then these two links are recorded, disclosed and tagged, and not recommended. Evidence: reports/verification-2026-11-17-3093e674.md, S36, S37, S38, S39.",
     ["S36", "S37", "S38", "S39"]),
    ("F77", "The root build now tags its outbound links; the s2 annex still publishes untagged ones, and both are served.",
     "build.py amazon_out_link() vs scripts/build_s2_site.py",
     "Recorded 2026-11-17 by arena/3093e674-zone1. From this date the canonical build composes every product CTA as https://www.amazon.com/dp/<ASIN>?tag=<data/config.json associate_tag>, and check_special_links() fails the build if a CTA lacks the configured tag. The s2 annex is another session's generator, outside this pass's declared scope, and it still renders plain untagged /dp/ URLs per its own data/config.json reading. Concretely: a reader or crawler following an s2 page's product link reaches Amazon with no Associates ID, so the referral cannot be credited, and the annex's pages claim the same products the root build claims. Nothing published in the annex was edited or deleted here, because its rows are cited as evidence by its own verifier (393 assertions). Decision needed: adopt the root link builder in scripts/build_s2_site.py, or label every annex page \\"dated evidence, no commercial links\\" and remove its CTAs. The root build is the one to fix first if only one is fixed, since it is what the site's index, feed and sitemap present to search.",
     ["S2"]),
]
'''
sub('''     []),
]

# Repository files that evidence a programme-level flag.''', '''     []),
''' + NEW_FLAGS + '''
# Repository files that evidence a programme-level flag.''', 'flags-appended')

sub('''REPO_EVIDENCE = {
    "F74":''', '''REPO_EVIDENCE = {
    "F76": ["data/link-intent.json", "data/products.json", "reports/verification-2026-11-17-3093e674.md"],
    "F77": ["build.py", "scripts/build_s2_site.py", "data/config.json"],
    "F74":''', 'repo-evidence')

p.write_text(s, encoding='utf-8')
print('patch 4 done:', len(orig), '->', len(s))
