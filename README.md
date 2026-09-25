# hummelllc.com — Hummel LLC website

Static, no-build website for Hummel LLC. Plain HTML + one stylesheet + one small JS file — nothing to install, nothing to compile, deploys to any static host as-is.

Copy source of truth: document `brief` (HUM-2, rev 4, APPROVED — intake COMPLETE 2026-09-25: hosting = GoDaddy, logo FINAL = HummelLLCLogo.png, LLC NOT YET FILED → legal-name guardrail below). Page copy: document `site-copy` (HUM-6, rev 2 — FINAL, style locked by founder 2026-09-25: tagline A1, voice V1 steady senior advisor, accent P-A slate & sage). All pages built against `site-copy` §3 verbatim (A1 hero). Nothing here invents claims — see Content rules below.

- Staging (GitHub Pages): `https://brendanhummel.github.io/hummelllc.com/`
- Production domain: `https://hummelllc.com/` (DNS cutover at launch, roadmap days 26–30)

## Pages

| File | Page | Slug |
|------|------|------|
| `index.html` | Home — "Your part-time IT leader." (A1) | `/` |
| `what-we-do/index.html` | What We Do | `/what-we-do/` |
| `who-its-for/index.html` | Who It's For | `/who-its-for/` |
| `how-it-works/index.html` | How It Works | `/how-it-works/` |
| `about/index.html` | About — founder-first | `/about/` |
| `engage/index.html` | Engage — form + intro call | `/engage/` |
| `404.html` | Not-found page | any miss |

## How to update content

Everything is plain HTML. No build step, nothing to install.

1. Edit the page file (e.g. open `about/index.html`, change a sentence, save).
2. Commit and push (deploys automatically from `main`):
   ```bash
   git add -A && git commit -m "Update about copy" && git push
   ```
3. Verify at the staging URL; production follows at DNS cutover.

Shared page furniture (header/nav/footer) is duplicated per page intentionally — seven small files, trivial to edit. If pages grow past ~10, migrate to a tiny template step (e.g. Eleventy) — revisit then, not now.

Design tokens (colors, radius, type) live in `assets/css/site.css` under `:root`. Brand treatment applied: **P-A Slate & Sage (LOCKED)** — ink `#232B36`, paper `#FAF8F4`, accent `#3E6B4F` (CTAs/links only), mono eyebrows (site-copy §4). Type: Inter 400/600 + IBM Plex Mono eyebrows, body 17px / line-height 1.6. No display font, no stock imagery.

## Content rules (MANDATORY — brief §6 / site-copy §6)

- **Source of truth:** the brief. No copy ships that isn't in it; any change goes through the brief first.
- **PCI:** proven — stated plainly ("payment-card (PCI) environments"). **HIPAA/CJIS/NIST:** never rendered as credentials — acronyms absent from page copy; plain language only ("healthcare, legal, and finance").
- **Market stats:** exactly two on-page, both attributed as directional context (Verizon 2025 DBIR on Home; industry research 2025–26 on Who It's For). Pricing line carries "(public benchmarks, Sept 2026)".
- **No 24/7 / always-on implication:** the only occurrences are explicit negations in approved copy ("not 24/7 support"; "not an always-on, ticket-driven MSP"). Do not add more.
- **Banned words** (both approved voices): 24/7 (except negations above), always-on (except the non-MSP block), best-in-class, enterprise-grade, seamless, robust, trusted by N clients, guaranteed, affordable plans starting at.
- No certs, client counts, headcounts, or revenue on any page.
- **LLC legal-name guardrail (brief rev 4):** "Hummel LLC" is brand/trade-name only — the LLC is NOT yet filed. No legal-entity claim in fine print, contracts, or invoices (e.g. do not write "Hummel LLC, a limited liability company"). Footer/title usage as a trade name is fine.

## Contact & scheduling (engage)

All wiring is one config object at the top of `assets/js/contact.js` (`window.HUMMEL_CONTACT`):

- `endpoint`: form provider URL (Formspree / Netlify Forms / Cloudflare Pages function). While empty, the form falls back to…
- `email`: set to `hello@hummelllc.com` **only once a mailbox/MX is confirmed live** — then the form opens a mailto instead. Until either is set, submitting shows a friendly pre-launch note (no dead inbox, no broken mailto).
- `scheduleUrl`: calendar link for the 30-minute intro call. While empty, the "Schedule a 30-minute intro call" button scrolls to the form. Note: README's earlier note said Zoho MX (mx1–3.zoho.com) resolves for the domain — whether a Zoho mailbox exists is unconfirmed (brief §7). Verify before setting `email`.

Analytics: **LOCKED = Cloudflare Web Analytics** (founder decision 2026-09-25 — free, cookie-free, no banner needed). Each page head has an `ANALYTICS SLOT` comment; to go live: create a free Cloudflare account, add the site, and paste the beacon snippet (with token) into the slot on all 6 pages. Nothing ships without the token. Site works fully without it.

## SEO & assets

- Titles/descriptions/canonical/OG per page (site-copy §3.7); canonical URLs point at the production domain with clean slugs.
- `sitemap.xml` + `robots.txt` at root.
- `assets/og-image.png` — social card (1200×630) generated from the FINAL logo (`HummelLLCLogo.png`, brief rev 4) on white with the trimmed logomark. `og:image` referenced from every page head.
- Header brand = `assets/logo.png` (trimmed full logo, mark + wordmark). Favicons: `assets/favicon-32.png`, `assets/favicon-180.png` (apple-touch-icon), `favicon.ico` (16/32/48) — all H-monogram crops of the final logo, generated from the same source file. **Regenerate any of them with `python3 scripts/make-logo-assets.py`** — the script reads the source logo from iCloud (`~/Library/Mobile Documents/com~apple~CloudDocs/Hummelllc/HummelLLCLogo.png`, 1144×1104 RGBA). Only that file is the logo source; no derivatives without founder OK.

## DNS / launch facts

- Registrar + hosting account: GoDaddy (brief rev 4 — both confirmed; nameservers ns23/ns24.domaincontrol.com, parked as of 2026-09-25).
- Email MX today: Zoho (mx1–3.zoho.com) — mailbox existence unconfirmed.
- **Launch host: GitHub Pages (LOCKED by founder — stack interaction 2026-09-25).** Staging URL becomes the production host; DNS cutover = add a `CNAME` from `www` to `brendanhummel.github.io` at GoDaddy (or use GoDaddy's web-forwarding to `www`), plus enable the custom domain in the Pages settings (Settings → Pages → Custom domain). Preserve existing MX/TXT records when editing DNS (brief §7).
- Full runbook lives in HUM-5 issue comments.