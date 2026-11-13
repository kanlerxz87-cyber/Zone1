/* Zone1 — site behaviours. No dependencies. */
(function () {
  'use strict';

  /* Mobile navigation */
  var menuBtn = document.querySelector('.menu-btn');
  if (menuBtn) {
    menuBtn.addEventListener('click', function () {
      document.body.classList.toggle('nav-open');
      menuBtn.textContent = document.body.classList.contains('nav-open') ? 'Close' : 'Menu';
    });
  }

  /* Copy affiliate link template */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.linkbox .copy');
    if (!btn) return;
    var box = btn.closest('.linkbox');
    var text = box.getAttribute('data-copy') || box.querySelector('.url').textContent.trim();
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { window.prompt('Copy the link:', text); });
    } else {
      window.prompt('Copy the link:', text);
    }
  });

  /* Table filtering — filter any table.data that follows a [data-filter-for] input */
  document.addEventListener('input', function (e) {
    var input = e.target.closest('[data-filter-for]');
    if (!input) return;
    var table = document.getElementById(input.getAttribute('data-filter-for'));
    if (!table) return;
    var q = input.value.toLowerCase().trim();
    Array.prototype.forEach.call(table.tBodies[0].rows, function (row) {
      var hit = !q || row.textContent.toLowerCase().indexOf(q) !== -1;
      row.style.display = hit ? '' : 'none';
    });
  });

  /* Filter chips — filter rows by data-tag */
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.chip[data-filter-table]');
    if (!chip) return;
    var table = document.getElementById(chip.getAttribute('data-filter-table'));
    if (!table) return;
    var tag = chip.getAttribute('data-tag') || '';
    var group = chip.getAttribute('data-filter-group');
    Array.prototype.forEach.call(document.querySelectorAll('.chip[data-filter-group="' + group + '"]'), function (c) {
      c.classList.remove('active');
    });
    chip.classList.add('active');
    Array.prototype.forEach.call(table.tBodies[0].rows, function (row) {
      var hit = tag === '' || (row.getAttribute('data-tags') || '').indexOf(tag) !== -1;
      row.style.display = hit ? '' : 'none';
    });
  });

  /* Mark the current page in the sidebar */
  var here = location.pathname.split('/').pop() || 'index.html';
  Array.prototype.forEach.call(document.querySelectorAll('.nav-group a'), function (a) {
    var href = a.getAttribute('href') || '';
    var target = href.split('/').pop();
    if (target === here) a.classList.add('active');
  });
})();
