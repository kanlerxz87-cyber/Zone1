# Executive summary

**Scope:** three Amazon.com products submitted for affiliate promotion. Data as of **2026-11-13**.

## What was done

- The three submitted links were opened. Each resolved to an Amazon.com product page. The ASIN, title, and Amazon department were read from each page. Sources: [P1 page](https://www.amazon.com/dp/B0CDY277D3), [P2 page](https://www.amazon.com/dp/B09B7SB46R), [P3 page](https://www.amazon.com/dp/B08DKYBTPH).
- Amazon's Associates Operating Agreement, Program Policies, and Creators API documentation were read. The FTC's disclosure guidance was read too. Each rule that affects the site is listed with a verbatim quote on the Compliance page. Sources: [Operating Agreement](https://affiliate-program.amazon.com/help/operating/agreement), [Program Policies](https://affiliate-program.amazon.com/help/operating/policies), [Creators API](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction), [FTC](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers).
- A static dashboard was built with a landing page, a category page, analysis, compliance, sources, repo review, and a Flagged for Review page. Every table row links to an official source. Unverified values are left blank and marked.

## Key findings

1. **All three products are air-fryer appliances** listed under Amazon's Home & Kitchen department, as stated on each product page: a 6 Qt dual-basket oven (P1), a 26 Qt French-door toaster oven (P2), and an 8 Qt 4-in-1 air fryer (P3).
2. **Verified:** ASIN, title, department, and product-page URL for all three products.
3. **Not verified, left blank:** price, rating, review count, best-sellers rank, availability, and commission rate, for all three products. The readable pages did not show these values, and the official rate schedule requires an Associates sign-in.
4. **Product identity needs your confirmation.** The submitted codes are 9 characters, not ASINs. A direct `/dp/` request with a code returns "Page Not Found". The redirect URLs carry `lv=shuf` and `plpRedirect=mhFallback`, which can indicate a fallback. Open each link and confirm it leads to the intended product.
5. **Commission attribution cannot be confirmed.** None of the resolved links contains an Associates tag. Program Policies require the tag on every link.
6. **Automated data is blocked for now.** PA-API 5 is deprecated and returns 403 errors. The Creators API requires at least 10 qualifying sales in the past 30 days and registered credentials.
7. **Compliance items to review:** the Associates disclosure sentence must appear on the site (done in the footer and beside links); prices may not be shown unless Amazon or the Creators API supplies them (no prices are shown); and product titles may count as Program Content that cannot be altered (flagged).

## What this does not do

- No click, conversion, or revenue tracking. That data sits in the Associates account, which is not accessible here.
- No niche, trend, competitor, or price analysis based on market data. The analysis uses listing titles only.
- No commission estimates. Commission is calculated as qualifying revenue times the official category rate, but the rate is unverified.

## Owner actions (no approval needed to publish; these improve accuracy)

1. Confirm the three product identities from the submitted links (F-04).
2. Provide your Associates tag so the links can be rebuilt with it (F-05).
3. Check the Standard Commission Income rate for each product's category in Associates Central (F-07).
4. Decide whether product titles may stay on the site (F-06).
5. Register for the Creators API once eligible, and provide the credentials through a secret store, not the repo (F-09).

The full list of flagged items is on the **Flagged for Review** page.
