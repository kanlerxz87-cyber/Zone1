/* Zone1 — renders data tables from ZONE1_DATA. No invented values. */
(function () {
  "use strict";
  var D = window.ZONE1_DATA;

  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    (children || []).forEach(function (c) { e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }

  function badge(text, kind) {
    return el("span", { class: "badge badge-" + kind }, [text]);
  }

  function srcLink(label, url) {
    return el("a", { class: "src", href: url, target: "_blank", rel: "noopener" }, [label || url]);
  }

  function cell(text, cls) {
    return el("td", cls ? { class: cls } : {}, [text || ""]);
  }

  function blank() {
    return el("td", {}, [el("span", { class: "unverified" }, ["— unverified —"])]);
  }

  function valueCell(v) {
    return v === "" ? blank() : cell(v);
  }

  function table(headers, rows) {
    var thead = el("thead", {}, [el("tr", {}, headers.map(function (h) { return el("th", {}, [h]); }))]);
    var tbody = el("tbody", {}, rows.map(function (r) { return el("tr", {}, r); }));
    return el("table", {}, [thead, tbody]);
  }

  function mount(id, node) {
    var target = document.getElementById(id);
    if (target) target.appendChild(node);
  }

  /* ---- Product catalog table ---- */
  function renderProducts() {
    var rows = D.products.map(function (p) {
      var status = p.status === "UNVERIFIED" ? badge("UNVERIFIED", "danger") : badge("VERIFIED", "ok");
      return [
        cell("<code>" + p.asin + "</code>"),
        valueCell(p.title),
        valueCell(p.brand),
        valueCell(p.category),
        valueCell(p.price),
        valueCell(p.rating),
        valueCell(p.reviewCount),
        valueCell(p.commissionRate),
        cell(srcLink("Amazon ↗", p.source)),
        cell(status)
      ];
    });
    mount("products-table", table(
      ["ASIN", "Title", "Brand", "Category", "Price", "Rating", "Reviews", "Commission", "Source (official)", "Status"],
      rows
    ));
  }

  /* ---- Commission Table 1 ---- */
  function renderCommission() {
    var rows = D.commissionTable.rows.map(function (r) { return [cell(r[0]), cell(r[1])]; });
    mount("commission-table", table(["Product Category", "Fixed Commission Income Rate"], rows));
    var src = document.getElementById("commission-source");
    if (src) src.href = D.commissionTable.source;
  }

  /* ---- Session rules ---- */
  function renderSessionRules() {
    var rows = D.sessionRules.rows.map(function (r) { return [cell(r[0], "unverified"), cell(r[1])]; });
    rows[0][0].className = ""; // header-ish first col keep normal
    mount("session-table", table(["Rule", "Verified detail (official)"], rows));
    var src = document.getElementById("session-source");
    if (src) src.href = D.sessionRules.source;
  }

  /* ---- Disqualifiers list ---- */
  function renderDisqualifiers() {
    var ul = el("ul", { class: "clean" }, D.disqualifiers.items.map(function (i) { return el("li", {}, [i]); }));
    mount("disqualifiers-list", ul);
    var src = document.getElementById("disqualifiers-source");
    if (src) src.href = D.disqualifiers.source;
  }

  /* ---- Flagged irregularities ---- */
  function renderFlagged() {
    var wrap = el("div", { class: "grid grid-2" });
    D.flagged.forEach(function (f) {
      var sev = f.severity === "High" ? badge("High", "danger") : badge("Medium", "warn");
      var card = el("div", { class: "card" }, [
        el("div", { style: "display:flex;gap:8px;align-items:center;margin-bottom:6px;" }, [
          el("strong", {}, [f.id]), sev
        ]),
        el("h3", {}, [f.title]),
        el("p", {}, [f.detail]),
        el("div", { style: "margin-top:8px;font-size:13px;" }, [
          el("strong", {}, ["Evidence / sources: "]),
          el("ul", { class: "clean" }, f.evidence.map(function (e) { return el("li", {}, [srcLink(e, e)]); }))
        ])
      ]);
      wrap.appendChild(card);
    });
    mount("flagged-grid", wrap);
  }

  /* ---- Verification log ---- */
  function renderVerification() {
    var rows = D.verificationLog.map(function (v) {
      var res = v.result.indexOf("VERIFIED") !== -1 ? badge("VERIFIED", "ok") : badge("UNVERIFIED", "danger");
      return [cell(v.item), cell(v.method), cell(res), cell(srcLink("Source ↗", v.source))];
    });
    mount("verification-table", table(["Checked item", "Method", "Result", "Official source"], rows));
  }

  /* ---- Stats on dashboard ---- */
  function renderStats() {
    var unverified = D.products.filter(function (p) { return p.status === "UNVERIFIED"; }).length;
    var verified = D.products.length - unverified;
    function stat(label, value, sub) {
      return el("div", { class: "stat" }, [
        el("div", { class: "label" }, [label]),
        el("div", { class: "value" }, [value]),
        el("div", { class: "sub" }, [sub])
      ]);
    }
    var grid = el("div", { class: "grid grid-3" }, [
      stat("Products supplied", String(D.products.length), "affiliate links provided"),
      stat("Verified listings", String(verified), "confirmed from an official source"),
      stat("Unverified listings", String(unverified), "attributes left blank — flagged"),
      stat("Commission categories", String(D.commissionTable.rows.length), "official rate table rows"),
      stat("Irregularities flagged", String(D.flagged.length), "see Flagged for Review"),
      stat("Sources of record", String(D.complianceSources.length + D.products.length), "official Amazon URLs")
    ]);
    mount("stats-grid", grid);
  }

  /* ---- Auto-run based on presence of mount points ---- */
  document.addEventListener("DOMContentLoaded", function () {
    renderStats();
    renderProducts();
    renderCommission();
    renderSessionRules();
    renderDisqualifiers();
    renderFlagged();
    renderVerification();
  });
})();
