# Launch runbook — hummelllc.com

Key: `launch-runbook` · Owner: Website Engineer (HUM-5) · Written 2026-09-25 · Updated 2026-09-28 (**rev 7** — post-launch payload + SEO pass, §6)
Build status: **COMPLETE AND LIVE IN PRODUCTION.** Both founder-input gates are **CLOSED** (Gate 1 contact delivery 2026-09-25; Gate 2 analytics 2026-09-25), the three launch-window decisions are **ANSWERED** (founder, 2026-09-27 — §0.1), and the **DNS cutover is done and verified** (HUM-11, 2026-09-27/28): `https://hummelllc.com/` serves the real site on a valid Let's Encrypt certificate that now covers **both** `hummelllc.com` and `www.hummelllc.com`, with mail (MX/SPF) intact. `python3 scripts/postcutover.py` → **PRODUCTION VERIFIED — 19 ok, 0 warn, 0 fail**. The only item left in §3 is one human action: send a real email to `hello@hummelllc.com` and confirm it lands.

- Staging (verified 2026-09-27, `main` @ `9b3c9c1`): https://brendanhummel.github.io/hummelllc.com/
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
| **Gate 1 — contact delivery** | **CLOSED 2026-09-25.** Founder created `hello@hummelllc.com` in Zoho and asked for a re-test; the re-test passed (two independent sends 17:08 EDT, no bounce after 9+ minutes — the *same* test had bounced in ~2 s twice at 16:38/16:42 while the mailbox was missing). `email: "hello@hummelllc.com"` is wired and live. See §1. |
| **Gate 2 — analytics token** | **CLOSED 2026-09-25.** Founder supplied the Cloudflare Web Analytics JS snippet containing the **public site token** (`382b5c…288d`). Wired into all 6 pages with `python3 scripts/set-analytics.py --snippet '…'`; `preflight.py` now reports "analytics beacon live on all pages". No API token was ever needed. See §2. |
| Copyright line (`© 2026 Hummel LLC`) | **RESOLVED 2026-09-25 — founder chose KEEP**, as approved copy (trade-name usage; LLC not filed). Remains a preflight WARN so it re-surfaces at LLC formation. |
| Scheduling link (`scheduleUrl`) | **DEFERRED BY THE FOUNDER 2026-09-28** — card `1ba38904` answered `not_yet` ("Not created yet — ask me again after cutover"). Cal.com remains the chosen provider (§0.1); the intro-call button keeps scrolling to the tested form, which is a **recorded choice, not an open question**. Wiring is still one command the moment the public URL exists (`scripts/set-contact.py --schedule <url>`, §4.1); preflight keeps the WARN deliberately, re-worded to carry the decision so it re-surfaces. Follow-up tracked as **HUM-13**. |
| DNS cutover | ✅ **CUTOVER COMPLETE AND FULLY VERIFIED 2026-09-28** — apex A → four GitHub IPs, `www` CNAME → `brendanhummel.github.io`, custom domain set, Enforce HTTPS on, **and the Pages certificate now covers both hostnames** (the last residual — the apex-only SAN — was resolved 2026-09-28 by the read-only Settings → Pages visit in §3). **`https://hummelllc.com/`: 200, valid cert. `https://www.hummelllc.com/`: valid cert, 301 → the secure canonical. All 6 routes 200 + beacon, mail intact.** `postcutover.py` → **PRODUCTION VERIFIED — 19 ok, 0 warn, 0 fail**. Tracked as **HUM-11**. |
| Post-launch payload + SEO pass | ✅ **DONE 2026-09-28 (§6).** Header logo 271,913 B → 9,990 B per page view (full home page ~280 KB → **17,833 B**); master retained as the brand source but referenced by no page; share-card tags added, plus a doctrine-exact `ProfessionalService` JSON-LD node (HUM-12); preflight now guards both. |

### 0.1 Launch-window decisions — ANSWERED (founder, 2026-09-27)

Card `979231b4-d260-4626-84f6-45a5f491b7df` ("Three launch-window decisions before cutover") was answered on 2026-09-27:

| Decision | Answer | What it changes in the build |
|---|---|---|
| Intro-call booking link | **Cal.com free plan** (`cal_com`), then **deferred 2026-09-28** (`not_yet`, card `1ba38904`) | The provider choice stands; the public URL does not exist yet, so **nothing changes in the build** — the button keeps scrolling to the tested form and the WARN is kept deliberately, carrying the decision. One command wires it whenever the URL appears (§4.1); re-raised as **HUM-13** once analytics show real traffic. |
| Launch hosting | **Keep GitHub Pages** (`keep_gh_pages`) | No change — staging URL becomes production at cutover (§3). The GoDaddy hosting plan stays unused; no migration, no extra credential. Founder is to revoke any Cloudflare API token created for this work (§2). |
| Engage form transport | **Keep `mailto:`** (`keep_mailto`) | No change — `hello@hummelllc.com` (Gate 1, §1) stays. Accepted trade-off, recorded in §4.2: a visitor with no configured mail client cannot send; revisit after launch when analytics show real traffic. |

---

## 1. Gate 1 — contact delivery — **CLOSED 2026-09-25**

**RESOLVED — the address is live and wired.** The founder created the `hello@hummelllc.com` mailbox in Zoho on 2026-09-25 and asked for a re-test. Re-test result: **two independent sends at 17:08 EDT (from the founder's Gmail and iCloud accounts via Mail.app) produced no bounce after 9+ minutes**, checked across every account's INBOX/Junk/Spam. The identical test had bounced twice in ~2 seconds earlier the same day while the mailbox was missing, so the address now accepts mail. Both test messages were confirmed in the accounts' Sent mailboxes and the outbox drained to 0.

Wired live with `python3 scripts/set-contact.py --email hello@hummelllc.com --verified` — `email: "hello@hummelllc.com"` in `assets/js/contact.js`, deployed, and `preflight.py` now reports Gate 1 **ok** (the transport line reads `contact transport configured (mailto: hello@hummelllc.com)`).

Residual check (owner: founder, ~1 minute, not a launch blocker): because the transport is a `mailto:`, the visitor's own mail client does the sending — so confirm one message actually *arrives* in the Zoho mailbox (write to `hello@` from any outside account and see it land). If mail to `hello@` ever starts bouncing again, do **not** leave it published: `python3 scripts/set-contact.py --clear` puts the form back in pre-launch mode in one command.

**History — why the form was held in pre-launch mode.** Founder selected it on 2026-09-25 and I wired it immediately, then tested real delivery before believing it. **Two independent sends bounced with a hard `550 5.1.1 User does not exist`** from `mx.zoho.com` (136.143.191.44, the server for `hummelllc.com`) at 16:38 and 16:42 EDT on 2026-09-25. Full diagnostic:

```
Final-Recipient: rfc822; hello@hummelllc.com
Action: failed
Status: 5.1.1
Remote-MTA: dns; mx.zoho.com.
Diagnostic-Code: smtp; 550 5.1.1 User does not exist - <hello@hummelllc.com>
```

Same test, same minute: **`brendan@hummelllc.com` was accepted by Zoho with no bounce** (consistent with the domain's DMARC report address). So the domain's mail is working — the `hello@` mailbox simply is not there.

I reverted the change. The form is back in pre-launch mode because a `mailto:` to a dead address is worse than no transport at all: the visitor's mail app opens, the mail bounces to *them*, and the inquiry is lost silently while the page looks like it works. Publishing a contact address is a founder decision, so I did not swap in `brendan@` on my own.

**Unblock menu — kept for reference; option 1 is what happened:**

1. **Create `hello@hummelllc.com` in Zoho Mail** (Zoho Mail admin → Users or Aliases for the `hummelllc.com` org; an alias on `brendan@` is fine). Then say so and I re-test within seconds — the bounce comes back in ~2 s, so this is a fast loop. Note: the domain's MX already point at Zoho, so if a mailbox is not appearing, check the mailbox is in the *same* Zoho org the domain is verified under. Wire it with `python3 scripts/set-contact.py --email hello@hummelllc.com --verified`.
2. **Publish `brendan@hummelllc.com` instead** — already proven to accept mail. `python3 scripts/set-contact.py --email brendan@hummelllc.com --verified`. No copy change is needed any more: the visitor-facing text is derived from the configured `email`, so the address lives in exactly one place (2026-09-25 changed the form's pre-launch line from naming `hello@` to naming no address at all — flagged to Brand & Content as UI text, not approved copy).
3. **Use a form provider** (`endpoint`) — Formspree / Netlify Forms / a Cloudflare Pages function. Then no mailbox is on the critical path at all, and the in-page experience is better than a mailto. `python3 scripts/set-contact.py --endpoint https://…`.

`--email` will not publish an address without `--verified`: it refuses, because a dead mailbox silently eats inquiries.

Config object (unchanged shape, three transports; edit via `scripts/set-contact.py`, never by hand):

```js
window.HUMMEL_CONTACT = {
  endpoint: "",     // → mode 1: form provider
  email: "",        // → mode 2: mailto (ONLY once a real send test shows no bounce)
  scheduleUrl: ""   // → the intro-call button
};
```

**Reproduce the check in 60 seconds:** send one email from any external account to the address, wait two minutes, and confirm `mailer-daemon` did not answer. Note on tooling (verified 2026-09-25): outbound port 25 from this machine times out, so an SMTP-level RCPT probe is not possible; port 587 connects but sending needs account credentials, which I do not hold and will not ask for. The test therefore runs through Mail.app's already-authenticated accounts (AppleScript), and bounces are read back from the accounts' INBOX/Junk/Spam.

The form is no longer in pre-launch mode — it opens a pre-filled mail app addressed to `hello@hummelllc.com`. What that changes for launch: the site **can now take an inquiry**, so Gate 1 no longer blocks announcement. Announcing is still gated on the roadmap (Gate 2 snippet + the DNS cutover, days 26–30) and on the founder's call.

---

## 2. Gate 2 — Cloudflare Web Analytics token — **CLOSED 2026-09-25**

**RESOLVED.** The founder posted the Cloudflare Web Analytics JS snippet; it carried the public site token, which is all this needed. Installed on all six pages in one pass:

```bash
python3 scripts/set-analytics.py --snippet '<script … data-cf-beacon='"'"'{"token": "382b5ca9…"}'"'"'></script>'
```

`preflight.py` now reports `ok analytics beacon live on all pages`. Committed and pushed; GitHub Pages redeploys on push, so the beacon is live on staging as soon as the build finishes (~1 minute). Data lags the first pageview by ~10 minutes; a beacon POST returning `204` means it is working.

**One cleanup item for the founder (not a launch blocker).** The same note said the API information was saved as `CloudFlareAPI.txt` in the iCloud folder `Hummelllc`. That file was **not found on this machine** (`~/Library/Mobile Documents/com~apple~CloudDocs/Hummelllc/` holds only `HummelLLCLogo.png`), so nothing was read from it and nothing from it was used. Nothing in this build needs a Cloudflare API token or API key — Web Analytics is installed by the public snippet alone, DNS stays at GoDaddy, and the host is GitHub Pages. **If a Cloudflare API token was created for this work, revoke it** (dash.cloudflare.com → My Profile → API Tokens) and delete the note. If the file does appear in iCloud later, treat it as an account credential: do not paste it into an issue comment, chat, or this repo — `scripts/set-analytics.py` and `scripts/preflight.py` both refuse credential-shaped input, and preflight fails the build if a page ever carries one.

Original instructions (kept for reference):

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
3. **Either** paste it into the `ANALYTICS SLOT` comment at the top of each page's `<head>` (search for `ANALYTICS SLOT` — all 6 pages have one, with the exact snippet pre-written and only the token missing), **or** send me just the snippet/token and I will wire it in one pass and redeploy — one command does all six pages:

   ```bash
   python3 scripts/set-analytics.py --snippet-file snippet.txt    # or --token <32-hex value>
   ```

   The token is public data, so sharing it is harmless either way. The script is idempotent, replaces the placeholder instead of duplicating it, and refuses account-credential-shaped input (`scripts/preflight.py` also fails the build if a page carries one).

Verification after wiring: `python3 scripts/preflight.py --live <url>` flips Gate 2 from FAIL to ok. Data can lag the first pageview by ~10 minutes; a beacon POST returning `204` means it is working.

---

## 3. DNS cutover (the launch step — days 26–30)

**Launch host: GitHub Pages — confirmed again by the founder 2026-09-27** (`keep_gh_pages`: no migration, no Cloudflare credential). Registrar + DNS: GoDaddy (`ns23/ns24.domaincontrol.com`). No nameserver move, no registrar change.

**Cutover status (re-verified live 2026-09-27 20:10 EDT):**

| Record | Before (2026-09-25) | Now |
|---|---|---|
| `@` A | `3.33.130.190`, `15.197.148.33` (GoDaddy parking) | ✅ **DONE** — `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| `www` | CNAME → `hummelllc.com` (follows the apex) | ✅ **DONE 2026-09-27** — CNAME → `brendanhummel.github.io` (founder, GoDaddy; verified at the authoritative nameserver and via the system resolver) |
| MX | Zoho mx/mx2/mx3 | **UNCHANGED — do not touch** (still 3 records) |
| TXT | SPF + Zoho includes | **UNCHANGED — do not touch** (SPF intact) |
| CAA | none present | leave absent — cert issuance unrestricted (checked: nothing blocks the Pages cert issuer) |

**Live state (re-verified 2026-09-27 21:20 EDT / 2026-09-28 01:20 UTC — production verified, 0 fail):**

- `https://hummelllc.com/` → **200, valid Let's Encrypt certificate** (SAN `hummelllc.com`, `www.hummelllc.com`); all 6 routes 200 with the analytics beacon; canonical tags correct.
- `https://www.hummelllc.com/` → ✅ **valid certificate, 301 → `https://hummelllc.com/`** (single hop, straight to the secure canonical). No hostname-verification error any more.
- `http://hummelllc.com/` and `http://www.hummelllc.com/` → **301 → `https://hummelllc.com/`** (Enforce HTTPS is ON).
- DNS unchanged from the cutover and still correct: four apex A records, `www` CNAME → `brendanhummel.github.io`, 3 Zoho MX + SPF intact, no CAA record.
- GitHub Pages (API): `cname = hummelllc.com`, `https_enforced = true`, `https_certificate.state = approved`, **`domains = [hummelllc.com, www.hummelllc.com]`**, `expires_at = 2026-12-26`; the repo carries a `CNAME` file containing `hummelllc.com` (committed by GitHub, `55ef060`).

**RESOLVED 2026-09-28 — the www SAN gap (history, kept for the next time it happens).** After the cutover the Pages certificate covered the apex only, so `https://www.hummelllc.com/` failed hostname verification while everything else about www was correct. That is a GitHub Pages behaviour, not a misconfiguration (independently reported in GitHub community discussion [#206519](https://github.com/orgs/community/discussions/206519) — same shape: four apex A records, `www CNAME <user>.github.io`, cert `domains: ["apex"]` only). Tried and **ineffective**: re-saving the same custom domain; removing and re-adding it (GitHub matched the identical apex-only cert, same expiry); a Pages rebuild; `GET /repos/…/pages/health`. **What worked, in one step:** loading **Settings → Pages in the browser once, read-only** (no Save, no Remove, no field change) and letting the page's own *DNS Check* finish. Observed live on 2026-09-28: the panel went `DNS Check in Progress` + *"TLS certificate is being provisioned… 1 of 3 Certificate Requested: Authorization created"* → **`DNS check successful`**, the certificate API flipped to `approved` with **both** SANs within ~4 minutes, the `Enforce HTTPS` checkbox re-enabled already ticked, and `https://www.hummelllc.com/` began answering **301 with a valid certificate**. Re-checked after: all four Pages IPs individually serve the two-SAN cert (`ssl_verify_result=0`), and 10 consecutive requests from the system resolver agreed. **Lesson: for a Pages custom domain, the browser settings page is the thing that (re)orders the certificate — the REST API cannot.** If it ever regresses, the fix is that same read-only visit, then `python3 scripts/postcutover.py`.

**Contingency if it regresses anyway**, in order of preference: (1) leave it — the launch is unaffected for anyone who types `hummelllc.com` or follows an `http://www` link, both of which land on the secure canonical in one hop; (2) front the domain with Cloudflare in proxied mode (fixes apex + www TLS in one move, adds CDN/caching) — but that is a nameserver move and a new account, so it contradicts the `keep_gh_pages` decision and needs an explicit founder call; (3) open a GitHub support ticket referencing discussion #206519.

**Order matters.** DNS first, custom domain second — GitHub only provisions the TLS certificate once the domain already resolves to it.

1. GoDaddy → **My Products → hummelllc.com → DNS** → edit the `@` A records to the four GitHub IPs (**done 2026-09-27**); change the `www` **CNAME** → `brendanhummel.github.io`. Delete only the parking A records. Leave every MX/TXT record exactly as it is.

   **Field-level detail for the `www` CNAME — the GoDaddy DNS form is `Type / Name / Value / TTL`:**

   | Field | What to put | Why |
   |---|---|---|
   | Type | `CNAME` | the www hostname is an alias, not an IP |
   | **Name** | **`www`** | just the subdomain label — the placeholder reads "blog or shop" because GoDaddy appends `.hummelllc.com` for you. `www.hummelllc.com` or `@` here are both wrong (`@` would try to CNAME the apex, which collides with MX/SPF and is not what Pages wants) |
   | Value | `brendanhummel.github.io` | the documented Pages target — **no** `https://`, **no** trailing dot, **no** trailing slash |
   | TTL | `1/2 Hour` (default) | fine; TTL only affects how fast the change propagates |

   **Edit the existing row, do not add a second one.** The zone already contains a `www` CNAME whose Value is `hummelllc.com` (GoDaddy's parking default, "follow the apex") — it will be listed with a Data/Value of `@` or `hummelllc.com`. Two CNAMEs on the same name is an invalid zone and will break www. Use the pencil on that row. **Do not touch the MX or TXT rows** — mail depends on them.

2. GitHub → repo `hummelllc.com` → **Settings → Pages → Custom domain** → enter `hummelllc.com` → Save. **DONE 2026-09-27** (via the Pages API; GitHub committed a `CNAME` file to the repo). **Enforce HTTPS: ON** (2026-09-27) — `http://hummelllc.com/` and `http://www.hummelllc.com/` both 301 to `https://hummelllc.com/`. **Certificate: `approved` for both hostnames since 2026-09-28** (see the www SAN note above). Enforce HTTPS only ever becomes unsafe if the certificate stops covering a hostname it redirects to, so re-check it with `postcutover.py` after any DNS or Pages-settings change.

   **Reading the Settings → Pages panel — what is normal, and what (if anything) is yours to do.** The founder asked about exactly this panel on **HUM-11, 2026-09-27 21:18 EDT**, with a screenshot showing the *in-between* state, so here is the decoder. Every row below is something I have observed live on this domain:

   | What the panel says | Means | Action for you |
   |---|---|---|
   | `Your site is live at https://hummelllc.com/` | Pages is serving the **custom domain**, not `github.io` — the cutover is real | none |
   | `Last deployed by brendanhummel … ago` | time of the last `git push` to `main` | none |
   | `DNS check successful` (green check) | the four apex A records **and** the `www` CNAME match what Pages expects | none |
   | `TLS certificate is being provisioned. This may take up to 15 minutes` + `n of 3` | GitHub is ordering the Let's Encrypt cert. **Normal transient state.** | none — it finishes on its own |
   | `Certificate Active … allow up to 30 minutes to 1 hour for it to be globally available` | cert issued; some resolvers/browsers still cache the old one | none; if a browser still warns, restart it |
   | `Enforce HTTPS` **greyed out / unticked** + `Not yet available… allow 24 hours` | the checkbox stays locked until the cert finishes issuing. **This is not a task for you.** | none — it re-enables already ticked |
   | `Unverified domain` banner / red `DNS check failed` | the only genuinely actionable case | see the TXT contingency below |

   Observed on this domain: at **21:18 EDT** the panel showed *provisioning + Enforce HTTPS greyed*; within minutes it read `DNS check successful`, and at **21:30 EDT** the API confirmed `https_certificate.state = approved` with **both** SANs and **`https_enforced = true`** — no founder action in between. **If the panel still looks greyed, hard-refresh it (`⌘⇧R`); the API is the authority, not the cached page.** When the panel and the checks disagree, trust `python3 scripts/postcutover.py`.

3. Verify: `https://hummelllc.com/` and `https://www.hummelllc.com/` both load with a valid certificate; the old staging URL redirects to the domain; then run the one-command production check:

   ```
   python3 scripts/postcutover.py
   ```

   It gates DNS (all four apex A records + `www` CNAME + MX/SPF survived), the live TLS certificate on both hostnames, all 6 routes, the canonical tags, the analytics beacon, the `curl -I` HEAD check, and the engage form — then hands off to `preflight.py --live https://hummelllc.com/ --dns`. Expect `PRODUCTION VERIFIED … 0 fail`. **Run it before the cutover and it fails on purpose** — that is how the gate proves it can see the difference (verified 2026-09-25 pre-cutover: 12 fail, and it correctly caught the parking page).

   > **A green padlock is not proof of launch.** GoDaddy's parking page already serves a *valid* `hummelllc.com` certificate (issuer: GoDaddy.com), so `https://hummelllc.com/` looks healthy today and returns HTTP 200 — it is just someone else's page. Only the DNS + route checks below distinguish the two; the cutover cert must be issued by GitHub Pages' issuer and the four A records must match exactly.

4. Post-cutover smoke test: all 6 pages, the form submit, one email to `hello@`, and `curl -I https://hummelllc.com/what-we-do/` for a 200. **Automated parts DONE and green 2026-09-28** — all 6 routes 200, the `curl -I` HEAD check 200, the engage transport verified against the JS the browser actually loads. **One human action remains:** send a real email to `hello@hummelllc.com` and confirm it lands (no bounce) — the same check that closed Gate 1 on 2026-09-25, repeated now that the DNS cutover has happened, since MX/SPF were verified intact but only a real send proves the path end-to-end.

**Gate fix 2026-09-27 — the engage check was reading the wrong place.** `check_engage_form()` looked for `hello@hummelllc.com` in the `/engage/` **HTML**, but the address lives in `assets/js/contact.js` (the page loads it; contact.js owns the value so it is set in exactly one place). On correct content that check reported `FAIL engage form: transport address … missing (Gate 1 regression)` — a false alarm on a healthy site. It now follows the page's own `<script src>`, fetches the JS the browser actually runs, and asserts the `email:`/`endpoint:` values in it — strictly stronger than grepping the HTML, since it validates the live transport rather than a copy of the string. Regression-proofed by `scripts/test-engage-gate.py` (7 cases: correct content, wrong address, empty transport, endpoint-only, missing script tag, missing form markup, unfetchable JS — all 7 behave correctly; run `python3 scripts/test-engage-gate.py`). Post-cutover tally after that fix was **17 ok, 0 warn, 2 fail** (both fails the www-certificate item, now resolved). **Final production tally 2026-09-28: `PRODUCTION VERIFIED — 19 ok, 0 warn, 0 fail`.** `preflight.py --live https://hummelllc.com/ --dns` → **LAUNCH-READY, 12 ok, 2 warn, 0 fail** — the 2 warns are the two known non-blockers (the `© 2026 Hummel LLC` line that re-surfaces at LLC formation, and the scheduling URL still owed by the founder).

**Contingency — GitHub domain verification.** If GitHub shows the custom domain as *unverified* (Settings → Pages, or a banner), it will hand you a `_github-pages-challenge-brendanhummel` **TXT** record to add at GoDaddy. Add it alongside the existing TXT records; do not replace them. It does not affect mail. This is the only DNS addition beyond the table above.

**Rollback:** revert step 1 (restore the two GoDaddy parking A records, drop the `www` CNAME). Email is untouched throughout, so rollback cannot break mail. The staging URL keeps serving either way.

Owner: founder (GoDaddy access — I have no registrar credentials and will not ask for them in chat). I drive the GitHub-side setting and run the verification. Founder access was needed for step 1 (**done 2026-09-27**). **No founder action remains on the cutover** — the read-only Settings → Pages visit described above was completed 2026-09-28 and the certificate now covers both hostnames. The only open human item in this runbook is the post-cutover email in step 4.

**Cutover readiness (verified 2026-09-25 17:5x EDT):** the GitHub-side step is credential-ready — `gh auth status` reports the `brendanhummel` account logged in with `repo` scope, so step 2 is a settings change I can make the moment step 1 resolves; no new secret and nothing to ask the founder for. Steps 3–4 (verification and smoke test) are already scripted: `python3 scripts/postcutover.py` (which hands off to `preflight.py --live https://hummelllc.com/ --dns`).

**Sequencing note (from HUM-9, Presence & Launch Lead, on the record):** the staging URL `brendanhummel.github.io/hummelllc.com/` must **not** appear in any profile field at any stage — `nap-doctrine` §4 bars it. Profiles published before cutover carry an empty website field, then take `https://hummelllc.com/` in one pass the day the domain resolves. My earlier offer to hand over the staging URL for profiles is therefore withdrawn; nothing in the build depends on it.

---

## 4. Open WARN items (not launch blockers, need a human call)

1. **Scheduling link** — **DEFERRED 2026-09-28 by the founder** (`not_yet`, card `1ba38904`): Cal.com is the chosen provider (§0.1) but the booking URL does not exist yet, so for launch the "Schedule a 30-minute intro call" button **keeps scrolling to the tested form**. That is a recorded decision, not an open question — nothing about launch depends on it, and every inquiry path already works via the form. The preflight WARN is **kept on purpose** (re-worded 2026-09-28 to carry the decision) so it re-surfaces instead of being silently lost. Wiring is one command whenever the URL exists:
   ```bash
   python3 scripts/set-contact.py --schedule "https://…"   # then commit + push
   ```
   Verified 2026-09-27 on a scratch clone of `main` with a placeholder Cal.com URL: the command writes exactly one line of `assets/js/contact.js`, reads it back off disk, and `preflight.py` flips from `WARN LAUNCH GATE — scheduleUrl empty` to **LAUNCH-READY — 6 ok / 1 warn / 0 fail**; `node scripts/test-contact-modes.js` stays green (incl. the two assertions on the stale-note branch). The same pass on 2026-09-25 fixed a real defect in what was previously called a "one-line change": setting the URL used to leave the Engage note ("A calendar link lands here before launch; until then the button takes you to the form below") visible *above* a working link. `contact.js` now hides that note whenever `scheduleUrl` is set. **Owner: founder (supply the public URL) or me (re-raise once analytics show real traffic) — tracked as HUM-13.**
   Asked again 2026-09-28 as a single-question `ask_user_questions` on HUM-5; the answer was `not_yet`. That card is answered, so **no question is pending on HUM-5** — re-raising it is HUM-13's job, not a live ask.
2. **Footer `© 2026 Hummel LLC`** — **RESOLVED 2026-09-25: founder reviewed and chose KEEP.** It is verbatim approved copy (`site-copy` §3.7), trade-name usage is allowed, and the LLC is not filed. I do not invent or rewrite legal text, so it ships as approved. The preflight WARN was kept deliberately (re-worded to record the decision) so the line re-surfaces when the LLC is actually formed — at that point the notice becomes accurate and the WARN can be retired.
3. **Hosting account is GoDaddy, launch host is GitHub Pages** — **ANSWERED 2026-09-27: stay on GitHub Pages** (`keep_gh_pages`, §0.1). The GoDaddy hosting plan sits unused; no rebuild, no redeploy path, no extra credential. If the founder later wants the paid plan used, that is a planned migration, not a launch change.
4. **Form transport stays `mailto:`** — **DECIDED 2026-09-27: keep `mailto:` for launch** (`keep_mailto`, §0.1). Accepted trade-off on the record: the visitor's own mail client does the sending, so an inquiry is lost if that visitor has no configured mail client, and there is no in-page record. Revisit after launch once analytics show real traffic — a provider installs with `python3 scripts/set-contact.py --endpoint <url>` (no rebuild).
5. **`hello@hummelllc.com`** — **RESOLVED 2026-09-25:** it bounced twice in ~2 s (`550 5.1.1` from `mx.zoho.com`) at 16:38/16:42 EDT, the founder then created the mailbox, and a re-test at 17:08 EDT (two independent external senders) produced no bounce after 9+ minutes. `email: "hello@hummelllc.com"` is wired and live. See §1.

---

## 5. Updating content after launch

Plain HTML, no build step: edit the page file → `git add -A && git commit -m "…" && git push` → live in about a minute. Then run `python3 scripts/preflight.py --live https://hummelllc.com/ --dns` to confirm nothing regressed — in particular that the guardrail words, the two attributed stats, and the relative internal links are still intact. Internal links must stay relative (see README); `404.html` is the deliberate exception and carries an inline style fallback so it also reads correctly on the staging subpath.

Guardrail reminder for whoever edits copy: the site's words come from `brief` and `site-copy` only. New claims require a brief update first.

---

## 6. Post-launch pass — payload + SEO (2026-09-28)

Ran on the live production domain immediately after the cutover closed. One real defect found and fixed; the rest was foundation work.

**Defect — header logo payload.** `assets/logo.png` is the 1083×1020 brand master (271,913 B) and every page served it as-is while the header renders it at `height: 2.9rem` (~46 px). Every page view therefore downloaded ~270 KB of pixels the browser discarded — by far the largest cost on an otherwise ~2 KB page. Measured before/after on production:

| | before | after |
|---|---|---|
| logo transferred per page view | 271,913 B | **9,990 B** (2× variant; 5,756 B at 1×) |
| full home page (HTML + CSS + JS + logo, gzip where applicable) | ~280 KB | **17,833 B (~18 KB)** |

Fix: `scripts/optimize-logo.py` derives `assets/logo-46.png` (49×46) and `assets/logo-93.png` (99×93) from the untouched master and wires the header `<img>` on all 7 pages with `srcset` + explicit width/height (no layout shift). The master stays in the repo as the brand source and is no longer referenced by any page. `preflight.py` now checks the local assets *and* the served bytes, so the master cannot come back silently — proven by reintroducing the defect on a scratch copy, which produced 2 FAILs.

**SEO foundation added:** `twitter:card = summary_large_image` + `twitter:title/description/image` + `og:site_name` + `og:image:width/height` on all 6 pages, and a `ProfessionalService` JSON-LD node on Home (**HUM-12, 2026-09-28**). The node's values are not written on the page: they are installed from `scripts/doctrine_nap.py`, which quotes `nap-doctrine` rev 3 §5 (`name`, `url`, `email`) plus §2 locality and the `profile-inventory` §3.1 service-area list — a closed 7-key set, with `telephone`/`streetAddress`/`openingHours`/legal-name/rating all banned by doctrine. Installed by `scripts/set-social-meta.py` (idempotent, `--check` supported), asserted by preflight both locally and live, and audited value-by-value by `python3 scripts/check-structured-data.py --url https://hummelllc.com/`.

**Rich Results Test, run against production 2026-09-28 21:56 EDT:** **2 valid items detected** (Local businesses → this node, plus the Organization entity Google derives from it), crawl successful, **0 errors**. Three *optional*-field notices appear — `postalCode`, `addressCountry`, `streetAddress` — and all three are deliberate: the address is never displayed (`nap-doctrine` §2, service-area business) and `postalCode` is PENDING (§5). They are warnings about fields the doctrine has not defined, not a defect; adding any of them requires a doctrine revision first. `validator.schema.org` on the same URL: `numObjects 1`, **0 errors, 0 warnings**.

**Verification after the change (production):** `postcutover.py` → **PRODUCTION VERIFIED — 19 ok, 0 warn, 0 fail**; `preflight.py --live https://hummelllc.com/ --dns` → **LAUNCH-READY — 15 ok, 2 warn, 0 fail**; `node scripts/test-contact-modes.js` → all contact-mode behaviours pass; `scripts/test-engage-gate.py` → 7/7 cases behave correctly.

**Deliberately not done:** the mark sits inside generous padding in the master (unchanged by this pass — proportions are identical to what was live before). Tightening that crop would change how the logo reads on the page, which is a brand decision, not an engineering one — left alone and raised for routing in the HUM-5 thread rather than changed unilaterally.
