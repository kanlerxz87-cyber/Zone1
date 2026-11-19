const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'analytics/client.js'), 'utf8');
const plan = JSON.parse(fs.readFileSync(path.join(root, 'data/analytics-plan.json'), 'utf8'));
const product = JSON.parse(fs.readFileSync(path.join(root, 'data/products.json'), 'utf8')).products[0].slug;

function boot(options = {}) {
  const events = [], listeners = {}, timers = new Map();
  const attributes = {
    'data-page-id': options.page || 'index',
    'data-page-type': options.type || 'page',
    'data-analytics-eligible': options.eligible === false ? 'false' : 'true'
  };
  let focused = true;
  const document = {
    currentScript: { getAttribute(name) {
      if (name === 'data-enabled') return options.disabled ? 'false' : 'true';
      if (name === 'data-target-ids') return [product, 'PI-04', 'PI-05'].join(',');
      return name === 'data-endpoint' ? (options.endpoint ?? '/api/analytics/events') :
        plan.events.filter(event => event.origin === 'browser').map(event => event.name).join(',');
    } },
    body: { getAttribute: name => attributes[name] },
    visibilityState: options.hidden ? 'hidden' : 'visible',
    prerendering: Boolean(options.prerendering),
    hasFocus: () => focused,
    addEventListener(name, fn) { listeners[name] = fn; }
  };
  const window = {
    location: { origin: 'https://zone1.example' },
    fetch(url, init) {
      if (options.offline) throw new Error('offline fixture');
      events.push({ url, init, payload: JSON.parse(init.body) });
      return Promise.resolve({ ok: true });
    },
    setInterval(fn) { const id = timers.size + 1; timers.set(id, fn); return id; },
    clearInterval(id) { timers.delete(id); },
    addEventListener(name, fn) { listeners[name] = fn; }
  };
  const navigator = {
    doNotTrack: options.dnt ? '1' : '0',
    globalPrivacyControl: Boolean(options.gpc),
    webdriver: Boolean(options.automation)
  };
  vm.runInNewContext(source, { document, window, navigator, URL, JSON, fetch:window.fetch, setInterval:window.setInterval, clearInterval:window.clearInterval });
  return {
    events, document, listeners, timers, navigator,
    focus(value) { focused = value; },
    tick(n = 1) { for (let i = 0; i < n; i++) [...timers.values()].forEach(fn => fn()); },
    click(event, { trusted = true, button = 0, target = product, type = 'click' } = {}) {
      const link = { getAttribute: key => key === 'data-analytics-event' ? event : target };
      const fn = listeners[type];
      if (fn) fn({ type, isTrusted: trusted, button, target: { closest: () => link } });
    }
  };
}

test('no endpoint, owner page, cross-origin or noncanonical path means no collection', () => {
  for (const options of [{ endpoint: '' }, { eligible: false }, { endpoint: 'https://other.example/api/analytics/events' },
    { endpoint: '/api/analytics/events?email=private' }, { endpoint: '/not-the-collector' }]) {
    assert.equal(boot(options).events.length, 0);
  }
});

test('DNT, Global Privacy Control and automation suppress every event', () => {
  for (const options of [{ dnt: true }, { gpc: true }, { automation: true }]) {
    const app = boot({ ...options, type: 'article', page: 'articles/how-to-clean-an-air-fryer' });
    app.click('outbound_click'); app.tick(100);
    assert.equal(app.events.length, 0);
  }
});

test('page view waits for visible non-prerendered display and fires once', () => {
  const app = boot({ hidden: true, prerendering: true });
  assert.equal(app.events.length, 0);
  app.document.visibilityState = 'visible'; app.listeners.visibilitychange();
  assert.equal(app.events.length, 0);
  app.document.prerendering = false; app.listeners.prerenderingchange(); app.listeners.visibilitychange();
  assert.deepEqual(app.events.map(x => x.payload), [{ event: 'page_view', page_id: 'index' }]);
});

test('only trusted explicit primary/keyboard or middle activations count; no ASIN guessing', () => {
  const app = boot();
  app.click('outbound_click', { trusted: false });
  app.click('outbound_click', { button: 2 });
  app.click('unrecognized');
  app.click('outbound_click');
  app.click('outbound_click', { type: 'auxclick', button: 1, target: 'PI-04' });
  assert.deepEqual(app.events.slice(1).map(x => x.payload), [
    { event: 'outbound_click', page_id: 'index', target_id: product },
    { event: 'outbound_click', page_id: 'index', target_id: 'PI-04' }
  ]);
});

test('engagement excludes hidden and unfocused time and sends only one fixed bucket', () => {
  const app = boot({ type: 'article', page: 'articles/how-to-clean-an-air-fryer' });
  app.document.visibilityState = 'hidden'; app.tick(80);
  app.document.visibilityState = 'visible'; app.focus(false); app.tick(80);
  assert.equal(app.events.length, 1);
  app.focus(true); app.tick(59); assert.equal(app.events.length, 1);
  app.tick(); app.tick(80);
  assert.equal(app.events.length, 2);
  assert.deepEqual(app.events[1].payload, {
    event: 'article_engagement', page_id: 'articles/how-to-clean-an-air-fryer', bucket: '60s'
  });
});

test('comparison event is an activation on compare, not a visibility impression', () => {
  const app = boot({ page: 'compare', type: 'comparison' });
  assert.equal(app.events.length, 1);
  app.click('comparison_interaction');
  assert.deepEqual(app.events[1].payload, { event: 'comparison_interaction', page_id: 'compare', target_id: product });
  const article = boot(); article.click('comparison_interaction');
  assert.equal(article.events.length, 1);
});

test('actual client payloads pass the Python collector unchanged and carry no connection metadata', () => {
  const article = boot({ type: 'article', page: 'articles/how-to-clean-an-air-fryer' });
  article.click('outbound_click'); article.tick(60);
  const comparison = boot({ page: 'compare', type: 'comparison' }); comparison.click('comparison_interaction');
  const samples = [...article.events, ...comparison.events];
  for (const { url, init, payload } of samples) {
    assert.equal(new URL(url, 'https://zone1.example').href, 'https://zone1.example/api/analytics/events');
    assert.equal(init.headers['Content-Type'], 'application/json');
    assert.equal(init.credentials, 'omit');
    assert.equal(init.referrerPolicy, 'no-referrer');
    assert.ok(Object.keys(payload).every(key => ['event', 'page_id', 'target_id', 'bucket'].includes(key)));
  }
  const result = execFileSync('python3', ['-c',
    'import json,sys; from analytics.collector import validate_payload; rows=json.load(sys.stdin); [validate_payload(row) for row in rows]; print(len(rows))'
  ], { cwd: root, input: JSON.stringify(samples.map(x => x.payload)), encoding: 'utf8' });
  assert.equal(Number(result.trim()), samples.length);
});

test('offline measurement is non-blocking and opt-out changes take effect immediately', () => {
  assert.doesNotThrow(() => { const app = boot({ offline: true }); app.click('outbound_click'); });
  const app = boot(); app.navigator.globalPrivacyControl = true; app.click('outbound_click');
  assert.equal(app.events.length, 1);
});
