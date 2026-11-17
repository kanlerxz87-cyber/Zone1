/*
 * Zone1 first-party aggregate event client.
 * Loaded only when data/analytics-plan.json explicitly enables collection. The current
 * build leaves it out: GitHub Pages has no deployed collector, and no visitor data is sent.
 * No cookies, local storage, IDs, referrer, query string, or destination URL are read.
 */
(function () {
  'use strict';
  var script = document.currentScript;
  if (!script || !document.body) return;

  var endpoint = script.getAttribute('data-endpoint') || '';
  var pageId = document.body.getAttribute('data-page-id') || '';
  var pageType = document.body.getAttribute('data-page-type') || '';
  if (!endpoint || !pageId) return;

  var url;
  try {
    url = new URL(endpoint, window.location.href);
  } catch (err) {
    return;
  }
  if (url.origin !== window.location.origin) return;

  function optedOut() {
    return navigator.doNotTrack === '1' || window.doNotTrack === '1' ||
      navigator.globalPrivacyControl === true;
  }

  function send(name, extra) {
    if (optedOut()) return;
    var payload = { event: name, page_id: pageId };
    if (extra && extra.target_id) payload.target_id = extra.target_id;
    if (extra && extra.bucket) payload.bucket = extra.bucket;
    try {
      fetch(url.href, {
        method: 'POST',
        mode: 'same-origin',
        credentials: 'omit',
        referrerPolicy: 'no-referrer',
        cache: 'no-store',
        keepalive: true,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(function () {});
    } catch (err) {
      // A blocked or unavailable collector must never interrupt the reader's page.
    }
  }

  send('page_view');

  document.addEventListener('click', function (event) {
    var node = event.target;
    var link = node && node.closest ? node.closest('a[data-analytics-event]') : null;
    if (!link) return;
    var name = link.getAttribute('data-analytics-event');
    if (name === 'outbound_click') {
      send(name, { target_id: link.getAttribute('data-analytics-target-id') || '' });
    } else if (name === 'comparison_interaction') {
      send(name, { target_id: link.getAttribute('data-analytics-target-id') || '' });
    }
  }, { capture: true, passive: true });

  if (pageType === 'article' || pageType === 'guide') {
    var activeSeconds = 0;
    var sent = false;
    window.setInterval(function () {
      if (sent || optedOut()) return;
      if (document.visibilityState === 'visible' && document.hasFocus()) activeSeconds += 1;
      if (activeSeconds >= 60) {
        sent = true;
        send('article_engagement', { bucket: '60s' });
      }
    }, 1000);
  }
})();
