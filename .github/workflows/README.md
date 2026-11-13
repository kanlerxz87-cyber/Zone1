# CI

`ci.yml` runs the same gate as the local `scripts/ci-check.sh`:

1. `platform/tests` — 33 regression tests, one per policy constraint enforced in code;
2. `platform/audit/report.py` — every `verified` row cites an official host, every
   `unverified` row is blank, every flag reference resolves;
3. rebuild + `--check` — the committed HTML must equal a rebuild from `data/*.json`, so a
   hand-edit of a table cell fails the build;
4. `scripts/check_links.py` — no broken internal link, and **no table row without a link**.

GitHub Pages for this site publishes from the **`main` branch root** (legacy build type), so the
generated HTML is committed and *is* the artifact; there is deliberately no `deploy-pages` job,
because adding one would switch the publishing source. See
[configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
and note that commits pushed with `GITHUB_TOKEN` do not trigger a Pages build.
