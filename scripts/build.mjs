#!/usr/bin/env node
// Static site builder for the Zone1 affiliate product dashboard.
// Reads data/*.json, validates every value against its source, and writes docs/ (served by GitHub Pages).
// Usage: node scripts/build.mjs            -> validate + build docs/ (exit 1 on any error)
//        node scripts/build.mjs --check    -> validate only, do not write
// No dependencies. Node >= 18.

import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, readdirSync, statSync, copyFileSync } from "node:fs";
import { join, dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const DATA = join(ROOT, "data");
const OUT = join(ROOT, "docs");
const CHECK_ONLY = process.argv.includes("--check");

const read = (f) => JSON.parse(readFileSync(join(DATA, f), "utf8"));
const products = read("products.json");
const sourcesDoc = read("sources.json");
const compliance = read("compliance.json");
const flagsDoc = read("flags.json");
const site = read("site.json");

const SOURCES = Object.fromEntries(sourcesDoc.sources.map((s) => [s.id, s]));
const OFFICIAL_HOSTS = ["www.amazon.com", "affiliate-program.amazon.com", "www.ftc.gov", "docs.github.com", "github.com"];
const errors = [];
const warnings = [];
const err = (m) => errors.push(m);

// ---------- validation ----------
for (const p of products.products) {
  const u = new URL(p.official_url);
  if (!OFFICIAL_HOSTS.includes(u.host)) err(`${p.id}: official_url host ${u.host} is not an official host`);
  if (!SOURCES[p.official_source]) err(`${p.id}: official_source ${p.official_source} not in sources.json`);
  if (!SOURCES[p.resolved_via]) err(`${p.id}: resolved_via ${p.resolved_via} not in sources.json`);
  if (!p.official_url.endsWith(`/dp/${p.asin}`)) err(`${p.id}: official_url does not match ASIN ${p.asin}`);
  for (const [key, v] of Object.entries(p.values)) {
    if (v.status === "verified" || v.status === "derived") {
      if (v.value === null || v.value === "") err(`${p.id}.${key}: status ${v.status} but value is empty`);
      if (!v.source || !SOURCES[v.source]) err(`${p.id}.${key}: value has no valid source`);
      else if (!["accessible", "resolved"].includes(SOURCES[v.source].status)) err(`${p.id}.${key}: cites source ${v.source} which is ${SOURCES[v.source].status}`);
    } else if (v.status === "unverified") {
      if (v.value !== null) err(`${p.id}.${key}: unverified value must be blank (found "${v.value}")`);
    } else {
      err(`${p.id}.${key}: unknown status ${v.status}`);
    }
  }
}
for (const s of sourcesDoc.sources) {
  const host = new URL(s.url).host;
  if (!OFFICIAL_HOSTS.includes(host) && !s.id.match(/^S(4|5|6)$/)) err(`${s.id}: host ${host} is not in the official host list`);
}
for (const r of compliance.rows) if (!SOURCES[r.source]) err(`${r.id}: source ${r.source} missing`);
for (const f of flagsDoc.flags) for (const s of f.sources) if (!SOURCES[s]) err(`${f.id}: source ${s} missing`);

// Coverage numbers (computed, never typed in).
let fieldTotal = 0, fieldVerified = 0;
for (const p of products.products) for (const v of Object.values(p.values)) {
  fieldTotal++;
  if (v.status === "verified" || v.status === "derived") fieldVerified++;
}
const coveragePct = Math.round((fieldVerified / fieldTotal) * 100);
const flagCounts = { High: 0, Medium: 0, Low: 0 };
for (const f of flagsDoc.flags) flagCounts[f.severity] = (flagCounts[f.severity] || 0) + 1;

// ---------- html helpers ----------
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const badge = (status) => {
  const map = {
    verified: ["ok", "Verified"],
    derived: ["info", "Derived from title"],
    unverified: ["warn", "Unverified"],
    Met: ["ok", "Met"],
    "Not met": ["bad", "Not met"],
    "Needs review": ["warn", "Needs review"],
    accessible: ["ok", "Accessible"],
    resolved: ["ok", "Resolved"],
    blocked: ["bad", "Blocked"],
    High: ["bad", "High"],
    Medium: ["warn", "Medium"],
    Low: ["info", "Low"],
  };
  const [cls, label] = map[status] || ["info", status];
  return `<span class="badge ${cls}">${esc(label)}</span>`;
};

const NAV = [
  { id: "overview", label: "Overview", href: "index.html" },
  { id: "home-kitchen-air-fryers", label: "Category (unverified)", href: "categories/home-kitchen-air-fryers.html" },
  { id: "analysis", label: "Analysis &amp; Findings", href: "analysis.html" },
  { id: "compliance", label: "Compliance", href: "compliance.html" },
  { id: "sources", label: "Sources", href: "sources.html" },
  { id: "flagged", label: "Flagged for Review", href: "flagged.html" },
];

const disclosure = () => `
<div class="disclosure" role="note">
  <strong>Affiliate disclosure.</strong> Some links on this site are Amazon links and may earn the site owner a commission.
  Amazon Associates status: <strong>${site.associates_status === "pending" ? "pending confirmation" : "active"}</strong>.
  Required statement: <em>“${esc(site.associates_statement)}”</em>
  ${site.associates_status === "pending" ? "It will be shown as an active statement once the Associates account is confirmed. See <a href=\"{P}flagged.html\">Flagged for Review</a> (F03, F06)." : ""}
</div>`;

const layout = ({ title, active, depth, body }) => {
  const P = depth === 0 ? "./" : "../".repeat(depth);
  const nav = NAV.map((n) => `<a href="${P}${n.href}" class="${n.id === active ? "active" : ""}">${n.label}</a>`).join("\n        ");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} · ${esc(site.site_title)}</title>
<meta name="description" content="Verified, source-linked dashboard of three Amazon.com products. Unverified values are left blank.">
<link rel="stylesheet" href="${P}assets/style.css">
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <div class="brand">Zone1<span>Affiliate research</span></div>
    <nav>
        ${nav}
    </nav>
    <div class="side-foot">As of ${esc(site.as_of)}<br><a href="${esc(site.repo_url)}">Repository</a></div>
  </aside>
  <main>
    ${disclosure().replaceAll("{P}", P)}
    ${body.replaceAll("{P}", P)}
    <footer class="foot">
      <p><strong>Affiliate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases (statement pending confirmation; see above).</p>
      <p>Every value on this site is either read from a cited official source on ${esc(site.as_of)} or left blank and marked unverified. Nothing is estimated. Amazon and Amazon.com are trademarks of Amazon.com, Inc. or its affiliates; this site is not affiliated with or endorsed by Amazon.</p>
    </footer>
  </main>
</div>
<script src="${P}assets/app.js"></script>
</body>
</html>
`;
};

const srcLink = (id, label) => {
  const s = SOURCES[id];
  return `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(label ?? id)}</a>`;
};
const cellValue = (v) => (v.value === null ? "" : esc(v.value));
const statusCell = (v) => (v.status === "unverified" ? badge("unverified") : badge(v.status));

// ---------- pages ----------
const pageIndex = () => {
  const counts = { products: products.products.length, asinsVerified: products.products.filter((p) => SOURCES[p.resolved_via]).length };
  const body = `
<header class="hero">
  <p class="eyebrow">Overview · as of ${esc(site.as_of)}</p>
  <h1>Amazon affiliate product research dashboard</h1>
  <p class="lede">A simple, source-linked view of the three Amazon products submitted for affiliate marketing. Each value is read from an official source or left blank and flagged.</p>
</header>

<section class="kpis">
  <div class="kpi"><div class="num">${counts.products}</div><div class="lbl">Products tracked</div></div>
  <div class="kpi"><div class="num">${counts.asinsVerified} / ${counts.products}</div><div class="lbl">ASINs confirmed from Amazon product URLs</div></div>
  <div class="kpi"><div class="num">${coveragePct}%</div><div class="lbl">Fields verified (${fieldVerified} of ${fieldTotal})</div></div>
  <div class="kpi warn"><div class="num">${flagsDoc.flags.length}</div><div class="lbl">Flagged for review (${flagCounts.High} high)</div></div>
</section>

<section class="card">
  <h2>Executive summary</h2>
  <ul class="summary">
    <li><strong>What this is.</strong> Three product links were supplied. None resolves to a product: the identifiers are 9 characters (ASINs are 10) and each canonical check returns Amazon's page-not-found (${srcLink("S13", "S13")}–${srcLink("S15", "S15")}). The link.amazon redirects land on Amazon's <em>missing-page fallback</em> (random listings) — see flag F17.</li>
    <li><strong>What is verified.</strong> Nothing product-level. All identity fields (title, brand, capacity, department, category) are blank and marked unverified because the mapping from submitted code to product is disputed (F17). The official commission rate table is verified (${srcLink("S16", "S16")}).</li>
    <li><strong>What is not verified.</strong> Product identity, price, rating, review count and per-product commission rate. These are left blank. No pricing, review or commission analysis is provided.</li>
    <li><strong>Compliance.</strong> None of the supplied links carry an Associates tag, and the Associates account is not confirmed. The required disclosure is shown with a pending status. See <a href="compliance.html">Compliance</a> and <a href="flagged.html">Flagged for Review</a>.</li>
    <li><strong>Not built.</strong> The full AI platform (automated product discovery, trend and niche detection, competitor analysis, article generation at scale, click and conversion tracking) needs Amazon API and account data that is not available here. No data was invented to fill that gap (flag F11).</li>
    <li><strong>Next step for review.</strong> Work through the <a href="flagged.html">Flagged for Review</a> list. High-severity items F01, F03, F06, F11 and F17 need an owner decision.</li>
  </ul>
</section>

<section class="card">
  <h2>Categories</h2>
  <div class="cats">
    <a class="cat" href="categories/home-kitchen-air-fryers.html">
      <div class="cat-title">Category page — identity unverified (F17)</div>
      <div class="cat-meta">${products.products.length} rows · identity fields blank: mapping from submitted code to product is disputed (F17) · page preserved for review</div>
    </a>
  </div>
</section>

<section class="card">
  <h2>Sources and method</h2>
  <p>Official sources used: Amazon.com product pages, Amazon Associates Central (Operating Agreement and Program Policies), the U.S. Federal Trade Commission, and GitHub Docs. The full list with retrieval status is on <a href="sources.html">Sources</a>. Data is also published as JSON in <a href="data/products.json">data/products.json</a>.</p>
</section>`;
  return layout({ title: "Overview", active: "overview", depth: 0, body });
};

const pageCategory = () => {
  const rows = products.products.map((p) => {
    const v = p.values;
    return `<tr>
  <td>${p.id}</td>
  <td class="wrap">${esc(v.product_title.value)}</td>
  <td><code>${esc(p.asin)}</code></td>
  <td>${cellValue(v.brand_as_titled)}</td>
  <td>${cellValue(v.capacity_as_titled)}</td>
  <td>${cellValue(v.product_type_as_titled)}</td>
  <td>${cellValue(v.department)}</td>
  <td class="blank" title="Unverified: not present in retrieved Amazon page text (F01)">${cellValue(v.price)}</td>
  <td class="blank" title="Unverified (F01)">${cellValue(v.rating)}</td>
  <td class="blank" title="Unverified (F01)">${cellValue(v.review_count)}</td>
  <td class="blank" title="Unverified: official schedule not reachable (F02)">${cellValue(v.commission_rate)}</td>
  <td><a href="${esc(p.submitted_link)}" target="_blank" rel="noopener">${esc(p.submitted_link.replace("https://", ""))}</a></td>
  <td><a href="${esc(p.official_url)}" target="_blank" rel="noopener">${esc(p.official_source)} · amazon.com/dp/${esc(p.asin)}</a></td>
  <td class="wrap">${badge("unverified")} identity, department (F17)<br>${badge("unverified")} price, rating, reviews, commission</td>
</tr>`;
  }).join("\n");
  const body = `
<header class="hero compact">
  <p class="eyebrow"><a href="{P}index.html">Overview</a> › Category (identity unverified)</p>
  <h1>Category page — identity unverified (F17)</h1>
  <p class="lede">Rows for the three submitted links. Identity fields are blank because the mapping from submitted code to product is disputed (see <a href="{P}flagged.html">Flagged for Review</a> F17): the codes resolve to no product, and the link.amazon redirects land on Amazon's missing-page fallback. Observations of the fallback listings are preserved in the findings below for review only.</p>
</header>

<section class="card">
  <div class="toolbar">
    <input type="search" class="filter" data-target="tbl-products" placeholder="Filter products (title, ASIN, brand…)" aria-label="Filter products">
    <span class="hint">${products.products.length} rows · every row links to its official source</span>
  </div>
  <div class="table-wrap">
  <table id="tbl-products" class="data">
    <thead><tr>
      <th>#</th><th>Product (title)</th><th>ASIN</th><th>Brand (as titled)</th><th>Capacity (as titled)</th><th>Type (as titled)</th><th>Department</th>
      <th>Price</th><th>Rating</th><th>Reviews</th><th>Commission rate</th>
      <th>Submitted link</th><th>Official source</th><th>Status</th>
    </tr></thead>
    <tbody>
${rows}
    </tbody>
  </table>
  </div>
</section>

<section class="card">
  <h2>Findings for this category</h2>
  <ul class="summary">
    <li><strong>Identity disputed (F17):</strong> the rows for P1–P3 have blank titles/brands/capacities/department. The submitted codes resolve to no product (${srcLink("S13", "S13")}–${srcLink("S15", "S15")}).</li>
    <li><strong>Fallback observations (for review only, not attributed to the submitted products):</strong> the link.amazon redirects landed on missing-page fallback listings whose page titles showed “Home &amp; Kitchen” (${srcLink("S1", "S1")}, ${srcLink("S2", "S2")}, ${srcLink("S6", "S6")}). Those titles described the fallback listings (air-fryer-type appliances: 6 Quart dual-basket oven, 26QT French-door toaster oven, 8 Qt basket fryer), not the submitted products.</li>
    <li><strong>Brands in fallback titles (unconfirmed):</strong> “CHEFMAN” and “Chefman” casing differs (${srcLink("S1", "S1")}, ${srcLink("S6", "S6")}); “Emeril Lagasse” in one (${srcLink("S2", "S2")}). Not attributed to the submitted products (F10, F17).</li>
    <li><strong>Pricing and commission potential:</strong> not analysed. Price and rating were not readable, and the commission rate is unverified. No commission figure is given. Standard commission is a percentage of Qualifying Revenue, which excludes shipping, taxes and fees (${srcLink("S8", "S8, Commission Income Statement s.1, s.3")}).</li>
    <li><strong>Competition and trends:</strong> not analysed. No verified competitor, sales-rank or trend data was collected.</li>
  </ul>
</section>`;
  return layout({ title: "Home & Kitchen › Air Fryers", active: "home-kitchen-air-fryers", depth: 1, body });
};

const pageAnalysis = () => {
  const brandCounts = {};
  for (const p of products.products) {
    const b = (p.values.brand_as_titled.value || "—").toLowerCase();
    brandCounts[b] = (brandCounts[b] || 0) + 1;
  }
  const body = `
<header class="hero compact">
  <p class="eyebrow"><a href="{P}index.html">Overview</a> › Analysis</p>
  <h1>Analysis &amp; findings</h1>
  <p class="lede">Only findings that follow from verified values are listed. Anything that needs price, rating, review or commission data is marked as not possible from current sources.</p>
</header>

<section class="kpis">
  <div class="kpi"><div class="num">${products.products.length}</div><div class="lbl">Unique ASINs</div></div>
  <div class="kpi"><div class="num">${Object.keys(brandCounts).length}</div><div class="lbl">Brand names as titled (${Object.entries(brandCounts).map(([b, n]) => `${esc(b)} ×${n}`).join(" · ")})</div></div>
  <div class="kpi"><div class="num">${coveragePct}%</div><div class="lbl">Field coverage (verified or derived)</div></div>
  <div class="kpi warn"><div class="num">${fieldTotal - fieldVerified}</div><div class="lbl">Blank fields (unverified)</div></div>
</section>

<section class="card">
  <h2>Verified findings</h2>
  <table class="data">
    <thead><tr><th>#</th><th>Finding</th><th>Basis (source)</th></tr></thead>
    <tbody>
      <tr><td>A1</td><td>All three submitted codes fail canonical checks: amazon.com/dp/&lt;code&gt; returns Amazon's page-not-found (${srcLink("S13")}, ${srcLink("S14")}, ${srcLink("S15")}). The link.amazon landings (${srcLink("S4")}, ${srcLink("S5")}, ${srcLink("S6")}) are Amazon's missing-page fallback redirects (final URLs carry <code>plpRedirect=mhFallback</code>), not confirmed product mappings (F17).</td><td>${srcLink("S4")}, ${srcLink("S5")}, ${srcLink("S6")}, ${srcLink("S13")}, ${srcLink("S14")}, ${srcLink("S15")}</td></tr>
      <tr><td>A2</td><td>The fallback landing pages showed “Home &amp; Kitchen” in their page titles. These describe the fallback listings only and are not attributed to the submitted products (F17).</td><td>${srcLink("S1")}, ${srcLink("S2")}, ${srcLink("S6")} (fallback page titles)</td></tr>
      <tr><td>A3</td><td>The earlier category label (“Air Fryers”) was derived from words in the fallback titles. It is not attributed to the submitted products; the Amazon browse node was never confirmed (F17).</td><td>${srcLink("S1")}, ${srcLink("S2")}, ${srcLink("S6")}</td></tr>
      <tr><td>A4</td><td>Fallback titles included Chefman-branded appliances with differing casing (“CHEFMAN” vs “Chefman”) and one Emeril Lagasse listing. Brand match unconfirmed and not attributed to the submitted products (F10, F17).</td><td>${srcLink("S1")}, ${srcLink("S6")}</td></tr>
      <tr><td>A5</td><td>Fallback titles described capacities from 6 Quart to 26QT (dual-basket oven, French-door toaster oven, basket air fryer). Observations preserved for review only; not attributed to the submitted products (F17).</td><td>${srcLink("S1")}, ${srcLink("S2")}, ${srcLink("S6")}</td></tr>
      <tr><td>A6</td><td>None of the three links carries an Associates tag, so none can be credited to an Associates account as supplied.</td><td>${srcLink("S4")}, ${srcLink("S5")}, ${srcLink("S6")}; ${srcLink("S8", "Participation Requirements s.2(b)")}</td></tr>
    </tbody>
  </table>
</section>

<section class="card">
  <h2>Not possible from current verified sources</h2>
  <table class="data">
    <thead><tr><th>Analysis</th><th>Why it is blocked</th><th>What would unblock it</th></tr></thead>
    <tbody>
      <tr><td>Price comparison and price trends</td><td>Price not in retrieved page text. Price display is limited to Amazon-served links or the PA-API / Creators API (${srcLink("S8", "s.2(b)")}).</td><td>Creators API / PA-API access through an Associates account (F01, F11).</td></tr>
      <tr><td>Reviews, ratings and sentiment</td><td>Rating and review count not in retrieved page text.</td><td>Same as above (F01).</td></tr>
      <tr><td>Commission potential (rate × revenue)</td><td>Per-product rate blank: product category is unverified (F17). The official rate table itself is verified and published (${srcLink("S16")} — partially resolves F02).</td><td>Verify the product category, then match it to the official rate table (${srcLink("S16")}).</td></tr>
      <tr><td>Competition and market share</td><td>No verified competitor or sales data.</td><td>An approved data source (F11).</td></tr>
      <tr><td>Trending or high-converting products; profitable niches</td><td>No verified trend, sales-rank or conversion data.</td><td>Analytics and sales data (F11). None are claimed here.</td></tr>
      <tr><td>Clicks and conversions</td><td>This /docs/ build has no tracking. The integrated root site ships a working local click tracker plus the production architecture (see the root site's Analytics page); Amazon Associates reports remain the conversion source of truth.</td><td>Associates reports, plus an analytics decision by the owner (F11).</td></tr>
    </tbody>
  </table>
</section>

<section class="card">
  <h2>How commission income is calculated (official method, no rate applied)</h2>
  <p>Standard Commission Income is a percentage of Qualifying Revenue. Qualifying Revenue is the amount Amazon receives, less shipping, gift wrap, handling fees, taxes, service charges, credits, rebates, card processing fees and bad debt (${srcLink("S8", "Commission Income Statement s.1 and s.3")}). The rate is set per category on the schedule that is not reachable (${srcLink("S9")}). No amount has been calculated for any product.</p>
</section>`;
  return layout({ title: "Analysis & Findings", active: "analysis", depth: 0, body });
};

const pageCompliance = () => {
  const rows = compliance.rows.map((r) => `<tr>
  <td>${r.id}</td>
  <td class="wrap">${esc(r.requirement)}</td>
  <td>${srcLink(r.source)}<br><span class="muted">${esc(r.section)}</span></td>
  <td>${badge(r.site_status)}</td>
  <td class="wrap">${esc(r.site_action)}</td>
</tr>`).join("\n");
  const body = `
<header class="hero compact">
  <p class="eyebrow"><a href="{P}index.html">Overview</a> › Compliance</p>
  <h1>Compliance checklist</h1>
  <p class="lede">Amazon Associates Program requirements and FTC disclosure guidance, each with its source. Items marked “Needs review” appear on <a href="{P}flagged.html">Flagged for Review</a>.</p>
</header>
<section class="card">
  <div class="table-wrap">
  <table class="data">
    <thead><tr><th>#</th><th>Requirement</th><th>Source</th><th>Site status</th><th>What the site does</th></tr></thead>
    <tbody>
${rows}
    </tbody>
  </table>
  </div>
</section>`;
  return layout({ title: "Compliance", active: "compliance", depth: 0, body });
};

const pageSources = () => {
  const rows = sourcesDoc.sources.map((s) => `<tr>
  <td>${s.id}</td>
  <td class="wrap">${esc(s.title)}<br><span class="muted">${esc(s.publisher)}</span></td>
  <td><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></td>
  <td>${esc(s.accessed)}</td>
  <td>${badge(s.status)}</td>
  <td class="wrap">${esc(s.supports)}${s.review_note ? `<br><span class="muted">Note: ${esc(s.review_note)}</span>` : ""}</td>
</tr>`).join("\n");
  const body = `
<header class="hero compact">
  <p class="eyebrow"><a href="{P}index.html">Overview</a> › Sources</p>
  <h1>Sources</h1>
  <p class="lede">Every value and policy statement on this site points to one of these sources. Status records what the retrieval returned on ${esc(sourcesDoc.as_of)}.</p>
</header>
<section class="card">
  <div class="toolbar"><input type="search" class="filter" data-target="tbl-sources" placeholder="Filter sources…" aria-label="Filter sources"></div>
  <div class="table-wrap">
  <table id="tbl-sources" class="data">
    <thead><tr><th>ID</th><th>Source</th><th>Link</th><th>Accessed</th><th>Status</th><th>What it supports</th></tr></thead>
    <tbody>
${rows}
    </tbody>
  </table>
  </div>
  <p class="muted">Machine-readable copies: <a href="data/sources.json">sources.json</a>, <a href="data/products.json">products.json</a>, <a href="data/compliance.json">compliance.json</a>, <a href="data/flags.json">flags.json</a>.</p>
</section>`;
  return layout({ title: "Sources", active: "sources", depth: 0, body });
};

const pageFlagged = () => {
  const rows = flagsDoc.flags.map((f) => `<tr>
  <td>${f.id}</td>
  <td>${badge(f.severity)}</td>
  <td>${esc(f.type)}</td>
  <td class="wrap"><strong>${esc(f.item)}</strong><br>${esc(f.detail)}</td>
  <td>${f.sources.map((s) => srcLink(s)).join(", ")}</td>
  <td class="wrap">${esc(f.action)}</td>
</tr>`).join("\n");
  const body = `
<header class="hero compact flagged-hero">
  <p class="eyebrow"><a href="{P}index.html">Overview</a> › Flagged for Review</p>
  <h1>Flagged for Review</h1>
  <p class="lede">Irregularities, unverified items and open decisions. These do not block publication. Each item links to its source so it can be checked directly. Owner decisions are needed on the high-severity items.</p>
  <p class="lede">${flagCounts.High} high · ${flagCounts.Medium} medium · ${flagCounts.Low} low · ${flagsDoc.flags.length} total</p>
</header>
<section class="card">
  <div class="toolbar"><input type="search" class="filter" data-target="tbl-flags" placeholder="Filter flags…" aria-label="Filter flags"></div>
  <div class="table-wrap">
  <table id="tbl-flags" class="data">
    <thead><tr><th>ID</th><th>Severity</th><th>Type</th><th>Item and detail</th><th>Sources</th><th>Action for review</th></tr></thead>
    <tbody>
${rows}
    </tbody>
  </table>
  </div>
</section>`;
  return layout({ title: "Flagged for Review", active: "flagged", depth: 0, body });
};

const CSS = `
:root{--navy:#14213d;--ink:#1d2433;--muted:#6b7280;--line:#e5e7eb;--bg:#f5f7fb;--card:#fff;--ok:#0f766e;--okbg:#e6f6f3;--warn:#a16207;--warnbg:#fff6df;--bad:#b42318;--badbg:#fdecea;--info:#1d4ed8;--infobg:#e8efff;--accent:#2563eb}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:var(--accent)}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-size:13px}
.shell{display:grid;grid-template-columns:230px 1fr;min-height:100vh}
.sidebar{background:var(--navy);color:#dbe4ff;padding:22px 16px;display:flex;flex-direction:column;gap:18px;position:sticky;top:0;height:100vh}
.brand{font-weight:700;font-size:18px;color:#fff;letter-spacing:.3px}
.brand span{display:block;font-weight:400;font-size:12px;color:#9fb3e0;margin-top:2px}
.sidebar nav{display:flex;flex-direction:column;gap:4px}
.sidebar nav a{color:#dbe4ff;text-decoration:none;padding:9px 10px;border-radius:8px;font-size:14px}
.sidebar nav a:hover{background:rgba(255,255,255,.08)}
.sidebar nav a.active{background:#2a3d6b;color:#fff;font-weight:600}
.side-foot{margin-top:auto;font-size:12px;color:#9fb3e0}
.side-foot a{color:#c7d6ff}
main{padding:24px 28px 40px;max-width:1280px;width:100%}
.disclosure{background:var(--warnbg);border:1px solid #f3d38a;color:#5b4300;padding:12px 14px;border-radius:10px;margin-bottom:18px;font-size:14px}
.hero{margin-bottom:18px}
.hero h1{font-size:28px;margin:4px 0 6px;color:var(--navy)}
.hero.compact h1{font-size:24px}
.eyebrow{margin:0;font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)}
.lede{margin:0;color:#374151;max-width:880px}
.flagged-hero h1{color:var(--bad)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin-bottom:18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.kpi .num{font-size:26px;font-weight:700;color:var(--navy)}
.kpi .lbl{font-size:13px;color:var(--muted);margin-top:2px}
.kpi.warn{border-color:#f3d38a}
.kpi.warn .num{color:var(--warn)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:18px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card h2{margin:0 0 10px;font-size:18px;color:var(--navy)}
.summary{margin:0;padding-left:18px}
.summary li{margin:6px 0}
.cats{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.cat{display:block;border:1px solid var(--line);border-radius:10px;padding:14px;text-decoration:none;color:var(--ink);background:#fbfcff}
.cat:hover{border-color:var(--accent)}
.cat-title{font-weight:700;color:var(--navy)}
.cat-meta{font-size:13px;color:var(--muted);margin-top:4px}
.toolbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px}
.filter{padding:9px 12px;border:1px solid #cbd5e1;border-radius:8px;min-width:280px;font:inherit}
.hint,.muted{color:var(--muted);font-size:13px}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table.data{width:100%;border-collapse:collapse;font-size:14px;background:#fff}
table.data th,table.data td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
table.data thead th{background:#f1f5fb;color:#334155;font-size:12px;text-transform:uppercase;letter-spacing:.4px;position:sticky;top:0;white-space:nowrap}
table.data tbody tr:nth-child(even){background:#fbfcfe}
table.data tbody tr:hover{background:#eef4ff}
td.blank{background:repeating-linear-gradient(45deg,#fffdf5,#fffdf5 6px,#fff6df 6px,#fff6df 12px)}
td.wrap{min-width:200px}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.badge.ok{background:var(--okbg);color:var(--ok)}
.badge.warn{background:var(--warnbg);color:var(--warn)}
.badge.bad{background:var(--badbg);color:var(--bad)}
.badge.info{background:var(--infobg);color:var(--info)}
.foot{margin-top:24px;color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:12px}
@media (max-width:860px){
  .shell{grid-template-columns:1fr}
  .sidebar{position:static;height:auto;flex-direction:column}
  .sidebar nav{flex-direction:row;flex-wrap:wrap}
  main{padding:16px}
  .filter{min-width:0;width:100%}
}
`;

const JS = `
document.querySelectorAll('input.filter').forEach(function(input){
  input.addEventListener('input', function(){
    var q = input.value.trim().toLowerCase();
    var table = document.getElementById(input.dataset.target);
    if(!table) return;
    table.querySelectorAll('tbody tr').forEach(function(tr){
      tr.style.display = tr.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
    });
  });
});
`;

// ---------- internal link check ----------
function listHtml(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...listHtml(p));
    else if (name.endsWith(".html")) out.push(p);
  }
  return out;
}

const pages = {
  "index.html": pageIndex(),
  "categories/home-kitchen-air-fryers.html": pageCategory(),
  "analysis.html": pageAnalysis(),
  "compliance.html": pageCompliance(),
  "sources.html": pageSources(),
  "flagged.html": pageFlagged(),
  "404.html": layout({
    title: "Page not found",
    active: "",
    depth: 0,
    body: `<section class="card"><h1>Page not found</h1><p>Go to the <a href="index.html">Overview</a>.</p></section>`,
  }),
};

const built = Object.entries(pages);
// Verify link targets against the planned output set (files are written only after validation passes).
const plannedFiles = new Set(built.map(([k]) => k).concat(["assets/style.css", "assets/app.js", "data/products.json", "data/sources.json", "data/compliance.json", "data/flags.json", "data/site.json"]));
for (const [rel, html] of built) {
  for (const m of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|#)/.test(href)) continue;
    const target = relative(ROOT, resolve(dirname(join(OUT, rel)), href.split("#")[0]));
    const normalized = target.split("\\").join("/").replace(/^docs\//, "");
    if (!plannedFiles.has(normalized)) err(`${rel}: link "${href}" -> ${normalized} is not a planned output`);
  }
}

// Every category page listed in products must exist.
for (const p of products.products) {
  if (!pages[`categories/${p.category_page}.html`]) err(`${p.id}: category page ${p.category_page} not built`);
}

// Report
console.log(`Products: ${products.products.length}`);
console.log(`Fields: ${fieldVerified}/${fieldTotal} verified or derived (${coveragePct}%)`);
console.log(`Flags: ${flagsDoc.flags.length} (High ${flagCounts.High}, Medium ${flagCounts.Medium}, Low ${flagCounts.Low})`);
console.log(`Sources: ${sourcesDoc.sources.length}`);
for (const w of warnings) console.log(`WARN: ${w}`);

if (errors.length) {
  console.error(`\nBUILD FAILED: ${errors.length} error(s)`);
  for (const e of errors) console.error(` - ${e}`);
  process.exit(1);
}

if (CHECK_ONLY) {
  console.log("Check passed (no files written).");
  process.exit(0);
}

// Write output
rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
for (const [rel, html] of built) {
  const p = join(OUT, rel);
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, html, "utf8");
}
mkdirSync(join(OUT, "assets"), { recursive: true });
writeFileSync(join(OUT, "assets", "style.css"), CSS.trimStart(), "utf8");
writeFileSync(join(OUT, "assets", "app.js"), JS.trimStart(), "utf8");
mkdirSync(join(OUT, "data"), { recursive: true });
for (const f of ["products.json", "sources.json", "compliance.json", "flags.json", "site.json"]) {
  copyFileSync(join(DATA, f), join(OUT, "data", f));
}
writeFileSync(join(OUT, ".nojekyll"), "", "utf8");
console.log(`Built ${built.length} pages into docs/`);
