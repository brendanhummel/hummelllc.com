#!/usr/bin/env python3
"""
Hummel LLC — post-cutover production verification (launch runbook §3, steps 3-4).

Run this AFTER the GoDaddy DNS records are changed and the GitHub Pages custom
domain is set. It checks the things that are only true once the domain is live,
then hands off to preflight.py for the standing guardrails.

    python3 scripts/postcutover.py

Before the cutover this script FAILS on purpose (DNS parked, custom domain not
serving) — that is the gate proving itself, not a bug.

Exit code 0 = production verified. Non-zero = at least one FAIL.

Stdlib only — nothing to install. Safe to run repeatedly; read-only, it never
writes to DNS, GitHub, or the repo.
"""

import json
import os
import re
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

DOMAIN = "hummelllc.com"
CANON = "https://hummelllc.com/"
STAGING = "https://brendanhummel.github.io/hummelllc.com/"
PREFLIGHT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preflight.py")

# Mirrors preflight.py: GitHub Pages apex A records for a custom domain.
GH_PAGES_A = {"185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"}
EXPECTED_WWW_FRAGMENT = "github.io"

# The six public routes (runbook §3 step 4: "all 6 pages").
ROUTES = ["", "what-we-do/", "who-its-for/", "how-it-works/", "about/", "engage/"]
CANONICAL_ROUTES = ["https://hummelllc.com/"] + [f"https://hummelllc.com/{r}" for r in ROUTES[1:]]

# Cloudflare Web Analytics public site token (Gate 2 — closed 2026-09-25).
BEACON_TOKEN = "382b5ca9e51244e9ac2817b82a6a288d"
BEACON_HOST = "static.cloudflareinsights.com/beacon.min.js"

UA = {"User-Agent": "hummelllc-postcutover/1 (launch verification)"}

FAILS, WARNS, OKS = [], [], []


def fail(m):
    FAILS.append(m)


def warn(m):
    WARNS.append(m)


def ok(m):
    OKS.append(m)


def dig(name, rtype):
    try:
        p = subprocess.run(["dig", "+short", rtype, name],
                           capture_output=True, text=True, timeout=15)
        return [l.strip().strip('"') for l in p.stdout.splitlines() if l.strip()]
    except Exception as e:  # noqa: BLE001
        warn(f"dig {rtype} {name} failed: {e}")
        return []


def fetch(url, method="GET"):
    """Return (status, body, final_url, error). Real TLS verification (default context)."""
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read() if method != "HEAD" else b""
            return r.status, raw.decode("utf-8", "replace"), r.geturl(), None
    except urllib.error.HTTPError as e:
        return e.code, "", url, None
    except Exception as e:  # noqa: BLE001
        return None, "", url, f"{type(e).__name__}: {e}"


# ----------------------------------------------------------------------- DNS
def check_dns():
    apex = set(dig(DOMAIN, "A"))
    if apex == GH_PAGES_A:
        ok(f"DNS: apex A -> GitHub Pages (4 records) — cutover live")
    elif apex & GH_PAGES_A:
        fail(f"DNS: apex only PARTIALLY cut over — {sorted(apex)}; all four of "
             f"{sorted(GH_PAGES_A)} are required for the Pages cert")
    elif not apex:
        fail("DNS: no apex A record — domain does not resolve")
    else:
        fail(f"DNS: apex still parked — {sorted(apex)} (launch sets the four GitHub Pages IPs)")

    www = dig("www." + DOMAIN, "CNAME")
    if any(EXPECTED_WWW_FRAGMENT in r for r in www):
        ok("DNS: www CNAME -> Pages host")
    else:
        fail(f"DNS: www CNAME is {www or 'missing'} — launch sets www -> brendanhummel.github.io")

    # Mail must survive the web cutover (brief §7). These are FAILs, not WARNs:
    # silent mail loss is the one outcomes rollback cannot undo.
    mx = dig(DOMAIN, "MX")
    if mx and all("zoho" in r.lower() or r.split()[-1].lower().endswith("zoho.com") for r in mx):
        ok(f"DNS: MX intact — {len(mx)} Zoho records (mail survives)")
    elif not mx:
        fail("DNS: MX records GONE — Zoho mail is broken. Restore mail before continuing.")
    else:
        fail(f"DNS: MX no longer all-Zoho — {mx}. Verify mail before continuing.")

    if "v=spf1" in " ".join(dig(DOMAIN, "TXT")):
        ok("DNS: SPF still present")
    else:
        fail("DNS: SPF record missing — outbound mail will fail SPF")

    caa = dig(DOMAIN, "CAA")
    if caa:
        warn(f"DNS: CAA present ({caa}) — must permit the Pages cert issuer or HTTPS will not issue")
    else:
        ok("DNS: no CAA records — cert issuance unrestricted")


# ----------------------------------------------------------------------- TLS
def check_tls(host, label):
    ctx = ssl.create_default_context()
    cert = None
    try:
        with socket.create_connection((host, 443), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
    except Exception as e:  # noqa: BLE001
        fail(f"TLS {label}: {host} — no valid certificate ({type(e).__name__}: {e})")
        return
    if not isinstance(cert, dict):
        fail(f"TLS {label}: {host} — no certificate returned")
        return

    sans = [str(v) for k, v in cert.get("subjectAltName", ()) if k == "DNS"]
    issuer = str(ss_name(cert, "issuer", "organizationName"))
    ok(f"TLS {label}: valid cert for {host} (issuer {issuer}; SAN {', '.join(sans[:4])})")
    if not any(s == host or (s.startswith("*.") and host.endswith(s[1:])) for s in sans):
        fail(f"TLS {label}: cert SAN {sans} does not cover {host}")


def ss_name(cert, field, key):
    """Pull one name out of a cert's subject/issuer RDN sequence."""
    for rdn in cert.get(field, ()):
        for k, v in rdn:
            if k == key:
                return v
    return "?"


# -------------------------------------------------------------------- routes
def check_routes():
    for r in ROUTES:
        url = CANON + r
        status, body, final, err = fetch(url)
        if err:
            fail(f"route {url} — {err}")
            continue
        if status != 200:
            fail(f"route {url} — HTTP {status} (expected 200)")
            continue
        if "hummelllc.com" not in body:
            fail(f"route {url} — 200 but body does not look like the site")
            continue
        if BEACON_HOST not in body or BEACON_TOKEN not in body:
            fail(f"route {url} — analytics beacon missing (Gate 2 regression)")
            continue
        ok(f"route {url} — 200, beacon present")


def check_head():
    """Mirror runbook step 4: curl -I https://hummelllc.com/what-we-do/ -> 200."""
    status, _, _, err = fetch(CANON + "what-we-do/", method="HEAD")
    if err:
        fail(f"HEAD {CANON}what-we-do/ — {err}")
    elif status != 200:
        fail(f"HEAD {CANON}what-we-do/ — HTTP {status} (expected 200)")
    else:
        ok(f"HEAD {CANON}what-we-do/ — 200 (curl -I equivalent)")


def check_www_and_redirect():
    status, body, final, err = fetch("https://www." + DOMAIN + "/")
    if err:
        fail(f"https://www.{DOMAIN}/ — {err}")
    elif status != 200:
        fail(f"https://www.{DOMAIN}/ — HTTP {status} (expected 200)")
    else:
        ok(f"https://www.{DOMAIN}/ — 200")

    status, _, final, err = fetch(STAGING)
    if err:
        warn(f"staging URL unreachable ({err}) — acceptable if Pages now redirects it")
    elif final.rstrip("/") != STAGING.rstrip("/") and DOMAIN in final:
        ok(f"staging URL redirects to {final}")
    elif status == 200:
        warn("staging URL still serves directly (GitHub usually redirects a project "
             "site to its custom domain) — cosmetic only, not a launch blocker")
    else:
        warn(f"staging URL returned HTTP {status}")


def check_canonicals():
    """Local check: canonical tags must already name the production domain."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pages = ["index.html"] + [f"{r}index.html" for r in ROUTES[1:]]
    bad = []
    for p in pages:
        path = os.path.join(root, p)
        try:
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
        except OSError as e:
            bad.append(f"{p} unreadable ({e})")
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if not m or not m.group(1).startswith("https://hummelllc.com/"):
            bad.append(f"{p} -> {m.group(1) if m else 'no canonical'}")
    if bad:
        fail("canonical tags: " + "; ".join(bad))
    else:
        ok(f"canonical tags name {CANON} on all {len(pages)} pages")


def check_engage_form():
    status, body, _, err = fetch(CANON + "engage/")
    if err or status != 200:
        fail(f"engage form: /engage/ not fetchable ({err or status})")
        return
    if 'id="contact-form"' not in body:
        fail("engage form: contact form markup missing on /engage/")
    elif "hello@hummelllc.com" not in body:
        fail("engage form: transport address hello@hummelllc.com missing (Gate 1 regression)")
    else:
        ok("engage form: present, wired to hello@hummelllc.com (submit is a mail-client "
           "action — requires a real human send to close)")


def check_preflight():
    if not os.path.exists(PREFLIGHT):
        fail(f"preflight.py not found at {PREFLIGHT}")
        return
    p = subprocess.run([sys.executable, PREFLIGHT, "--live", CANON, "--dns"],
                       capture_output=True, text=True, timeout=180)
    tail = [l for l in p.stdout.strip().splitlines() if l.strip()]
    verdict = tail[-1] if tail else "(no output)"
    for line in tail:
        if "FAIL" in line:
            fail(f"preflight: {line.strip()}")
    if p.returncode == 0:
        ok(f"preflight --live {CANON} --dns -> {verdict}")
    elif not any("FAIL" in l for l in tail):
        fail(f"preflight exited {p.returncode} without a FAIL line: {verdict}")


def main():
    print(f"Post-cutover verification — {DOMAIN}\n")
    check_dns()
    check_tls(DOMAIN, "apex")
    check_tls("www." + DOMAIN, "www")
    check_canonicals()
    check_routes()
    check_head()
    check_www_and_redirect()
    check_engage_form()
    check_preflight()

    for m in OKS:
        print(f"  ok    {m}")
    for m in WARNS:
        print(f"  WARN  {m}")
    for m in FAILS:
        print(f"  FAIL  {m}")

    print()
    if FAILS:
        print(f"NOT LAUNCHED ({len(FAILS)} fail) — {len(OKS)} ok, {len(WARNS)} warn")
        print("Pre-cutover? Expect DNS + TLS fails until the GoDaddy records are changed "
              "and the Pages custom domain is set (runbook §3 steps 1-2).")
    else:
        print(f"PRODUCTION VERIFIED — {len(OKS)} ok, {len(WARNS)} warn, 0 fail")
        print("Remaining human step: send one real email to hello@hummelllc.com and confirm "
              "no bounce (runbook §3 step 4).")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())