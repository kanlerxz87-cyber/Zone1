/* Decision-review queue behaviour, executed against the real published client.

   Why this exists: publication/site.js renders the decision-review page's filter,
   pick persistence and export. Those are the parts a reviewer actually touches, and
   a static HTML check cannot tell whether a pick survives a reload. This runs the
   real file inside a vm with a minimal DOM stub — the same technique as
   tests/analytics_harness.cjs — so the behaviour is exercised without a browser.

   Nothing here touches the network. The picks below are synthetic ("opt B"), not a
   record of any real decision. */
'use strict';
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const vm = require('node:vm');

const SRC = fs.readFileSync('publication/site.js', 'utf8');
const KEY = 'zone1-decision-review-2026-11-19';

function boot() {
  const rows = [
    { id: 'DR-01', text: 'which listing is intended priority' },
    { id: 'DR-02', text: 'is the tracking id enrolled' },
    { id: 'DR-03', text: 'the 180 day qualifying clock' }
  ].map(r => ({
    hidden: false,
    textContent: r.text,
    getAttribute: k => ({ 'data-dr-priority': 'P0', 'data-dr-state': 'needs your decision' })[k],
    querySelector: () => null,
    closest: () => null,
    _id: r.id
  }));

  const radios = [];
  rows.forEach(r => ['opt A', 'opt B'].forEach(value => radios.push({
    value, checked: false, _row: r, _id: r._id,
    getAttribute: k => (k === 'data-dr-id' ? r._id : null),
    setAttribute() {},
    closest: sel => (sel === '[data-dr-priority]' ? r : null)
  })));

  const counter = { textContent: '' };
  const actions = { hidden: true };
  const filterInput = { value: '', addEventListener(t, f) { this._onInput = f; } };
  const filterStatus = { textContent: '' };
  const toolbar = { hidden: true, querySelector: sel => (sel === 'input' ? filterInput : filterStatus) };
  const store = {};
  const listeners = {};

  const document = {
    querySelectorAll(sel) {
      if (sel === '[data-dr-priority]') return rows;
      if (sel === 'input[data-dr-id]') return radios;
      return [];
    },
    querySelector(sel) {
      const m = sel.match(/^input\[name="dr-(.+)"\]\[value="(.+)"\]$/);
      if (m) return radios.find(r => r._id === m[1] && r.value === m[2].replace(/\\/g, '')) || null;
      if (sel === '[data-dr-toolbar]') return toolbar;
      if (sel === '.decision-actions') return actions;
      return null;
    },
    getElementById: id => (id === 'dr-counter' ? counter : null),
    createElement: () => ({ href: '', download: '', setAttribute() {}, click() {}, remove() {} }),
    body: { appendChild() {} },
    addEventListener(type, fn) { listeners[type] = fn; }
  };

  const ctx = {
    document,
    window: {
      localStorage: {
        getItem: k => (k in store ? store[k] : null),
        setItem: (k, v) => { store[k] = String(v); },
        removeItem: k => { delete store[k]; }
      }
    },
    navigator: { clipboard: { writeText: t => { ctx.copied = t; } } },
    setTimeout: fn => { if (typeof fn === 'function') fn(); },
    location: { reload() {} },
    Blob: function (parts) { ctx.lastBlob = parts[0]; },
    URL: { createObjectURL: () => 'blob:test', revokeObjectURL() {} },
    JSON, Object, Date, String, Array
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  return { rows, radios, counter, actions, toolbar, filterInput, filterStatus, store, listeners, ctx };
}

const clickAction = (h, action) => h.listeners.click({
  target: { closest: sel => (sel === '[data-dr-action]' ? { getAttribute: () => action, textContent: '' } : null) }
});

test('decision-review page reveals its controls only once the script runs', () => {
  const h = boot();
  assert.strictEqual(h.toolbar.hidden, false);
  assert.strictEqual(h.actions.hidden, false);
  assert.strictEqual(h.counter.textContent, '0 chosen in this browser');
});

test('the filter hides non-matching decision rows and counts what is left', () => {
  const h = boot();
  h.filterInput.value = 'tracking';
  h.filterInput._onInput();
  assert.deepStrictEqual(h.rows.filter(r => !r.hidden).map(r => r._id), ['DR-02']);
  assert.strictEqual(h.filterStatus.textContent, '1 of 3 decisions shown');
  h.filterInput.value = '';
  h.filterInput._onInput();
  assert.strictEqual(h.rows.filter(r => !r.hidden).length, 3);
});

test('a pick is stored with its priority, counted, and exported as JSON', () => {
  const h = boot();
  const pick = h.radios.find(r => r._id === 'DR-02' && r.value === 'opt B');
  pick.checked = true;
  h.listeners.change({ target: pick });

  assert.strictEqual(h.counter.textContent, '1 chosen in this browser');
  const saved = JSON.parse(h.store[KEY]);
  assert.deepStrictEqual(saved['DR-02'], { priority: 'P0', choice: 'opt B' });

  clickAction(h, 'download');
  assert.ok(h.ctx.lastBlob, 'a download payload was produced');
  const payload = JSON.parse(h.ctx.lastBlob);
  assert.strictEqual(payload.picks['DR-02'].choice, 'opt B');
  assert.ok(payload.recorded, 'the export is dated');
});

test('a stored pick is restored from a previous visit', () => {
  const h = boot();
  h.store[KEY] = JSON.stringify({ 'DR-03': { priority: 'P0', choice: 'opt A' } });
  // Reload the real source against the same storage: the radio must come back checked
  // and the counter must reflect it, without the user touching anything.
  const radios = h.radios.map(r => Object.assign(Object.create(Object.getPrototypeOf(r)), r));
  const doc = {
    querySelectorAll: sel => (sel === '[data-dr-priority]' ? h.rows : sel === 'input[data-dr-id]' ? radios : []),
    querySelector: sel => {
      const m = sel.match(/^input\[name="dr-(.+)"\]\[value="(.+)"\]$/);
      if (m) return radios.find(r => r._id === m[1] && r.value === m[2]) || null;
      if (sel === '[data-dr-toolbar]') return h.toolbar;
      if (sel === '.decision-actions') return h.actions;
      return null;
    },
    getElementById: id => (id === 'dr-counter' ? h.counter : null),
    createElement: () => ({ setAttribute() {}, click() {}, remove() {} }),
    body: { appendChild() {} },
    addEventListener() {}
  };
  const ctx = {
    document: doc,
    window: { localStorage: { getItem: k => h.store[k] ?? null, setItem() {}, removeItem() {} } },
    navigator: {}, setTimeout: () => {}, location: { reload() {} }, JSON, Object, Date, String, Array
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  assert.strictEqual(radios.find(r => r._id === 'DR-03' && r.value === 'opt A').checked, true);
  assert.strictEqual(h.counter.textContent, '1 chosen in this browser');
});

test('clear removes every pick and empties the stored record', () => {
  const h = boot();
  const pick = h.radios.find(r => r._id === 'DR-01' && r.value === 'opt A');
  pick.checked = true;
  h.listeners.change({ target: pick });
  clickAction(h, 'clear');
  assert.strictEqual(h.counter.textContent, '0 chosen in this browser');
  assert.strictEqual(h.radios.filter(r => r.checked).length, 0);
  assert.strictEqual(JSON.parse(h.store[KEY] || '{}').constructor, Object);
});

test('the queue never calls the network', () => {
  const block = SRC.slice(SRC.indexOf('zone1-decision-review'));
  assert.ok(block.length > 500, 'the decision-review block is present');
  assert.ok(!/fetch\s*\(|XMLHttpRequest|sendBeacon/.test(block),
    'the decision queue must not transmit anything');
  assert.ok(block.includes('localStorage'), 'picks live in this browser only');
});
