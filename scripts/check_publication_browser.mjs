#!/usr/bin/env node
// Optional dev-only browser acceptance. Never opens/activates an Amazon link.
// Dependencies: see README. All network is limited to this temporary strict subpath fixture.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFile, stat, mkdir, writeFile } from 'node:fs/promises';
import { resolve, extname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const suggestionCount = JSON.parse(await readFile(resolve(root,'data/suggestions.json'),'utf8')).suggestions.length;
const { default: chromium, inflate, setupLambdaEnvironment } = await import(new URL('../.cache/browser/node_modules/@sparticuz/chromium/build/index.js', import.meta.url));
const { chromium: playwright } = await import(new URL('../.cache/browser/node_modules/playwright-core/index.mjs', import.meta.url));
await inflate(resolve(root, '.cache/browser/node_modules/@sparticuz/chromium/bin/al2023.tar.br'));
setupLambdaEnvironment('/tmp/al2023/lib');
const types = { '.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.json':'application/json',
  '.svg':'image/svg+xml', '.webp':'image/webp', '.png':'image/png', '.woff2':'font/woff2', '.xml':'application/xml' };
const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://fixture.invalid');
    assert(url.pathname.startsWith('/Zone1/'));
    const path = decodeURIComponent(url.pathname.slice('/Zone1/'.length));
    assert(!path.split('/').some(part => part.startsWith('.')));
    let file = resolve(root, path || 'index.html');
    assert(!relative(root, file).startsWith('..'));
    assert(!file.endsWith('.sqlite3') && !file.includes('analytics-data'));
    if ((await stat(file)).isDirectory()) file = resolve(file, 'index.html');
    res.writeHead(200, { 'Content-Type': (types[extname(file)] || 'text/plain') + (['.html','.css','.js'].includes(extname(file)) ? '; charset=utf-8' : ''), 'Cache-Control':'no-store' });
    res.end(await readFile(file));
  } catch {
    res.writeHead(404, { 'Content-Type':'text/plain' }); res.end('Not found');
  }
});
await new Promise(done => server.listen(0, '0.0.0.0', done));
const origin = `http://127.0.0.1:${server.address().port}`;
const base = origin + '/Zone1/';
const failures = [], blockedExternal = [], result = { viewports: [], interactions: [], noJavaScript: [] };
let browser;
try {
  browser = await playwright.launch({ executablePath: await chromium.executablePath(), headless: true,
    args: chromium.args.filter(arg => !arg.includes('disable-web-security') && !arg.includes('allow-running-insecure-content')) });
  const context = await browser.newContext({ deviceScaleFactor: 1 });
  await context.route('**/*', route => {
    if (new URL(route.request().url()).origin !== origin) {
      blockedExternal.push(route.request().url()); return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', error => failures.push(error.message));
  page.on('response', response => { if (response.status() >= 400) failures.push(`${response.status()} ${response.url()}`); });
  const pages = ['', 'picks.html', 'categories/kitchen-appliances.html', 'products/chefman-6qt-dual-basket.html',
    'products/chefman-8qt-turbofry.html', 'products/emeril-26qt-french-door.html', 'compare.html',
    'guides/buying-guide-air-fryers.html', 'articles/extension-cord-rules-in-the-manuals.html',
    'suggestions.html', 'decision-log.html', 'measurement.html', 'categories/cooking-thermometers.html', 'about.html'];
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: width < 500 ? 844 : 1000 });
    for (const path of pages) {
      const response = await page.goto(base + path, { waitUntil:'load' });
      assert.equal(response.status(), 200, path);
      await page.evaluate(() => document.fonts.ready);
      for (const image of await page.locator('img').all()) {
        await image.scrollIntoViewIfNeeded(); await image.evaluate(img => img.decode());
      }
      await page.evaluate(() => window.scrollTo({top:0, behavior:'instant'}));
      const metrics = await page.evaluate(() => {
        const band = document.querySelector('.disclosure-bar');
        const rect = band.getBoundingClientRect();
        return { width:innerWidth, scroll:document.documentElement.scrollWidth, fonts:document.fonts.status,
          disclosure:band.textContent.includes('As an Amazon Associate I earn from qualifying purchases.') && rect.top >= 0 && rect.bottom < innerHeight,
          images:[...document.images].every(img => img.complete && img.naturalWidth > 0),
          analytics:document.querySelectorAll('script[src*="analytics.js"]').length };
      });
      if (metrics.scroll > width + 1) console.error(await page.evaluate(() => [...document.querySelectorAll('main *')].filter(el => el.getBoundingClientRect().right > innerWidth + 1 && getComputedStyle(el).position !== 'absolute' && !el.closest('.tablewrap')).map(el=>({tag:el.tagName, class:el.className, right:el.getBoundingClientRect().right, text:el.textContent.slice(0,90)})).slice(0,12)));
      assert(metrics.scroll <= width + 1, `${width} ${path || '/'} overflows to ${metrics.scroll}`);
      assert(metrics.disclosure, `${width} ${path}: disclosure not visible above the fold`);
      assert(metrics.images, `${path}: incomplete image`);
      assert.equal(metrics.fonts, 'loaded'); assert.equal(metrics.analytics, 0);
      result.viewports.push({ width, page:path || '/', overflow:false, disclosureAboveFold:true });
      if (process.env.PUBLICATION_SCREENSHOTS && [390,1440].includes(width) && ['', 'products/chefman-6qt-dual-basket.html', 'articles/extension-cord-rules-in-the-manuals.html', 'suggestions.html'].includes(path)) {
        const dir = resolve(root, '.cache/publication-screenshots'); await mkdir(dir, { recursive:true });
        await page.screenshot({ path:resolve(dir, `${width}-${path.replaceAll('/','_') || 'home'}.png`), fullPage:true });
      }
    }
  }

  await page.setViewportSize({ width:390, height:844 });
  await page.goto(base, { waitUntil:'load' });
  await page.keyboard.press('Tab');
  assert.equal(await page.locator(':focus').textContent(), 'Skip to main content');
  await page.keyboard.press('Enter'); assert.equal(new URL(page.url()).hash, '#main-content');
  const summary = page.locator('.workspace-menu > summary');
  await summary.focus(); await page.keyboard.press('Enter');
  assert(await page.locator('.workspace-menu').evaluate(el => el.open));
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('.workspace-menu').evaluate(el => el.open), false);
  assert(await summary.evaluate(el => el === document.activeElement));
  await summary.click(); await page.mouse.click(4, 200);
  assert.equal(await page.locator('.workspace-menu').evaluate(el => el.open), false);
  await page.locator('[data-format-filter="dual"]').click();
  assert.equal(await page.locator('.publication-product:visible').count(), 1);
  assert.equal(await page.locator('[data-format-filter="dual"]').getAttribute('aria-pressed'), 'true');
  assert.match(await page.locator('[data-format-status]').textContent(), /1 format shown/);
  await page.locator('[data-format-filter="all"]').click();
  assert.equal(await page.locator('.publication-product:visible').count(), 3);
  result.interactions.push('keyboard skip link; native workspace Enter/Escape/focus return/outside click; real format filter and live status');

  await page.goto(base + 'compare.html', { waitUntil:'load' });
  const scroller = page.locator('.tablewrap[tabindex="0"]').first();
  await scroller.waitFor(); await scroller.focus();
  assert(await scroller.getAttribute('aria-label'));
  await page.keyboard.press('ArrowRight');
  await page.waitForFunction(() => document.querySelector('.tablewrap[tabindex="0"]').scrollLeft > 0);
  result.interactions.push('comparison table exposes labelled keyboard-scrollable region');

  await page.goto(base + 'suggestions.html', { waitUntil:'load' });
  const search = page.locator('#suggestion-query');
  await search.fill('zzzz-no-matching-suggestion-zzzz');
  assert.equal(await page.locator('[data-suggestion]:visible').count(), 0);
  assert.match(await page.locator('[data-suggestion-toolbar] output').textContent(), new RegExp(`^0 of ${suggestionCount}`));
  await page.evaluate(() => { location.hash = 'sg-08'; });
  await page.locator('#sg-08').waitFor({ state:'visible' });
  assert.equal(await search.inputValue(), '');
  assert(await page.locator('#sg-08 > details').evaluate(el => el.open));
  assert.equal(await page.locator('[data-suggestion]:visible').count(), suggestionCount);
  result.interactions.push('suggestion search, empty state, anchor recovery and opened alternatives');

  await page.goto(base + 'decision-log.html', { waitUntil:'load' });
  assert.match(await page.locator('#decision-counter').textContent(), new RegExp(`^0 of ${suggestionCount}`));
  await page.locator('#decision-picker fieldset').first().locator('input[type="radio"]').first().check();
  await page.locator('#decision-picker fieldset').first().locator('textarea').fill('Automated local fixture only; not an owner decision.');
  assert.match(await page.locator('#decision-counter').textContent(), new RegExp(`^1 of ${suggestionCount}`));
  await page.reload({ waitUntil:'load' });
  assert.match(await page.locator('#decision-counter').textContent(), new RegExp(`^1 of ${suggestionCount}`));
  const downloaded = page.waitForEvent('download');
  await page.locator('[data-decision-action="download"]').click();
  const download = await downloaded;
  const payload = JSON.parse(await readFile(await download.path(), 'utf8'));
  assert.equal(payload.choices.length, 1);
  assert.match(payload.choices[0].note, /Automated local fixture only/);
  await page.locator('[data-decision-action="clear"]').click();
  assert.match(await page.locator('#decision-counter').textContent(), new RegExp(`^0 of ${suggestionCount}`));
  result.interactions.push('isolated browser-only fixture choice persists, exports JSON and clears; no repository ledger or owner choice written');

  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'clipboard', { configurable:true, value:{writeText:() => Promise.reject(new Error('test denial'))} });
    document.execCommand = () => false;
  });
  await page.goto(base + 'articles/extension-cord-rules-in-the-manuals.html', { waitUntil:'load' });
  await page.locator('.copylink').click();
  await page.locator('.copylink').filter({ hasText:'Copy blocked' }).waitFor();
  result.interactions.push('denied clipboard reports failure instead of claiming a copy');

  const nojs = await browser.newContext({ javaScriptEnabled:false, viewport:{width:390,height:844} });
  await nojs.route('**/*', route => {
    if (new URL(route.request().url()).origin !== origin) { blockedExternal.push(route.request().url()); return route.abort(); }
    return route.continue();
  });
  const plain = await nojs.newPage();
  plain.on('pageerror', error => failures.push(error.message));
  plain.on('response', response => { if (response.status() >= 400) failures.push(`${response.status()} ${response.url()}`); });
  await plain.goto(base, { waitUntil:'load' });
  assert.equal(await plain.locator('.publication-product:visible').count(), 3);
  assert.equal(await plain.locator('[data-format-controls]').isVisible(), false);
  await plain.locator('.workspace-menu > summary').click();
  assert(await plain.locator('.workspace-menu').evaluate(el => el.open));
  result.noJavaScript.push('all three formats and native workspace remain usable; nonfunctional filter UI stays hidden');
  await plain.goto(base + 'suggestions.html', { waitUntil:'load' });
  assert.equal(await plain.locator('[data-suggestion]:visible').count(), suggestionCount);
  assert.equal(await plain.locator('[data-suggestion-toolbar]').isVisible(), false);
  await plain.locator('#sg-08 > details > summary').click();
  assert(await plain.locator('#sg-08 > details').evaluate(el => el.open));
  result.noJavaScript.push('all registered suggestion cards and their native alternatives remain readable');
  await plain.goto(base + 'articles/extension-cord-rules-in-the-manuals.html', { waitUntil:'load' });
  assert.equal(await plain.locator('.reading-body h2').count(), 4);
  result.noJavaScript.push('article and all four sourced sections render without scripts');
  // Close contexts together in finally: serverless single-process Chromium can
  // terminate its process when an individual isolated context is closed.
  assert.deepEqual(failures, []); assert.deepEqual(blockedExternal, []);
  result.pageErrors = failures; result.externalRequests = blockedExternal;
  await mkdir(resolve(root,'.cache'), {recursive:true});
  await writeFile(resolve(root,'.cache/browser-acceptance.json'), JSON.stringify(result,null,2)+'\n');
  console.log(`PASS: ${result.viewports.length} page/viewport combinations, ${result.interactions.length} interaction groups, ${result.noJavaScript.length} no-JS checks; no external request or page error.`);
} finally {
  if (browser) await browser.close();
  await new Promise(done => server.close(done));
}
