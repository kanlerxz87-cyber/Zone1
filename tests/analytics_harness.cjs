/* Execute the actual generated-client source without a browser/network dependency.
   All events below are explicitly synthetic fixtures, never production measurements. */
const fs = require('node:fs');
const vm = require('node:vm');
const config = JSON.parse(process.argv[2] || '{}');
const source = fs.readFileSync('analytics/client.js', 'utf8');
const sent = [], listeners = {}, timers = [];
const attrs = {
  'data-enabled': config.disabled ? 'false' : 'true',
  'data-endpoint': config.endpoint || '/api/analytics/events',
  'data-events': 'page_view,outbound_click,article_engagement,comparison_interaction',
  'data-target-ids': 'chefman-6qt-dual-basket,PI-04,PI-05'
};
const body = {
  'data-page-id': config.page || 'index',
  'data-page-type': config.type || 'page',
  'data-analytics-eligible': config.ineligible ? 'false' : 'true'
};
const document = {
  currentScript: {getAttribute: key => attrs[key] || null},
  body: {getAttribute: key => body[key] || null},
  visibilityState: config.hidden ? 'hidden' : 'visible',
  hasFocus: () => !config.unfocused,
  addEventListener(name, callback) { (listeners[name] ||= []).push(callback); }
};
const navigator = {
  doNotTrack: config.dnt ? '1' : '0',
  globalPrivacyControl: Boolean(config.gpc)
};
const sandbox = {
  document, navigator, window: {addEventListener(name, callback) { (listeners[name] ||= []).push(callback); }},
  fetch(route, options) { sent.push({route, options, body: JSON.parse(options.body)}); return Promise.resolve({status: 202}); },
  setInterval(fn) { timers.push(fn); return timers.length; },
  clearInterval(id) { timers[id - 1] = null; }
};
vm.runInNewContext(source, sandbox);
function fire(name, event) { (listeners[name] || []).forEach(fn => fn(event)); }
function click(name, targetId, trusted = true, button = 0, eventType = 'click') {
  const link = {getAttribute: key => ({'data-analytics-event': name, 'data-analytics-target-id': targetId})[key]};
  fire(eventType, {type: eventType, isTrusted: trusted, button, target: {closest: () => link}});
}
(config.actions || []).forEach(action => {
  if (action.kind === 'click') click(action.event || 'outbound_click', action.target || 'chefman-6qt-dual-basket', action.trusted !== false, action.button || 0, action.eventType || 'click');
  if (action.kind === 'visible') { document.visibilityState = action.value ? 'visible' : 'hidden'; fire('visibilitychange'); }
  if (action.kind === 'focus') config.unfocused = !action.value;
  if (action.kind === 'ticks') for (let i = 0; i < action.count; i++) timers.slice().forEach(fn => fn && fn());
});
process.stdout.write(JSON.stringify(sent));
