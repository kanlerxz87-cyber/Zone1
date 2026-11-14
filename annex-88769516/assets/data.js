/*
 * Zone1 — Amazon Affiliate Platform data layer.
 * Every value here is either (a) taken verbatim from an official source with a
 * source link, or (b) left blank and flagged UNVERIFIED because it could not be
 * confirmed from an official source. No values are inferred or filled.
 *
 * Sources are recorded inline. Product attributes for the three user-supplied
 * ASINs could NOT be verified (see methodology.html / flagged-for-review.html).
 */
window.ZONE1_DATA = {
  meta: {
    repo: "kanlerxz87-cyber/Zone1",
    branch: "arena/88769516-zone1",
    generated: "2026-11-13",
    session: "session-88769516"
  },

  /* ---- User-supplied affiliate links / products ----
     Only the ASIN and the provided link are CONFIRMED inputs.
     All product attributes are left blank = UNVERIFIED. */
  products: [
    {
      id: "B04G1MEwY",
      asin: "B04G1MEwY",
      providedLink: "https://link.amazon/B04G1MEwY",
      canonicalLink: "https://www.amazon.com/dp/B04G1MEwY",
      title: "",
      brand: "",
      category: "",
      price: "",
      listPrice: "",
      rating: "",
      reviewCount: "",
      availability: "",
      commissionRate: "",
      commissionPotential: "",
      source: "https://www.amazon.com/dp/B04G1MEwY",
      status: "UNVERIFIED"
    },
    {
      id: "B02NbDxp3",
      asin: "B02NbDxp3",
      providedLink: "https://link.amazon/B02NbDxp3",
      canonicalLink: "https://www.amazon.com/dp/B02NbDxp3",
      title: "",
      brand: "",
      category: "",
      price: "",
      listPrice: "",
      rating: "",
      reviewCount: "",
      availability: "",
      commissionRate: "",
      commissionPotential: "",
      source: "https://www.amazon.com/dp/B02NbDxp3",
      status: "UNVERIFIED"
    },
    {
      id: "B00hJ57DV",
      asin: "B00hJ57DV",
      providedLink: "https://link.amazon/B00hJ57DV",
      canonicalLink: "https://www.amazon.com/dp/B00hJ57DV",
      title: "",
      brand: "",
      category: "",
      price: "",
      listPrice: "",
      rating: "",
      reviewCount: "",
      availability: "",
      commissionRate: "",
      commissionPotential: "",
      source: "https://www.amazon.com/dp/B00hJ57DV",
      status: "UNVERIFIED"
    }
  ],

  /* ---- Official Amazon Associates Standard Commission Income Statement (Table 1)
     Source: https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ ---- */
  commissionTable: {
    source: "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ",
    title: "Associates Program Standard Commission Income Statement — Table 1",
    rows: [
      ["Luxury Beauty, Luxury Stores Beauty, Amazon Explore", "10.00%"],
      ["Digital Music, Physical Music, Handmade, Digital Videos", "5.00%"],
      ["Physical Books, Kitchen, Automotive", "4.50%"],
      ["Amazon Fire Tablet Devices, Amazon Kindle Devices, Luxury Stores Fashion, Apparel, Amazon Cloud Cam Devices, Fire TV Edition Smart TVs, Amazon Fire TV Devices, Amazon Echo Devices, Ring Devices, Watches, Jewelry, Luggage, Shoes, and Handbags & Accessories", "4.00%"],
      ["Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins", "3.00%"],
      ["PC, PC Components, DVD & Blu-Ray", "2.50%"],
      ["Televisions, Digital Video Games", "2.00%"],
      ["Amazon Fresh, Physical Video Games & Video Game Consoles, Grocery, Health & Personal Care", "1.00%"],
      ["Gift Cards; Wireless Service Plans; Alcoholic Beverages; Digital Kindle Products purchased as a subscription; Vehicles – Leasing and Sales; Pet Prescription Medications; Food prepared and delivered from a restaurant; Amazon Appstore, Prime Now, or Amazon Pay Places", "0.00%"],
      ["Coach", "0.00%"],
      ["All Other Categories", "4.00%"]
    ]
  },

  /* ---- Verified session / qualifying-purchase rules (official Program Policies) ---- */
  sessionRules: {
    source: "https://affiliate-program.amazon.com/help/operating/policies",
    rows: [
      ["Session length", "Begins at Special Link click; ends at the first of: (x) 24 hours elapse, (y) customer places an order for a Product (non-digital), or (z) customer clicks through a Special Link that is not yours."],
      ["Shopping-cart window", "Customer adds Product to cart and completes order no later than 89 days after the initial click-through."],
      ["Ship / payment window", "Within 180 days of purchase, the Product is shipped to, streamed/downloaded by, and paid for by the customer."],
      ["Qualifying Revenue", "Amount Amazon actually receives, less shipping, gift-wrapping, handling, taxes, service charges, credits, rebates, credit-card processing fees, and bad debt."],
      ["Standard Commission Income", "Calculated as a percentage of Qualifying Revenue, per the category rate table."]
    ]
  },

  /* ---- Disqualified purchases (official Program Policies) — verified highlights ---- */
  disqualifiers: {
    source: "https://affiliate-program.amazon.com/help/operating/policies",
    items: [
      "Product purchased after termination of the Agreement.",
      "Order where cancellation, return, or refund has been initiated.",
      "Purchase referred via a Prohibited Paid Search Placement (bidding on keywords containing \"amazon\" or \"kindle\" or any Amazon Mark / misspelling).",
      "Purchase referred by a link generated/displayed on a Search Engine.",
      "Purchase referred by a Redirecting Link (sends users indirectly without an affirmative click).",
      "Purchase not correctly tracked/reported because links are not properly formatted.",
      "Purchase via a Mobile Application that is not an Approved Mobile Application or not served via Creators API / PA API.",
      "Product subject to a Bounty Event (handled as Special Commission Income).",
      "Subscription Product unless otherwise provided.",
      "Pre-release or pre-order Product not available on a Product listing page."
    ]
  },

  /* ---- Compliance sources (official) ---- */
  complianceSources: [
    { name: "Associates Program Operating Agreement (updated Oct 15, 2025)", url: "https://affiliate-program.amazon.com/help/operating/agreement" },
    { name: "Associates Program Policies (updated April 14, 2026)", url: "https://affiliate-program.amazon.com/help/operating/policies" },
    { name: "Associates Program Standard Commission Income Statement", url: "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ" },
    { name: "Associates Central — Help index", url: "https://affiliate-program.amazon.com/help/node" },
    { name: "Amazon Associates program home", url: "https://affiliate-program.amazon.com/" }
  ],

  /* ---- Flagged irregularities ---- */
  flagged: [
    {
      id: "IRR-1",
      title: "Requested ASINs cannot be verified as valid, listed products",
      severity: "High",
      detail: "No official Amazon product page could be loaded for any of the three ASINs (Amazon bot-blocks automated access on every route tested). No Wayback snapshot exists and there is no search-engine footprint. Two independent trackers (CamelCamelCamel, Keepa) report no valid record / 'invalid product identifier'. Consequently every product attribute (title, brand, price, rating, availability, category) is left blank and flagged UNVERIFIED. No value was inferred or filled.",
      evidence: [
        "https://www.amazon.com/dp/B04G1MEwY",
        "https://www.amazon.com/dp/B02NbDxp3",
        "https://www.amazon.com/dp/B00hJ57DV"
      ]
    },
    {
      id: "IRR-2",
      title: "Provided link.amazon short links fall back to unrelated ASINs",
      severity: "High",
      detail: "Each provided link does NOT resolve to amazon.com/dp/<ASIN>. Each redirects with a 'plpRedirect=mhFallback' (marketplace fallback) parameter to a DIFFERENT product ASIN. This indicates the ASINs in the links do not resolve to a resolvable listing.",
      evidence: [
        "https://link.amazon/B04G1MEwY -> https://www.amazon.com/dp/B0CDY277D3 (fallback)",
        "https://link.amazon/B02NbDxp3 -> https://www.amazon.com/dp/B09B7SB46R (fallback)",
        "https://link.amazon/B00hJ57DV -> https://www.amazon.com/dp/B08DKYBTPH (fallback)"
      ]
    },
    {
      id: "IRR-3",
      title: "Direct Amazon verification blocked from this environment",
      severity: "Medium",
      detail: "Amazon bot-blocks automated fetchers; even known-valid ASINs return 404 via the available routes (direct fetch, Jina reader, microlink real-browser, UK/DE marketplaces). Product data can only be confirmed by opening the links in a normal browser or via the Amazon Product Advertising API (no credentials available here).",
      evidence: [
        "https://www.amazon.com/dp/B08N5WRWNW (known-valid ASIN, also 404 via automated routes — calibration)"
      ]
    },
    {
      id: "IRR-4",
      title: "Commission potential not computable for the three ASINs",
      severity: "Medium",
      detail: "Commission is category-based. The category for each ASIN is UNVERIFIED, so no commission figure is shown. Commission rates themselves are verified from the official Commission Income Statement.",
      evidence: [
        "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ"
      ]
    }
  ],

  /* ---- Verification log (what was checked, against which official source) ---- */
  verificationLog: [
    { item: "ASIN B04G1MEwY product page", method: "Direct + proxy + archive", result: "UNVERIFIED (blocked / no snapshot)", source: "https://www.amazon.com/dp/B04G1MEwY" },
    { item: "ASIN B02NbDxp3 product page", method: "Direct + proxy + archive", result: "UNVERIFIED (blocked / no snapshot)", source: "https://www.amazon.com/dp/B02NbDxp3" },
    { item: "ASIN B00hJ57DV product page", method: "Direct + proxy + archive", result: "UNVERIFIED (blocked / no snapshot)", source: "https://www.amazon.com/dp/B00hJ57DV" },
    { item: "link.amazon redirect chains", method: "HTTP redirect capture", result: "Marketplace fallback to different ASINs", source: "https://link.amazon/B04G1MEwY" },
    { item: "CamelCamelCamel ASIN records", method: "Third-party tracker", result: "No record / invalid identifier", source: "https://camelcamelcamel.com/product/B04G1MEwY" },
    { item: "Keepa ASIN records", method: "Third-party tracker", result: "Not a valid ASIN", source: "https://keepa.com/product/3-B04G1MEwY" },
    { item: "Commission Income Statement (Table 1)", method: "Official page fetch", result: "VERIFIED", source: "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ" },
    { item: "Operating Agreement", method: "Official page fetch", result: "VERIFIED", source: "https://affiliate-program.amazon.com/help/operating/agreement" },
    { item: "Program Policies (session / disqualifiers)", method: "Official page fetch", result: "VERIFIED", source: "https://affiliate-program.amazon.com/help/operating/policies" }
  ]
};
