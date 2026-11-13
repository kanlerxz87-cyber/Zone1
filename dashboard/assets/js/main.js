/* Zone1 dashboard helpers: link builder + analytics rendering. */
(function () {
  // ---- Affiliate link builder (links.html) ----
  var buildBtn = document.getElementById("build-link-btn");
  if (buildBtn) {
    buildBtn.addEventListener("click", function () {
      var asin = (document.getElementById("builder-asin") || {}).value || "";
      var tag = (document.getElementById("builder-tag") || {}).value || "";
      asin = asin.trim().toUpperCase();
      tag = tag.trim();
      var out = document.getElementById("builder-out");
      var warn = document.getElementById("builder-warn");
      if (!out) return;
      var problems = [];
      if (!/^[A-Z0-9]{10}$/.test(asin)) problems.push("ASIN must be exactly 10 letters/digits (the supplied IDs are 9 and invalid).");
      if (!/^[A-Za-z0-9_-]{1,20}-2[0-9]$/.test(tag)) problems.push("Tracking tag should look like yourtag-20 (Associates tracking ID).");
      if (problems.length) {
        warn.innerHTML = problems.map(function (p) { return "⚠ " + p; }).join("<br>");
        warn.hidden = false;
        out.textContent = "";
      } else {
        warn.hidden = true;
        out.textContent = "https://www.amazon.com/dp/" + asin + "?tag=" + encodeURIComponent(tag);
      }
    });
    var copyBtn = document.getElementById("builder-copy");
    if (copyBtn) copyBtn.addEventListener("click", function () {
      var out = document.getElementById("builder-out");
      if (out && out.textContent) {
        navigator.clipboard && navigator.clipboard.writeText(out.textContent);
        copyBtn.textContent = "Copied";
        setTimeout(function () { copyBtn.textContent = "Copy"; }, 1500);
      }
    });
  }

  // ---- Analytics dashboard (analytics.html) ----
  var panel = document.getElementById("analytics-panel");
  if (panel && window.Zone1Tracker) {
    var render = function () {
      var clicks = window.Zone1Tracker.clicks();
      var convs = window.Zone1Tracker.convs();
      var byId = {};
      clicks.forEach(function (c) { byId[c.id] = byId[c.id] || { clicks: 0, convs: 0 }; byId[c.id].clicks++; });
      convs.forEach(function (v) { byId[v.id] = byId[v.id] || { clicks: 0, convs: 0 }; byId[v.id].convs++; });
      var ids = ["P1", "P2", "P3", "unassigned"].filter(function (i) { return byId[i]; });
      var rows = ids.map(function (i) {
        var d = byId[i];
        var rate = d.clicks ? Math.round((d.convs / d.clicks) * 100) : 0;
        return "<tr><td class='mono'>" + i + "</td><td>" + d.clicks + "</td><td>" + d.convs +
          "</td><td>" + rate + "%</td></tr>";
      }).join("");
      var last = clicks.slice(-8).reverse().map(function (c) {
        return "<tr><td class='mono'>" + c.id + "</td><td class='small'>" + new Date(c.t).toLocaleString() +
          "</td><td class='small mono'>" + (c.target || "").slice(0, 60) + "</td></tr>";
      }).join("");
      panel.innerHTML =
        "<div class='kpis'>" +
        "<div class='kpi'><div class='n'>" + clicks.length + "</div><div class='l'>Link clicks (this browser)</div></div>" +
        "<div class='kpi'><div class='n'>" + convs.length + "</div><div class='l'>Marked conversions</div></div>" +
        "<div class='kpi'><div class='n'>" + Object.keys(byId).length + "</div><div class='l'>Tracked link IDs</div></div>" +
        "</div>" +
        "<h3>Per-link totals</h3><div class='table-wrap'><table><thead><tr><th>Link ID</th><th>Clicks</th><th>Conversions</th><th>Conv. rate</th></tr></thead><tbody>" +
        (rows || "<tr><td colspan='4' class='muted'>No clicks recorded yet. Use the test buttons on the <a href='links.html'>Link Manager</a>.</td></tr>") +
        "</tbody></table></div>" +
        "<h3>Recent clicks</h3><div class='table-wrap'><table><thead><tr><th>Link ID</th><th>When</th><th>Target</th></tr></thead><tbody>" +
        (last || "<tr><td colspan='3' class='muted'>—</td></tr>") +
        "</tbody></table></div>";
    };
    render();
    var markBtn = document.getElementById("mark-conv-btn");
    if (markBtn) markBtn.addEventListener("click", function () {
      var id = (document.getElementById("conv-link-id") || {}).value || "P1";
      var note = (document.getElementById("conv-note") || {}).value || "";
      window.Zone1Tracker.recordConversion(id, note);
      render();
    });
    var resetBtn = document.getElementById("reset-btn");
    if (resetBtn) resetBtn.addEventListener("click", function () {
      window.Zone1Tracker.reset();
      render();
    });
    var exportBtn = document.getElementById("export-btn");
    if (exportBtn) exportBtn.addEventListener("click", function () {
      var blob = new Blob([window.Zone1Tracker.exportAll()], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "zone1-tracker-export.json";
      a.click();
    });
    // live region for tracker toasts
    var toast = document.getElementById("tracker-toast");
    if (toast && !toast.hasAttribute("hidden")) toast.hidden = true;
  }
})();
