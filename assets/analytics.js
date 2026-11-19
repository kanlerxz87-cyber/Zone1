/* Zone1 Kitchen: first-party aggregate events, disabled until deployment gates pass.
   Canonical schema: data/analytics-plan.json. No identifiers or browsing history.
   Failure to measure never changes a link or prevents a reader from leaving. */
(function () {
  "use strict";
  var script = document.currentScript;
  var root = document.body;
  if (!script || !root || root.getAttribute("data-analytics-eligible") !== "true") return;
  var rawEndpoint = script.getAttribute("data-endpoint") || "";
  if (!rawEndpoint || navigator.webdriver === true) return;
  var endpoint;
  try { endpoint = new URL(rawEndpoint, window.location.origin); } catch (_) { return; }
  if (endpoint.origin !== window.location.origin || endpoint.pathname !== "/api/analytics/events" ||
      endpoint.search || endpoint.hash || endpoint.username || endpoint.password) return;
  var wanted = (script.getAttribute("data-events") || "").split(",");
  var pageId = root.getAttribute("data-page-id");
  var pageType = root.getAttribute("data-page-type");
  if (!pageId) return;

  function optedOut() {
    return navigator.doNotTrack === "1" || window.doNotTrack === "1" ||
      navigator.globalPrivacyControl === true;
  }
  if (optedOut()) return;

  function send(event, fields) {
    if (optedOut() || wanted.indexOf(event) === -1) return;
    var payload = { event: event, page_id: pageId };
    if (fields && fields.target_id) payload.target_id = fields.target_id;
    if (fields && fields.bucket) payload.bucket = fields.bucket;
    try {
      window.fetch(endpoint.href, {
        method: "POST", mode: "same-origin", credentials: "omit",
        referrerPolicy: "no-referrer", keepalive: true,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      }).catch(function () { /* Measurement must never break navigation. */ });
    } catch (_) { /* Offline, unavailable, or blocked: do not retry or queue. */ }
  }

  var viewed = false;
  function pageView() {
    if (viewed || document.visibilityState !== "visible" || document.prerendering) return;
    viewed = true;
    send("page_view");
  }
  document.addEventListener("visibilitychange", pageView);
  document.addEventListener("prerenderingchange", pageView, { once: true });
  pageView();

  function activation(ev) {
    if (!ev.isTrusted || (ev.type === "click" ? ev.button !== 0 : ev.button !== 1)) return;
    var link = ev.target && ev.target.closest ? ev.target.closest("a[data-analytics-event]") : null;
    if (!link) return;
    var event = link.getAttribute("data-analytics-event");
    var target = link.getAttribute("data-analytics-target-id");
    if (!target) return;
    if (event === "outbound_click" || (event === "comparison_interaction" && pageId === "compare")) {
      send(event, { target_id: target });
    }
  }
  document.addEventListener("click", activation, { passive: true });
  document.addEventListener("auxclick", activation, { passive: true });

  // A single coarse engagement bucket, not a claim that an article was completed.
  if (pageType === "article" || pageType === "guide") {
    var activeTicks = 0;
    var timer = window.setInterval(function () {
      if (optedOut()) { window.clearInterval(timer); return; }
      if (document.visibilityState !== "visible" || document.prerendering || !document.hasFocus()) return;
      activeTicks += 1;
      if (activeTicks >= 60) {
        window.clearInterval(timer);
        send("article_engagement", { bucket: "60s" });
      }
    }, 1000);
    window.addEventListener("pagehide", function () { window.clearInterval(timer); }, { once: true });
  }
})();
