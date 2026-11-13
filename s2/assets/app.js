
/* Progressive enhancement only. The site is complete and readable with
   JavaScript disabled; this just makes the long tables searchable. */
(function () {
  if (!document.querySelector) return;
  var wraps = document.querySelectorAll('.tw');
  Array.prototype.forEach.call(wraps, function (wrap, i) {
    var table = wrap.querySelector('table');
    if (!table) return;
    var rows = table.querySelectorAll('tbody tr');
    if (rows.length < 6) return;
    var bar = document.createElement('div');
    bar.className = 'tools';
    var input = document.createElement('input');
    input.type = 'search';
    input.placeholder = 'Filter ' + rows.length + ' rows — try a rule id, a word, or "blank"';
    input.setAttribute('aria-label', 'Filter table');
    var count = document.createElement('span');
    count.className = 'note';
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.textContent = 'Unverified only';
    var onlyBlank = false;
    function apply() {
      var q = input.value.toLowerCase().trim();
      var shown = 0;
      Array.prototype.forEach.call(rows, function (tr) {
        var text = tr.textContent.toLowerCase();
        var hit = !q || text.indexOf(q) >= 0;
        if (onlyBlank) hit = hit && /blank|unverified|no source|needs review/.test(text);
        tr.hidden = !hit;
        if (hit) shown++;
      });
      count.textContent = shown + ' of ' + rows.length + ' rows';
    }
    btn.addEventListener('click', function () {
      onlyBlank = !onlyBlank;
      btn.classList.toggle('on', onlyBlank);
      btn.textContent = onlyBlank ? 'Showing unverified' : 'Unverified only';
      apply();
    });
    input.addEventListener('input', apply);
    bar.appendChild(input);
    bar.appendChild(btn);
    bar.appendChild(count);
    wrap.parentNode.insertBefore(bar, wrap);
    apply();
  });
})();
