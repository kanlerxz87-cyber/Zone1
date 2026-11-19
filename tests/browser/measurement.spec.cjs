const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
const BASE = 'https://localhost:8123';

async function stats(request) { return (await request.get('/__test/stats')).json(); }
async function count(request, event) {
  return (await stats(request)).filter(row => row.event === event).reduce((sum, row) => sum + row.count, 0);
}
async function noRetailNavigation(context) {
  await context.route('**/*', route => {
    if (/^https?:/.test(route.request().url()) && !route.request().url().startsWith(BASE + '/')) return route.abort();
    return route.continue();
  });
}

test.beforeEach(async ({ request, context }) => {
  await request.post('/__test/reset');
  // Controlled bot signal only in the enabled synthetic fixture, never production.
  await context.addInitScript(() => Object.defineProperty(navigator, 'webdriver', { get: () => false }));
});

test('real browser trusted primary, keyboard and middle clicks reach the aggregate HTTP collector', async ({ page, context, request }) => {
  await noRetailNavigation(context);
  await context.addCookies([{ name: 'synthetic-cookie-not-to-send', value: 'test', url: BASE }]);
  const sent = [], responses = [], headers = [];
  context.on('request', event => {
    if (!event.url().endsWith('/api/analytics/events')) return;
    sent.push(event.postDataJSON()); headers.push(event.headers());
  });
  context.on('response', response => { if (response.url().endsWith('/api/analytics/events')) responses.push(response.status()); });
  await page.goto('/__test/product.html?utm_source=private&tag=private&asin=private', { waitUntil: 'domcontentloaded' });
  await expect.poll(() => count(request, 'page_view')).toBe(1);
  const link = page.getByRole('link', { name: /View on Amazon/ }).first();
  await link.evaluate(node => node.dispatchEvent(new MouseEvent('click', { bubbles: true, button: 0, cancelable: true })));
  await expect.poll(() => count(request, 'outbound_click')).toBe(0);
  await page.bringToFront();
  await link.click();
  await expect.poll(() => count(request, 'outbound_click')).toBe(1);
  await page.bringToFront();
  await link.focus();
  await page.keyboard.press('Enter');
  await expect.poll(() => count(request, 'outbound_click')).toBe(2);
  await page.bringToFront();
  await link.click({ button: 'middle' });
  await expect.poll(() => count(request, 'outbound_click')).toBe(3);
  await page.bringToFront();
  await link.click({ button: 'right' });
  await page.keyboard.press('Escape');
  await expect.poll(() => count(request, 'outbound_click')).toBe(3);
  expect(sent).toHaveLength(4);
  expect(responses).toEqual([202, 202, 202, 202]);
  for (const payload of sent) {
    expect(Object.keys(payload).sort()).toEqual(payload.event === 'page_view'
      ? ['event', 'page_id'] : ['event', 'page_id', 'target_id']);
    expect(JSON.stringify(payload)).not.toMatch(/private|utm_|https:|shopnow|B0CDY/);
  }
  for (const header of headers) {
    expect(header.cookie).toBeUndefined();
    expect(header.referer).toBeUndefined();
    expect(header.origin).toBe(BASE);
  }
  const rows = await stats(request);
  for (const row of rows) expect(Object.keys(row).sort()).toEqual(['bucket', 'count', 'day', 'event', 'page_id', 'target_id']);
});

test('comparison view does not become an interaction until a trusted detail activation', async ({ page, context, request }) => {
  await noRetailNavigation(context);
  await page.goto('/__test/compare.html', { waitUntil: 'domcontentloaded' });
  await expect.poll(() => count(request, 'page_view')).toBe(1);
  expect(await count(request, 'comparison_interaction')).toBe(0);
  const detail = page.locator('a[data-analytics-event="comparison_interaction"]').first();
  await detail.click();
  await expect.poll(() => count(request, 'comparison_interaction')).toBe(1);
  expect(await count(request, 'article_engagement')).toBe(0);
});

test('real-client reading bucket with a virtual clock and controlled focus/visibility', async ({ page, request }) => {
  // Headless Chromium/Playwright emulate every tab as focused. Control these two
  // inputs explicitly; this verifies the client/state/HTTP contract, not OS focus.
  await page.addInitScript(() => {
    window.__zone1TestFocused = true;
    window.__zone1TestVisible = true;
    Object.defineProperty(document, 'hasFocus', { value: () => window.__zone1TestFocused });
    Object.defineProperty(document, 'visibilityState', { get: () => window.__zone1TestVisible ? 'visible' : 'hidden' });
  });
  await page.clock.install();
  await page.goto('/__test/article.html', { waitUntil: 'domcontentloaded' });
  await page.clock.runFor(59_000);
  expect(await count(request, 'article_engagement')).toBe(0);
  await page.evaluate(() => { window.__zone1TestFocused = false; });
  await page.clock.runFor(60_000);
  expect(await count(request, 'article_engagement')).toBe(0);
  await page.evaluate(() => { window.__zone1TestFocused = true; window.__zone1TestVisible = false; });
  await page.clock.runFor(60_000);
  expect(await count(request, 'article_engagement')).toBe(0);
  await page.evaluate(() => { window.__zone1TestVisible = true; });
  await page.clock.runFor(1_000);
  await expect.poll(() => count(request, 'article_engagement')).toBe(1);
  await page.clock.runFor(60_000);
  expect(await count(request, 'article_engagement')).toBe(1);
  const engagement = (await stats(request)).find(row => row.event === 'article_engagement');
  expect(engagement.bucket).toBe('60s');
});

test('DNT and GPC suppress actual-browser enabled fixtures', async ({ browser, request }) => {
  for (const mode of ['dnt', 'gpc']) {
    await request.post('/__test/reset');
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    await noRetailNavigation(context);
    await context.addInitScript(mode => {
      Object.defineProperty(navigator, 'webdriver', { get: () => false });
      if (mode === 'dnt') Object.defineProperty(navigator, 'doNotTrack', { get: () => '1' });
      if (mode === 'gpc') Object.defineProperty(navigator, 'globalPrivacyControl', { get: () => true });
    }, mode);
    const page = await context.newPage();
    await page.goto(BASE + '/__test/product.html', { waitUntil: 'domcontentloaded' });
    await page.getByRole('link', { name: /View on Amazon/ }).first().click();
    expect(await stats(request)).toEqual([]);
    await context.close();
  }
});

test('browser-only fixtures never change repository collection, link or campaign state', async () => {
  const root = path.resolve(__dirname, '../..');
  const config = JSON.parse(fs.readFileSync(path.join(root, 'data/config.json')));
  const plan = JSON.parse(fs.readFileSync(path.join(root, 'data/analytics-plan.json')));
  const intent = JSON.parse(fs.readFileSync(path.join(root, 'data/product-intent.json')));
  const ledger = JSON.parse(fs.readFileSync(path.join(root, 'data/campaign-ledger.json')));
  expect(config.analytics.enabled).toBe(false);
  expect(plan.collection.enabled).toBe(false);
  expect(plan.collection.endpoint_deployed).toBe(false);
  expect(config.associate_tag).toBe('');
  expect(intent.tracking_id_applied_to_links).toBe(false);
  expect(ledger.rows).toEqual([]);
});


test('an ordinary automated browser is excluded from enabled synthetic measurement', async ({ browser, request }) => {
  await request.post('/__test/reset');
  const context = await browser.newContext({ ignoreHTTPSErrors:true });
  const page = await context.newPage();
  await page.goto(BASE + '/__test/product.html', { waitUntil:'domcontentloaded' });
  expect(await page.evaluate(() => navigator.webdriver)).toBe(true);
  expect(await stats(request)).toEqual([]);
  await context.close();
});
