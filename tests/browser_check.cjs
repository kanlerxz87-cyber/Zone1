// Real headless-Chromium checks against local HTTPS and the actual Python collector.
// Test-only: no external network is allowed; no Amazon request or campaign data is made.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const https = require('node:https');
const { spawn } = require('node:child_process');
const { createInterface } = require('node:readline');
const { createRequire } = require('node:module');
const root = path.resolve(__dirname, '..');
const dependencies = createRequire(path.join(root, 'tests/browser-tools/package.json'));
const { chromium: playwright } = dependencies('playwright-core');
const chromiumModule = dependencies('@sparticuz/chromium');
const chromium = chromiumModule.default || chromiumModule;
const axePath = dependencies.resolve('axe-core/axe.min.js');

function state(origin) {
  return new Promise((resolve, reject) => {
    https.get(origin + '/__fixture_state__', { rejectUnauthorized: false }, response => {
      let data = '';
      response.on('data', part => { data += part; });
      response.on('end', () => { try { resolve(JSON.parse(data)); } catch (e) { reject(e); } });
    }).on('error', reject);
  });
}
function count(snapshot, event) {
  return snapshot.rows.filter(row => row.event === event).reduce((n, row) => n + row.count, 0);
}

(async () => {
  const fixture = spawn('python3', ['tests/browser_fixture.py'], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
  let fixtureErrors = '';
  fixture.stderr.on('data', part => { fixtureErrors += part; });
  const ready = new Promise((resolve, reject) => {
    const lines = createInterface({ input: fixture.stdout });
    lines.once('line', line => { try { resolve(JSON.parse(line)); } catch (e) { reject(e); } });
    fixture.once('exit', code => reject(new Error('fixture exited ' + code + ': ' + fixtureErrors)));
  });
  let browser;
  try {
    const { origin } = await ready;
    // The npm distribution bundles Chromium and its missing sandbox system libraries;
    // no remote browser download or system-package installation is needed.
    if (chromiumModule.inflate) {
      await chromiumModule.inflate(path.join(path.dirname(dependencies.resolve('@sparticuz/chromium')), '../bin/al2023.tar.br'));
      process.env.LD_LIBRARY_PATH = '/tmp/al2023/lib:' + (process.env.LD_LIBRARY_PATH || '');
    }
    browser = await playwright.launch({ executablePath: await chromium.executablePath(), headless: true,
      args: ['--no-sandbox', '--disable-dev-shm-usage', '--no-zygote', '--use-gl=angle', '--use-angle=swiftshader'] });
    const context = await browser.newContext({ ignoreHTTPSErrors: true, viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const errors = [], external = [], layoutFailures = [];
    page.on('pageerror', error => errors.push(error.message));
    await context.route('**/*', route => {
      if (route.request().url().startsWith(origin + '/')) return route.continue();
      external.push(route.request().url());
      return route.abort();
    });
    const pages = fs.readdirSync(root).filter(name => name.endsWith('.html'));
    for (const dir of ['articles', 'products', 'guides', 'categories']) {
      pages.push(...fs.readdirSync(path.join(root, dir)).filter(name => name.endsWith('.html')).map(name => dir + '/' + name));
    }
    const widths = [320, 390, 768, 1440];
    for (const width of widths) {
      await page.setViewportSize({ width, height: 1000 });
      for (const rel of pages) {
        // 404.html intentionally has absolute canonical links/assets; do not navigate
        // them outside the fixture. Test its structure separately in Python instead.
        if (rel === '404.html') continue;
        await page.goto(origin + '/' + rel, { waitUntil: 'load' });
        const result = await page.evaluate(() => {
          const band = document.querySelector('.disclosure-bar').getBoundingClientRect();
          const header = document.querySelector('.masthead').getBoundingClientRect();
          return { overflow: document.documentElement.scrollWidth > innerWidth + 1,
            disclosure: band.top >= header.bottom - 1 && band.bottom < innerHeight && band.height > 0,
            missingImages: [...document.images].some(image => !image.complete || !image.naturalWidth) };
        });
        if (result.overflow || !result.disclosure || result.missingImages) layoutFailures.push({ width, rel, ...result });
      }
    }
    assert.deepEqual(layoutFailures, [], 'no page-wide overflow, broken image or misplaced disclosure');
    assert.equal(count(await state(origin), 'page_view'), 0, 'disabled production HTML must not send');

    // Source- and workspace-heavy pages are included, not just the pretty homepage.
    const accessibilityPages = ['index.html', 'about.html', 'compare.html', 'workspace.html', 'measurement.html',
      'products/chefman-6qt-dual-basket.html', 'products/chefman-8qt-turbofry.html', 'products/emeril-26qt-french-door.html',
      'articles/air-fryer-capacity-guide.html', 'articles/extension-cord-rules-in-the-manuals.html'];
    const violations = [];
    await page.setViewportSize({ width: 390, height: 1000 });
    for (const rel of accessibilityPages) {
      await page.goto(origin + '/' + rel);
      await page.addScriptTag({ path: axePath });
      const audit = await page.evaluate(async () => {
        const result = await axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'] } });
        return result.violations.map(v => ({ id: v.id, impact: v.impact, targets: v.nodes.map(n => n.target) }));
      });
      violations.push(...audit.map(issue => ({ rel, ...issue })));
    }
    assert.deepEqual(violations.filter(v => ['serious', 'critical'].includes(v.impact)), [], 'serious/critical automated accessibility violations');

    await page.goto(origin + '/index.html');
    await page.keyboard.press('Tab');
    assert.equal(await page.locator('.skip-link').evaluate(el => document.activeElement === el), true);
    await page.locator('.workspace-menu summary').click();
    assert.equal(await page.locator('.workspace-menu').getAttribute('open'), '');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.workspace-menu').getAttribute('open'), null);
    await page.locator('.reader-menu summary').click();
    assert.equal(await page.locator('.reader-menu nav a').count(), 4);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.reader-menu summary').evaluate(el => document.activeElement === el), true);
    assert.ok(await page.locator('.reader-menu summary').evaluate(el => parseFloat(getComputedStyle(el).outlineWidth) > 0), 'keyboard focus is visible');
    await page.goto(origin + '/compare.html');
    await page.locator('.tablewrap').first().focus();
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('.tablewrap').first().evaluate(el => document.activeElement === el), true);

    await page.emulateMedia({ media: 'print' });
    assert.equal(await page.locator('.shopbar').evaluate(el => getComputedStyle(el).display), 'none');
    assert.notEqual(await page.locator('.disclosure-bar').evaluate(el => getComputedStyle(el).display), 'none');
    assert.notEqual(await page.locator('.footer-legal').evaluate(el => getComputedStyle(el).display), 'none');
    await page.emulateMedia({ media: 'screen', reducedMotion: 'reduce' });

    const noJSContext = await browser.newContext({ ignoreHTTPSErrors: true, javaScriptEnabled: false,
      viewport: { width: 390, height: 1000 } });
    await noJSContext.route('**/*', route => {
      if (route.request().url().startsWith(origin + '/')) return route.continue();
      external.push(route.request().url());
      return route.abort();
    });
    const noJSPage = await noJSContext.newPage();
    await noJSPage.goto(origin + '/index.html');
    assert.match(await noJSPage.locator('h1').innerText(), /Good food/);
    await noJSPage.locator('.workspace-menu summary').click();
    assert.equal(await noJSPage.locator('.workspace-menu').getAttribute('open'), '');
    assert.equal(await noJSPage.locator('.workspace-dropdown a').count(),
      await page.locator('.workspace-dropdown a').count());
    await noJSPage.locator('.workspace-menu summary').click();
    await noJSPage.locator('.reader-menu summary').click();
    await noJSPage.locator('.reader-menu nav a').filter({ hasText: 'Compare' }).click();
    assert.match(noJSPage.url(), /compare.html$/);
    assert.ok(await noJSPage.locator('table').count());
    await noJSContext.close();
    await page.bringToFront();

    // Local enabled-path E2E. These patches affect fixture responses only; real config,
    // generated HTML and the committed campaign ledger remain disabled/unchanged.
    await context.addCookies([{ name: 'test_cookie_must_not_be_sent', value: 'fixture',
      domain: '127.0.0.1', path: '/', secure: true, sameSite: 'Lax' }]);
    await Promise.all([
      page.waitForResponse(r => r.url().endsWith('/api/analytics/events') && r.status() === 202),
      page.goto(origin + '/__enabled__/compare.html')
    ]);
    const product = JSON.parse(fs.readFileSync(path.join(root, 'data/products.json'))).products[0].slug;
    const accepted = page.waitForResponse(r => r.url().endsWith('/api/analytics/events') && r.status() === 202);
    await page.locator('a[data-analytics-event="comparison_interaction"]').first().click();
    await accepted;
    // A fixture-only tagged link is used for activation. Prevent its navigation *in
    // the test harness* and block all nonlocal requests as a second safeguard.
    await page.evaluate(slug => {
      const anchor = document.createElement('a');
      anchor.id = 'test-amazon-activation';
      anchor.href = 'https://www.amazon.com/dp/TEST-FIXTURE-NOT-A-PRODUCT';
      anchor.dataset.analyticsEvent = 'outbound_click';
      anchor.dataset.analyticsTargetId = slug;
      anchor.textContent = 'Local measurement fixture, never navigate';
      anchor.addEventListener('click', event => event.preventDefault());
      document.body.prepend(anchor);
    }, product);
    let snapshot = await state(origin);
    const beforeOutbound = count(snapshot, 'outbound_click');
    await page.locator('#test-amazon-activation').evaluate(el => el.click());
    assert.equal(count(await state(origin), 'outbound_click'), beforeOutbound, 'synthetic click ignored');
    const clickReceipt = page.waitForResponse(r => r.url().endsWith('/api/analytics/events') && r.status() === 202);
    await page.locator('#test-amazon-activation').click();
    await clickReceipt;
    assert.equal(count(await state(origin), 'outbound_click'), beforeOutbound + 1);

    await page.clock.install();
    await page.goto(origin + '/__enabled__/articles/air-fryer-capacity-guide.html');
    assert.equal(await page.evaluate(() => document.hasFocus()), true);
    await page.clock.runFor(59000);
    assert.equal(count(await state(origin), 'article_engagement'), 0);
    const engagementReceipt = page.waitForResponse(r => r.url().endsWith('/api/analytics/events') && r.status() === 202);
    await page.clock.runFor(1000);
    await engagementReceipt;
    await page.clock.runFor(120000);
    snapshot = await state(origin);
    assert.equal(count(snapshot, 'article_engagement'), 1, 'one fixed threshold event');
    assert.equal(count(snapshot, 'comparison_interaction'), 1);
    assert.ok(snapshot.headers.every(h => !h.cookie && !h.referrer && h.origin === origin && h.content_type === 'application/json'));
    const beforeOptOut = snapshot.headers.length;
    await page.addInitScript(() => Object.defineProperty(navigator, 'globalPrivacyControl', { get: () => true }));
    await page.goto(origin + '/__enabled__/index.html');
    assert.equal((await state(origin)).headers.length, beforeOptOut, 'GPC suppresses requests');
    assert.deepEqual(errors, [], 'browser JavaScript errors');
    assert.deepEqual(external, [], 'no external request was attempted, including Amazon');
    const results = { scope: 'Local HTTPS fixtures, not a production deployment or Associates test',
      layoutChecks: (pages.length - 1) * widths.length, viewports: widths, accessibilityPages: accessibilityPages.length,
      accessibilityViolations: violations, keyboardMenuAndFocus: true, noJavaScriptNavigation: true, printDisclosure: true,
      events: snapshot.rows, externalRequests: external.length, javaScriptErrors: errors.length,
      campaignLedgerRows: JSON.parse(fs.readFileSync(path.join(root, 'data/campaign-ledger.json'))).rows.length };
    fs.mkdirSync(path.join(root, '.arena'), { recursive: true });
    fs.writeFileSync(path.join(root, '.arena/browser-results.json'), JSON.stringify(results, null, 2));
    console.log(JSON.stringify(results, null, 2));
  } finally {
    if (browser) await browser.close();
    fixture.kill('SIGTERM');
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
