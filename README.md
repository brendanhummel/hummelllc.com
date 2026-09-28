# hummelllc.com — Hummel LLC website

Static, no-build website for Hummel LLC. Plain HTML + one stylesheet + one small JS file — nothing to install, nothing to compile, deploys to any static host as-is.

Copy source of truth: document `brief` (HUM-2, rev 4, APPROVED — intake COMPLETE 2026-09-25: hosting = GoDaddy, logo FINAL = HummelLLCLogo.png, LLC NOT YET FILED → legal-name guardrail below). Page copy: document `site-copy` (HUM-6, rev 2 — FINAL, style locked by founder 2026-09-25: tagline A1, voice V1 steady senior advisor, accent P-A slate & sage). All pages built against `site-copy` §3 verbatim (A1 hero). Nothing here invents claims — see Content rules below.

- Production (LIVE since 2026-09-27): `https://hummelllc.com/` — DNS cutover complete, verified 2026-09-28 (`postcutover.py` → PRODUCTION VERIFIED, 19 ok / 0 warn / 0 fail). Valid Let's Encrypt certificate covering **both** `hummelllc.com` and `www.hummelllc.com`; `http://` and `www` 301 to the apex.
- Staging (still served, not linked anywhere): `https://brendanhummel.github.io/hummelllc.com/`

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
3. Verify on production: <https://hummelllc.com/> (live since the 2026-09-27 DNS cutover; check the page you edited plus `/scripts/preflight.py --live`).

> **Internal links are RELATIVE on purpose.** GitHub Pages serves this repo under `/hummelllc.com/`, so absolute paths (`/assets/...`, `/what-we-do/`) 404 against the origin root. Root pages use `assets/...`/`what-we-do/...` (no leading slash); subfolder pages use `../assets/...`. These resolve at both the subpath staging URL and the apex production domain. `404.html` is the exception — root-absolute (it's served at arbitrary paths). Canonical/OG/sitemap URLs stay absolute (production domain). Don't "clean up" the relative refs.

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
- `email`: the address the form opens in the visitor's mail app — set it **only once that mailbox is confirmed to accept mail** (send one test, confirm no bounce). Until `endpoint` or `email` is set, submitting shows a short pre-launch note (no dead inbox, no broken mailto).
- `scheduleUrl`: calendar link for the 30-minute intro call. While empty, the "Schedule a 30-minute intro call" button scrolls to the form and the "A calendar link lands here before launch" note stays. Once set, the button goes straight to the calendar and that note is hidden automatically — left visible it would contradict the working link sitting right under it.

**Launch-window decisions (founder, 2026-09-27):** transport stays **`mailto:`** (not a form provider) for launch; the intro-call button becomes a **Cal.com** booking link — the public URL is still owed, so the button keeps scrolling to the form until it arrives. Revisit the transport after launch once analytics show real traffic.

**Set these with the helper, not by hand:**

```bash
python3 scripts/set-contact.py --show                                   # what is configured now
python3 scripts/set-contact.py --endpoint https://formspree.io/f/abc123  # provider transport
python3 scripts/set-contact.py --email brendan@hummelllc.com --verified  # mailto transport
python3 scripts/set-contact.py --schedule https://cal.com/brendan/30min
```

`--email` refuses to publish an address unless you also pass `--verified`, because a mailto to a dead address is worse than no transport at all: the visitor's mail app opens, the bounce goes back to *them*, and the inquiry is lost while the page looks fine. (That is exactly how `hello@hummelllc.com` failed on 2026-09-25 — hard `550 5.1.1 User does not exist` from `mx.zoho.com`, twice; `brendan@hummelllc.com` was accepted in the same test.)

The visitor-facing text is derived from `email`, so the address is configured in exactly one place and cannot drift. Behaviour of all three transports is covered by `node scripts/test-contact-modes.js`.

Analytics: **INSTALLED 2026-09-25 — Cloudflare Web Analytics beacon live on all 6 pages** (founder decision 2026-09-25 — free, cookie-free, no banner needed). The founder supplied the dashboard snippet; it was installed in one pass with `python3 scripts/set-analytics.py --snippet '<the snippet>'`, which wrote the beacon (public site token `382b5c…288d`) into every page head. `preflight.py` reports `ok analytics beacon live on all pages`. To change it (new token/site), re-run:

```bash
python3 scripts/set-analytics.py --snippet-file snippet.txt   # or --token <32-hex value>
```

The script is idempotent (re-running reports "already current"), replaces the placeholder rather than duplicating it, and **refuses anything that looks like account credentials** — see the security note below. **No Cloudflare API token is required.** The `token` in the snippet is a *public site token*: it is visible in the page source of every site using CWA and grants no account permissions. No nameserver change, no Cloudflare zone, DNS stays at GoDaddy. Nothing ships without the snippet; the site works fully without it. Full detail: `LAUNCH-RUNBOOK.md` §2.

> **Never put a credential on this site, and never paste one into an issue comment or chat.** Cloudflare API tokens and API keys are account-level credentials; nothing in this build needs one, ever. `scripts/set-analytics.py` and `scripts/preflight.py` both reject API-token-shaped input, and preflight fails the build if any page carries one. If you created an API token for this work, revoke it: Cloudflare dashboard → My Profile → API Tokens.

## Scripts

| Script | What it does |
|---|---|
| `scripts/preflight.py` | The launch gate — copy guardrails, structure, credential scan, the three launch gates, `--live` route fetches, `--dns` cutover check. Run it before launch and after any change. |
| `scripts/postcutover.py` | **Post-cutover production verification (runbook §3).** One command: DNS gate (four apex A + `www` CNAME + MX/SPF survived), live TLS cert on both hostnames, all 6 routes, canonical tags, analytics beacon, the `curl -I` HEAD check, engage form, then hands off to `preflight.py`. Exits non-zero until production is genuinely serving. |
| `scripts/set-analytics.py` | Installs the Cloudflare Web Analytics beacon on all 6 pages from a token or snippet. Idempotent; refuses account-credential-shaped input. |
| `scripts/set-contact.py` | Sets the Engage form's `endpoint` / `email` / `scheduleUrl` (Gate 1). `--email` requires `--verified`. `--show` prints the current config. |
| `scripts/test-contact-modes.js` | `node scripts/test-contact-modes.js` — runs the real `contact.js` in a small DOM shim and asserts what a visitor sees in each of the three transports. |
| `scripts/make-logo-assets.py` | Regenerates the header logo, favicons and OG card from the founder's `HummelLLCLogo.png`. |
| `scripts/optimize-logo.py` | Derives the display-sized header logo variants (`logo-46.png` / `logo-93.png`) from the 272 KB master and wires the `srcset` on all pages. `--check` verifies without writing; preflight fails if a page goes back to the master. |
| `scripts/set-social-meta.py` | Installs/refreshes the share-card tags (`twitter:card`, `og:site_name`, og image dimensions) on all pages and the structured-data block on Home. Idempotent; `--check` verifies. The JSON-LD values are installed verbatim from `scripts/doctrine_nap.py` — this script never invents one. |
| `scripts/doctrine_nap.py` | The entity values for the JSON-LD, each quoted from `nap-doctrine` rev 3 (`§5` name/website/email, `§2` locality + service area via `profile-inventory` §3.1). Also holds the closed key list and the named bans (`telephone`, `streetAddress`, `openingHours`, `legalName`, …) with the rule each one breaks. **Change the doctrine first, then this file** (`nap-doctrine` §6.1). |
| `scripts/check-structured-data.py` | Verifies the JSON-LD against the doctrine value by value: `--url https://hummelllc.com/` for production, `--file <page>` for a fixture, `--json` to print the node for Google's Rich Results Test. Exit 1 on any drift. |
| `scripts/verify-presence.py` (+ `presence-manifest.json`, `test-verify-presence.py`) | **M3-B profile verification (Presence & Launch Lead).** `python3 scripts/verify-presence.py scripts/presence-manifest.json --all` checks every profile that has a URL — HTTP 200, exact `Hummel LLC`, canonical `https://hummelllc.com/`, the canonical phone on the platforms that publish one, no staging URL, and a negation-aware guardrail scan — plus the `hummelllc.com` site anchor on every run. The manifest holds the canonical strings copied from `nap-doctrine` §5; `scripts/test-verify-presence.py` proves the checker fails the right things (9 fault-injection cases). Run it after any profile change and at each NAP audit. |

## SEO & assets

- Titles/descriptions/canonical/OG per page (site-copy §3.7); canonical URLs point at the production domain with clean slugs.
- Share cards: `twitter:card = summary_large_image` + `og:site_name` + OG image dimensions on every page, installed by `scripts/set-social-meta.py`.
- Structured data: a `ProfessionalService` JSON-LD node on Home (HUM-12, 2026-09-28). Values are `nap-doctrine` rev 5 §5 exactly — `name`, `url`, `email`, plus `address` locality/region (`§2`) and the 10-place `areaServed` list (`profile-inventory` §3.1). **The key list is closed:** no `telephone`, no `streetAddress` (service-area business, `§2`), no `openingHours` (`§4`), no legal-name/date fields (`§1`), no rating or review (no clients yet). `telephone` stays banned now that the phone exists (`nap-doctrine` §3, FINAL 2026-09-28) because the founder's answer scoped the number to the **profiles** (Google requires one to claim); the site publishes email-only contact by design. Adding the phone to the site is a copy/site decision (`Brand & Content` + `Website Engineer`), not a profile one — the asymmetry is deliberate and recorded in `nap-doctrine` §3, not an oversight. `ProfessionalService` is a LocalBusiness type, so the locality and service area are machine-readable — that is the point of the node. Verify with `python3 scripts/check-structured-data.py --url https://hummelllc.com/`; change values in `scripts/doctrine_nap.py` only after the doctrine changes.
- `sitemap.xml` + `robots.txt` at root.
- `assets/og-image.png` — social card (1200×630) generated from the FINAL logo (`HummelLLCLogo.png`, brief rev 4) on white with the trimmed logomark. `og:image` referenced from every page head.
- **Header logo payload (2026-09-28):** the header renders the logo at 46 px tall, so pages serve `assets/logo-46.png` (5.8 KB) / `assets/logo-93.png` (10 KB) via `srcset` instead of the 272 KB master `assets/logo.png` — that master is the brand source and is no longer referenced by any page. Found: every page view was downloading ~270 KB of pixels it discarded; full home page is now ~18 KB. Change the logo with `python3 scripts/make-logo-assets.py`, then `python3 scripts/optimize-logo.py`.
- Header brand = `assets/logo.png` (trimmed full logo, mark + wordmark) — kept as the brand source; the pages serve the two display-sized derivatives above. Favicons: `assets/favicon-32.png`, `assets/favicon-180.png` (apple-touch-icon), `favicon.ico` (16/32/48) — all H-monogram crops of the final logo, generated from the same source file. **Regenerate any of them with `python3 scripts/make-logo-assets.py`** — the script reads the source logo from iCloud (`~/Library/Mobile Documents/com~apple~CloudDocs/Hummelllc/HummelLLCLogo.png`, 1144×1104 RGBA). Only that file is the logo source; no derivatives without founder OK.

## DNS / launch facts

- Registrar + hosting account: GoDaddy (brief rev 4 — both confirmed; nameservers ns23/ns24.domaincontrol.com, parked as of 2026-09-25). The GoDaddy *hosting plan* stays unused — the site runs on GitHub Pages.
- Email MX today: Zoho (mx1–3.zoho.com) — `hello@hummelllc.com` **live and wired 2026-09-25** (mailbox created, no bounce on re-test; the form uses it).
- **Launch host: GitHub Pages — LOCKED by founder 2026-09-25, re-confirmed 2026-09-27** (founder decision "keep GitHub Pages"; no Cloudflare Pages migration, no API token needed). **Cutover DONE 2026-09-27, fully verified 2026-09-28:** apex A → four GitHub IPs, `www` CNAME → `brendanhummel.github.io`, custom domain `hummelllc.com`, Enforce HTTPS on, certificate `approved` for both hostnames. MX/TXT were preserved (Zoho mail intact). If the Pages certificate ever loses the `www` SAN, the fix is a one-off read-only visit to Settings → Pages in a browser — the REST API cannot re-order it (see LAUNCH-RUNBOOK.md §3).
- Full runbook lives in HUM-5 issue comments.

## Preflight / launch gate

Run this before launch and after any copy change — it is the guardrail net, so a regression can't ship quietly:

```bash
python3 scripts/preflight.py                                   # copy guardrails + structure + assets + launch config
python3 scripts/preflight.py --live https://hummelllc.com/     # + fetch every route and the served assets
python3 scripts/preflight.py --live https://hummelllc.com/ --dns   # + DNS vs the launch target
```

Exit code 0 = no FAIL. It checks: the site-copy §2 banned-word list (24/7 and always-on allowed only inside the approved negations), HIPAA/CJIS/NIST absent as credentials, no certs/client counts/revenue, both attributed market stats present, the pricing benchmark label, one `<h1>` per page, meta/canonical/OG/skip links, every internal link resolving on disk, sitemap/robots completeness, **no credentials on any page** (API-key/bearer/secret shapes; the analytics token must be the 32-hex public site token), the **header logo payload** (display-sized variants exist, are within a 24 KB budget, and no page references the 272 KB master), the **share-card + structured-data tags** (`twitter:card`, `og:site_name`, and the Home JSON-LD compared against `nap-doctrine` rev 3 key by key — locally and on the live page), and the three launch gates:

1. **Contact delivery configured** (`contact.js` `endpoint` or `email`) — otherwise the Engage form tells visitors delivery "goes live with launch", i.e. the site cannot take inquiries.
2. **Cloudflare Web Analytics beacon** live on all 6 pages (no `<TOKEN>` placeholder left).
3. **DNS** (`--dns`): apex A records at GitHub Pages, `www` CNAME at `brendanhummel.github.io`, and MX/TXT/SPF still intact (brief §7 — the Zoho mail must survive the web cutover). Also confirms no CAA record blocks the cert issuer.

WARNs (Cal.com booking URL still owed by the founder, parked DNS, the `© 2026 Hummel LLC` footer line) need a human decision, not a code fix — see the runbook for owner and severity.

> `404.html` keeps **root-absolute** refs on purpose (it is served at arbitrary depths in production). The staging URL lives under `/hummelllc.com/`, where those refs 404, so the page carries a small inline `<style>` fallback to stay readable there. Do not "fix" it to relative refs — they cannot work at arbitrary depth.