# Verification report — arena/b3ed16c4-zone1

**Date:** 19 November 2026 (UTC)
**Base:** `main` @ `2be3bea` (merge of PR #163)
**Scope:** findability and index boundary; live re-read of the five supplied links; two gate defects; three decision rows; the release record.

This pass repaired one thing a reader can see and could not previously see: the site asked a
search engine to rank seven differently-worded versions of the same subject from one address.
It did not add product facts, prices, ratings, traffic figures or conversion claims.

---

## 1. What was read live, and when

Every item below was fetched in this session. Nothing is quoted from memory or from an earlier
pass's notes.

| Source | URL | What it was read for | Result |
|---|---|---|---|
| **S46** RFC 9309 | <https://www.rfc-editor.org/rfc/rfc9309.html> | §2.3 "Access Method": the rules MUST be accessible in a file named `/robots.txt` "in the top-level path of the service", URI `scheme://authority/robots.txt`. §2.2.4: crawlers MAY interpret other records there, naming Sitemaps, and such parsing MUST NOT interfere with the protocol's own records. | Confirms a `robots.txt` at `/Zone1/site/` is never the file. It does not by itself prove a crawler ignores a `Sitemap:` line in one; see §4. |
| **S47** Google: block indexing | <https://developers.google.com/search/docs/crawling-indexing/block-indexing> | That `noindex` is a `<meta>`/header rule; that "specifying the `noindex` rule in the robots.txt file is not supported by Google"; that a robots.txt block stops the tag being seen at all. Page last updated 2025-12-10 UTC. | Confirms the mechanism chosen, and why `robots.txt` Disallow would have been the wrong tool. |
| **S30** Google: robots.txt intro | <https://developers.google.com/search/docs/crawling-indexing/robots/intro> | "it is not a mechanism for keeping a web page out of Google"; a robots.txt-blocked page's URL "can still appear in search results". | Bounds the claim: `noindex` is the mechanism, `robots.txt` is crawl control. |
| **S31** Google: qualify outbound links | <https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links> | Already registered; not re-read in substance this pass. | Unchanged. |
| **PI-01** supplied link | <https://link.amazon/B04G1MEwY> | Followed live. Lands on `https://www.amazon.com/dp/B0CDY277D3`, title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…", breadcrumb Home & Kitchen › … › Air Fryers. | Matches the recorded observation for 2026-11-19. Product *intent* still unconfirmed. |
| **PI-02** supplied link | <https://link.amazon/B02NbDxp3> | Followed live. Lands on `https://www.amazon.com/dp/B09B7SB46R`, "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…". | Matches the record. Intent unconfirmed. |
| **PI-03** supplied link | <https://link.amazon/B00hJ57DV> | Followed live. Lands on `https://www.amazon.com/dp/B08DKYBTPH`, "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option…". | Matches the record. Intent unconfirmed. |
| **PI-04** supplied link | <https://link.amazon/B0c8moW59> | Followed live. Lands on `https://www.amazon.com/dp/B0DHZTCNR5`, "ThermoMaven 1 Sec Professional Digital Meat Thermometer… Black". | Matches the record. Intent unconfirmed. |
| **PI-05** supplied link | <https://link.amazon/B0f3GKalj> | Followed live. Lands on `https://www.amazon.com/dp/B0DZFD6R9Z`, "CHEF iQ Sense \| Smart Wireless Meat Thermometer \| 3 Ultra-Thin Probes… Gen3". | Matches the record. Intent unconfirmed. |

**Not verified, and not claimed:** whether `shopnow047c-20` is the tag on any of these five
links; whether that tracking ID exists in the owner's account; whether any of the five
destinations is the *intended* listing. All five land on `plpRedirect=mhFallback` URLs, which is
an observation about the redirect, not evidence of intent or attribution. `data/config.json`
keeps `associate_tag` blank and `build.py` fails if a tag is configured before the confirmation
and enrolled-test fields are filled.

---

## 2. Defect 1 — six annex trees were indexable, and two of them could not have been excluded

**Found by:** enumerating every `*.html` file in the repository and reading its `<head>`, then
comparing that list against the canonical build's `PUBLIC_INDEX_PAGES` set.

**Observed before repair:**

| Tree | Pages | `<meta name="robots">` | Own `robots.txt`/`sitemap.xml` | Canonical |
|---|---|---|---|---|
| `site/` | 11 | `index,follow` on all 11 | yes / no | none |
| `dashboard/` | 14 | none | yes / yes (15 URLs) | `/Zone1/dashboard/` on index only |
| `research/` | 12 | none | no / no | **relative**, e.g. `href="analysis.html"` |
| `s2/` | 13 | none | no / no | none |
| `annex-88769516/` | 10 | none | no / no | none |
| `session-3740f69d/` | 11 | none | no / no | none |

Two of these also declared canonicals that did not identify one URL set: `research/` emitted a
bare relative canonical (`href="analysis.html"`), which is interpreted against whatever URL the
crawler fetched, so the same file could be canonicalised to two different addresses depending on
which link was followed. (`docs/` also points its canonical at `/Zone1/index.html`, but there it
is correct: those pages are a retired redirect to that page — see §4.5.)

**Repaired:**

- `site/` and `dashboard/`, and `research/`, `s2/`, `annex-88769516/`, `session-3740f69d`:
  every page now carries `<meta name="robots" content="noindex,follow">`.
- `research/` and `site/` and `s2/` now emit an **absolute** canonical to their own address
  (`research/build_research.py` gained a `SITE` constant before `layout()` uses it — the first
  attempt emitted nested pages as `/Zone1/research/<basename>`, which was wrong and was corrected
  in the same pass before commit).
- The three trees with no generator were repaired by `scripts/add_annex_noindex.py`, which is
  idempotent and additive: it inserts a `<meta>` and a `<link>` and alters nothing else.
- `dashboard/robots.txt`, `dashboard/sitemap.xml` and `site/robots.txt` were **deleted**;
  `scripts/build_site.py` no longer writes one and says why in place. The two dashboard pages
  that linked them now link the site-root pair.
- `verify.py` check 4b fails the build if any annex page lacks the directive, asks to be indexed,
  or if any sub-directory `robots.txt`/`sitemap.xml` reappears.

**Proven to fail** (a guard that cannot fail is decoration):

```
--- verify.py should FAIL ---
errors             : 1
  FAIL  dashboard/index.html: annex page asks to be indexed; only the canonical publication
                                may be indexed (annex boundary, F105)
--- restored ---
errors             : 0
```

Also covered by four new tests in `tests/test_publication.py` (`AnnexBoundaryTests`).

**Boundary of the claim:** this makes the *published HTML* ask for one indexable site. It does
not prove any engine has already indexed an annex URL, does not force recrawls, and does not
make the canonical shop rank for anything. Those need Search Console (SG-51, owner-only).

---

## 3. Defect 2 — a described check that checked nothing

`verify.py` contained, under the heading "source badges resolve to declared sources":

```python
for m in re.finditer(r'title="([^"]*?)\s*—', text):
    pass
```

A loop over every citation badge whose body was `pass`. The docstring's promise — "every source
badge points at a real official URL" — was therefore carried only by a separate string test for
`"unknown source"`, which a badge with the wrong URL never contains.

**Repaired:** the no-op loop is gone and replaced with check **2b**, which parses every
`<a class="src" href="…">S#</a>` and fails if the id is unregistered or the href differs from
the URL registered in `data/sources.json` for that id. The `.src` class is also used for internal
question/decision cross-references, so the check is scoped to `S`-ids.

**Measured first, then gated:** 1,400 S-badges across the 136 published pages, **0 mismatches**.
The check therefore starts green and exists to keep it that way.

---

## 4. What this pass did *not* establish

Recorded so a later pass does not inherit a stronger claim than the evidence supports.

1. **No `Sitemap:` line was added to `robots.txt`, and no `Sitemap:` line was claimed to be
   invalid.** RFC 9309 §2.2.4 lists Sitemaps explicitly as a record crawlers MAY interpret and
   says such parsing MUST NOT interfere; it does not say the record is only read at the root, and
   it does not name Sitemaps in the ABNF. Google's own documentation directs publishers to submit
   through Search Console or the robots.txt `Sitemap` line, and the root sitemap is already
   declared there. The finding above rests on RFC 9309 §2.3 — the **robots.txt file itself** is
   only fetched at the authority root — which is unambiguous, and on the pages' own
   `noindex` directives, which are unambiguous.
2. **The five supplied links are not declared valid, invalid or non-compliant.** §1 records what
   each one resolved to on 2026-11-19. The unresolved external record remains
   <https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003>.
3. **No traffic, ranking, click or conversion number is asserted anywhere in this pass.** The
   campaign ledger is still empty and production analytics is still off.
4. **No annex page body was rewritten.** Six trees belong to other sessions' passes; this pass
   added a `<meta>` and a `<link>` and changed nothing a reader reads.
5. **`docs/` was read and left alone, because it is already correct.** It is not a live annex
   build: all seven pages are titled "Moved · Zone1 Kitchen", carry `noindex,follow`, and their
   canonical points at `https://kanlerxz87-cyber.github.io/Zone1/index.html` — which is what a
   retired copy that redirects should say. Reading it first is why it is not in the repaired set.
   An earlier draft of this report called it a defect; the page text was checked and the claim
   withdrawn.

---

## 5. Gates run on the final tree

| Gate | Command | Result |
|---|---|---|
| Canonical build | `python3 build.py` | 58 pages, 36 sitemap URLs, 24 RSS items |
| Canonical verify | `python3 verify.py` | 136 pages, 77 spec rows (75 verified, 2 blank+flagged), **47 sources**, 0 errors, **0 external warnings** |
| Root unit tests | `python3 -m unittest discover -s tests` | **66 tests**, OK (61 before this pass) |
| JS client tests | `node --test tests/*.test.cjs` | 8 tests, 0 fail |
| Platform tests | `python3 -m unittest discover -s platform/tests -t platform` | 33 tests, OK |
| Data audit | `python3 platform/audit/report.py` | AUDIT PASSED, 0 warnings |
| Annex verifier | `python3 scripts/verify_site.py` | 393 assertions, ALL CHECKS PASSED |
| Annex build currency | `python3 scripts/build_s2_site.py --check` | build current, 16 files |
| Research section | `python3 research/check_research.py` | OK — no broken links, no unsourced rows, disclosure on every page |
| Link coverage | `python3 scripts/check_links.py` | 11,342 links OK |
| Deterministic rebuild | `git diff --exit-code` after `build.py` | clean |

Page-level metadata on the canonical 58 pages: **0 duplicate titles, 0 duplicate descriptions,
0 missing descriptions** — checked across all 136 published HTML files during this pass.

---

## 6. New register rows

- **F105** — the annex index boundary, its evidence and its limits (§2, §4).
- **S46** RFC 9309; **S47** Google block-indexing. Both read live 2026-11-19.
- **SG-51** — claim the property and read a real report before writing another guide.
- **SG-52** — whether the six annex builds stay published at all.
- **SG-53** — one decision path from each product page instead of a citation block.
- **SG-05** — current state refreshed; it previously described the annex situation as
  "partial" without naming the boundary.

## 7. Open items handed forward

| Item | Why it is not done here | Where it is tracked |
|---|---|---|
| Search Console property, sitemap submission, first query report | Needs the account holder's sign-in | SG-51, F101 |
| `docs/` is a correct retired redirect; the live annex set is the six trees in §2 | Not a defect — read, confirmed, left alone | this report §4.5 |
| Annex pages carry no "canonical site is here" banner | Their bodies belong to other passes | SG-52 |
| Photography rights, editorial byline, cadence | Owner decisions | SG-42, SG-32, Q-32 |
| `shopnow047c-20` applied to links | Blocked by intent + enrolled-test fields | F76, F101, `data/product-intent.json` |
