// Zone1 Kitchen: progressive reader controls and the local-only owner picker.
// No analytics or network requests; collection, if enabled, lives in analytics/client.js.
(function () {
  var menu = document.querySelector('.workspace-menu');
  if (!menu) return;
  document.addEventListener('click', function (ev) {
    if (menu.open && !menu.contains(ev.target)) menu.open = false;
  });
  document.addEventListener('keydown', function (ev) {
    if (ev.key === 'Escape' && menu.open) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });
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

// A failed clipboard request must not pretend that anything was copied.
document.addEventListener('click', function (ev) {
  var button = ev.target.closest('.copylink');
  if (!button) return;
  var link = button.getAttribute('data-link') || location.href;
  function feedback(ok) {
    var label = button.textContent;
    button.textContent = ok ? 'Copied' : 'Copy blocked — use the address bar';
    setTimeout(function () { button.textContent = label; }, 2200);
  }
  function fallback() {
    var area = document.createElement('textarea');
    area.value = link;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed'; area.style.opacity = '0';
    document.body.appendChild(area); area.select();
    var copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { /* Explain failure below. */ }
    area.remove(); feedback(copied); button.focus();
  }
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(link).then(function () { feedback(true); }, fallback);
  } else { fallback(); }
});

// revenue scenario calculator — arithmetic on two published inputs only
(function () {
  var form = document.getElementById('calc');
  if (!form) return;
  function num(id) {
    var field = document.getElementById(id);
    return field.value.trim() === '' || !field.checkValidity() ? NaN : Number(field.value);
  }
  function run() {
    var price = num('price'), rate = num('rate') / 100,
        conv = num('conv') / 100, clicks = num('clicks');
    if (![price, rate, conv, clicks].every(Number.isFinite)) {
      ['out-commission', 'out-sales', 'out-revenue', 'out-epc'].forEach(function (id) {
        document.getElementById(id).textContent = '—';
      });
      return;
    }
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
      var i = Array.from(fs.querySelectorAll('input')).find(function (input) { return input.value === v.path; });
      if (i) i.checked = true;
    }
    var t = fs.querySelector('textarea.dec-note');
    if (t && typeof v.note === 'string') t.value = v.note;
  });
  paint();
})();

// Shopfront pass (2026-11-17, arena/fd9778a1-zone1) — two presentation behaviours.
// Both are progressive: with JavaScript off the tables still scroll (the fade is the
// only thing missing), the comparison bar stays visible, and no content is hidden.
// These display controls make no network requests and store nothing. The owner
// picker above is explicitly local-only; analytics is a separate, gated client.
(function () {
  // Tell the reader a wide table continues past the right edge. The hint element
  // lives outside the scroller, so it stays put while the table moves.
  var wraps = Array.prototype.slice.call(document.querySelectorAll('.tablewrap'));
  function paint() {
    wraps.forEach(function (wrap) {
      var wide = wrap.scrollWidth - wrap.clientWidth > 4;
      var hint = wrap.nextElementSibling;
      if (!hint || !hint.classList.contains('tablewrap-hint')) {
        hint = document.createElement('p');
        hint.className = 'tablewrap-hint';
        hint.textContent = 'Scroll the table sideways to see every column →';
        wrap.insertAdjacentElement('afterend', hint);
      }
      hint.classList.toggle('show', wide && wrap.scrollWidth - wrap.clientWidth - wrap.scrollLeft > 4);
      if (wide) {
        wrap.tabIndex = 0;
        wrap.setAttribute('role', 'region');
        var caption = wrap.querySelector('caption');
        wrap.setAttribute('aria-label', caption ? caption.textContent : 'Scrollable data table');
      } else {
        wrap.removeAttribute('tabindex'); wrap.removeAttribute('role'); wrap.removeAttribute('aria-label');
      }
    });
  }
  if (wraps.length) {
    wraps.forEach(function (wrap) { wrap.addEventListener('scroll', paint, { passive: true }); });
    window.addEventListener('resize', paint);
    document.addEventListener('toggle', paint, true);
    if ('ResizeObserver' in window) {
      var observer = new ResizeObserver(paint); wraps.forEach(function (wrap) { observer.observe(wrap); });
    }
    if (document.fonts) document.fonts.ready.then(paint);
    paint();
  }

  // Step the sticky bar out of the way once the footer is on screen, so it never
  // covers the disclosure text or the source list.
  var bar = document.querySelector('.shopbar');
  var foot = document.querySelector('footer.site');
  if (bar && foot && 'IntersectionObserver' in window) {
    var footerVisible = false;
    var hero = document.querySelector('.publication-hero');
    var heroVisible = Boolean(hero);
    function barState() { bar.classList.toggle('hide', footerVisible || heroVisible); }
    new IntersectionObserver(function (entries) {
      footerVisible = entries[0].isIntersecting; barState();
    }, { rootMargin: '0px 0px -8px 0px' }).observe(foot);
    if (hero) {
      new IntersectionObserver(function (entries) {
        heroVisible = entries[0].isIntersecting; barState();
      }).observe(hero);
    }
    barState();
  }
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
      var detail = target.querySelector('details');
      if (detail) detail.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener('hashchange', revealAnchor); revealAnchor();
})();
