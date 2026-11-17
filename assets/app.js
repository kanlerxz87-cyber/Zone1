
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
// A static host has nowhere to POST a choice, so the picker keeps it in this browser and exports
// the exact JSON body of data/decision-log.json. Progressive: with JS off the page still reads end
// to end, every default is printed in the register table, and only the picking needs the script.
// No dependency, no network call, nothing leaves the page.
(function () {
  var root = document.getElementById('decision-picker');
  if (!root) return;
  var KEY = 'zone1-***';
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
      note: 'Merge choices[] into data/decision-log.json. A recorded choice outranks the default; ' +
            'a suggestion absent from this list keeps its default.'
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

// Shopfront pass (2026-11-17, arena/fd9778a1-zone1) — two presentation behaviours.
// Both are progressive: with JavaScript off the tables still scroll (the fade is the
// only thing missing), the comparison bar stays visible, and no content is hidden.
// No network call, no storage, no measurement — this site records nothing (see the
// cookies notice in the footer and measurement.html).
(function () {
  // Tell the reader a wide table continues past the right edge. The hint element
  // lives outside the scroller, so it stays put while the table moves.
  var wraps = Array.prototype.slice.call(document.querySelectorAll('.tablewrap'));
  function paint() {
    wraps.forEach(function (w) {
      var hint = w.nextElementSibling;
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

  // Step the sticky bar out of the way once the footer is on screen, so it never
  // covers the disclosure text or the source list.
  var bar = document.querySelector('.shopbar');
  var foot = document.querySelector('footer.site');
  if (bar && foot && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { bar.classList.toggle('hide', en.isIntersecting); });
    }, { rootMargin: '0px 0px -8px 0px' }).observe(foot);
  }
})();
