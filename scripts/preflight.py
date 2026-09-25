#!/usr/bin/env python3
"""
Hummel LLC — site preflight / launch-readiness gate.

One command that checks the three things that must be true before hummelllc.com
goes live, plus the standing copy guardrails (brief §6 / site-copy §6) so they
cannot silently regress after launch.

    python3 scripts/preflight.py                      # local checks only
    python3 scripts/preflight.py --live <base_url>    # + fetch every route
    python3 scripts/preflight.py --dns                # + DNS vs launch target
    python3 scripts/preflight.py --live https://brendanhummel.github.io/hummelllc.com/ --dns

Exit code 0 = no FAIL. WARNs never fail the run; they need a human decision.
Stdlib only — nothing to install.
"""

import argparse
import os
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    "index.html",
    "what-we-do/index.html",
    "who-its-for/index.html",
    "how-it-works/index.html",
    "about/index.html",
    "engage/index.html",
]
ERROR_PAGE = "404.html"
ALL_HTML = PAGES + [ERROR_PAGE]

# GitHub Pages apex A records (custom-domain target).
GH_PAGES_A = {"185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"}
# Launch host per locked stack decision (README "DNS / launch facts").
EXPECTED_WWW_TARGET_FRAGMENT = "github.io"
EXPECTED_CANON_HOST = "hummelllc.com"

FAILS, WARNS, OKS = [], [], []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNS.append(msg)


def ok(msg):
    OKS.append(msg)


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- guardrails
# site-copy §2 banned list. "24/7" and "always-on" are allowed ONLY inside the
# approved negations ("not 24/7 support"; "not an always-on, ticket-driven MSP").
BANNED_PLAIN = [
    "best-in-class",
    "enterprise-grade",
    "seamless",
    "robust",
    "trusted by",
    "guaranteed",
    "affordable plans",
    "world-class",
    "cutting-edge",
    "one-stop",
    "turnkey",
]
BANNED_NEGATION_ONLY = ["24/7", "always-on"]
NEGATION_MARKERS = ("not ", "never", "no ", "n't", "without")
FORBIDDEN_ACRONYMS = ["HIPAA", "CJIS", "NIST"]
# No certs, client counts, headcounts, revenue (brief §6).
UNSUPPORTED_CLAIMS = [
    r"\bcertified\b",
    r"\bcertification\b",
    r"\bCISSP\b",
    r"\bCISM\b",
    r"\bISO\s?27001\b",
    r"\bSOC\s?2\b",
    r"\btrusted by\s+\d+",
    r"\b\d+\+?\s+clients\b",
    r"\b\d+\s+(?:employees|staff|engineers)\b",
    r"\b(?:annual\s+)?revenue\s+of\b",
    r"\baward[- ]winning\b",
]
# The only two market stats allowed on-page, each attributed (site-copy §6.4).
STAT_ATTRIBUTIONS = [
    r"Verizon\s+2025\s+Data\s+Breach\s+Investigations\s+Report",
    r"industry\s+research\s+compiled\s+2025",
]
# Pricing line must stay labelled as a public benchmark, not our own data.
PRICING_LABEL = r"public\s+benchmarks"


def check_guardrails():
    for page in ALL_HTML:
        text = read(page)
        low = text.lower()
        for term in BANNED_PLAIN:
            if term in low:
                fail(f"{page}: banned claim word '{term}' (site-copy §2)")
        for term in BANNED_NEGATION_ONLY:
            for m in re.finditer(re.escape(term), low):
                line = low[max(0, low.rfind("\n", 0, m.start())): low.find("\n", m.end())]
                if not any(n in line for n in NEGATION_MARKERS):
                    fail(f"{page}: '{term}' outside an approved negation (site-copy §6.5)")
        for acr in FORBIDDEN_ACRONYMS:
            if re.search(r"\b" + acr + r"\b", text):
                fail(f"{page}: forbidden credential acronym '{acr}' (brief §6)")
        for pat in UNSUPPORTED_CLAIMS:
            m = re.search(pat, text, re.I)
            if m:
                fail(f"{page}: unsupported claim '{m.group(0)}' — no certs/counts/revenue (brief §6)")

    home = read("index.html")
    if "proven pci environment experience" not in home.lower():
        warn("index.html: PCI may be stated plainly — wording not found (site-copy §6.1)")
    for pat in STAT_ATTRIBUTIONS:
        if not re.search(pat, "\n".join(read(p) for p in ALL_HTML)):
            fail(f"attributed market stat missing: /{pat}/ (site-copy §6.4)")
    if not re.search(PRICING_LABEL, read("what-we-do/index.html"), re.I):
        warn("what-we-do: pricing benchmark label '(public benchmarks, …)' not found (site-copy §6.4)")
    ok("copy guardrails scanned (brief §6 / site-copy §6)")


def check_no_secrets():
    """Nothing on a public page may be a credential. The only token allowed is the
    public 32-hex Cloudflare Web Analytics site token (checked in check_launch_config)."""
    patterns = [
        (r"api[_-]?key", "an API key reference"),
        (r"Bearer\s+[A-Za-z0-9._\-]{16,}", "a bearer token"),
        (r"\b[0-9a-fA-F]{37}\b", "a 37-hex value (Cloudflare global API key shape)"),
        (r"(?:secret|password|passwd|api[_-]?token)[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-]{16,}",
         "a named secret value"),
    ]
    for page in ALL_HTML:
        text = read(page)
        for pat, label in patterns:
            m = re.search(pat, text, re.I)
            if m:
                fail(f"{page}: looks like {label} ({m.group(0)[:24]}…) — never put credentials on the site; "
                     f"revoke it and use the public site token only (LAUNCH-RUNBOOK.md §2)")
    ok("no credentials on any page (public site token only)")


# ---------------------------------------------------------------- structure
def check_structure():
    internal = re.compile(r'(?:href|src)="(/[^"/][^"]*)"')
    for page in ALL_HTML:
        text = read(page)
        n = text.count("<h1")
        if n != 1:
            fail(f"{page}: expected exactly 1 <h1>, found {n}")
        required = [("<title>", "title"), ('lang="en"', "lang attribute"), ("skip", "skip link")]
        if page != ERROR_PAGE:
            required += [
                ('name="description"', "meta description"),
                ('rel="canonical"', "canonical"),
                ('property="og:image"', "og:image"),
            ]
        else:
            required.append(('name="robots" content="noindex"', "noindex robots meta"))
        for need, label in required:
            if need not in text:
                fail(f"{page}: missing {label}")
        if page != ERROR_PAGE:
            for m in internal.finditer(text):
                fail(f"{page}: root-absolute internal ref '{m.group(1)}' — 404s on the staging subpath "
                     f"(README: internal links are relative on purpose)")

    # every local href/src target must exist on disk (root-absolute refs on 404.html
    # resolve against the site root, as they do in production)
    for page in ALL_HTML:
        base = ROOT if page == ERROR_PAGE else os.path.dirname(os.path.join(ROOT, page))
        for m in re.finditer(r'(?:href|src)="([^"#?]+)', read(page)):
            ref = m.group(1)
            if re.match(r"^(https?:|mailto:|tel:|data:|//)", ref) or ref == "":
                continue
            target = os.path.normpath(os.path.join(base, ref.lstrip("/")))
            if ref.endswith("/") or os.path.isdir(target):
                target = os.path.join(target, "index.html")
            if not os.path.exists(target):
                fail(f"{page}: internal link '{ref}' has no file on disk")

    canon = re.search(r'rel="canonical" href="https?://([^/"]+)', read("index.html"))
    if not canon or canon.group(1) != EXPECTED_CANON_HOST:
        fail(f"canonical host is not {EXPECTED_CANON_HOST} (SEO must point at production)")

    sitemap = read("sitemap.xml")
    for slug in ["", "what-we-do/", "who-its-for/", "how-it-works/", "about/", "engage/"]:
        if f"https://{EXPECTED_CANON_HOST}/{slug}<" not in sitemap:
            fail(f"sitemap.xml missing entry for /{slug}")
    robots = read("robots.txt")
    if "Sitemap:" not in robots:
        fail("robots.txt has no Sitemap directive")
    ok("page structure, internal links, canonicals, sitemap, robots")


# ---------------------------------------------------------------- launch gates
def check_launch_config():
    contact = read("assets/js/contact.js")
    endpoint = re.search(r'endpoint:\s*"([^"]*)"', contact)
    email = re.search(r'email:\s*"([^"]*)"', contact)
    sched = re.search(r'scheduleUrl:\s*"([^"]*)"', contact)
    has_transport = bool((endpoint and endpoint.group(1)) or (email and email.group(1)))
    if not has_transport:
        fail("LAUNCH GATE — contact delivery is NOT configured (contact.js endpoint/email both empty): "
             "the Engage form will tell visitors 'delivery goes live with launch'. "
             "Fix: python3 scripts/set-contact.py --endpoint <provider URL> "
             "(or --email <verified mailbox> --verified). See LAUNCH-RUNBOOK.md §1.")
    else:
        ok(f"contact transport configured ({'endpoint' if endpoint and endpoint.group(1) else 'mailto: ' + email.group(1)})")
    if not (sched and sched.group(1)):
        warn("LAUNCH GATE — scheduleUrl empty: 'Schedule a 30-minute intro call' scrolls to the form instead of booking")

    missing = []
    for page in PAGES:
        # Only live markup counts: the ANALYTICS SLOT note is an HTML comment holding a
        # template snippet, so strip comments before deciding whether the beacon is installed.
        live = re.sub(r"<!--.*?-->", "", read(page), flags=re.S)
        if "static.cloudflareinsights.com/beacon.min.js" not in live:
            missing.append(page)
            continue
        tok = re.search(r'data-cf-beacon=[\'"]?\{[^}]*"token":\s*"([^"]+)"', live)
        if not tok:
            missing.append(page)
        elif not re.fullmatch(r"[0-9a-fA-F]{32}", tok.group(1)):
            fail(f"{page}: analytics beacon token is not the 32-hex PUBLIC site token — it looks like an "
                 f"account credential. Remove it from the page and revoke it (Cloudflare dashboard -> "
                 f"My Profile -> API Tokens): nothing in this build needs one.")
    if missing:
        fail("LAUNCH GATE — Cloudflare Web Analytics beacon not live on: " + ", ".join(missing) +
             " (locked provider; needs only the PUBLIC site token from the CF dashboard snippet, "
             "never an API token). Fix: python3 scripts/set-analytics.py --token <32-hex site token> "
             "or --snippet-file <file>. See LAUNCH-RUNBOOK.md §2.")
    else:
        ok("analytics beacon live on all pages")

    if re.search(r"(?:©|&copy;)\s*\d{4}\s+Hummel LLC", read("index.html")):
        warn("legal-name guardrail (brief rev 4 §7): footer reads '© 2026 Hummel LLC' — an ownership "
             "claim naming the unformed entity. RESOLVED 2026-09-25: founder reviewed and chose to KEEP "
             "it as approved copy (trade-name usage; LLC not filed). Stays a WARN so the decision is "
             "re-surfaced when the LLC is formed — at that point the line becomes accurate and the WARN "
             "can be retired.")
    ok("legal-name guardrail checked")


# ---------------------------------------------------------------- live + dns
def fetch(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "hummelllc-preflight"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read(200000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(50000).decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return None, f"{type(e).__name__}: {e}"


def check_live(base):
    base = base.rstrip("/") + "/"
    for slug in ["", "what-we-do/", "who-its-for/", "how-it-works/", "about/", "engage/", "sitemap.xml", "robots.txt"]:
        status, body = fetch(base + slug)
        if status != 200:
            fail(f"live: {base}{slug} -> {status if status else body}")
        elif slug in ("", "about/"):
            if "stylesheet" not in body and "site.css" not in body:
                fail(f"live: {base}{slug} served but no stylesheet link (asset path bug)")
    status, body = fetch(base + "definitely-not-a-page-xyz/")
    if status != 404:
        fail(f"live: unknown route returned {status}, expected 404")
    elif "404" not in body and "isn" not in body:
        warn("live: 404 status returned but custom not-found page text not detected")
    ok(f"live routes fetched from {base}")


def dig(name, rtype):
    try:
        out = subprocess.run(["dig", "+short", rtype, name], capture_output=True, text=True, timeout=15)
        return [l.strip().strip('"') for l in out.stdout.splitlines() if l.strip()]
    except Exception as e:  # noqa: BLE001
        warn(f"dig {rtype} {name} failed: {e}")
        return []


def check_dns():
    apex_a = set(dig(EXPECTED_CANON_HOST, "A"))
    if not apex_a:
        fail("DNS: no A record for apex — domain not resolvable")
    elif apex_a == GH_PAGES_A:
        ok("DNS: apex A records point at GitHub Pages (cutover complete)")
    elif apex_a & GH_PAGES_A:
        warn(f"DNS: apex partially cut over — {sorted(apex_a)}")
    else:
        warn(f"DNS pre-cutover (expected until launch): apex A = {sorted(apex_a)} — parked; "
             f"launch sets {sorted(GH_PAGES_A)}")

    www = dig("www." + EXPECTED_CANON_HOST, "CNAME")
    if any(EXPECTED_WWW_TARGET_FRAGMENT in r for r in www):
        ok("DNS: www CNAME points at the Pages host")
    else:
        warn(f"DNS pre-cutover: www CNAME = {www or 'none'} (launch sets www -> brendanhummel.github.io)")

    # Email must survive the web cutover (brief §7).
    mx = dig(EXPECTED_CANON_HOST, "MX")
    if not mx:
        fail("DNS: no MX records — Zoho mail would break")
    elif not any("zoho" in r.lower() for r in mx):
        warn(f"DNS: MX is no longer Zoho: {mx}")
    else:
        ok(f"DNS: MX intact ({len(mx)} Zoho records)")
    txt = " ".join(dig(EXPECTED_CANON_HOST, "TXT"))
    if "v=spf1" not in txt:
        warn("DNS: no SPF record found on apex TXT")
    else:
        ok("DNS: SPF present")
    caa = dig(EXPECTED_CANON_HOST, "CAA")
    if caa:
        warn(f"DNS: CAA records present ({caa}) — confirm they permit the Pages cert issuer (letsencrypt.org)")
    else:
        ok("DNS: no CAA records — cert issuance unrestricted for GitHub Pages")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", metavar="BASE_URL", help="fetch every route from this base URL")
    ap.add_argument("--dns", action="store_true", help="check DNS against the launch target")
    args = ap.parse_args()

    check_guardrails()
    check_no_secrets()
    check_structure()
    check_launch_config()
    if args.live:
        check_live(args.live)
    if args.dns:
        check_dns()

    for m in OKS:
        print(f"  ok    {m}")
    for m in WARNS:
        print(f"  WARN  {m}")
    for m in FAILS:
        print(f"  FAIL  {m}")
    verdict = "LAUNCH-READY" if not FAILS else f"NOT LAUNCH-READY ({len(FAILS)} fail)"
    print(f"\n{verdict} — {len(OKS)} ok, {len(WARNS)} warn, {len(FAILS)} fail")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())