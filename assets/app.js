
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
