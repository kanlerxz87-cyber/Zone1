
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
    navigator.clipboard.writeText(link).then(done, done);
  } else {
    var ta = document.createElement('textarea');
    ta.value = link; document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    document.body.removeChild(ta); done();
  }
});

document.addEventListener('click', function (ev) {
  var t = ev.target.closest('.navtoggle');
  if (!t) return;
  var nav = document.getElementById(t.getAttribute('aria-controls'));
  if (!nav) return;
  var open = nav.classList.toggle('open');
  t.setAttribute('aria-expanded', open ? 'true' : 'false');
});

// revenue scenario calculator — arithmetic on two published inputs only
(function () {
  var form = document.getElementById('calc');
  if (!form) return;
  var fields = ['profit', 'price', 'rate', 'conv'];
  function num(id, d) { var v = parseFloat(document.getElementById(id).value); return isFinite(v) ? v : d; }
  function run() {
    var price = num('price', 0), rate = num('rate', 0) / 100,
        conv = num('conv', 0) / 100, clicks = num('clicks', 0);
    var commission = price * rate;
    var sales = clicks * conv;
    var revenue = sales * commission;
    document.getElementById('out-commission').textContent = '$' + commission.toFixed(2);
    document.getElementById('out-sales').textContent = sales.toFixed(1);
    document.getElementById('out-revenue').textContent = '$' + revenue.toFixed(2);
    document.getElementById('out-epc').textContent = '$' + (clicks > 0 ? revenue / clicks : 0).toFixed(3);
  }
  form.addEventListener('input', run);
  form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
  run();
})();

// Owner decision picker (2026-11-16, arena/ba29c641) — decision-log.html only.
// A static host has nowhere to POST a choice, so the picker keeps it in this browser and
// exports the exact JSON body of data/decision-log.json. Progressive: with JS off the page
// still reads end to end and every default is printed in the register table; only the
// picking needs the script. No dependency, no network call, nothing leaves the page.
(function () {
  var root = document.getElementById('decision-picker');
  if (!root) return;
  var KEY = 'zone1-decision-log-v1';
  var counter = document.getElementById('decision-counter');
  var out = document.getElementById('decision-output');
  var store = {};
  try { store = JSON.parse(window.localStorage.getItem(KEY) || '{}') || {}; } catch (err) { store = {}; }

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
      note: 'Merge choices[] into data/decision-log.json. A recorded choice outranks the default; a suggestion absent from this list keeps its default.'
    }, null, 1);
  }
  function paint() {
    if (!counter) return;
    var n = collect().length;
    counter.textContent = n + ' of ' + panels().length + ' picked in this browser' +
      (n ? ' — copy or download to hand it back' : ' — nothing picked yet');
  }
  function persist() {
    try { window.localStorage.setItem(KEY, JSON.stringify(store)); } catch (err) {}
  }
  function record(target) {
    var fs = target.closest ? target.closest('fieldset[data-sg]') : null;
    if (!fs) return null;
    var id = fs.getAttribute('data-sg');
    store[id] = { path: chosen(fs), note: note(fs) };
    persist();
    paint();
    return fs;
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
    if (act === 'download') {
      if (!collect().length) { flash(btn, 'nothing picked yet'); return; }
      var blob = new Blob([text], { type: 'application/json' });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'decision-log.json';
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
      flash(btn, 'downloaded');
      return;
    }
    if (out) { out.hidden = false; out.textContent = text; }
    if (!collect().length) { flash(btn, 'nothing picked yet'); return; }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { flash(btn, 'copied — paste it into any session'); },
                                                function () { flash(btn, 'shown below — select and copy'); });
    } else {
      flash(btn, 'shown below — select and copy');
    }
  });
  function flash(btn, msg) {
    var old = btn.textContent;
    btn.textContent = msg;
    setTimeout(function () { btn.textContent = old; }, 1800);
  }
  panels().forEach(function (fs) {
    var v = store[fs.getAttribute('data-sg')];
    if (!v) return;
    if (v.path) {
      var i = fs.querySelector('input[value="' + v.path + '"]');
      if (i) i.checked = true;
    }
    var t = fs.querySelector('textarea.dec-note');
    if (t && v.note) t.value = v.note;
  });
  paint();
})();
