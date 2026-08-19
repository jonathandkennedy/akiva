# Akiva Shapiro Law — High-Intent Landing Page Hub

The `results.goldbergloren.com` pattern for Akiva: a standalone conversion hub, separate
from the main site. Deploy this folder to its own subdomain (e.g. `results.akivashapirolawpllc.com`)
as a second Vercel/Netlify project — it is fully self-contained (single-file pages, only
external request is Google Fonts).

## What's here
| Page | Keyword target | Index? |
|---|---|---|
| `index.html` | probate attorney long island (7,400-word fact-checked cornerstone) | **indexable** |
| `probate-attorney-nassau-county.html` | probate attorney nassau county ($14 CPC, KD 0) | noindex |
| `probate-attorney-suffolk-county.html` | probate attorney suffolk county | noindex |
| `estate-administration-lawyer-long-island.html` | estate administration / died without a will | noindex |
| `small-estate-voluntary-administration-ny.html` | small estate affidavit ny / under $50k | noindex |
| `will-contest-lawyer-long-island.html` | will contest lawyer / estate litigation | noindex |
| `medicaid-planning-attorney-long-island.html` | medicaid planning attorney ($11 CPC, KD 0) | noindex |
| `guardianship-attorney-long-island.html` | guardianship attorney / article 81 | noindex |
| `estate-planning-attorney-long-island.html` | estate planning attorney long island (KD 0) | noindex |

Case-type pages are `noindex` (paid-traffic tools; avoids cannibalizing the main site).
The hub cornerstone is indexable — it's the organic play from the competitive analysis.

## Geo personalization (Goldberg pattern)
Append `?geo=<town>` to any page to swap the visible geography for ad-group matching:
`?geo=massapequa`, `?geo=plainview`, `?geo=hicksville`, `?geo=syosset`, `?geo=riverhead`, etc.
Full list in `build_landers.py` → `GEOS`.

## Design
Implements the client's **Design System v1.0** PDF: Fraunces + Inter, ink navy `#16233A`,
brass `#A9824C`, warm paper `#F7F4EE`, sage/amber triage tags, one repeated CTA
("Get My Free Case Review" / call), calm motion (single hero fade, nothing else).

## Facts & compliance
- Body copy on `index.html` is the client-supplied fact-checked draft (verified against
  tax.ny.gov + nycourts.gov 8/15/26): SCPA 2402 fee brackets, SCPA 2307 commissions,
  $50k small-estate threshold, $7.35M 2026 exclusion, Mineola/Riverhead court addresses.
- **Corrected from the source docs:** trust bar says "St. John's J.D. · Duke MBA" —
  the drafts' "J.D. & MBA, Duke University" was wrong (J.D. is St. John's).
- Review badge/testimonials use the REAL Google profile (5.0, 34 reviews, named reviewers)
  — not the drafts' invented "4.9/37" placeholder or mock quotes.
- Flat fee: `FLAT_FEE_LINE` in `build_landers.py` is empty → a graceful no-number sentence
  renders. When Akiva supplies a real figure, set it and rebuild. Do not invent one.
- Attorney-advertising + no-attorney-client-relationship disclaimers on every page.

## Before launch
1. Set `FORMSPREE_ENDPOINT` (same warning system as the main site — forms are dead until then).
2. Set `GA4_ID` for conversion tracking (`phone_call`, `generate_lead` events already fire).
3. Get the flat-fee number from Akiva → `FLAT_FEE_LINE`.
4. Point the subdomain at this folder; keep landers out of the main site's sitemap (they are).

## Rebuild
```bash
python3 build_landers.py
```
