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
| **Gate 1 — contact delivery** | **OPEN — the chosen address does not exist.** Founder chose `hello@hummelllc.com` (2026-09-25); a live delivery test bounced twice with a hard `550 5.1.1 User does not exist` from `mx.zoho.com`. Form is held in "pre-launch" mode on purpose — see §1. `brendan@hummelllc.com` **was** accepted with no bounce in the same test. |
| **Gate 2 — analytics token** | **OPEN — waiting on the founder's snippet.** Founder confirmed Cloudflare Web Analytics and chose to send the JS snippet; nothing needed on the code side beyond pasting it. Site works without it, but launch traffic is unmeasurable. |
| Copyright line (`© 2026 Hummel LLC`) | **RESOLVED 2026-09-25 — founder chose KEEP**, as approved copy (trade-name usage; LLC not filed). Remains a preflight WARN so it re-surfaces at LLC formation. |
| DNS cutover | Not started (correct — it is the launch step, days 26–30) |

---

## 1. Gate 1 — contact delivery (blocks launch) — the chosen address BOUNCES

**Do not publish `hello@hummelllc.com`.** Founder selected it on 2026-09-25 and I wired it immediately, then tested real delivery before believing it. **Two independent sends bounced with a hard `550 5.1.1 User does not exist`** from `mx.zoho.com` (136.143.191.44, the server for `hummelllc.com`) at 16:38 and 16:42 EDT on 2026-09-25. Full diagnostic:

```
Final-Recipient: rfc822; hello@hummelllc.com
Action: failed
Status: 5.1.1
Remote-MTA: dns; mx.zoho.com.
Diagnostic-Code: smtp; 550 5.1.1 User does not exist - <hello@hummelllc.com>
```

Same test, same minute: **`brendan@hummelllc.com` was accepted by Zoho with no bounce** (consistent with the domain's DMARC report address). So the domain's mail is working — the `hello@` mailbox simply is not there.

I reverted the change. The form is back in pre-launch mode because a `mailto:` to a dead address is worse than no transport at all: the visitor's mail app opens, the mail bounces to *them*, and the inquiry is lost silently while the page looks like it works. Publishing a contact address is a founder decision, so I did not swap in `brendan@` on my own.

**Unblock — pick one, and I wire it in one line:**

1. **Create `hello@hummelllc.com` in Zoho Mail** (Zoho Mail admin → Users or Aliases for the `hummelllc.com` org; an alias on `brendan@` is fine). Then say so and I re-test within seconds — the bounce comes back in ~2 s, so this is a fast loop. Note: the domain's MX already point at Zoho, so if a mailbox is not appearing, check the mailbox is in the *same* Zoho org the domain is verified under.
2. **Publish `brendan@hummelllc.com` instead** — already proven to accept mail. One-line change here, **plus** a copy change from Brand & Content: `site-copy` §3.6 names `hello@` in the fallback text, and `contact.js` mode-1 error text mentions it too.
3. **Use a form provider** (`endpoint`) — Formspree / Netlify Forms / a Cloudflare Pages function. Then no mailbox is on the critical path at all, and the in-page experience is better than a mailto.

Config object (unchanged shape, three transports):

```js
window.HUMMEL_CONTACT = {
  endpoint: "",     // → mode 1: form provider
  email: "",        // → mode 2: mailto (ONLY once a real send test shows no bounce)
  scheduleUrl: ""   // → the intro-call button
};
```

**Reproduce the check in 60 seconds:** send one email from any external account to the address, wait two minutes, and confirm `mailer-daemon` did not answer. Outbound SMTP is blocked from this machine (ports 25 and 587 both time out), which is why the test has to go through a real mail client.

While this is open, visitors submitting the form are told delivery arrives with launch. That is honest, but it is not a launch state — **do not announce the site publicly until Gate 1 is set.**

---

## 2. Gate 2 — Cloudflare Web Analytics token (2 minutes, founder)

Locked provider (founder, 2026-09-25): Cloudflare Web Analytics — free, cookie-free, so no consent banner.

> **No API token is needed. Not a read token, not a write token, none.**
> Web Analytics is set up with a **site token** that ships inside the public JS
> snippet — it is visible in the page source of every site that uses it, so it
> grants no account permissions and cannot read or change anything. Do not
> create an API token, do not paste an API key anywhere, and do not send a
> Cloudflare password. `hummelllc.com` does **not** need to be added as a
> Cloudflare zone and its DNS stays at GoDaddy — the snippet is the manual
> installation path for a site Cloudflare does not host.
> (An API token would only be relevant if we ever moved *deployments* onto
> Cloudflare Pages — we did not; launch host is GitHub Pages, §3. If that ever
> changes, the ask would be a scoped `Cloudflare Pages: Edit` token, never a
> global key.)

1. Create/sign in at https://dash.cloudflare.com → **Analytics & Logs → Web Analytics → Add a site** → hostname `hummelllc.com` → **Done** (skip any offer to change nameservers).
2. Open **Manage site** and copy the JS snippet it shows (it contains `"token": "…"`). If prompted, choose **Enable with JS Snippet installation** — not the automatic option, which only works for zones proxied through Cloudflare.
3. **Either** paste it into the `ANALYTICS SLOT` comment at the top of each page's `<head>` (search for `ANALYTICS SLOT` — all 6 pages have one, with the exact snippet pre-written and only the token missing), **or** send me just the snippet/token and I will wire it in one pass and redeploy. The token is public data, so sharing it is harmless either way.

Verification after wiring: `python3 scripts/preflight.py --live <url>` flips Gate 2 from FAIL to ok. Data can lag the first pageview by ~10 minutes; a beacon POST returning `204` means it is working.

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
2. **Footer `© 2026 Hummel LLC`** — **RESOLVED 2026-09-25: founder reviewed and chose KEEP.** It is verbatim approved copy (`site-copy` §3.7), trade-name usage is allowed, and the LLC is not filed. I do not invent or rewrite legal text, so it ships as approved. The preflight WARN was kept deliberately (re-worded to record the decision) so the line re-surfaces when the LLC is actually formed — at that point the notice becomes accurate and the WARN can be retired.
3. **Hosting account is GoDaddy, launch host is GitHub Pages** — the GoDaddy hosting plan sits unused (brief rev 4 §7 says hosting account = GoDaddy; the founder separately locked GitHub Pages in the stack decision). I recommend staying on Pages: free, repo-backed, no build step, and the current staging URL simply becomes production. Moving to GoDaddy hosting would mean a rebuild/redeploy path with no launch benefit. Flagging for visibility — Chief of staff's call if the founder wants the paid plan used.
4. **`hello@hummelllc.com` does not exist** — ~~unverifiable from this machine~~ **now tested and it FAILS**: hard `550 5.1.1 User does not exist` from `mx.zoho.com`, twice. See §1. Outbound SMTP is blocked from this machine (ports 25/587 time out), so the test ran through a real mail client instead. `brendan@hummelllc.com` was accepted with no bounce in the same run.

---

## 5. Updating content after launch

Plain HTML, no build step: edit the page file → `git add -A && git commit -m "…" && git push` → live in about a minute. Then run `python3 scripts/preflight.py --live https://hummelllc.com/ --dns` to confirm nothing regressed — in particular that the guardrail words, the two attributed stats, and the relative internal links are still intact. Internal links must stay relative (see README); `404.html` is the deliberate exception and carries an inline style fallback so it also reads correctly on the staging subpath.

Guardrail reminder for whoever edits copy: the site's words come from `brief` and `site-copy` only. New claims require a brief update first.