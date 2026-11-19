/* Zone1 Kitchen — first-party aggregate measurement, contract v2.
   Source for assets/analytics.js. Disabled without a verified same-origin endpoint.
   No cookies, storage, reader IDs, destination URLs or query parameters. */
(function () {
  "use strict";
  var script = document.currentScript;
  if (!script || script.getAttribute("data-enabled") !== "true") return;
  if (navigator.doNotTrack === "1" || window.doNotTrack === "1" ||
      navigator.globalPrivacyControl === true) return;

  var route = script.getAttribute("data-endpoint") || "";
  // Deliberately same-origin. An external URL, even HTTPS, is not this contract.
  if (route !== "/api/analytics/events") return;
  var page = document.body.getAttribute("data-page-id");
  if (!page) return;
  var wanted = (script.getAttribute("data-events") || "").split(",");
  var targets = (script.getAttribute("data-target-ids") || "").split(",");

  function send(event, extra) {
    if (wanted.indexOf(event) === -1) return;
    if (navigator.globalPrivacyControl === true || navigator.doNotTrack === "1") return;
    var body = { event: event, page_id: page };
    if (extra) Object.keys(extra).forEach(function (key) { body[key] = extra[key]; });
    // fetch can omit credentials and the Referer; sendBeacon cannot guarantee that.
    // Never wait for a result or change a reader's navigation.
    try {
      fetch(route, {
        method: "POST", mode: "same-origin", credentials: "omit",
        referrerPolicy: "no-referrer", keepalive: true, cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      }).catch(function () {});
    } catch (ignored) { /* measurement must never break the publication */ }
  }

  var viewed = false;
  function pageView() {
    if (viewed || document.visibilityState !== "visible") return;
    viewed = true;
    send("page_view");
  }
  pageView();
  document.addEventListener("visibilitychange", pageView);

  function activation(ev) {
    if (!ev.isTrusted) return;
    if (ev.type === "click" && ev.button !== 0) return;
    if (ev.type === "auxclick" && ev.button !== 1) return;
    var link = ev.target.closest ? ev.target.closest("a[data-analytics-event]") : null;
    if (!link) return;
    var event = link.getAttribute("data-analytics-event");
    var target = link.getAttribute("data-analytics-target-id") || "";
    if (targets.indexOf(target) === -1) return;
    if (event === "outbound_click") send(event, { target_id: target });
    if (event === "comparison_interaction" && page === "compare") {
      send(event, { target_id: target });
    }
  }
  document.addEventListener("click", activation, { passive: true });
  document.addEventListener("auxclick", activation, { passive: true });

  // A coarse 60-second active-reading bucket, not a claim that a guide was finished.
  var type = document.body.getAttribute("data-page-type");
  if ((type === "article" || type === "guide") && wanted.indexOf("article_engagement") !== -1) {
    var activeTicks = 0;
    var timer = setInterval(function () {
      if (document.visibilityState !== "visible" || !document.hasFocus()) return;
      activeTicks += 1;
      if (activeTicks >= 60) {
        clearInterval(timer);
        send("article_engagement", { bucket: "60s" });
      }
    }, 1000);
  }
})();
