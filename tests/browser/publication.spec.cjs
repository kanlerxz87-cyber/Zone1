const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '../..');
const BASE = 'https://localhost:8123';
const CANONICAL = 'https://kanlerxz87-cyber.github.io/Zone1';
const disclosure = 'As an Amazon Associate I earn from qualifying purchases.';
const pages = ['.', 'products', 'categories', 'guides', 'articles'].flatMap(folder =>
  fs.readdirSync(path.join(ROOT, folder)).filter(name => name.endsWith('.html'))
    .map(name => folder === '.' ? name : `${folder}/${name}`));
const representative = [
  'index.html', 'categories/kitchen-appliances.html', 'categories/cooking-thermometers.html',
  'products/chefman-6qt-dual-basket.html', 'compare.html',
  'articles/dual-basket-vs-oven-air-fryer.html', 'about.html', 'executive-summary.html',
  'suggestions.html', 'questions.html', 'decision-log.html', 'product-intent.html',
];

// The production 404 deliberately has absolute canonical recovery/asset URLs.
// Serve those from the local checkout during this offline test, never the network.
test.beforeEach(async ({ context }) => {
  await context.route(CANONICAL + '/**', async route => {
    const response = await context.request.get(route.request().url().replace(CANONICAL, BASE));
    await route.fulfill({ response });
  });
});

async function snapshot(page) {
  return page.evaluate(() => {
    const bar = document.querySelector('.disclosure-bar').getBoundingClientRect();
    const header = document.querySelector('header.topbar').getBoundingClientRect();
    return {
      viewport: innerWidth, width: document.documentElement.scrollWidth,
      bar: { top: bar.top, bottom: bar.bottom, height: bar.height },
      headerBottom: header.bottom, height: innerHeight,
      h1: document.querySelectorAll('h1').length,
      images: [...document.images].every(image => image.complete && image.naturalWidth > 0),
    };
  });
}

async function gatePage(page, route) {
  const response = await page.goto('/' + route, { waitUntil: 'networkidle' });
  expect(response.status(), route).toBe(200);
  await page.evaluate(() => document.fonts.ready);
  const state = await snapshot(page);
  expect(state.width, `${route}: document horizontal overflow`).toBeLessThanOrEqual(state.viewport + 1);
  expect(state.bar.top, `${route}: strip under masthead`).toBeGreaterThanOrEqual(state.headerBottom - 1);
  expect(state.bar.bottom, `${route}: disclosure fully above fold`).toBeLessThan(state.height);
  expect(state.h1, route).toBe(1);
  expect(state.images, `${route}: image decoding`).toBe(true);
  await expect(page.locator('.disclosure-bar')).toContainText(disclosure);
  await expect(page.locator('footer.site')).toContainText(disclosure);
  await expect(page.locator('.workspace-menu')).toHaveCount(1);
  await expect(page.locator('script[src*="analytics.js"]')).toHaveCount(0);
  await expect(page.locator('meta[name="google-site-verification"]')).toHaveCount(0);
  expect(await page.evaluate(() => document.cookie)).toBe('');
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
}

test('all canonical pages: four viewport widths, local assets and disclosure', async ({ page, context }, info) => {
  const errors = [], failed = [], analytics = [], foreign = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('response', response => { if (response.status() >= 400) failed.push(`${response.status()} ${response.url()}`); });
  context.on('request', request => {
    if (request.url().includes('/api/analytics/')) analytics.push(request.url());
    if (/^https?:/.test(request.url()) && !request.url().startsWith(BASE + '/') && !request.url().startsWith(CANONICAL + '/')) foreign.push(request.url());
  });
  for (const viewport of [{ width: 320, height: 800 }, { width: 390, height: 844 },
                          { width: 768, height: 1024 }, { width: 1440, height: 1000 }]) {
    await page.setViewportSize(viewport);
    for (const route of pages) {
      await gatePage(page, route);
      if ([390, 1440].includes(viewport.width) &&
          ['index.html', 'compare.html', 'products/chefman-6qt-dual-basket.html',
           'articles/dual-basket-vs-oven-air-fryer.html', 'executive-summary.html'].includes(route)) {
        await page.screenshot({ path: info.outputPath(`${route.replaceAll('/', '-')}-${viewport.width}.png`), fullPage: true });
      }
    }
  }
  expect(errors).toEqual([]);
  expect(failed).toEqual([]);
  expect(analytics).toEqual([]);
  expect(foreign).toEqual([]);
  expect(await context.cookies()).toEqual([]);
});

test('reader routes and native Workspace remain usable with JavaScript disabled', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, ignoreHTTPSErrors: true,
                                            viewport: { width: 320, height: 800 } });
  const page = await context.newPage();
  for (const route of representative) await gatePage(page, route);
  await page.goto('/');
  await page.getByText('Workspace', { exact: true }).click();
  await expect(page.locator('.workspace-menu')).toHaveAttribute('open', '');
  await page.locator('.workspace-links').getByText('Executive summary & index', { exact: true }).click();
  await expect(page).toHaveURL(/executive-summary\.html$/);
  await page.goto('/');
  await page.getByRole('link', { name: 'Explore the product guide' }).first().click();
  await expect(page).toHaveURL(/products\/chefman-6qt-dual-basket\.html$/);
  await expect(page.getByRole('link', { name: /View on Amazon/ }).first()).toBeVisible();
  await page.locator('#source-record > summary').click();
  await expect(page.locator('#source-record')).toHaveAttribute('open', '');
  await expect(page.locator('#source-record table').first()).toBeVisible();
  await page.goto('/compare.html');
  const table = page.locator('.tablewrap').first();
  await table.focus();
  await page.keyboard.press('ArrowRight');
  await expect.poll(() => table.evaluate(node => node.scrollLeft)).toBeGreaterThan(0);
  await page.goto('/decision-log.html');
  await expect(page.locator('[data-decision-action="download"]')).toBeHidden();
  const notice = page.locator('noscript p');
  await expect(notice).toBeVisible();
  // Text locators intentionally exclude NOSCRIPT, even when scripting is disabled.
  expect(await notice.evaluate(node => node.textContent)).toContain('Decision drafting/export needs JavaScript');
  await context.close();
});

test('keyboard menu, focus return, scrolling and local decision draft export', async ({ page, context }) => {
  const events = [];
  context.on('request', request => { if (request.method() !== 'GET') events.push(request.url()); });
  await page.goto('/');
  const summary = page.locator('.workspace-menu > summary');
  await summary.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('.workspace-menu')).toHaveAttribute('open', '');
  await page.keyboard.press('Tab');
  await expect(page.locator('.workspace-links a').first()).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.locator('.workspace-menu')).not.toHaveAttribute('open', '');
  await expect(summary).toBeFocused();
  await summary.click();
  await page.locator('h1').click();
  await expect(page.locator('.workspace-menu')).not.toHaveAttribute('open', '');
  await page.goto('/decision-log.html');
  const choice = page.locator('fieldset[data-sg="SG-04"] input[value="A"]');
  await choice.check();
  await page.locator('fieldset[data-sg="SG-04"] textarea').fill('Synthetic local draft; not a repository approval.');
  await expect(page.locator('#decision-counter')).toContainText('1 of');
  await page.reload();
  await expect(choice).toBeChecked();
  const downloadPromise = page.waitForEvent('download');
  await page.locator('[data-decision-action="download"]').click();
  const download = await downloadPromise;
  const exported = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
  expect(exported.choices).toHaveLength(1);
  expect(exported.choices[0].id).toBe('SG-04');
  await page.locator('[data-decision-action="clear"]').click();
  await expect(choice).not.toBeChecked();
  expect(await page.evaluate(() => localStorage.length)).toBe(0);
  expect(events).toEqual([]);
});

test('malformed or unavailable local storage does not break the workspace', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.evaluate(() => localStorage.setItem('zone1.decision-drafts.v2', JSON.stringify({ 'SG-04': { path: '"]broken', note: {} } })));
  await page.goto('/decision-log.html');
  await expect(page.locator('#decision-counter')).toContainText('nothing picked');
  expect(errors).toEqual([]);
  await page.addInitScript(() => Object.defineProperty(window, 'localStorage', { get() { throw new Error('Test storage denied'); } }));
  await page.reload();
  await expect(page.locator('#decision-counter')).toContainText('storage unavailable');
  await page.locator('fieldset[data-sg="SG-04"] input[value="A"]').check();
  expect(errors).toEqual([]);
});

test('scoped axe accessibility checks on reader and critical workspace pages', async ({ page }, info) => {
  const findings = [];
  for (const width of [390, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const route of representative) {
      await page.goto('/' + route, { waitUntil: 'networkidle' });
      await page.addScriptTag({ path: require.resolve('axe-core/axe.min.js') });
      const result = await page.evaluate(() => axe.run(document, {
        runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] },
      }));
      for (const violation of result.violations) findings.push({ route, width, id: violation.id,
        impact: violation.impact, help: violation.help, nodes: violation.nodes.map(node => node.target) });
    }
  }
  await info.attach('axe-findings', { body: JSON.stringify(findings, null, 2), contentType: 'application/json' });
  expect(findings).toEqual([]);
});
