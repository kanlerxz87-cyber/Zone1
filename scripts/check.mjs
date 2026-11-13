// Integrity checks for data/ and docs/. Exits non-zero on any failure.
// Run after build: node scripts/build.mjs && node scripts/check.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = path.join(ROOT, 'docs');
const readJSON = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const errors = [];
const ok = [];
const fail = (msg) => errors.push(msg);

// Official hosts allowed as source links.
const OFFICIAL_HOSTS = new Set([
  'www.amazon.com', 'affiliate-program.amazon.com', 'link.amazon', 'www.ftc.gov',
  'github.com', 'api.github.com',
]);
const hostOf = (u) => { try { return new URL(u).host; } catch { return null; } };

// ---------- data ----------
const products = readJSON('data/products.json');
const compliance = readJSON('data/compliance.json');
const flags = readJSON('data/flags.json');
const sources = readJSON('data/sources.json');

const FIELDS = ['price', 'rating', 'review_count', 'best_sellers_rank', 'availability', 'commission_rate'];
for (const p of products.products) {
  if (!/^[A-Z0-9]{10}$/.test(p.asin)) fail(`${p.id}: ASIN "${p.asin}" is not 10 alphanumeric characters`);
  if (p.source_url !== `https://www.amazon.com/dp/${p.asin}`) fail(`${p.id}: source_url does not match ASIN`);
  if (!p.resolved_url.includes(p.asin)) fail(`${p.id}: resolved_url does not contain ASIN`);
  if (!p.title || !p.amazon_department) fail(`${p.id}: title/department missing`);
  for (const f of FIELDS) {
    const isBlank = p[f] == null;
    const listed = p.unverified_fields.includes(f);
    if (isBlank && !listed) fail(`${p.id}: blank "${f}" is not listed as unverified`);
    if (!isBlank && listed) fail(`${p.id}: "${f}" has a value but is listed as unverified`);
    if (!isBlank) fail(`${p.id}: "${f}" has a value; no source for it is recorded`);
  }
}
if (!errors.length) ok.push(`products: ${products.products.length} rows, each with an ASIN-matched official source; ${products.products.reduce((n, p) => n + p.unverified_fields.length, 0)} blank fields all flagged`);

for (const r of compliance.rows) {
  if (!['verified', 'unverified'].includes(r.status)) fail(`${r.id}: bad status "${r.status}"`);
  if (!hostOf(r.source_url) || !OFFICIAL_HOSTS.has(hostOf(r.source_url))) fail(`${r.id}: source host not official: ${r.source_url}`);
  if (r.status === 'verified' && !r.quote) fail(`${r.id}: verified row has no quote`);
}
ok.push(`compliance: ${compliance.rows.length} rows, all with official source hosts`);

const ids = new Set();
for (const f of flags.flags) {
  if (ids.has(f.id)) fail(`duplicate flag id ${f.id}`);
  ids.add(f.id);
  if (!hostOf(f.source_url) || !OFFICIAL_HOSTS.has(hostOf(f.source_url))) fail(`${f.id}: source host not official: ${f.source_url}`);
}
ok.push(`flags: ${flags.flags.length} unique IDs, each with a source link`);

for (const s of sources.sources) {
  if (!/^https:\/\//.test(s.url)) fail(`${s.id}: source url not https`);
}
ok.push(`sources: ${sources.sources.length} entries`);

// ---------- built site ----------
if (!fs.existsSync(DOCS)) {
  fail('docs/ does not exist; run node scripts/build.mjs first');
} else {
  const htmlFiles = fs.readdirSync(DOCS).filter((f) => f.endsWith('.html'));
  const required = ['index.html', 'executive-summary.html', 'category-air-fryers.html', 'analysis.html',
    'compliance.html', 'sources.html', 'repo-review.html', 'flagged.html'];
  for (const r of required) if (!htmlFiles.includes(r)) fail(`missing page ${r}`);

  const idsIn = (file) => new Set([...fs.readFileSync(path.join(DOCS, file), 'utf8').matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  let linkCount = 0;
  for (const file of htmlFiles) {
    const html = fs.readFileSync(path.join(DOCS, file), 'utf8');
    if (/localhost|127\.0\.0\.1/.test(html)) fail(`${file}: references localhost`);

    // Every table body row must carry at least one official source link.
    const tbodies = [...html.matchAll(/<tbody>([\s\S]*?)<\/tbody>/g)];
    for (const tb of tbodies) {
      const rows = [...tb[1].matchAll(/<tr[\s>][\s\S]*?<\/tr>/g)].map((m) => m[0]);
      rows.forEach((row, i) => {
        if (!/href="https:\/\//.test(row)) fail(`${file}: table body row ${i + 1} has no source link`);
      });
    }

    // Links.
    for (const m of html.matchAll(/href="([^"]+)"/g)) {
      const href = m[1];
      linkCount++;
      if (/^https:\/\//.test(href)) {
        if (!OFFICIAL_HOSTS.has(hostOf(href)) && !/^https:\/\/kanlerxz87-cyber\.github\.io\//.test(href)) {
          fail(`${file}: external link to non-allowed host ${href}`);
        }
        continue;
      }
      if (/^(mailto:|javascript:)/.test(href)) fail(`${file}: disallowed link ${href}`);
      if (/^http:\/\//.test(href)) fail(`${file}: insecure link ${href}`);
      const [fileRef, frag] = href.split('#');
      const target = fileRef === '' ? file : fileRef;
      if (!target.startsWith('data/') && !target.startsWith('assets/') && !fs.existsSync(path.join(DOCS, target))) {
        fail(`${file}: broken internal link ${href}`);
        continue;
      }
      if (frag && target.endsWith('.html') && fs.existsSync(path.join(DOCS, target)) && !idsIn(target).has(frag)) {
        fail(`${file}: anchor #${frag} not found in ${target}`);
      }
    }
  }
  if (!fs.existsSync(path.join(DOCS, 'assets', 'style.css'))) fail('missing assets/style.css');
  if (!fs.existsSync(path.join(DOCS, '.nojekyll'))) fail('missing .nojekyll');
  ok.push(`site: ${htmlFiles.length} pages, ${linkCount} links checked, all internal targets and anchors exist`);
}

for (const line of ok) console.log(`ok  ${line}`);
if (errors.length) {
  console.error(`\n${errors.length} check(s) FAILED:`);
  for (const e of errors) console.error(`  - ${e}`);
  process.exit(1);
}
console.log('\nall checks passed');
