// No npm dependencies. Execute the actual generated script, not a reimplementation.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/analytics.js'), 'utf8');
const product = JSON.parse(fs.readFileSync(path.join(root, 'data/products.json'))).products[0].slug;

function harness(options = {}) {
  const listeners = {};
  const requests = [];
  const intervals = new Map();
  let now = 0;
  const attrs = { 'data-endpoint': '/api/analytics/events', 'data-collection': 'enabled', ...options.attrs };
  const document = {
    currentScript: { getAttribute: key => attrs[key] || '' },
    body: { getAttribute: key => key === 'data-page-id' ? (options.page || 'index') : (options.type || 'page') },
    visibilityState: options.visibility || 'visible',
    focused: true,
    hasFocus() { return this.focused; },
    addEventListener: (name, handler) => { (listeners[name] ||= []).push(handler); },
    removeEventListener: (name, handler) => { listeners[name] = (listeners[name] || []).filter(fn => fn !== handler); }
  };
  // These accessors throw if a future counter starts reading reader identifiers.
  for (const key of ['cookie', 'referrer']) {
    Object.defineProperty(document, key, { get() { throw new Error('forbidden: ' + key); } });
  }
  const navigator = { ...options.navigator };
  Object.defineProperty(navigator, 'userAgent', { get() { throw new Error('forbidden user agent'); } });
  const location = { href: 'https://publication.test/Zone1/index.html', origin: 'https://publication.test' };
  const context = {
    document, navigator, URL, Object, JSON, Math,
    window: { location }, performance: { now: () => now },
    fetch: (url, init) => { requests.push({ url, ...init, payload: JSON.parse(init.body) }); return Promise.resolve({ status: 202 }); },
    setInterval: fn => { const id = intervals.size + 1; intervals.set(id, fn); return id; },
    clearInterval: id => intervals.delete(id)
  };
  vm.runInNewContext(source, context, { filename: 'generated-assets/analytics.js' });
  return {
    requests, document, navigator,
    dispatch(name, event) { (listeners[name] || []).slice().forEach(fn => fn(event)); },
    tick(seconds) { for (let i = 0; i < seconds; i++) { now += 1000; [...intervals.values()].forEach(fn => fn()); } }
  };
}
function anchor(event = 'outbound_click', href = 'https://link.amazon/B04G1MEwY') {
  return { href, getAttribute: key => key === 'data-analytics-target-id' ? product : event };
}
function click(node, trusted = true, button = 0, type = 'click') {
  return { type, isTrusted: trusted, button, target: { closest: () => node } };
}
function validateWithCollector(payload) {
  const result = spawnSync('python3', ['-c',
    'import json,sys; from analytics.collector import validate_payload; validate_payload(json.load(sys.stdin))'
  ], { cwd: root, input: JSON.stringify(payload), encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
}

test('generated output is exactly the maintained client source', () => {
  assert.equal(source, fs.readFileSync(path.join(root, 'analytics/client.js'), 'utf8'));
});
test('no endpoint, explicit disable, foreign endpoint, DNT or GPC means no requests', () => {
  for (const options of [
    { attrs: { 'data-endpoint': '' } }, { attrs: { 'data-collection': '' } },
    { attrs: { 'data-endpoint': 'https://foreign.test/events' } },
    ...['//foreign.test/api/analytics/events', '/other', '/api/analytics/events?x=1', '/api/analytics/events#x',
      'http://publication.test/api/analytics/events', 'https://user@publication.test/api/analytics/events',
      'https://publication.test:444/api/analytics/events'].map(endpoint => ({ attrs: { 'data-endpoint': endpoint } })),
    { navigator: { doNotTrack: '1' } }, { navigator: { globalPrivacyControl: true } }
  ]) { assert.equal(harness(options).requests.length, 0); }
});
test('a hidden document counts only once when first visible', () => {
  const h = harness({ visibility: 'hidden' });
  assert.equal(h.requests.length, 0);
  h.document.visibilityState = 'visible';
  h.dispatch('visibilitychange');
  h.dispatch('visibilitychange');
  assert.equal(h.requests.length, 1);
});
test('page views are minimal JSON, same-origin, cookieless and referrer-free', () => {
  const { requests } = harness();
  assert.deepEqual(requests[0].payload, { event: 'page_view', page_id: 'index' });
  assert.equal(requests[0].mode, 'same-origin');
  assert.equal(requests[0].credentials, 'omit');
  assert.equal(requests[0].referrerPolicy, 'no-referrer');
  assert.equal(requests[0].headers['Content-Type'], 'application/json');
  validateWithCollector(requests[0].payload);
});
test('short links count without guessing an ASIN; synthetic/foreign clicks do not', () => {
  const h = harness();
  h.dispatch('click', click(anchor(), false));
  h.dispatch('click', click(anchor('outbound_click', 'https://amazon.com.evil.test/dp/B000000000')));
  h.dispatch('click', click(anchor(), true, 2));
  assert.equal(h.requests.length, 1);
  h.dispatch('click', click(anchor()));
  h.dispatch('auxclick', click(anchor(), true, 1, 'auxclick'));
  assert.equal(h.requests.length, 3);
  for (const req of h.requests.slice(1)) {
    assert.deepEqual(req.payload, { event: 'outbound_click', page_id: 'index', target_id: product });
    validateWithCollector(req.payload);
  }
});
test('comparison event means a real internal product-guide activation, not table visibility', () => {
  const h = harness({ page: 'compare' });
  h.dispatch('click', click(anchor('comparison_interaction', 'https://publication.test/Zone1/about.html')));
  h.dispatch('click', click(anchor('comparison_interaction', 'https://foreign.test/Zone1/products/' + product + '.html')));
  h.dispatch('click', click(anchor('comparison_interaction', 'https://publication.test/Zone1/products/different.html')));
  assert.equal(h.requests.length, 1);
  h.dispatch('click', click(anchor('comparison_interaction', 'https://publication.test/Zone1/products/' + product + '.html')));
  assert.equal(h.requests[1].payload.event, 'comparison_interaction');
  validateWithCollector(h.requests[1].payload);
});
test('engagement waits for 60 active seconds, pauses hidden, and fires only once', () => {
  const h = harness({ page: 'articles/air-fryer-capacity-guide', type: 'article' });
  h.tick(30);
  h.document.visibilityState = 'hidden'; h.tick(100);
  assert.equal(h.requests.length, 1);
  h.document.visibilityState = 'visible';
  h.document.focused = false; h.tick(100);
  assert.equal(h.requests.length, 1);
  h.document.focused = true; h.tick(29);
  assert.equal(h.requests.length, 1);
  h.tick(1); h.tick(120);
  assert.equal(h.requests.length, 2);
  assert.deepEqual(h.requests[1].payload, { event: 'article_engagement', page_id: 'articles/air-fryer-capacity-guide', bucket: '60s' });
  validateWithCollector(h.requests[1].payload);
});
test('an opt-out set after page load suppresses later clicks', () => {
  const h = harness();
  h.navigator.globalPrivacyControl = true;
  h.dispatch('click', click(anchor()));
  assert.equal(h.requests.length, 1);
});
