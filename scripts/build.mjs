// Builds the static GitHub Pages site in docs/ from data/*.json and the markdown reports.
// No dependencies. Run: node scripts/build.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DOCS = path.join(ROOT, 'docs');
const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');
const readJSON = (p) => JSON.parse(read(p));

const products = readJSON('data/products.json');
const compliance = readJSON('data/compliance.json');
const flags = readJSON('data/flags.json');
const sources = readJSON('data/sources.json');
const AS_OF = products.as_of;
const DISCLOSURE = 'As an Amazon Associate I earn from qualifying purchases.';

// ---------- helpers ----------
const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function inline(text) {
  let s = esc(text);
  s = s.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+|[^)\s]+)\)/g, (_, t, u) => {
    const ext = /^https?:\/\//.test(u);
    return `<a href="${u}"${ext ? ' target="_blank" rel="noopener"' : ''}>${t}</a>`;
  });
  return s;
}

// Minimal markdown: #/##/### headings, paragraphs, bullets, numbered lists, tables, blockquotes, hr.
function markdown(src) {
  const lines = src.split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { i++; continue; }
    const h = /^(#{1,3})\s+(.*)$/.exec(line);
    if (h) { out.push(`<h${h[1].length}>${inline(h[2])}</h${h[1].length}>`); i++; continue; }
    if (/^---+\s*$/.test(line)) { out.push('<hr>'); i++; continue; }
    if (line.startsWith('|')) {
      const rows = [];
      while (i < lines.length && lines[i].startsWith('|')) { rows.push(lines[i]); i++; }
      const cells = (r) => r.replace(/^\|/, '').replace(/\|\s*$/, '').split('|').map((c) => c.trim());
      const head = cells(rows[0]);
      const body = rows.slice(2).map(cells);
      out.push('<div class="table-wrap"><table><thead><tr>' +
        head.map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>' +
        body.map((r) => '<tr>' + r.map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>').join('') +
        '</tbody></table></div>');
      continue;
    }
    if (line.startsWith('> ')) {
      const buf = [];
      while (i < lines.length && lines[i].startsWith('> ')) { buf.push(lines[i].slice(2)); i++; }
      out.push(`<blockquote>${inline(buf.join(' '))}</blockquote>`);
      continue;
    }
    if (/^- /.test(line)) {
      const items = [];
      while (i < lines.length && /^- /.test(lines[i])) { items.push(lines[i].slice(2)); i++; }
      out.push('<ul>' + items.map((t) => `<li>${inline(t)}</li>`).join('') + '</ul>');
      continue;
    }
    if (/^\d+\. /.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+\. /.test(lines[i])) { items.push(lines[i].replace(/^\d+\.\s/, '')); i++; }
      out.push('<ol>' + items.map((t) => `<li>${inline(t)}</li>`).join('') + '</ol>');
      continue;
    }
    const buf = [];
    while (i < lines.length && lines[i].trim() && !/^(#{1,3}\s|\||> |- |\d+\. |---+\s*$)/.test(lines[i])) {
      buf.push(lines[i]); i++;
    }
    out.push(`<p>${inline(buf.join(' '))}</p>`);
  }
  return out.join('\n');
}

const badge = (kind, text) => `<span class="badge ${kind}">${esc(text)}</span>`;
const unverified = (flagId) => `${badge('unverified', 'UNVERIFIED')} <a class="flaglink" href="flagged.html#${flagId}">${flagId}</a>`;
const fieldFlag = { commission_rate: 'F-07', price: 'F-08', rating: 'F-08', review_count: 'F-08', best_sellers_rank: 'F-08', availability: 'F-08' };
const fieldLabel = { price: 'Price', rating: 'Rating', review_count: 'Review count', best_sellers_rank: 'Best-sellers rank', availability: 'Availability', commission_rate: 'Commission rate' };

// ---------- layout ----------
const NAV = [
  ['index.html', 'Dashboard'],
  ['executive-summary.html', 'Executive summary'],
  ['category-air-fryers.html', 'Air Fryers'],
  ['analysis.html', 'Analysis'],
  ['compliance.html', 'Compliance'],
  ['sources.html', 'Sources'],
  ['repo-review.html', 'Repo review'],
  ['flagged.html', '⚑ Flagged for Review'],
];

function page({ file, title, active, body }) {
  const nav = NAV.map(([href, label]) =>
    `<a href="${href}"${href === active ? ' class="active"' : ''}>${esc(label)}</a>`).join('');
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} · Amazon Affiliate Dashboard</title>
<meta name="description" content="Source-linked Amazon affiliate product dashboard. Data as of ${AS_OF}.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="topbar">
  <div class="brand"><a href="index.html">Amazon Affiliate Dashboard</a></div>
  <nav>${nav}</nav>
</header>
<main>
${body}
</main>
<footer>
  <p class="disclosure"><strong>Affiliate disclosure:</strong> ${esc(DISCLOSURE)} This site is not affiliated with, sponsored by, or endorsed by Amazon.com, Inc.</p>
  <p>Data as of ${AS_OF}. Every value links to its official source. Blank cells are unverified and listed on the <a href="flagged.html">Flagged for Review</a> page. Not financial advice.</p>
  <p>Built from <code>data/*.json</code> and <code>reports/*.md</code> by <code>scripts/build.mjs</code>. <a href="data/products.json">products.json</a> · <a href="data/compliance.json">compliance.json</a> · <a href="data/flags.json">flags.json</a> · <a href="data/sources.json">sources.json</a></p>
</footer>
</body>
</html>
`;
  fs.writeFileSync(path.join(DOCS, file), html);
}

// ---------- counts used on the dashboard ----------
const VERIFIED_FIELDS = ['asin', 'title', 'amazon_department', 'source_url'];
const verifiedCount = products.products.length * VERIFIED_FIELDS.length;
const unverifiedCount = products.products.reduce((n, p) => n + p.unverified_fields.length, 0);
const complianceVerified = compliance.rows.filter((r) => r.status === 'verified').length;
const highFlags = flags.flags.filter((f) => f.severity === 'high');

// ---------- pages ----------
function buildDashboard() {
  const kpi = (n, label, cls = '') => `<div class="kpi ${cls}"><div class="kpi-n">${n}</div><div class="kpi-l">${esc(label)}</div></div>`;
  const body = `
<section class="hero">
  <h1>Amazon affiliate product dashboard</h1>
  <p class="lede">Three Amazon.com products, each with its source link. Verified values are shown. Unverified values are blank and flagged. Data as of <strong>${AS_OF}</strong>.</p>
  <p class="disclose-inline">${esc(DISCLOSURE)}</p>
</section>
<section class="kpis">
  ${kpi(products.products.length, 'Products tracked')}
  ${kpi(verifiedCount, 'Verified values (ASIN, title, department, link)', 'ok')}
  ${kpi(unverifiedCount, 'Unverified values (left blank)', 'warn')}
  ${kpi(flags.flags.length, `Open flags (${highFlags.length} high severity)`, 'warn')}
  ${kpi(`${complianceVerified}/${compliance.rows.length}`, 'Compliance rules verified against official text', 'ok')}
</section>
<section class="cards">
  <a class="card" href="category-air-fryers.html">
    <h2>Air Fryers</h2>
    <p>${products.products.length} products · product table with ASIN, title, department, source link, and blank unverified fields.</p>
  </a>
  <a class="card" href="executive-summary.html">
    <h2>Executive summary</h2>
    <p>What was done, what was found, what is still open, and the owner actions.</p>
  </a>
  <a class="card" href="analysis.html">
    <h2>Analysis</h2>
    <p>Niche, pricing, reviews, competition, commission potential, and the title-based buying notes. Each claim is limited to verified data.</p>
  </a>
  <a class="card" href="compliance.html">
    <h2>Compliance</h2>
    <p>Associates and FTC rules with verbatim quotes, the source for each, and what the site does about it.</p>
  </a>
  <a class="card" href="sources.html">
    <h2>Sources</h2>
    <p>Every official page used, when it was checked, and the sources that were rejected.</p>
  </a>
  <a class="card warn-card" href="flagged.html">
    <h2>⚑ Flagged for Review</h2>
    <p>${flags.flags.length} flagged items and every unverified value, with links for manual review.</p>
  </a>
</section>
<section>
  <h2>High-severity items</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Item</th><th>Source</th></tr></thead>
    <tbody>
${highFlags.map((f) => `<tr><td><a href="flagged.html#${f.id}">${f.id}</a></td><td>${esc(f.item)}</td><td><a href="${esc(f.source_url)}" target="_blank" rel="noopener">source ↗</a></td></tr>`).join('\n')}
    </tbody>
  </table></div>
</section>`;
  page({ file: 'index.html', title: 'Dashboard', active: 'index.html', body });
}

function buildCategory() {
  const rows = products.products.map((p, idx) => {
    const cell = (k) => (p[k] == null ? unverified(fieldFlag[k]) : esc(p[k]));
    const unvCells = ['price', 'rating', 'review_count', 'best_sellers_rank', 'availability', 'commission_rate']
      .map((k) => `<td data-label="${esc(fieldLabel[k])}">${cell(k)}</td>`).join('');
    return `<tr>
  <td data-label="#">${idx + 1}<br><span class="muted">${esc(p.id)}</span></td>
  <td data-label="Product" class="title-cell">${esc(p.title)}</td>
  <td data-label="ASIN"><code>${esc(p.asin)}</code></td>
  <td data-label="Department">${esc(p.amazon_department)}</td>
  <td data-label="Identity">${badge('unverified', 'TO CONFIRM')} <a class="flaglink" href="flagged.html#F-04">F-04</a></td>
  <td data-label="Submitted link"><a href="${esc(p.submitted_link)}" target="_blank" rel="noopener">${esc(p.submitted_link.replace('https://', ''))} ↗</a></td>
  ${unvCells}
  <td data-label="Source"><a href="${esc(p.source_url)}" target="_blank" rel="noopener">amazon.com/dp/${esc(p.asin)} ↗</a><br><span class="muted">checked ${esc(p.source_checked)}</span></td>
</tr>`;
  }).join('\n');

  const specs = products.products.map((p) => `<tr>
  <td data-label="Product">${esc(p.id)} · ${esc(p.title_brand_prefix)}</td>
  <td data-label="Capacity (title)">${esc(p.title_capacity_stated)}</td>
  <td data-label="Features (title)">${esc(p.title_features_stated)}</td>
  <td data-label="Source"><a href="${esc(p.source_url)}" target="_blank" rel="noopener">amazon.com/dp/${esc(p.asin)} ↗</a></td>
</tr>`).join('\n');

  const body = `
<section class="page-head">
  <p class="crumb"><a href="index.html">Dashboard</a> › Air Fryers</p>
  <h1>Air Fryers</h1>
  <p class="lede">Three air-fryer products from Amazon.com's Home &amp; Kitchen department, read from their product pages on ${AS_OF}. Only title facts are shown. Price, rating, review count, rank, availability, and commission rate are unverified and blank.</p>
  <p class="disclose-inline"><strong>Affiliate links.</strong> The submitted links below are affiliate links. ${esc(DISCLOSURE)}</p>
</section>
<section>
  <h2>Product table</h2>
  <div class="table-wrap"><table class="wide">
    <thead><tr>
      <th>#</th><th>Product (title as listed)</th><th>ASIN</th><th>Department</th><th>Identity</th><th>Submitted link</th>
      <th>Price</th><th>Rating</th><th>Review count</th><th>Best-sellers rank</th><th>Availability</th><th>Commission rate</th><th>Source</th>
    </tr></thead>
    <tbody>
${rows}
    </tbody>
  </table></div>
  <p class="muted">Identity "TO CONFIRM": the submitted short link redirects to this ASIN, but the redirect carries fallback parameters. Confirm it by opening the link (<a href="flagged.html#F-04">F-04</a>).</p>
</section>
<section>
  <h2>Specs stated in each listing title</h2>
  <p>These are copied from the title text only. Nothing is added.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Product</th><th>Capacity (title)</th><th>Features (title)</th><th>Source</th></tr></thead>
    <tbody>
${specs}
    </tbody>
  </table></div>
</section>
<section>
  <h2>Notes</h2>
  <ul>
    <li><strong>No prices are shown.</strong> Amazon's Program Policies allow prices only when Amazon serves them or the Creators API supplies them (<a href="compliance.html">C4</a>).</li>
    <li><strong>Commission is not calculated.</strong> The official rate schedule needs an Associates sign-in (<a href="flagged.html#F-07">F-07</a>).</li>
    <li><strong>Product titles are Amazon text.</strong> Whether they may stay on the site is flagged (<a href="flagged.html#F-06">F-06</a>).</li>
  </ul>
</section>`;
  page({ file: 'category-air-fryers.html', title: 'Air Fryers', active: 'category-air-fryers.html', body });
}

function buildCompliance() {
  const rows = compliance.rows.map((r) => `<tr>
  <td data-label="ID">${esc(r.id)}</td>
  <td data-label="Topic">${esc(r.topic)}<br><span class="muted">${esc(r.section)}</span></td>
  <td data-label="Requirement">${esc(r.requirement)}</td>
  <td data-label="Quote"><blockquote class="quote">${esc(r.quote)}</blockquote></td>
  <td data-label="Status">${r.status === 'verified' ? badge('ok', 'VERIFIED') : badge('unverified', 'UNVERIFIED')}</td>
  <td data-label="Site action">${esc(r.site_action)}</td>
  <td data-label="Source"><a href="${esc(r.source_url)}" target="_blank" rel="noopener">official page ↗</a><br><span class="muted">${esc(r.source_updated)}</span></td>
</tr>`).join('\n');
  const body = `
<section class="page-head">
  <p class="crumb"><a href="index.html">Dashboard</a> › Compliance</p>
  <h1>Compliance: Amazon Associates and FTC</h1>
  <p class="lede">Rules that shape what this site may show, with the verbatim text and the official page for each. ${complianceVerified} of ${compliance.rows.length} rows are verified. The one unverified row is the commission schedule, which needs an Associates sign-in.</p>
</section>
<section>
  <div class="table-wrap"><table class="wide">
    <thead><tr><th>ID</th><th>Topic</th><th>Requirement</th><th>Quote</th><th>Status</th><th>Site action</th><th>Source</th></tr></thead>
    <tbody>
${rows}
    </tbody>
  </table></div>
  <p class="muted">${esc(compliance.note)}</p>
</section>`;
  page({ file: 'compliance.html', title: 'Compliance', active: 'compliance.html', body });
}

function buildSources() {
  const rows = sources.sources.map((s) => `<tr>
  <td data-label="ID">${esc(s.id)}</td>
  <td data-label="Source">${esc(s.title)}<br><span class="muted">${esc(s.publisher)}</span></td>
  <td data-label="Type">${s.type === 'rejected' ? badge('unverified', 'REJECTED') : badge('ok', 'OFFICIAL')}</td>
  <td data-label="Used for">${esc(s.used_for)}</td>
  <td data-label="Result">${esc(s.result)}</td>
  <td data-label="Link">${s.type === 'rejected'
    ? `<span class="muted">Rejected, not linked: ${esc(s.url)}</span><br><a href="https://affiliate-program.amazon.com/help/operating/schedule" target="_blank" rel="noopener">official Associates rate schedule ↗</a>`
    : `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)} ↗</a>`}</td>
</tr>`).join('\n');
  const body = `
<section class="page-head">
  <p class="crumb"><a href="index.html">Dashboard</a> › Sources</p>
  <h1>Sources and verification method</h1>
  <p class="lede">Every source used on this site, when it was checked (${AS_OF}), and what it supports. Sources marked REJECTED were checked and not used for any value.</p>
</section>
<section>
  <div class="table-wrap"><table class="wide">
    <thead><tr><th>ID</th><th>Source</th><th>Type</th><th>Used for</th><th>Result</th><th>Link</th></tr></thead>
    <tbody>
${rows}
    </tbody>
  </table></div>
</section>
<section>
  <h2>How values were verified</h2>
  <ul>
    <li>A value is shown only if it was read from an official page on ${AS_OF}. Otherwise the cell is blank and listed on the Flagged page.</li>
    <li>Product facts come from the Amazon.com product page each submitted link resolves to.</li>
    <li>Policy facts come from affiliate-program.amazon.com and ftc.gov, quoted word for word.</li>
    <li>Nothing is estimated. Analysis uses only verified values and states its limits.</li>
  </ul>
  <h2>Privacy</h2>
  <p>${esc(sources.privacy_note)}</p>
  <p>Raw data: <a href="data/products.json">products.json</a> · <a href="data/compliance.json">compliance.json</a> · <a href="data/flags.json">flags.json</a> · <a href="data/sources.json">sources.json</a>.</p>
</section>`;
  page({ file: 'sources.html', title: 'Sources', active: 'sources.html', body });
}

function buildFlagged() {
  const flagRows = flags.flags.map((f) => `<tr id="${esc(f.id)}">
  <td data-label="ID"><strong>${esc(f.id)}</strong></td>
  <td data-label="Severity">${badge(f.severity === 'high' ? 'unverified' : 'ok', f.severity.toUpperCase())}</td>
  <td data-label="Area">${esc(f.area)}</td>
  <td data-label="Item">${esc(f.item)}</td>
  <td data-label="Detail">${esc(f.detail)}</td>
  <td data-label="Owner action">${esc(f.owner_action)}</td>
  <td data-label="Source"><a href="${esc(f.source_url)}" target="_blank" rel="noopener">source ↗</a></td>
  <td data-label="Status">${badge('review', 'NEEDS REVIEW')}</td>
</tr>`).join('\n');

  const unvRows = [];
  products.products.forEach((p) => {
    p.unverified_fields.forEach((k) => {
      unvRows.push(`<tr>
  <td data-label="Product">${esc(p.id)} · <code>${esc(p.asin)}</code></td>
  <td data-label="Field">${esc(fieldLabel[k] || k)}</td>
  <td data-label="Status">${badge('unverified', 'UNVERIFIED · blank')}</td>
  <td data-label="Flag"><a href="flagged.html#${fieldFlag[k]}">${fieldFlag[k]}</a></td>
  <td data-label="Source"><a href="${esc(p.source_url)}" target="_blank" rel="noopener">amazon.com/dp/${esc(p.asin)} ↗</a></td>
</tr>`);
    });
  });

  const body = `
<section class="page-head flagged-head">
  <p class="crumb"><a href="index.html">Dashboard</a> › Flagged for Review</p>
  <h1>⚑ Flagged for Review</h1>
  <p class="lede">These items are published for your review. They do not block the site or its merge. Each row has a source link. Use the owner actions to request changes.</p>
</section>
<section>
  <h2>Flagged items (${flags.flags.length})</h2>
  <div class="table-wrap"><table class="wide">
    <thead><tr><th>ID</th><th>Severity</th><th>Area</th><th>Item</th><th>Detail</th><th>Owner action</th><th>Source</th><th>Status</th></tr></thead>
    <tbody>
${flagRows}
    </tbody>
  </table></div>
</section>
<section>
  <h2>Unverified values (left blank)</h2>
  <p>These values were not readable from an official source, so they are blank. None were estimated.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Product</th><th>Field</th><th>Status</th><th>Flag</th><th>Source checked</th></tr></thead>
    <tbody>
${unvRows.join('\n')}
    </tbody>
  </table></div>
</section>`;
  page({ file: 'flagged.html', title: 'Flagged for Review', active: 'flagged.html', body });
}

function buildMarkdownPage({ file, title, active, src, crumb, lede }) {
  src = src.replace(/^# [^\n]*\n/, '');
  const body = `
<section class="page-head">
  <p class="crumb"><a href="index.html">Dashboard</a> › ${esc(crumb)}</p>
  <h1>${esc(title)}</h1>
  ${lede ? `<p class="lede">${esc(lede)}</p>` : ''}
</section>
<section class="prose">
${markdown(src)}
</section>`;
  page({ file, title, active, body });
}

// ---------- write ----------
fs.mkdirSync(path.join(DOCS, 'assets'), { recursive: true });
fs.mkdirSync(path.join(DOCS, 'data'), { recursive: true });
fs.writeFileSync(path.join(DOCS, '.nojekyll'), '');
fs.writeFileSync(path.join(DOCS, 'assets', 'style.css'), read('scripts/style.css'));
for (const f of ['products.json', 'compliance.json', 'flags.json', 'sources.json']) {
  fs.copyFileSync(path.join(ROOT, 'data', f), path.join(DOCS, 'data', f));
}

buildDashboard();
buildCategory();
buildCompliance();
buildSources();
buildFlagged();
buildMarkdownPage({ file: 'executive-summary.html', title: 'Executive summary', active: 'executive-summary.html', src: read('EXECUTIVE_SUMMARY.md'), crumb: 'Executive summary' });
buildMarkdownPage({ file: 'analysis.html', title: 'Analysis', active: 'analysis.html', src: read('reports/analysis.md'), crumb: 'Analysis' });
buildMarkdownPage({ file: 'repo-review.html', title: 'Repo review', active: 'repo-review.html', src: read('reports/repo-review.md'), crumb: 'Repo review' });

console.log(`built ${fs.readdirSync(DOCS).filter((f) => f.endsWith('.html')).length} pages in docs/`);
