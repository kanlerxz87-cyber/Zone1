
/* Zone1 Kitchen - privacy-preserving outbound-click counter.
   Shipped by build.py. Behaviour is driven entirely by the data attributes on
   the script tag: with no data-endpoint the file does nothing at all.
   No cookie, no identifier, no IP, no user agent, no referrer. */
(function () {
  "use strict";

  var tag = document.currentScript;
  if (!tag) { return; }
  var endpoint = (tag.getAttribute("data-endpoint") || "").trim();
  if (!endpoint) { return; }                 // no sink -> the counter is inert
  var wanted = (tag.getAttribute("data-events") || "EV-01,EV-02,EV-03,EV-04")
                 .split(",").map(function (s) { return s.trim(); })
                 .filter(function (s) { return s.length > 0; });

  function enabled(id) { return wanted.indexOf(id) !== -1; }
  function utcDate() { return new Date().toISOString().slice(0, 10); }
  function slug() {
    var p = window.location.pathname;
    var i = p.indexOf("/Zone1/");
    if (i !== -1) { p = p.slice(i + 7); }
    return p.replace(/index\.html$/, "") || "index.html";
  }
  function asinFrom(href) {
    var m = /\/dp\/([A-Z0-9]{10})/.exec(href || "");
    return m ? m[1] : "";
  }
  function tagFrom(href) {
    var m = /[?&]tag=([^&]+)/.exec(href || "");
    return m ? decodeURIComponent(m[1]) : "";
  }

  // The whole payload. Five named fields, no more. If a field is not known it
  // is omitted rather than filled with a guess.
  function optedOut() {
    // Do Not Track / Global Privacy Control honoured (collector-plan client).
    return navigator.doNotTrack === "1" || window.doNotTrack === "1" ||
           navigator.globalPrivacyControl === true;
  }

  function send(id, extra) {
    if (!enabled(id)) { return; }
    if (optedOut()) { return; }
    var body = { event: id, page: slug(), date: utcDate() };
    if (extra) {
      for (var k in extra) {
        if (Object.prototype.hasOwnProperty.call(extra, k) && extra[k]) {
          body[k] = extra[k];
        }
      }
    }
    var payload = JSON.stringify(body);
    try {
      if (navigator.sendBeacon) {
        // text/plain keeps this a simple request: no CORS preflight, and the
        // body is never sent as a form post.
        var blob = new Blob([payload], { type: "text/plain;charset=UTF-8" });
        if (navigator.sendBeacon(endpoint, blob)) { return; }
      }
    } catch (err) { /* fall through to fetch */ }
    try {
      fetch(endpoint, {
        method: "POST",
        mode: "no-cors",
        keepalive: true,
        credentials: "omit",
        referrerPolicy: "no-referrer",
        headers: { "Content-Type": "text/plain;charset=UTF-8" },
        body: payload
      }).catch(function () { /* a lost beacon must never break the page */ });
    } catch (err) { /* ignore */ }
  }

  // EV-02: only a real click on an Amazon product link.
  document.addEventListener("click", function (ev) {
    if (!ev.isTrusted || ev.button !== 0) { return; }
    var el = ev.target;
    while (el && el !== document.body) {
      if (el.tagName === "A" && el.href) { break; }
      el = el.parentNode;
    }
    if (!el || el.tagName !== "A") { return; }
    var asin = asinFrom(el.href);
    if (!asin) { return; }
    send("EV-02", { asin: asin, tag: tagFrom(el.href) });
  }, { passive: true });

  // EV-01: one page view, on the pages the measurement spec names.
  var pageType = document.documentElement.getAttribute("data-zone1-page-type");
  if (pageType) {
    var q = window.location.search || "";
    var hasUtm = /(^|[?&])utm_(source|campaign)=/.test(q);
    send("EV-01", { page_type: pageType, utm: hasUtm ? "1" : "" });
  }

  // EV-03 and EV-04: an element becomes visible. Observed, not polled.
  if (typeof IntersectionObserver === "function") {
    var fired = {};
    var marks = document.querySelectorAll("[data-zone1-track]");
    for (var i = 0; i < marks.length; i++) {
      (function (node) {
        var kind = node.getAttribute("data-zone1-track");
        var obs = new IntersectionObserver(function (entries) {
          for (var j = 0; j < entries.length; j++) {
            if (entries[j].isIntersecting && !fired[kind]) {
              fired[kind] = true;
              send(kind, {});
              obs.disconnect();
            }
          }
        }, { threshold: 0.6 });
        obs.observe(node);
      })(marks[i]);
    }
  }
})();
