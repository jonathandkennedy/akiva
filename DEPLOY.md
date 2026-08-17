# Akiva Shapiro Law — Deployment & Migration Notes

Static site output lives in `site/`. It is plain HTML/CSS/JS — host anywhere (Netlify, Cloudflare Pages, S3+CloudFront, or a plain Apache/Nginx box). No build step, no database.

## Before go-live — resolve these NAP conflicts
The site currently ships with **(516) 806-0762** and hours **Mon–Thu 9:30–5:30 / Fri 9:30–4:00** (from the firm's own website). Confirm against the Google Business Profile, which shows a different phone **(347) 435-6529** and hours **Mon–Fri 9:00–5:00**. Pick one canonical value for each and make website + GBP + Yelp match. If the number changes, update `PHONE_DISPLAY` / `PHONE_TEL` in `generate_site.py` and rebuild.

Also: **claim the Yelp listing** (currently unclaimed, 0 reviews) and point a few clients there.

## What the rebuild preserves (SEO safety)
- Every indexable URL path from the old WordPress sitemap is preserved 1:1 (same slugs).
- Titles, meta descriptions, and H1s were kept and improved, never blanked (baseline in `baseline.csv`).
- Homepage now has a proper H1 (old site had none).

## Redirects — 32 total (`site/_redirects` for Netlify, `site/.htaccess` for Apache)
- **22 duplicate-content consolidations** — near-identical Q&A pairs (e.g. `/what-happens-if-i-die-without-a-will/` → `/what-happens-if-i-die-without-a-will-in-new-york/`) 301'd to the stronger URL.
- **3 contact-page consolidations** — `/contact/`, `/contact-us-covid-19/`, `/sign-up/` → `/contact-us/`.
- **7 dev/junk pages** — `/testpage/`, `/test-build/`, `/sample-page-2/`, etc. → home.
- Old `/blog/` and `/news/` → `/faq/` (the new Legal Answers library).
- The 2 URLs that 404'd in the old sitemap are 301'd to their correct live equivalents.

If hosting on Apache, drop `.htaccess` at web root. On Netlify/Cloudflare Pages, `_redirects` is picked up automatically. On Nginx, translate the `.htaccess` rules to `rewrite ... permanent;`.

## Schema (JSON-LD) shipped
- Sitewide: `WebSite`, `LegalService`+`Attorney`, `Person` (Akiva, with alumni/memberships/sameAs).
- Homepage/firm: `aggregateRating` **5.0 / 34** + three real `Review` nodes (from Google).
- Each Q&A article: `FAQPage`, `Article` (author = Akiva, dated), `BreadcrumbList`, and `VideoObject` where a video exists.
- Practice pages: `Service` + `BreadcrumbList`.
- Validate post-launch at search.google.com/test/rich-results.

## Post-launch checklist
1. Point DNS / deploy `site/` to web root.
2. Confirm the 301s resolve (spot-check 5–6 from `_redirects`).
3. Submit `https://www.akivashapirolawpllc.com/sitemap.xml` in Google Search Console.
4. Request re-crawl of the homepage + top practice pages.
5. Run Rich Results Test on homepage, one practice page, one Q&A article.
6. Confirm the canonical phone number is correct sitewide.
7. Keep the old WordPress reachable for a few days as fallback, then retire.

## Turning on the contact form & analytics (launch config)
All three switches live at the top of `generate_site.py` — set the value, run the rebuild command, redeploy.

**Contact form** (on `/contact-us/`): uses **Formspree** — works on any host.

⚠️ **The form is not live yet.** `FORMSPREE_ENDPOINT` is still the placeholder
`https://formspree.io/f/REPLACE_ME`, and the build prints a warning until it's replaced. To activate:
1. At [formspree.io](https://formspree.io), create a **new form for Akiva** and set its notification email to a firm address (e.g. Akiva@AkivaShapiroLawPLLC.com).
2. Copy the endpoint (`https://formspree.io/f/xxxxxxxx`) into `FORMSPREE_ENDPOINT` at the top of `generate_site.py`.
3. Rebuild and redeploy. The warning disappears when it's set.
4. Submit the form once on the live site — Formspree requires confirming the first submission to activate the address.

**Create a dedicated endpoint for this site.** Do not reuse a Formspree endpoint from another project — inquiries would be delivered to the wrong inbox, which for a law firm is a confidentiality problem.

Form details already wired: `_next` redirects to `/thank-you/` after submit, `_subject` labels the notification email, `_gotcha` is Formspree's spam honeypot, and the consent checkbox carries the no-attorney-client-relationship disclaimer.

*(If you ever switch to Netlify hosting and prefer its built-in forms, set `FORM_NETLIFY = True` — the generator emits the Netlify variant automatically.)*

**Analytics**: paste the real IDs and rebuild.
- `GA4_ID = "G-XXXXXXXXXX"` → injects Google Analytics 4 site-wide. (Create the GA4 property in Akiva's Google account first; that ID can't be generated here.)
- `GTM_ID = "GTM-XXXXXXX"` → optional Google Tag Manager, if preferred over raw GA4.
- Leave empty = no analytics injected (current state).
- Conversion events already fire (no-op until analytics is on): `phone_call` on every tel: click, `email_click` on mailto clicks, `generate_lead` on contact-form submit. Mark `phone_call` and `generate_lead` as conversions in GA4.
- **Call tracking** (e.g. CallRail) is a separate follow-up — it needs a vendor account and ties to the phone-number decision (516 vs 347).

## Rebuild command
```
python3 generate_site.py
```
Regenerates everything from `pages.json`, `site-plan.json`, `local-data.json`, and `articles/*.json`.

## Known gaps / follow-ups
- **Video embeds:** only 1 Vimeo ID survived in the scrape; the old Q&A pages loaded video via a third-party "Speak API" plugin, so most embed IDs weren't in the HTML. To restore video on the articles, pull the Vimeo (or YouTube) IDs from the firm's account and add them to each article's `vimeo` field.
- **Photos:** using the best headshot + office image from the old site. Higher-res originals (via WP Media Library) would sharpen the hero.
- **Service-area / town pages:** not built yet — pending the target town list (Plainview, Hicksville, Syosset, Bethpage, Melville, etc.) for local-SEO expansion.
