# hummelllc.com — Hummel LLC website

Static, no-build website for Hummel LLC. Deploys automatically to GitHub Pages on every push to `main`.

- Staging URL: `https://brendanhummel.github.io/hummelllc.com/`
- Production domain: `https://hummelllc.com/` (DNS cutover scheduled at launch, roadmap Day 26–30)

## Pages (brief §8 page map)

| File | Page |
|------|------|
| `index.html` | Home — "Your part-time IT leader." |
| `what-we-do.html` | What We Do |
| `who-its-for.html` | Who It's For |
| `how-it-works.html` | How It Works |
| `about.html` | About |
| `engage.html` | Engage |
| `404.html` | Not-found page |

## How to update content

Everything is plain HTML + one stylesheet. No build step, nothing to install.

1. Edit the page's `.html` file (e.g. open `about.html`, change a sentence, save).
2. Commit and push:
   ```bash
   git add -A && git commit -m "Update about copy" && git push
   ```
3. The GitHub Actions workflow (`Deploy to GitHub Pages`) publishes automatically (~1 min).
4. Verify at the staging URL; production follows at DNS cutover.

Shared page furniture (header/nav/footer) is duplicated per page intentionally — six pages, trivial to edit. If pages grow past ~10, migrate to a tiny template step (e.g. Eleventy) and this file documents that decision.

Design tokens (colors, radius, type) live in `assets/css/site.css` under `:root` — swap brand colors in one place when the Brand & Content Lead locks the treatment.

## Content rules (MANDATORY — see company brief §6)

- **Source of truth:** the company brief (`brief`, rev 2 — approved 2026-09-25). No copy ships that isn't in the brief.
- **Claim guardrails:** PCI environment experience: proven, may be stated plainly. HIPAA/CJIS/NIST: transferable awareness only — never claim certification or audit-level qualification. Market stats only as attributable, labeled estimates. Never imply 24/7 support or always-on ops (year one = advisor + scoped work, ~5 hrs/wk).
- Copy blocks awaiting Brand & Content Lead (HUM-6) are marked `<!-- COPY: ... -->` in the HTML. Contact details on `engage.html` are pending founder intake and must be filled before staging review.

## SEO & analytics

- Titles/descriptions/canonical/OpenGraph per page; canonical URLs point at the production domain.
- `sitemap.xml` + `robots.txt` live at site root.
- Analytics: provider TBD at stack approval (Plausible or Cloudflare Web Analytics). Until wired, `index.html` carries a placeholder comment — no tracking script ships without a decision.

## DNS / launch facts

- Registrar: GoDaddy (nameservers ns23/ns24.domaincontrol.com — parked A records as of 2026-09-25).
- Email MX today: Zoho (mx1–3.zoho.com).
- Cutover (launch): add custom domain in Pages settings + point DNS at GitHub Pages (A records 185.199.108.153/154/155/156 and/or the `hummelllc.com` CNAME to `brendanhummel.github.io`) — full runbook in HUM-5 comments.