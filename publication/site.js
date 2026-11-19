// Progressive controls are hidden in the HTML until their handlers can run.
document.querySelectorAll('[data-js-required]').forEach(function (node) { node.hidden = false; });

// copy-to-clipboard for article share rows (2026-11-15, arena/792c279e).
// Progressive: without JS the button does nothing and the URL is still in the address bar,
// so no functionality depends on it.
document.addEventListener('click', function (ev) {
  var c = ev.target.closest('.copylink');
  if (!c) return;
  var link = c.getAttribute('data-link') || location.href;
  var done = function () {
    var old = c.textContent;
    c.textContent = 'Copied';
    setTimeout(function () { c.textContent = old; }, 1600);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(link).then(done, function () { c.textContent = 'Copy blocked — use the address bar'; });
  } else {
    var ta = document.createElement('textarea');
    ta.value = link; document.body.appendChild(ta); ta.select();
    var copied = false;
    try { copied = document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta);
    if (copied) done(); else c.textContent = 'Copy blocked — use the address bar';
  }
});

// The native Workspace disclosure works without JavaScript. These shortcuts
// only close it on Escape or an outside activation; no keyboard focus is trapped.
document.addEventListener('keydown', function (event) {
  if (event.key !== 'Escape') return;
  var menu = document.querySelector('.workspace-menu[open]');
  if (!menu) return;
  menu.open = false;
  menu.querySelector('summary').focus();
});
document.addEventListener('click', function (event) {
  var menu = document.querySelector('.workspace-menu[open]');
  if (menu && !menu.contains(event.target)) menu.open = false;
});

// Owner decision picker (2026-11-16, arena/ba29c641) — decision-log.html only.
// A static host has nowhere to POST a choice, so the picker keeps it in this browser and exports
// the exact JSON body of data/decision-log.json. Progressive: with JS off the page still reads end
// to end, every default is printed in the register table, and only the picking needs the script.
// No dependency, no network call, nothing leaves the page.
(function () {
  var root = document.getElementById('decision-picker');
  if (!root) return;
  var KEY = 'zone1.decision-drafts.v2';
  var counter = document.getElementById('decision-counter');
  var out = document.getElementById('decision-output');
  var store = {};
  var storageReady = true;
  try { store = JSON.parse(window.localStorage.getItem(KEY) || '{}') || {}; } catch (err) { store = {}; storageReady = false; }
  if (typeof store !== 'object' || Array.isArray(store)) store = {};

  function panels() {
    return Array.prototype.slice.call(root.querySelectorAll('fieldset[data-sg]'));
  }
  function chosen(fs) {
    var i = fs.querySelector('input:checked');
    return i ? i.value : '';
  }
  function note(fs) {
    var t = fs.querySelector('textarea.dec-note');
    return t ? t.value.trim() : '';
  }
  function collect() {
    var today = new Date().toISOString().slice(0, 10);
    var picked = [];
    panels().forEach(function (fs) {
      var path = chosen(fs), txt = note(fs);
      if (!path && !txt) return;
      picked.push({
        id: fs.getAttribute('data-sg'),
        suggestion: fs.getAttribute('data-title'),
        chosen_path: path === 'HOLD' ? 'hold' : path,
        default_if_silent: fs.getAttribute('data-default') || 'none',
        overrode_default: !!(path && path !== 'HOLD' && fs.getAttribute('data-default') &&
                            path !== fs.getAttribute('data-default')),
        note: txt,
        recorded_at: today
      });
    });
    return picked;
  }
  function payload() {
    return JSON.stringify({
      version: '1.1',
      exported: new Date().toISOString().slice(0, 10),
      exported_from: 'decision-log.html',
      choices: collect(),
      note: 'Merge choices[] into data/decision-log.json. A recorded choice outranks the default; ' +
            'a suggestion absent from this list keeps its default.'
    }, null, 1);
  }
  function paint() {
    if (!counter) return;
    var n = collect().length;
    counter.textContent = n + ' of ' + panels().length + ' picked in this browser' +
      (storageReady ? (n ? ' — copy or download to hand it back' : ' — nothing picked yet') : ' — storage unavailable; copy/download to retain');
  }
  function persist() {
    try { window.localStorage.setItem(KEY, JSON.stringify(store)); } catch (err) { storageReady = false; }
  }
  function record(target) {
    var fs = target.closest ? target.closest('fieldset[data-sg]') : null;
    if (!fs) return;
    store[fs.getAttribute('data-sg')] = { path: chosen(fs), note: note(fs) };
    persist();
    paint();
  }
  function flash(btn, msg) {
    var old = btn.textContent;
    btn.setAttribute('data-label', old);
    btn.textContent = msg;
    setTimeout(function () { btn.textContent = old; }, 1900);
  }
  root.addEventListener('change', function (ev) { record(ev.target); });
  root.addEventListener('input', function (ev) {
    if (ev.target && ev.target.tagName === 'TEXTAREA') record(ev.target);
  });
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest ? ev.target.closest('[data-decision-action]') : null;
    if (!btn) return;
    var act = btn.getAttribute('data-decision-action');
    if (act === 'clear') {
      store = {};
      try { window.localStorage.removeItem(KEY); } catch (err) {}
      root.querySelectorAll('input').forEach(function (i) { i.checked = false; });
      root.querySelectorAll('textarea').forEach(function (t) { t.value = ''; });
      if (out) { out.hidden = true; out.textContent = ''; }
      paint();
      return;
    }
    var text = payload();
    var n = collect().length;
    if (act === 'download') {
      if (!n) { flash(btn, 'nothing picked yet'); return; }
      var blob = new Blob([text], { type: 'application/json' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'decision-log.json';
      document.body.appendChild(link);
      link.click();
      setTimeout(function () { URL.revokeObjectURL(link.href); link.remove(); }, 0);
      flash(btn, 'downloaded');
      return;
    }
    if (out) { out.hidden = false; out.textContent = text; }
    if (!n) { flash(btn, 'nothing picked yet'); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { flash(btn, 'copied — paste it into any session'); },
        function () { flash(btn, 'shown below — select and copy'); });
    } else {
      flash(btn, 'shown below — select and copy');
    }
  });
  panels().forEach(function (fs) {
    var v = store[fs.getAttribute('data-sg')];
    if (!v || typeof v !== 'object') return;
    if (typeof v.path === 'string' && /^(?:[A-Z]|HOLD)$/.test(v.path)) {
      var i = fs.querySelector('input[value="' + v.path + '"]');
      if (i) i.checked = true;
    }
    var t = fs.querySelector('textarea.dec-note');
    if (t && typeof v.note === 'string') t.value = v.note;
  });
  paint();
})();

// Shopfront pass (2026-11-17, arena/fd9778a1-zone1) — two presentation behaviours.
// Wide tables remain keyboard-scrollable without JavaScript. Dynamic edge hints and
// removing unnecessary tab stops on non-overflowing tables are progressive enhancements.
// These presentation behaviours make no network call or storage write. The separate
// measurement client has its own deployment and privacy gates; see measurement.html.
(function () {
  // Tell the reader a wide table continues past the right edge. The hint element
  // lives outside the scroller, so it stays put while the table moves.
  var wraps = Array.prototype.slice.call(document.querySelectorAll('.tablewrap'));
  function paint() {
    wraps.forEach(function (w) {
      var hint = w.nextElementSibling;
      var wide = w.scrollWidth - w.clientWidth > 4;
      w.tabIndex = wide ? 0 : -1;
      var caption = w.querySelector('caption');
      if (wide && caption) w.setAttribute('aria-label', caption.textContent + ' — scroll horizontally for more columns');
      if (!hint || !hint.classList.contains('tablewrap-hint')) return;
      var past = w.scrollWidth - w.clientWidth - w.scrollLeft;
      hint.classList.toggle('show', w.scrollWidth - w.clientWidth > 4 && past > 4);
    });
  }
  if (wraps.length) {
    wraps.forEach(function (w) { w.addEventListener('scroll', paint, { passive: true }); });
    window.addEventListener('resize', paint);
    paint();
  }

})();

(function () {
  var controls = document.querySelector('[data-format-controls]');
  if (!controls) return;
  var cards = Array.from(document.querySelectorAll('.publication-product[data-format]'));
  var status = document.querySelector('[data-format-status]');
  if (!cards.length) return;
  controls.hidden = false;
  controls.addEventListener('click', function (ev) {
    var button = ev.target.closest('[data-format-filter]');
    if (!button) return;
    var filter = button.getAttribute('data-format-filter');
    controls.querySelectorAll('button').forEach(function (item) {
      item.setAttribute('aria-pressed', item === button ? 'true' : 'false');
    });
    var shown = 0;
    cards.forEach(function (card) {
      card.hidden = filter !== 'all' && card.getAttribute('data-format') !== filter;
      if (!card.hidden) shown += 1;
    });
    if (status) status.textContent = shown + (shown === 1 ? ' format shown.' : ' formats shown.');
  });
})();

(function () {
  var toolbar = document.querySelector('[data-suggestion-toolbar]');
  if (!toolbar) return;
  var field = toolbar.querySelector('input');
  var status = toolbar.querySelector('output');
  var cards = Array.from(document.querySelectorAll('[data-suggestion]'));
  toolbar.hidden = false;
  function filter() {
    var query = field.value.trim().toLocaleLowerCase();
    var visible = 0;
    cards.forEach(function (card) {
      card.hidden = query !== '' && card.textContent.toLocaleLowerCase().indexOf(query) === -1;
      if (!card.hidden) visible += 1;
    });
    status.textContent = visible + ' of ' + cards.length + ' detailed suggestions shown';
  }
  field.addEventListener('input', filter); filter();
  // Following an ID anchor should always reveal the target, even after a search.
  function revealAnchor() {
    var target = document.getElementById(location.hash.slice(1));
    if (target && target.hasAttribute('data-suggestion')) {
      if (target.hidden) { field.value = ''; filter(); }
      var detail = target.matches('details') ? target : target.querySelector('details');
      if (detail) detail.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener('hashchange', revealAnchor); revealAnchor();
})();

/* Decision-review queue (decision-review.html, added 2026-11-19).
   Browser-only, like the decision log above: a pick is kept in localStorage so a
   reviewer can keep their place, and the export is a local file download. Nothing
   is submitted to any server from this static page. */
(function () {
  var rows = Array.from(document.querySelectorAll('[data-dr-priority]'));
  if (!rows.length) return;
  var KEY = 'zone1-decision-review-2026-11-19';
  var toolbar = document.querySelector('[data-dr-toolbar]');
  var actions = document.querySelector('.decision-actions');
  var counter = document.getElementById('dr-counter');
  var store = {};
  try { store = JSON.parse(window.localStorage.getItem(KEY) || '{}') || {}; } catch (err) { store = {}; }
  function persist() {
    try { window.localStorage.setItem(KEY, JSON.stringify(store)); } catch (err) {}
  }
  function paints() {
    var n = 0;
    Object.keys(store).forEach(function (id) {
      var entry = store[id];
      var choice = entry && typeof entry === 'object' ? entry.choice : entry;
      if (typeof choice !== 'string') return;
      var safe = choice.replace(/\\/g, '\\\\').replace(/"/g, '\\"');
      var input = document.querySelector('input[name="dr-' + id + '"][value="' + safe + '"]');
      if (input) input.checked = true;
      n += 1;
    });
    if (counter) counter.textContent = n + ' chosen in this browser';
  }
  document.addEventListener('change', function (ev) {
    var input = ev.target;
    if (!input || !input.getAttribute || !input.getAttribute('data-dr-id')) return;
    store[input.getAttribute('data-dr-id')] = { priority: '', choice: input.value };
    var row = input.closest('[data-dr-priority]');
    if (row) store[input.getAttribute('data-dr-id')].priority = row.getAttribute('data-dr-priority');
    persist(); paints();
  });
  function payload() {
    return JSON.stringify({ recorded: new Date().toISOString(), picks: store }, null, 2);
  }
  document.addEventListener('click', function (ev) {
    var btn = ev.target.closest ? ev.target.closest('[data-dr-action]') : null;
    if (!btn) return;
    var act = btn.getAttribute('data-dr-action');
    if (act === 'clear') {
      store = {};
      try { window.localStorage.removeItem(KEY); } catch (err) {}
      document.querySelectorAll('input[data-dr-id]').forEach(function (i) { i.checked = false; });
      persist(); paints(); return;
    }
    if (!Object.keys(store).length) { btn.textContent = 'nothing chosen yet'; setTimeout(function () { location.reload(); }, 900); return; }
    if (act === 'download') {
      var blob = new Blob([payload()], { type: 'application/json' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'decision-review.json';
      document.body.appendChild(link); link.click();
      setTimeout(function () { URL.revokeObjectURL(link.href); link.remove(); }, 0);
      return;
    }
    if (act === 'copy' && navigator.clipboard) { navigator.clipboard.writeText(payload()); }
  });
  if (toolbar) {
    var field = toolbar.querySelector('input');
    var status = toolbar.querySelector('output');
    toolbar.hidden = false;
    var filter = function () {
      var q = field.value.trim().toLocaleLowerCase();
      var visible = 0;
      rows.forEach(function (row) {
        row.hidden = q !== '' && row.textContent.toLocaleLowerCase().indexOf(q) === -1;
        if (!row.hidden) visible += 1;
      });
      status.textContent = visible + ' of ' + rows.length + ' decisions shown';
    };
    field.addEventListener('input', filter); filter();
  }
  if (actions) actions.hidden = false;
  document.querySelectorAll('input[data-dr-id]').forEach(function (i) { i.setAttribute('data-js-required', ''); });
  paints();
})();
