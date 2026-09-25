#!/usr/bin/env python3
"""
Hummel LLC — install the Cloudflare Web Analytics beacon into every page.

One command, no secrets, idempotent.

    python3 scripts/set-analytics.py --token 0123456789abcdef0123456789abcdef
    python3 scripts/set-analytics.py --snippet-file /path/to/snippet.txt
    python3 scripts/set-analytics.py --snippet '<script defer src="..."></script>'
    python3 scripts/set-analytics.py --token <tok> --preflight   # + run the launch gate

WHAT THIS NEEDS (and what it must never be given)
-------------------------------------------------
Cloudflare Web Analytics is installed with a **site token**. That token is public
by design: it ships inside the page source of every site running CWA, so it grants
no account access and cannot read or change anything. Pasting it in a comment or
in chat is harmless.

It is NOT a Cloudflare API token and NOT an API key. This script actively refuses
anything that looks like account credentials, so that a secret cannot end up in a
public page. If you created an API token for this, delete it: Cloudflare dashboard
-> My Profile -> API Tokens. Nothing in this build has ever needed one.

Exit code 0 = every page carries the beacon (or already did).
"""

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = [
    "index.html",
    "what-we-do/index.html",
    "who-its-for/index.html",
    "how-it-works/index.html",
    "about/index.html",
    "engage/index.html",
]

BLOCK_RE = re.compile(r"<!-- ANALYTICS SLOT:.*?-->\s*", re.S)
BEACON_RE = re.compile(r"static\.cloudflareinsights\.com/beacon\.min\.js")
TOKEN_IN_SNIPPET_RE = re.compile(r"""["']?token["']?\s*:\s*["']([^"']+)["']""")
SITE_TOKEN_RE = re.compile(r"^[0-9a-fA-F]{32}$")
# Cloudflare *account* credentials: API tokens are 40 chars of [A-Za-z0-9_-];
# global API keys are 37 hex chars. Neither belongs on a public page.
API_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{40}$")
GLOBAL_KEY_RE = re.compile(r"^[0-9a-fA-F]{37}$")

SNIPPET = (
    '<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
    "data-cf-beacon='{\"token\": \"@TOKEN@\", \"spa\": true}'></script>"
)
NOTES = (
    "  <!-- Installed by scripts/set-analytics.py on {date}. Cloudflare Web Analytics:\n"
    "       free, cookie-free, no consent banner. The token below is PUBLIC site data\n"
    "       (it is visible in the page source of every CWA site) — it is not an API\n"
    "       token and grants no account access. Replace via scripts/set-analytics.py. -->\n"
)


def die(msg, code=2):
    print(f"REFUSED: {msg}", file=sys.stderr)
    return code


def normalise_token(raw):
    """Accept a bare token or a pasted snippet; return (token, error)."""
    s = raw.strip().strip("'\"")
    if not s:
        return None, "empty input."
    looks_like_snippet = "<" in s and ("script" in s.lower() or "data-cf-beacon" in s.lower())
    if looks_like_snippet:
        m = TOKEN_IN_SNIPPET_RE.search(s)
        if not m:
            return None, "could not find a \"token\" value in that snippet."
        s = m.group(1).strip()
    elif s.startswith("<") and s.endswith(">"):
        return None, f"that is the placeholder {s!r}, not a real token."
    if s.startswith("<") or s.lower() in ("token", "your-token", "paste-token-here"):
        return None, f"that is the placeholder {s!r}, not a real token."
    if re.search(r"\s", s):
        return None, "input contains whitespace — pass just the token, or a single snippet."
    if API_TOKEN_RE.match(s) or GLOBAL_KEY_RE.match(s):
        return None, (
            "that looks like a Cloudflare *account credential* (API token or global API key), "
            "not a Web Analytics site token.\n"
            "  Do NOT put it on the site, and do not paste it into an issue comment or chat.\n"
            "  Cloudflare Web Analytics needs only the public site token from the JS snippet\n"
            "  (Cloudflare dashboard -> Analytics & Logs -> Web Analytics -> hummelllc.com ->\n"
            "  Manage site -> JS snippet). If you already created an API token for this, revoke\n"
            "  it: dashboard -> My Profile -> API Tokens. Nothing in this build needs one."
        )
    if SITE_TOKEN_RE.match(s):
        return s.lower(), None
    return None, (
        f"unrecognised token shape ({len(s)} chars). Expected the 32-character hex site token\n"
        "  from the Cloudflare Web Analytics JS snippet. If you pasted a full snippet, the\n"
        "  token is the value of \"token\" inside it."
    )


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    ap = argparse.ArgumentParser(description="Install the Cloudflare Web Analytics beacon into every page.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--token", help="the public 32-hex site token from the CWA snippet")
    src.add_argument("--snippet", help="the whole <script …> snippet pasted from the dashboard")
    src.add_argument("--snippet-file", help="path to a file holding the snippet")
    ap.add_argument("--preflight", action="store_true", help="run scripts/preflight.py afterwards")
    args = ap.parse_args()

    raw = args.token or args.snippet
    if args.snippet_file:
        with open(args.snippet_file, encoding="utf-8") as fh:
            raw = fh.read()
    token, err = normalise_token(raw)
    if err:
        return die(err)
    assert token is not None  # normalise_token returns a token or an error, never both

    snippet = SNIPPET.replace("@TOKEN@", token)
    date = subprocess.run(["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip() or "undated"

    changed, already = [], []
    for page in PAGES:
        text = read(page)
        live = BEACON_RE.search(text) and token in text
        if live and not BLOCK_RE.search(text):
            already.append(page)
            continue
        if not BLOCK_RE.search(text):
            # No placeholder block (e.g. hand-edited page): insert before </head>.
            if "</head>" not in text:
                return die(f"{page}: no ANALYTICS SLOT block and no </head> — refusing to guess.")
            text = text.replace(
                "</head>", NOTES.format(date=date) + "  " + snippet + "\n</head>", 1
            )
        else:
            text = BLOCK_RE.sub(NOTES.format(date=date) + "  " + snippet + "\n", text, count=1)
        write(page, text)
        changed.append(page)

    print(f"token: {token[:6]}…{token[-4:]} ({len(token)} hex chars — public site token)")
    print(f"beacon installed on {len(changed)} page(s): {', '.join(changed) or 'none'}")
    if already:
        print(f"already current (no change): {', '.join(already)}")

    # Idempotency + correctness check straight from disk.
    bad = [p for p in PAGES if not (BEACON_RE.search(read(p)) and token in read(p))]
    if bad:
        print(f"FAIL: beacon missing after write on: {', '.join(bad)}", file=sys.stderr)
        return 1
    print("verified: every page carries the beacon with this token")

    if args.preflight:
        return subprocess.call([sys.executable, os.path.join(ROOT, "scripts", "preflight.py")],
                               cwd=ROOT)
    print("next: python3 scripts/preflight.py --live <url>  (Gate 2 flips to ok), then commit + push")
    return 0


if __name__ == "__main__":
    sys.exit(main())