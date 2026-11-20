<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$full_title</title>
<meta name="description" content="$description">
$canonical_tag
<meta name="robots" content="$robots">
<meta property="og:type" content="$og_type">
<meta property="og:site_name" content="$site_name">
<meta property="og:title" content="$full_title">
<meta property="og:description" content="$description">
<meta property="og:url" content="$canonical">
<meta property="og:image" content="$og_image">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="$og_alt">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="$full_title">
<meta name="twitter:description" content="$description">
<meta name="twitter:image" content="$og_image">
<meta name="twitter:image:alt" content="$og_alt">
$jsonld
<link rel="preload" href="${prefix}assets/fonts/dm-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="${prefix}assets/fonts/dm-serif-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="${prefix}assets/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%23294f3f'/%3E%3Ctext x='16' y='22' font-family='serif' font-size='18' fill='%23fff' text-anchor='middle'%3Ez1%3C/text%3E%3C/svg%3E">
<link rel="alternate" type="application/rss+xml" title="Zone1 Kitchen — new guides" href="${prefix}feed.xml">
$search_console_tag
<meta name="theme-color" content="#294f3f">
</head>
<body class="$body_class" data-page-id="$page_id" data-page-type="$page_type" data-analytics-eligible="$analytics_eligible">
<a class="skip-link" href="#main-content">Skip to main content</a>
<header class="topbar">
  <div class="header-inner">
    <a class="brand" href="${prefix}index.html" aria-label="Zone1 Kitchen home">
      <span class="brand-icon" aria-hidden="true"><svg viewBox="0 0 40 40" fill="none"><path d="M5 23h30c0 8-6 13-15 13S5 31 5 23Z" stroke="currentColor" stroke-width="1.6"/><path d="M10 18h20M16 12c-3-4 1-5 0-9M24 14c-3-4 2-6 1-10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></span>
      <span class="brand-wordmark">zone1 <small>Kitchen</small></span>
    </a>
    <nav class="topnav" aria-label="Primary">$topnav</nav>
    <span class="header-note">A little clarity for<br>your countertop.</span>
    <details class="workspace-menu">
      <summary>Workspace</summary>
      <div class="workspace-panel">
        <p class="menu-heading">Behind the publication</p>
        <p class="tiny muted">Public decisions, evidence and operating notes. Reader guides stay out front.</p>
        <nav class="workspace-links" aria-label="Owner workspace">$workspace_links</nav>
      </div>
    </details>
  </div>
</header>
<div class="disclosure-bar" role="note" aria-label="Affiliate disclosure">
  <strong>Affiliate disclosure:</strong> $disclosure
  <a href="${prefix}compliance.html">How links work</a>
</div>
<div class="shell">
  <main id="main-content">
    $workspace_status
    $body
  </main>
</div>
<footer class="site">
  <div class="inner">
    <div class="foot-brand">
      <span class="brand-wordmark">zone1 <small>Kitchen</small></span>
      <p>Less guesswork. More room for dinner. Practical kitchen buying guides, grounded in the manuals—not hands-on tests.</p>
      <a class="text-link" href="${prefix}feed.xml">Follow new guides via RSS <span aria-hidden="true">↗</span></a>
    </div>
    <div>
      <h2>Find your fit</h2>
      <ul>
        <li><a href="${prefix}categories/kitchen-appliances.html">Air fryers &amp; ovens</a></li>
        <li><a href="${prefix}picks.html">Format finder</a></li>
        <li><a href="${prefix}categories/cooking-thermometers.html">Thermometer link notes</a></li>
        <li><a href="${prefix}compare.html">Compare the air fryers</a></li>
        <li><a href="${prefix}articles/index.html">All buying guides</a></li>
      </ul>
    </div>
    <div>
      <h2>A closer look</h2>
      <ul>
        <li><a href="${prefix}about.html">Our approach &amp; authorship</a></li>
        <li><a href="${prefix}how-we-research.html">What we read &amp; what changed</a></li>
        <li><a href="${prefix}compliance.html">Disclosure &amp; link policy</a></li>
        <li><a href="${prefix}flagged.html">Flagged for review</a></li>
        <li><a href="${prefix}data.html#sources">Official source register</a></li>
      </ul>
    </div>
    <div class="foot-owner">
      <h2>Owner workspace</h2>
      <ul>
        <li><a href="${prefix}executive-summary.html">Executive summary &amp; index</a></li>
        <li><a href="${prefix}decision-review.html">Decision review queue</a></li>
        <li><a href="${prefix}suggestions.html">Suggestions decision queue</a></li>
        <li><a href="${prefix}questions.html">Known facts &amp; missing answers</a></li>
        <li><a href="${prefix}product-intent.html">Links, attribution &amp; ledger</a></li>
      </ul>
      <details class="footer-workspace"><summary>All workspace pages</summary><ul>$footer_workspace</ul></details>
    </div>
  </div>
  <div class="foot-bottom">
    <p><strong>$disclosure</strong> We may earn a commission if Amazon credits a qualifying purchase through an eligible link. Intended listings and account attribution for the submitted links are not yet confirmed.</p>
    <details class="privacy-details">
      <summary>Privacy, local drafts &amp; hosting</summary>
      $privacy
    </details>
    <p class="legal">Zone1 Kitchen is an affiliate publication, not a product-testing laboratory. It is not owned by or endorsed by Amazon or any named manufacturer. Brand names identify the products discussed. AI-assisted research and decorative imagery are explained in <a href="${prefix}about.html">our approach</a>; no named human editor or personal product experience is invented.</p>
  </div>
</footer>
<script src="${prefix}assets/app.js" defer></script>
$analytics_tag
</body>
</html>
