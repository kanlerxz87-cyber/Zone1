import json, pathlib, collections

D = pathlib.Path('data')
TODAY = "2026-11-17"
SESS = "arena/3093e674-zone1"


def load(name):
    return json.load(open(D / name, encoding='utf-8'), object_pairs_hook=collections.OrderedDict)


def save(name, d):
    json.dump(d, open(D / name, 'w'), indent=2, ensure_ascii=False)
    open(D / name, 'a').write("\n")


def od(*pairs):
    return collections.OrderedDict(pairs)


# ================================================================ 1. config: the endpoint key the contract reads
cfg = load('config.json')
if 'analytics_endpoint' not in cfg:
    ordered = collections.OrderedDict()
    for k, v in cfg.items():
        ordered[k] = v
        if k == 'sub_tags':
            ordered['analytics_endpoint'] = ""
    ordered.setdefault('analytics_endpoint', "")
    ordered['analytics_endpoint_note'] = (
        "The one place a measurement endpoint would be configured. Empty means nothing is collected off the "
        "device, which is what measurement.html and the footer both claim. check_measurement_contract() fails "
        "the build if a non-empty endpoint ever coexists with those sentences, so turning collection on is a "
        "data edit plus a disclosure rewrite - never a silent script.")
    cfg = ordered
    save('config.json', cfg)
print('config keys:', list(cfg.keys()))

# ================================================================ 2. requirements
req = load('requirements.json')
by = {r['id']: r for r in req['requirements']}

by['A-09']['status'] = 'delivered'  # unchanged; touched only to assert the key exists

req['purpose'] = (f" Every requirement in the brief, one row each, with the status judged against what is "
                  f"actually in this repository and published on this site on {TODAY} - not against what the "
                  f"plan says. Where a requirement cannot be met, the row names the exact missing input and the "
                  f"clause that makes it missing.")
req['compiled'] = TODAY
req['session'] = f"{SESS} (pass 13; statuses for E-01 to E-05, C-01 and B-07 re-judged against the link and " \
                  f"measurement work of this date)"

# --- E-01: publish and manage affiliate links. The typed anchor count is gone for good: it was stale the
#     moment CTAs appeared on more pages, and a register that types a count cannot be trusted to update it.
e1 = by['E-01']
e1['status'] = 'partial'
e1['where'] = ["products/chefman-6qt-dual-basket.html", "compare.html", "picks.html",
               "categories/kitchen-appliances.html", "links.html", "build.py"]
e1['evidence'] = [od(("label", "a product page"), ("url", "products/chefman-6qt-dual-basket.html")),
                  od(("label", "the link record"), ("url", "links.html"))]
e1['why'] = ("Every outbound commercial anchor on the site is now built by one function and is qualified by "
             "another: product pages, the comparison matrix, the category table and the picks cards all carry the "
             "same tagged canonical link, each with rel=\"sponsored\", because qualify_affiliate_links() rewrites "
             "them and check_affiliate_link_qualification() fails the build if any is unqualified. The row states "
             "no anchor count on purpose - the last version of this sentence typed 'thirteen' and went stale "
             "within a day of being written. What is still not managed is the destination's provenance: the tag "
             "the links carry has not been confirmed inside Associates Central (E-02), and the three product "
             "identities remain candidates (C-01).")
e1['sources'] = ["S30", "S31", "S2"]

# --- E-02: attach the owner's tag.  blocked -> partial: the mechanism now exists and is enforced.
e2 = by['E-02']
e2['status'] = 'partial'
e2['where'] = ["links.html", "data/config.json", "build.py", "handover.html"]
e2['evidence'] = [od(("label", "the link record, row by row"), ("url", "links.html")),
                  od(("label", "the generator's link builder"), ("url", "build.py"))]
e2['why'] = ("Two facts changed on 2026-11-17. The owner named the tracking ID to publish with "
             "('Selected Tracking ID:shopnow047c-20'), recorded in data/config.json with its provenance, and the "
             "root build stopped depending on the supplied short links: it now composes the canonical "
             "/dp/<ASIN>?tag=\u2026 Special Link itself, and check_special_links() fails the build if a buy CTA "
             "forgets the tag, points at the redirector, or carries a tag the config never declared. What stays "
             "open is not mechanism but proof - whether that ID is live in an approved account, and whether Amazon "
             "credits a hand-composed link (Q-04, Q-30). One click and one report row answers both, and that test "
             "is the first step on handover.html. Until it passes the site is compliant in form and unproven in "
             "fact, which is why this row is not 'delivered'.")

# --- E-03: track clicks.  not_delivered -> partial: on-device counting shipped, aggregation did not.
e3 = by['E-03']
e3['status'] = 'partial'
e3['where'] = ["measurement.html", "assets/app.js", "data/measurement.json"]
e3['evidence'] = [od(("label", "what is counted and what is not"), ("url", "measurement.html"))]
e3['why'] = ("A measurement layer now exists: five events specified in data/measurement.json and counted by the "
             "visitor's own browser, exported or erased on the same page. It is deliberately not an aggregate - "
             "there is no collector, because a third-party tracker would make the footer's 'this site runs no "
             "analytics and sets no cookies' false, and Program Policies \u00a73(e) requires that statement to be "
             "accurate. check_measurement_contract() holds both halves together: the shipped script may make no "
             "network request or set a cookie, and the sentence may not survive on any page while an endpoint is "
             "configured in data/config.json. So the owner can see what they clicked; nobody can see what anyone "
             "else clicked. Page-level attribution is available without a tracker through Amazon's own tracking "
             "IDs, and that path is blocked only on the account (Q-28).")
e3['sources'] = ["S2"]

# --- E-04: conversions. stays blocked, but the reason is now narrower.
by['E-04']['why'] = ("Conversions are reported only by Amazon, inside the Associates account, after real sales; "
                     "nothing on this site can observe them and no third-party estimate would be the owner's actual "
                     "number. What changed on 2026-11-17 is what happens when that number arrives: campaign "
                     "figures now have one legal home, data/campaign-ledger.json, and a row without a dated "
                     "provenance line fails the build - so the account report can be transcribed without becoming "
                     "a forecast, an earnings claim or a fabricated conversion rate.")

# --- E-05: optimise campaigns. not_delivered -> partial: the loop's input now has a schema and a gate.
e5 = by['E-05']
e5['status'] = 'partial'
e5['where'] = ["platform/pipeline/rot_sweep.py", "measurement.html#ledger", "data/campaign-ledger.json"]
e5['evidence'] = [od(("label", "rotation sweep"), ("url", "platform/pipeline/rot_sweep.py")),
                  od(("label", "the ledger it would read"), ("url", "data/campaign-ledger.json"))]
e5['why'] = ("The input problem is partly built now. There is a place to put a campaign period and the numbers "
             "observed in it (data/campaign-ledger.json, rendered as a table on measurement.html), the rules that "
             "decide whether a figure may enter it, and an on-device click counter that answers the denominator "
             "question for a single visitor. There are no rows, because rows are an owner transcription from "
             "Associates Central and the ledger is empty on purpose: a generated row would be a fabricated fact. "
             "The rotation sweep still has nothing to act on, and it will not until either the ledger has dated "
             "rows or the account's own tracking-ID report is in use (Q-28).")

# --- C-01: resolve the three supplied links. blocked, but the record is now published and checkable.
c1 = by['C-01']
c1['where'] = ["data/products.json", "data/link-intent.json", "links.html", "data/flags.json"]
c1['evidence'] = [od(("label", "the link record"), ("url", "links.html")),
                  od(("label", "the supplied link"), ("url", "https://link.amazon/B04G1MEwY"))]
c1['why'] = c1['why'] + (" The record is now a published register of its own (data/link-intent.json, shown on "
                         "links.html) with five rows \u2014 the three original tokens plus the two added by the "
                         "brief of 2026-11-17 \u2014 each keeping 'intended' and 'observed' as separate fields, and "
                         "a build guard that fails if a row ever merges them without a confirmation from the "
                         "account holder. Status stays blocked: the only thing that closes it is someone who can "
                         "see the account reading the listing.")

# --- B-07: organic traffic. still not delivered; say what changed in the shape of the attempt.
by['B-07']['why'] = ("Still the honest gap, and still not delivered: nothing has been submitted to a search "
                     "engine, no page has an inbound link, the domain is a github.io project subpath rather than "
                     "one the owner controls, and the measurement layer is on-device only, so even a visitor would "
                     "leave no trace here. What this pass changed is the side the owner does not control: the "
                     "fourth editorial hypothesis in the brief is now an article "
                     "(articles/questions-before-a-multi-function-appliance.html), the front page leads with the "
                     "buyer's own four questions instead of a product grid, and every page keeps its answer sourced "
                     "to a dated read. Sitemap and feed remain preconditions, not causes.")

# --- new rows: the three mechanisms this pass actually added
req['requirements'] += [
    od(("id", "E-07"), ("scope", "Publishing"),
       ("requirement", "No link may reach Amazon without the account's identifier attached to it"),
       ("clause", "publish and manage affiliate links \u2014 Program Policies 2(a)/(b), Operating Agreement 3"),
       ("status", "delivered"),
       ("where", ["links.html", "build.py", "data/link-intent.json"]),
       ("evidence", [od(("label", "the generator's guard and builder"), ("url", "build.py"))]),
       ("why", ("Enforced, not hoped for. Special Links must use the assigned Associates ID as a URL parameter, and "
                "the fee obligation does not survive a badly formed link, so every buy CTA is composed from one "
                "config value and check_special_links() fails the build on an untagged anchor, on a link aimed at "
                "the redirector instead of the product, on a tag the config never declared, and on any tag that "
                "does not match Amazon's own XXXXX-## shape \u2014 including every sub-tag in "
                "data/config.json. {n_link_rows} rows of intent data are cross-checked in the same run, so a "
                "marketed product with no covering link row is also a build failure.")),
       ("sources", ["S2", "S16", "S17", "S36", "S37", "S38", "S39"])),
    od(("id", "F-09"), ("scope", "Compliance"),
       ("requirement", "No revenue, forecast or conversion claim may be published as if it were observed"),
       ("clause", "no inaccurate, overbroad or misleading claims \u2014 Program Policies 2(b); and the brief's "
                  "demand for real traffic, not a simulation of it"),
       ("status", "delivered"),
       ("where", ["measurement.html#ledger", "data/campaign-ledger.json", "build.py"]),
       ("evidence", [od(("label", "the ledger's derivation rules"), ("url", "data/campaign-ledger.json"))]),
       ("why", ("The campaign ledger is the site's only place for a performance number, and it is gated: a row "
                "needs a period, a named source whose host is one this repository already recognises, and the "
                "date it was obtained, and the words revenue, forecast, conversion_rate and expected_earnings are "
                "rejected as fields outright. {n_ledger_rows} rows are published \u2014 the honest answer, because "
                "no sales have been observed. The generator refuses to invent a figure, which is the same rule "
                "that leaves a product spec blank.")),
       ("sources", ["S2"])),
    od(("id", "F-10"), ("scope", "Compliance"),
       ("requirement", "What the site says about tracking must be true of the code it ships"),
       ("clause", "disclose technology use accurately \u2014 Program Policies 3(e); FTC clear-and-conspicuous"),
       ("status", "delivered"),
       ("where", ["measurement.html", "assets/app.js", "data/measurement.json", "build.py"]),
       ("evidence", [od(("label", "the contract and its guards"), ("url", "measurement.html"))]),
       ("why", ("The privacy statement in the footer was written as a promise, so it became a test: "
                "check_measurement_contract() reads the shipped JavaScript and fails if it contains a fetch, an "
                "XMLHttpRequest, a beacon, a cookie write or a dynamic import, fails if a spec event is not "
                "implemented, and fails if any page still says 'runs no analytics' after an endpoint has been "
                "configured in data/config.json. The measurement layer is therefore specified, switched off, and "
                "unable to drift into being something else without a build failure.")),
       ("sources", ["S1", "S2"])),
    od(("id", "D-07"), ("scope", "Content"),
       ("requirement", "Cover the buyer's questions, not just the products supplied"),
       ("clause", "generate SEO-optimized product articles, comparisons, and buying guides"),
       ("status", "partial"),
       ("where", ["articles/questions-before-a-multi-function-appliance.html",
                  "articles/meat-thermometer-in-an-air-fryer.html", "data/topics.json", "index.html"]),
       ("evidence", [od(("label", "the topic register"), ("url", "data/topics.json")),
                     od(("label", "the front page's question band"), ("url", "index.html"))]),
       ("why", ("{n_topics} topics are registered and {n_articles} articles are published, so all four editorial "
                "hypotheses the brief named now have an answer on the site, and the front page opens with the "
                "questions rather than the grid. The gap is the same one every content row points at: no "
                "performance data, so whether any of it earns a click is unknown and unmeasured off-device (B-07), "
                "and the topic that would follow \u2014 a thermometer category \u2014 is held behind the owner's "
                "scope decision (Q-27) rather than written speculatively.")),
       ("sources", ["S27", "S28", "S38", "S39", "S40"])),
]
save('requirements.json', req)
print('requirements:', len(req['requirements']))

# ================================================================ 3. design prompt pack
dp = load('design-prompt.json')
dp['compiled'] = TODAY
dp['how_to_read'] = (f"Status values describe the repository as built on {TODAY} and are checked against the files "
                     f"themselves, not against this document. A row may only claim 'implemented' if the path named "
                     f"on it exists.")
dby = {x['id']: x for x in dp['design']}
dby['D-13']['status_note'] = dby['D-13'].get('status_note', '') if 'D-13' in dby else ''

dp['design'].append(od(
    ("id", "D-14"),
    ("suggestion", "Build every call to action from one function, so a compliance rule can only be applied site-wide or not at all"),
    ("why", ("A pattern that exists in three places is three patterns. The disclosure, the rel attributes and the "
             "tag are the same obligation on every page, so they must come from the same builder or they will "
             "disagree the first time someone edits one copy.")),
    ("path", ("product_cta() and cta_inline() in build.py: one composes the tagged canonical link, the other is "
              "its one-line form for tables and cards. Used by the product pages, the comparison matrix, the "
              "category table and the picks cards.")),
    ("status", "implemented"),
    ("status_note", ("Added 2026-11-17 by " + SESS + " after the pass that finally supplied a tag: the compact form "
                     "carries the same rel=\"nofollow sponsored noopener\", the same 'Affiliate link' chip and the "
                     "same guarded URL, and check_special_links() reads data-z1k markers rather than prose, so a "
                     "page that forgets the pattern fails the build instead of quietly shipping.")),
    ("sources", [od(("label", "Program Policies 2(b)"), ("url", "https://affiliate-program.amazon.com/help/operating/policies"))]),
    ("links", [od(("label", "links.html"), ("url", "links.html"))])))

dp['design'].append(od(
    ("id", "D-15"),
    ("suggestion", "Let the front page start with the shopper's question, and put the products second"),
    ("why", ("A searcher arrives holding a sentence, not a model number. Four passes of hero tuning had produced a "
             "confident masthead about formats, which is a category's vocabulary rather than a buyer's.")),
    ("path", ("The 'start with a question' band on index.html, above the format guide, four cards into the four "
              "guides; the format guide and the product cards stay where they were.")),
    ("status", "implemented"),
    ("status_note", "Added 2026-11-17 by " + SESS + ". The band links only to articles that already cite their sources, so the change required no new verification."),
    ("sources", [od(("label", "Google: creating helpful, people-first content"),
                    ("url", "https://developers.google.com/search/docs/fundamentals/creating-helpful-content"))]),
    ("links", [od(("label", "the guide that completes the four"),
                  ("url", "articles/questions-before-a-multi-function-appliance.html"))])))

dp['tactics'].append(od(
    ("id", "T-12"),
    ("tactic", "Date every seasonal claim and let the build expire it"),
    ("how", ("A season block on the article row in data/articles.json \u2014 label, window, expiry date, what the "
             "page is and is not claiming, and the removal duty in the retailer's words. The article page renders "
             "it; check_seasonal_expiry() fails the build the day after the date passes.")),
    ("status", "implemented"),
    ("status_note", ("Added 2026-11-17 by " + SESS + " on the Black Friday investigation and the holiday gift "
                     "guide. The gate reads the calendar so the page does not: the rendered output stays "
                     "reproducible while the obligation stops depending on memory.")),
    ("sources", [od(("label", "Program Policies 2(b) \u2014 limited-time promotions"),
                    ("url", "https://affiliate-program.amazon.com/help/operating/policies"))]),
    ("links", [od(("label", "a seasonal page with its window on it"),
                  ("url", "articles/black-friday-model-number-switch.html"))])))

dp['decisions'].append(od(
    ("id", "R-9"),
    ("suggestion", "Whether the site may count anything at all on a reader's device"),
    ("options", [od(("label", "A. On-device only, exported by the visitor"),
                    ("what", "Five events, one localStorage key, no request of any kind. The footer's 'no analytics, no cookies' stays literally true and the owner still gets a denominator."),
                    ("effort", "M"), ("risk", "low"), ("reversible", True)),
                od(("label", "B. A self-hosted collector"),
                   ("what", "Real aggregates on a static Pages site with no server, so not available at all without new infrastructure and a privacy rewrite."),
                   ("effort", "L"), ("risk", "high"), ("reversible", True)),
                od(("label", "C. Nothing"),
                   ("what", "The state until today: compliant, and blind."),
                   ("effort", "S"), ("risk", "medium"), ("reversible", True))]),
    ("recommended", "A"),
    ("status", "implemented"),
    ("status_note", ("A is built as of 2026-11-17 by " + SESS + " and pinned by check_measurement_contract(); the "
                     "endpoint that would turn it into B is specified in data/measurement.json and left empty in "
                     "data/config.json, which is the shape of a decision still pending rather than one avoided.")),
    ("sources", [od(("label", "Program Policies 3(e)"),
                    ("url", "https://affiliate-program.amazon.com/help/operating/policies"))]),
    ("links", [od(("label", "measurement.html"), ("url", "measurement.html"))])))

save('design-prompt.json', dp)
print('design', len(dp['design']), 'tactics', len(dp['tactics']), 'decisions', len(dp['decisions']))

# ================================================================ 4. decision log: what this pass auto-adopted
dl = load('decision-log.json')
rows = [
    od(("id", "SG-36"), ("session", SESS), ("date", TODAY), ("path", "A"),
       ("what", ("Every outbound product CTA is now composed by the build as a canonical "
                 "amazon.com/dp/<ASIN>?tag=<config tag> link, with check_special_links() failing the build on an "
                 "untagged anchor, a link aimed at the short-link redirector, a tag the config never declared, or a "
                 "tag whose shape violates Amazon's published XXXXX-## pattern. The supplied short links stay "
                 "visible on each product page as the artefact being checked, not the destination.")),
       ("why_allowed", ("The owner supplied the tracking ID in writing on 2026-11-17, so the value is an instruction "
                        "rather than an invention; the change is reversible by deleting one config key; and it "
                        "publishes no Amazon-served price, no rating and no product fact the registers have not "
                        "already recorded. The scope_limit on this page forbids spending money and asserting "
                        "unverified facts - neither is done: the ASINs are carried forward as candidates.")),
       ("evidence", ["build.py", "data/config.json", "data/link-intent.json", "links.html"])),
    od(("id", "SG-39"), ("session", SESS), ("date", TODAY), ("path", "A"),
       ("what", "Added the compact call-to-action produced by the same builder to the category table, the comparison matrix's final row and the picks cards, each carrying the affiliate chip and the page-level disclosure rather than a duplicated paragraph."),
       ("why_allowed", "Reversible, low-risk, no new claims: it links to the same three candidate ASINs already marketed on the product pages, and it was the row that made the tag change worth shipping.",),
       ("evidence", ["build.py", "compare.html", "picks.html", "categories/kitchen-appliances.html"])),
    od(("id", "SG-40"), ("session", SESS), ("date", TODAY), ("path", "A"),
       ("what", ("Gave the two seasonal articles an explicit validity window in data/articles.json, rendered it on "
                 "their pages, and added check_seasonal_expiry() so the build fails the day after a window closes "
                 "until someone re-dates it against a fresh read or removes the row.")),
       ("why_allowed", "Amazon's policy states the removal duty in dated terms, the change adds a constraint rather than a claim, and the failure mode it prevents is a page asserting a promotion that ended. Reversible by deleting the season block, which would be a regression, not a preference.",),
       ("evidence", ["data/articles.json", "build.py", "articles/black-friday-model-number-switch.html"])),
    od(("id", "SG-41"), ("session", SESS), ("date", TODAY), ("path", "A"),
       ("what", "Added a four-question band to the front page above the format guide, each card linking an article that answers it, and wrote the fourth guide (multi-function buying questions) that the brief listed and the article set lacked."),
       ("why_allowed", "Content shape, not a commercial claim: every link in the band points at an existing sourced article, the new guide cites only manufacturer pages and manuals, and the register records the traffic argument as a judgement rather than a measured demand signal.",),
       ("evidence", ["data/articles.json", "data/topics.json", "index.html"])),
    od(("id", "SG-38"), ("session", SESS), ("date", TODAY), ("path", "A (mechanism only)"),
       ("what", ("Built the page-level attribution mechanism and stopped at its door: sub_tags.assigned in "
                 "data/config.json is read, validated and applied per page, and left empty. Creating the tracking "
                 "IDs themselves is an action inside the owner's Amazon account.")),
       ("why_allowed", "The half that can be automated was done; the half that would require acting as the account holder was not, which is what the standing scope limit requires.",),
       ("evidence", ["data/config.json", "build.py", "questions.html#q-28"])),
]
have = {r['id'] for r in dl['implemented']}
dl['implemented'] = [r for r in dl['implemented']] + [r for r in rows if r['id'] not in have]
dl['implemented_note'] = (f"Rows are written by the agent that did the work, on the date it was done, and only for "
                         f"suggestions the adopt-after-silence policy covers. {TODAY} ({SESS}): five rows added, "
                         f"one of them a partial adoption whose remaining half is an owner action. Nothing here "
                         f"records an owner's choice - that column is still empty, and the two decisions waiting "
                         f"on it (the product-set question and the account-side attribution) are named on "
                         f"questions.html rather than assumed here.")
dl['version'] = "1.2"
dl['compiled'] = TODAY
save('decision-log.json', dl)
print('decision-log implemented:', len(dl['implemented']), '| choices:', len(dl['choices']))
