import re, sys, pathlib

p = pathlib.Path('build.py')
s = p.read_text(encoding='utf-8')
orig = s


def sub(old, new, label, count=1):
    global s
    if s.count(old) != count:
        print(f'!! MISS [{label}] expected {count} got {s.count(old)}')
        sys.exit(1)
    s = s.replace(old, new, count)
    print(f'ok [{label}]')


# ================================================================ CSS (additive block)
CSS_ADD = '''
/* ---- pass 13 (2026-11-17, arena/3093e674-zone1): the buy block, the link record, the
   local ledger. Additive only - every value here reuses the shipped palette's own
   variables, so a change to the brand tokens moves these with it instead of forking. */
.btn-sm{padding:.42rem .7rem; font-size:.86rem; border-radius:8px; white-space:nowrap}
.affiliate-tag{display:inline-block; margin-left:.4rem; font-size:.7rem; text-transform:uppercase;
  letter-spacing:.06em; color:var(--muted, #66707a); border:1px solid rgba(0,0,0,.12);
  border-radius:999px; padding:.08rem .4rem; vertical-align:middle}
.cta-alt{display:inline-block; margin:.15rem 0 .1rem; font-size:.92rem}
.cta-row .tiny.muted{flex:1 1 14rem; min-width:12rem}
.li-cell-blank{color:var(--muted, #66707a); font-style:italic}
.ledger-panel{border:1px solid rgba(0,0,0,.1); border-radius:12px; padding:.9rem 1rem;
  background:rgba(36,87,70,.045); margin:1rem 0}
.ledger-panel h3{margin:.2rem 0 .5rem}
.ledger-panel table{margin:.4rem 0}
.ledger-panel .z1k-actions{display:flex; flex-wrap:wrap; gap:.5rem; margin-top:.7rem}
.ledger-panel button{font:inherit; font-size:.85rem; padding:.34rem .7rem; border-radius:8px;
  border:1px solid rgba(0,0,0,.18); background:#fff; cursor:pointer}
.ledger-panel button:hover{border-color:var(--brand, #245746); color:var(--brand, #245746)}
.ledger-empty{font-size:.9rem; color:var(--muted, #66707a); margin:.2rem 0 0}
'''
sub('''CSS = r"""''', '''CSS = r"""''', 'css-anchor-check')
i = s.index('CSS = r"""')
j = s.index('\n"""', i)
s = s[:j] + "\n" + CSS_ADD.rstrip("\n") + s[j:]
print('ok [css-append]')

# ================================================================ JS (on-device ledger)
JS_ADD = r'''
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
'''
i = s.index('JS = r"""')
j = s.index('\n"""', i)
s = s[:j] + "\n" + JS_ADD.rstrip("\n") + s[j:]
print('ok [js-append]')

# mark the CTA rows so EVT-2 can fire, in both the full block and the compact one
sub('''  <a class="btn" href="{e(url)}" target="_blank" rel="nofollow sponsored noopener" data-z1k="outlink" data-asin="{e(p['asin']['v'])}">See this model on Amazon <span aria-hidden="true">↗</span></a>''',
    '''  <div class="cta-block" data-z1k="cta" data-asin="{e(p['asin']['v'])}"><a class="btn" href="{e(url)}" target="_blank" rel="nofollow sponsored noopener" data-z1k="outlink" data-tagged="{e('1' if state != 'untagged' else '')}" data-asin="{e(p['asin']['v'])}">See this model on Amazon <span aria-hidden="true">↗</span></a></div>''',
    'cta-block-mark')
sub('''    return (f'<a class="btn btn-sm" href="{e(url)}" target="_blank" rel="nofollow sponsored noopener" '
            f'data-z1k="outlink" data-asin="{e(p["asin"]["v"])}">{e(label)} <span aria-hidden="true">↗</span></a>'
            f'<span class="tiny muted affiliate-tag">Affiliate link</span>')''',
    '''    return (f'<span data-z1k="cta" data-asin="{e(p["asin"]["v"])}">'
            f'<a class="btn btn-sm" href="{e(url)}" target="_blank" rel="nofollow sponsored noopener" '
            f'data-z1k="outlink" data-tagged="{e("1" if state != "untagged" else "")}" '
            f'data-asin="{e(p["asin"]["v"])}">{e(label)} <span aria-hidden="true">↗</span></a></span>'
            f'<span class="tiny muted affiliate-tag">Affiliate link</span>')''',
    'cta-inline-mark')

p.write_text(s, encoding='utf-8')
print('patch 3 done:', len(orig), '->', len(s))
