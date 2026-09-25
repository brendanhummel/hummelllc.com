# Launch runbook — hummelllc.com

Key: `launch-runbook` · Owner: Website Engineer (HUM-5) · Written 2026-09-25
Build status: **complete and verified live on staging.** Two launch gates remain open, both needing a founder input (not engineering work). Everything else is copy-paste.

- Staging (verified today, commit `113d3c0`): https://brendanhummel.github.io/hummelllc.com/
- Repo: `brendanhummel/hummelllc.com` (public, branch-deploy from `main` — push = publish)
- Production target: `https://hummelllc.com/`

---

## 0. Where the build stands

| Item | State |
|---|---|
| 6 pages + 404, sitemap, robots | Live on staging, all 6 routes 200, unknown routes 404 with the custom page |
| Copy fidelity | Built verbatim from `site-copy` rev 2 (HUM-6), which traces to `brief` rev 2 §1–§5 |
| Claim guardrails (brief §6) | Scanned PASS: no HIPAA/CJIS/NIST anywhere; PCI stated plainly only; exactly two attributed market stats; 24/7 + always-on appear **only** in the approved negations; no certs, client counts, headcounts, revenue |
| Brand | P-A Slate & Sage locked palette; FINAL logo `HummelLLCLogo.png` wired into header, favicons, OG card (brief rev 4) |
| Mobile/a11y | Single `<h1>` per page, skip links, contrast ≥ 4.5:1, `prefers-reduced-motion` respected, no horizontal overflow measured at 390/768/1440 |
| Preflight gate | `python3 scripts/preflight.py --live <url> --dns` — run before launch; exits non-zero while a gate is open |
| **Gate 1 — contact delivery** | **OPEN.** Form is in "pre-launch" mode: it tells visitors delivery goes live with launch. The site cannot accept inquiries until this is set. |
| **Gate 2 — analytics token** | **OPEN.** Cloudflare Web Analytics locked as provider; beacon slot in every page head, token not yet pasted. Site works without it — but shipping without analytics means launch traffic is unmeasurable. |
| DNS cutover | Not started (correct — it is the launch step, days 26–30) |

---

## 1. Gate 1 — contact delivery (blocks launch)

`assets/js/contact.js` has one config object with three transports. **Set one and the site can take inquiries.** Nothing else changes.

```js
window.HUMMEL_CONTACT = {
  endpoint: "",     // → mode 1: form provider
  email: "",        // → mode 2: mailto (only once the mailbox is confirmed live)
  scheduleUrl: ""   // → the intro-call button
};
```

Verified today (2026-09-25) by DNS on `hummelllc.com`:

- MX = `mx.zoho.com` (10), `mx2.zoho.com` (20), `mx3.zoho.com` (50) — Zoho Mail is the mail host
- SPF present; DKIM present (`zoho._domainkey`); DMARC `p=quarantine` with reports to `brendan@hummelllc.com`
- So mail *delivery to the domain works*. What is unconfirmed is whether a **`hello@` mailbox/alias actually exists** — `brief` rev 4 §7 says hello@/admin@ routing "can be set up in Zoho", i.e. intended, not confirmed.

**Owner: Brand & Content Lead (Zoho routing), with the founder for the test.** Ask / action:

1. Confirm (or create) `hello@hummelllc.com` in Zoho Mail, and set a catch-up rule or forward if the founder prefers `brendan@`.
2. **60-second proof:** send one email from any account to `hello@hummelllc.com` and confirm it arrives (a bounce means no mailbox).
3. Tell me it is live → I set `email: "hello@hummelllc.com"` in one line, push, and the form opens the visitor's mail app pre-filled. No third-party account needed, no monthly cost.

Alternative if the founder prefers a real submitted-form inbox: create a free Formspree account (or Netlify Forms / a Cloudflare Pages function), send me the form URL, and I set `endpoint` instead — same one-line change, and then the form posts in-page instead of opening a mail app. Either is fine; `email` is the zero-dependency path.

While this is open, visitors submitting the form are told delivery arrives with launch. That is honest, but it is not a launch state — **do not announce the site publicly until Gate 1 is set.**

---

## 2. Gate 2 — Cloudflare Web Analytics token (2 minutes, founder)

Locked provider (founder, 2026-09-25): Cloudflare Web Analytics — free, cookie-free, so no consent banner.

1. Create/sign in at https://dash.cloudflare.com → **Analytics & Logs → Web Analytics → Add a site** → `hummelllc.com`.
2. Copy the JS snippet it shows (it contains a `token`).
3. **Either** paste it into the `ANALYTICS SLOT` comment at the top of each page's `<head>` (search for `ANALYTICS SLOT` — all 6 pages have one, with the exact snippet pre-written and only the token missing), **or** send me the token and I will wire it in one pass and redeploy.

Verification after wiring: `python3 scripts/preflight.py --live <url>` flips Gate 2 from FAIL to ok.

---

## 3. DNS cutover (the launch step — days 26–30)

**Launch host: GitHub Pages (locked).** Registrar + DNS: GoDaddy (`ns23/ns24.domaincontrol.com`). No nameserver move, no registrar change.

Verified DNS state today (2026-09-25):

| Record | Now | At launch |
|---|---|---|
| `@` A | `3.33.130.190`, `15.197.148.33` (GoDaddy parking) | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| `www` | CNAME → `hummelllc.com` (follows the apex) | CNAME → `brendanhummel.github.io` |
| MX | Zoho mx/mx2/mx3 | **UNCHANGED — do not touch** |
| TXT | SPF + Zoho includes | **UNCHANGED — do not touch** |
| CAA | none present | leave absent — cert issuance unrestricted (checked: nothing blocks the Pages cert issuer) |

**Order matters.** DNS first, custom domain second — GitHub only provisions the TLS certificate once the domain already resolves to it.

1. GoDaddy → **My Products → hummelllc.com → DNS** → edit the `@` A records to the four GitHub IPs; add/replace a `www` **CNAME** → `brendanhummel.github.io`. Delete only the parking A records. Leave every MX/TXT record exactly as it is.
2. GitHub → repo `hummelllc.com` → **Settings → Pages → Custom domain** → enter `hummelllc.com` → Save. (Ticking **Enforce HTTPS** is safe once the certificate shows as issued; it can take up to ~24h, usually minutes.)
3. Verify: `https://hummelllc.com/` and `https://www.hummelllc.com/` both load with a valid certificate; the old staging URL redirects to the domain; then run `python3 scripts/preflight.py --live https://hummelllc.com/ --dns` — expect **no FAIL**.
4. Post-cutover smoke test: all 6 pages, the form submit, one email to `hello@`, and `curl -I https://hummelllc.com/what-we-do/` for a 200.

**Rollback:** revert step 1 (restore the two GoDaddy parking A records, drop the `www` CNAME). Email is untouched throughout, so rollback cannot break mail. The staging URL keeps serving either way.

Owner: founder (GoDaddy access — I have no registrar credentials and will not ask for them in chat). I drive the GitHub-side setting and run the verification. Founder access is needed only for step 1.

---

## 4. Open WARN items (not launch blockers, need a human call)

1. **Scheduling link** — `scheduleUrl` empty, so "Schedule a 30-minute intro call" scrolls to the form instead of booking. Give me a calendar URL (e.g. Cal.com / Google Appointment) and it is a one-line change. Owner: founder.
2. **Footer `© 2026 Hummel LLC`** — this is verbatim approved copy (`site-copy` §3.7), written *before* `brief` rev 4 §7 added the legal-name guardrail: the LLC is **not filed**, and "do not use 'LLC' as a legal-entity claim in fine print" is exactly what an ownership notice does. Trade-name usage is allowed, the README calls it fine, and I do not invent or rewrite legal text — so it ships as approved. Flagging for a Brand & Content / founder decision: keep it, or swap to something like `© 2026 Hummel Technologies` / `© 2026 B. Hummel` until formation. One-line change either way.
3. **Hosting account is GoDaddy, launch host is GitHub Pages** — the GoDaddy hosting plan sits unused (brief rev 4 §7 says hosting account = GoDaddy; the founder separately locked GitHub Pages in the stack decision). I recommend staying on Pages: free, repo-backed, no build step, and the current staging URL simply becomes production. Moving to GoDaddy hosting would mean a rebuild/redeploy path with no launch benefit. Flagging for visibility — Chief of staff's call if the founder wants the paid plan used.
4. **Mailbox existence for `hello@`** — see Gate 1; unverifiable from this machine (outbound SMTP port 25 is blocked here, so I cannot probe the MX directly). Requires the 60-second send test above.

---

## 5. Updating content after launch

Plain HTML, no build step: edit the page file → `git add -A && git commit -m "…" && git push` → live in about a minute. Then run `python3 scripts/preflight.py --live https://hummelllc.com/ --dns` to confirm nothing regressed — in particular that the guardrail words, the two attributed stats, and the relative internal links are still intact. Internal links must stay relative (see README); `404.html` is the deliberate exception and carries an inline style fallback so it also reads correctly on the staging subpath.

Guardrail reminder for whoever edits copy: the site's words come from `brief` and `site-copy` only. New claims require a brief update first.