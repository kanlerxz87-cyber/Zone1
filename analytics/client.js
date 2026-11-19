/* Zone1 Kitchen: first-party aggregate events, v2.
   No request until a deployment is explicitly enabled by build.py.
   No beacon API: fetch with credentials omitted avoids sending cookies. */
(function () {
  "use strict";
  var script = document.currentScript;
  if (!script) { return; }
  var rawEndpoint = script.getAttribute("data-endpoint") || "";
  if (!rawEndpoint) { return; }
  var endpoint;
  try {
    endpoint = new URL(rawEndpoint, window.location.href);
    if (endpoint.origin !== window.location.origin || endpoint.protocol !== "https:" ||
        endpoint.pathname !== "/api/analytics/events" || endpoint.username || endpoint.password ||
        endpoint.search || endpoint.hash) { return; }
  } catch (err) { return; }
  function optedOut() {
    return navigator.doNotTrack === "1" || window.doNotTrack === "1" ||
           navigator.globalPrivacyControl === true;
  }
  if (optedOut()) { return; }
  var page = document.body.getAttribute("data-page-id");
  var type = document.body.getAttribute("data-page-type");
  if (!page || script.getAttribute("data-collection") !== "enabled") { return; }

  function send(name, extra) {
    if (optedOut()) { return; }
    var body = { event: name, page_id: page };
    if (extra) {
      Object.keys(extra).forEach(function (key) { body[key] = extra[key]; });
    }
    try {
      fetch(endpoint.href, {
        method: "POST", mode: "same-origin", credentials: "omit",
        keepalive: true, referrerPolicy: "no-referrer",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify(body)
      }).catch(function () { /* Measurement must not interrupt navigation. */ });
    } catch (err) { /* Measurement must not interrupt navigation. */ }
  }

  // EV-01. Page loads are counts, not unique people or sessions.
  if (document.visibilityState === "visible") {
    send("page_view");
  } else {
    var firstVisible = function () {
      if (document.visibilityState === "visible") {
        send("page_view");
        document.removeEventListener("visibilitychange", firstVisible);
      }
    };
    document.addEventListener("visibilitychange", firstVisible);
  }

  // EV-02 / EV-04. Observe real activations; never wrap, delay or redirect a link.
  function activation(ev) {
    if (!ev.isTrusted || (ev.type === "click" && ev.button !== 0) ||
        (ev.type === "auxclick" && ev.button !== 1)) { return; }
    var anchor = ev.target.closest ? ev.target.closest("a[data-analytics-target-id]") : null;
    if (!anchor) { return; }
    var id = anchor.getAttribute("data-analytics-target-id");
    var url;
    try { url = new URL(anchor.href, window.location.href); } catch (err) { return; }
    if (anchor.getAttribute("data-analytics-event") === "outbound_click" &&
        url.protocol === "https:" &&
        ["link.amazon", "www.amazon.com", "amazon.com"].indexOf(url.hostname) !== -1) {
      send("outbound_click", { target_id: id });
    } else if (page === "compare" &&
               anchor.getAttribute("data-analytics-event") === "comparison_interaction" &&
               url.origin === window.location.origin &&
               url.pathname.endsWith("/products/" + id + ".html")) {
      send("comparison_interaction", { target_id: id });
    }
  }
  document.addEventListener("click", activation, { passive: true });
  document.addEventListener("auxclick", activation, { passive: true });

  // EV-03. Once per document after 60 visible, focused seconds. No scroll trace,
  // exact duration or cross-page identity is transmitted. A timer is kept in memory.
  if (type === "article" || type === "guide") {
    var elapsed = 0;
    var last = performance.now();
    var timer = setInterval(function () {
      var now = performance.now();
      if (document.visibilityState === "visible" && document.hasFocus()) {
        elapsed += Math.min(now - last, 2000);
      }
      last = now;
      if (elapsed >= 60000) {
        send("article_engagement", { bucket: "60s" });
        clearInterval(timer);
      }
    }, 1000);
  }
  // EV-05 is NEVER a browser event. Use analytics/report_import.py with a dated,
  // authorized first-party aggregate report; clicks cannot establish an order.
})();
