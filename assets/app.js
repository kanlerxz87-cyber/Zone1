
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

// Pass 13 (2026-11-17, arena/3093e674-zone1): the five defined events, counted on the reader's
// own device. The contract is deliberately small and it is checked by the build
// (check_measurement_contract): no network call of any kind, no cookie, no generated identifier,
// and the whole ledger is one key in this browser's localStorage. data/measurement.json is the
// specification; this is its only implementation. With JavaScript disabled nothing is counted and
// measurement.html still reads end to end, which is the point of putting the viewer on its own page
// rather than in a banner on somebody's buying decision.
(function () {
  var KEY = 'z1k.ledger.v1';
  var MAX = 500;            // ring buffer: the newest MAX records on the device, nothing more
  var panel = document.getElementById('z1k-panel');
  var isOutboundAmazon = function (host) {
    return /(^|\.)amazon\.(com|co\.uk|de|fr|ca|co\.jp|in|com\.au|sg|com\.br|ca)$/i.test(host || '');
  };
  function read() {
    try { return JSON.parse(window.localStorage.getItem(KEY) || '{"events":[]}') || {events: []}; }
    catch (err) { return {events: []}; }
  }
  function write(b) {
    try { window.localStorage.setItem(KEY, JSON.stringify(b)); } catch (err) { /* private mode: no-op */ }
  }
  function push(name, data) {
    var b = read();
    b.events.push({t: name, at: new Date().toISOString(), p: location.pathname.split('/').pop() || 'index.html', d: data || {}});
    if (b.events.length > MAX) b.events = b.events.slice(b.events.length - MAX);
    write(b);
    return b;
  }
  function totals(b) {
    var t = {outbound_click: 0, cta_impression: 0, article_read: 0, no_click_exit: 0, link_health_failure: 0};
    var byPage = {};
    (b.events || []).forEach(function (ev) {
      if (t[ev.t] === undefined) return;
      t[ev.t] += 1;
      byPage[ev.p] = byPage[ev.p] || {};
      byPage[ev.p][ev.t] = (byPage[ev.p][ev.t] || 0) + 1;
    });
    return {t: t, byPage: byPage};
  }
  function esc(v) {
    return String(v).replace(/[&<>"]/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c];
    });
  }
  function render() {
    if (!panel) return;
    var b = read(), tt = totals(b), rows = '';
    Object.keys(tt.byPage).sort().forEach(function (page) {
      var c = tt.byPage[page];
      rows += '<tr><td><code>' + esc(page) + '</code></td><td>' + (c.outbound_click || 0) + '</td><td>' +
              (c.cta_impression || 0) + '</td><td>' + (c.article_read || 0) + '</td><td>' +
              (c.no_click_exit || 0) + '</td><td>' + (c.link_health_failure || 0) + '</td></tr>';
    });
    var total = (b.events || []).length;
    panel.innerHTML =
      '<h3>' + (total ? total + ' event' + (total === 1 ? '' : 's') + ' on this device' : 'Nothing counted on this device yet') + '</h3>' +
      (total
        ? '<div class="tablewrap"><table><caption>Local ledger, newest ' + Math.min(total, MAX) + ' records only</caption>' +
          '<thead><tr><th>Page</th><th>Outbound clicks</th><th>CTA impressions</th><th>Reads</th>' +
          '<th>No-click exits</th><th>Link faults</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
          '<div class="z1k-actions"><button type="button" class="z1k-export">Copy this device\u2019s JSON</button>' +
          '<button type="button" class="z1k-reset">Erase this device\u2019s ledger</button></div>' +
          '<p class="tiny muted">Latest record: ' + esc((b.events[b.events.length - 1] || {}).at || '') + '. ' +
          'Nothing here leaves your browser, so nothing here is a site-wide number.</p>'
        : '<p class="ledger-empty">Zero events stored. The counter only records an outbound click, a CTA in view, ' +
          'a scroll past 75% of an article, a no-click exit or a link fault - all of them on this device.</p>');
    var ex = panel.querySelector('.z1k-export');
    if (ex) ex.addEventListener('click', function () {
      var txt = JSON.stringify({site: 'zone1-kitchen', schema: '1', exported_at: new Date().toISOString(),
                                events: b.events}, null, 1);
      var done = function () { ex.textContent = 'Copied'; setTimeout(function () { ex.textContent = 'Copy this device\u2019s JSON'; }, 1800); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, done);
      else done();
    });
    var rs = panel.querySelector('.z1k-reset');
    if (rs) rs.addEventListener('click', function () {
      try { window.localStorage.removeItem(KEY); } catch (err) {}
      render();
    });
  }
  // EVT-1, and the EVT-5 audit of the link that was just clicked.
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest && ev.target.closest('a[href]');
    if (!a) return;
    var host = a.host || '';
    if (!isOutboundAmazon(host)) return;
    var href = a.getAttribute('href') || '';
    var asin = (href.match(/\/dp\/([A-Z0-9]{10})/) || [])[1] || '';
    var tagged = /(^|[?&])tag=/.test(href) || !!a.getAttribute('data-tagged');
    push('outbound_click', {asin: asin, tagged: tagged, kind: a.getAttribute('data-z1k') || 'link'});
    if (a.getAttribute('data-z1k') === 'outlink' && !tagged) {
      push('link_health_failure', {reason: 'a product CTA reached a reader without the configured tag', href: href.slice(0, 120)});
    }
    render();
  }, true);
  // EVT-2 and EVT-3: what a reader actually saw, not what a page served.
  var seen = {}, t0 = Date.now();
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, k = el.getAttribute('data-z1k');
        if (k === 'cta' && !seen['cta:' + location.pathname]) {
          seen['cta:' + location.pathname] = 1;
          push('cta_impression', {product: el.getAttribute('data-asin') || ''});
          io.unobserve(el);
          render();
        }
      });
    }, {threshold: 0.5});
    document.querySelectorAll('[data-z1k="cta"]').forEach(function (el) { io.observe(el); });
  }
  function depth() {
    var de = document.documentElement;
    var scrolled = (window.scrollY || de.scrollTop) + window.innerHeight;
    var full = de.scrollHeight || 1;
    if (scrolled / full >= 0.75) {
      var art = /\/articles\//.test(location.pathname);
      if (art && !seen['read:' + location.pathname]) {
        seen['read:' + location.pathname] = 1;
        push('article_read', {seconds: Math.round((Date.now() - t0) / 1000)});
        render();
      }
    }
  }
  document.addEventListener('scroll', depth, {passive: true});
  // EVT-4: the page a reader left without touching a buy link.
  function exitCheck() {
    if (!/\/(products|compare|picks)|buying-guide|^index\.html/.test(location.pathname)) return;
    var b = read();
    var mine = b.events.filter(function (e) { return e.p === (location.pathname.split('/').pop() || 'index.html'); });
    var clicked = mine.some(function (e) { return e.t === 'outbound_click'; });
    if (!clicked && !seen['exit:' + location.pathname]) {
      seen['exit:' + location.pathname] = 1;
      push('no_click_exit', {seconds: Math.round((Date.now() - t0) / 1000)});
      render();
    }
  }
  window.addEventListener('pagehide', exitCheck);
  render();
})();
