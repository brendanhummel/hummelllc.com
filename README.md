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
- `scheduleUrl`: calendar link for the 30-minute intro call. While empty, the "Schedule a 30-minute intro call" button scrolls to the form.

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
| `scripts/set-analytics.py` | Installs the Cloudflare Web Analytics beacon on all 6 pages from a token or snippet. Idempotent; refuses account-credential-shaped input. |
| `scripts/set-contact.py` | Sets the Engage form's `endpoint` / `email` / `scheduleUrl` (Gate 1). `--email` requires `--verified`. `--show` prints the current config. |
| `scripts/test-contact-modes.js` | `node scripts/test-contact-modes.js` — runs the real `contact.js` in a small DOM shim and asserts what a visitor sees in each of the three transports. |
| `scripts/make-logo-assets.py` | Regenerates the header logo, favicons and OG card from the founder's `HummelLLCLogo.png`. |

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

## Preflight / launch gate

Run this before launch and after any copy change — it is the guardrail net, so a regression can't ship quietly:

```bash
python3 scripts/preflight.py                                   # copy guardrails + structure + launch config
python3 scripts/preflight.py --live https://brendanhummel.github.io/hummelllc.com/
python3 scripts/preflight.py --live <base> --dns               # + DNS vs the launch target
```

Exit code 0 = no FAIL. It checks: the site-copy §2 banned-word list (24/7 and always-on allowed only inside the approved negations), HIPAA/CJIS/NIST absent as credentials, no certs/client counts/revenue, both attributed market stats present, the pricing benchmark label, one `<h1>` per page, meta/canonical/OG/skip links, every internal link resolving on disk, sitemap/robots completeness, **no credentials on any page** (API-key/bearer/secret shapes; the analytics token must be the 32-hex public site token), and the three launch gates:

1. **Contact delivery configured** (`contact.js` `endpoint` or `email`) — otherwise the Engage form tells visitors delivery "goes live with launch", i.e. the site cannot take inquiries.
2. **Cloudflare Web Analytics beacon** live on all 6 pages (no `<TOKEN>` placeholder left).
3. **DNS** (`--dns`): apex A records at GitHub Pages, `www` CNAME at `brendanhummel.github.io`, and MX/TXT/SPF still intact (brief §7 — the Zoho mail must survive the web cutover). Also confirms no CAA record blocks the cert issuer.

WARNs (scheduling link, parked DNS, the `© 2026 Hummel LLC` footer line) need a human decision, not a code fix — see the runbook for owner and severity.

> `404.html` keeps **root-absolute** refs on purpose (it is served at arbitrary depths in production). The staging URL lives under `/hummelllc.com/`, where those refs 404, so the page carries a small inline `<style>` fallback to stay readable there. Do not "fix" it to relative refs — they cannot work at arbitrary depth.