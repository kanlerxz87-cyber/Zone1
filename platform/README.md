# platform/ — the affiliate engine

Dependency-free Python 3 (stdlib only). Nothing here reaches the network at build
time, and nothing here invents a value.

## The rule the whole package is built around

A product field is either **sourced from an official page** or **blank**. `None` is a
valid value; a plausible guess is not. `platform/audit/report.py` enforces that on the
published data, and CI fails when it is violated.

```
platform/
  _common.py              Fact / Report types; the official-host allowlist
  credentials.py           env-only credential detection; placeholders are rejected
  research.py              intake -> candidate records (fields empty until sourced)
  resolver/link.py          fallback-shuffle detector: refuses to attribute a shuffle
  catalog/asin.py           ASIN + ISBN validation, /dp/ and short-link parsing
  links/validator.py        tag presence, XXXXX-## form, redirector and sub-tag rules
  compliance/gates.py       the 25 program rules, as callable guards
  content/generator.py      article / comparison / guide templates with placeholders
  content/claims_checker.py  every sentence needs a source, or it does not ship
  content/lint.py           Program-Content alteration, bookmark CTAs, list context
  content/similarity.py     transformative-use ratio (originality requirement)
  model/attribution.py      24h session, 89-day cart, 180-day fulfilment
  model/economics.py          Qualifying Revenue, rate refusal, payout minimums
  pricing/source_guard.py   prices only from an Amazon-served link or Creators/PA API
  training/gate.py          blocks Program Content from model training datasets
  templates/comparison.py   lowest-new / lowest-used comparison rule
  pipeline/rot_sweep.py     staleness expiry for point-in-time fields
  pipeline/promo_expiry.py  prune finished promotion claims automatically
  pipeline/eligibility.py   subscription / pre-order / 404 exclusions
  scoring.py                disclosed-weight scoring; refuses on partial input
  audit/report.py           CI data-integrity audit (A1..A5)
  tests/test_platform.py    33 regression tests, one per enforced rule
```

## Run it

```bash
python3 -m unittest discover -s platform/tests -t platform   # 33 tests
python3 -c "import sys;sys.path.insert(0,'platform');from audit.report import audit_data;print(audit_data().to_dict())"
```

## Resolver note (why `resolver/link.py` exists)

`https://link.amazon/<token>` for an unknown token answers with a real product page
carrying `lv=shuf` and `plpRedirect=mhFallback` — Amazon's "we could not find that
page, here is something popular" shuffle. A naive follow-the-redirect resolver reports
that as a successful resolution. It is not one, and `classify()` refuses it.
