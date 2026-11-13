/* Zone1 click & conversion tracker (client-side demo layer).
   Records clicks on .aff-link elements and manual conversions in localStorage.
   Production note: a static host cannot attribute Amazon conversions — Amazon
   Associates reports remain the source of truth for conversions/commissions. */
(function () {
  var CLICK_KEY = "zone1_clicks";
  var CONV_KEY = "zone1_convs";

  function read(key) {
    try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) { return []; }
  }
  function write(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* private mode */ }
  }

  window.Zone1Tracker = {
    clicks: function () { return read(CLICK_KEY); },
    convs: function () { return read(CONV_KEY); },
    recordClick: function (linkId, target) {
      var c = read(CLICK_KEY);
      c.push({ id: linkId, target: target, t: new Date().toISOString() });
      write(CLICK_KEY, c);
      return c;
    },
    recordConversion: function (linkId, note) {
      var v = read(CONV_KEY);
      v.push({ id: linkId, note: note || "", t: new Date().toISOString() });
      write(CONV_KEY, v);
      return v;
    },
    reset: function () {
      write(CLICK_KEY, []); write(CONV_KEY, []);
    },
    exportAll: function () {
      return JSON.stringify({ clicks: read(CLICK_KEY), conversions: read(CONV_KEY) }, null, 2);
    }
  };

  document.addEventListener("click", function (e) {
    var el = e.target.closest ? e.target.closest(".aff-link") : null;
    if (!el) return;
    var id = el.getAttribute("data-aff") || "unassigned";
    window.Zone1Tracker.recordClick(id, el.getAttribute("href") || el.getAttribute("data-target") || "");
    var toast = document.getElementById("tracker-toast");
    if (toast) {
      toast.textContent = "Click recorded for “" + id + "” (local demo tracker).";
      toast.hidden = false;
      clearTimeout(window.__zone1Toast);
      window.__zone1Toast = setTimeout(function () { toast.hidden = true; }, 2600);
    }
  });
})();
