#!/usr/bin/env python3
"""
Hummel LLC — close or change Launch Gate 1 (contact delivery) in one command.

    # publish a mailbox (only after a real send test came back clean)
    python3 scripts/set-contact.py --email brendan@hummelllc.com --verified

    # or route the form through a provider instead (no mailbox on the path)
    python3 scripts/set-contact.py --endpoint https://formspree.io/f/abcdwxyz

    # and/or point the "30-minute intro call" button at a real calendar
    python3 scripts/set-contact.py --schedule https://cal.com/brendan/30min

    # show what is configured now
    python3 scripts/set-contact.py --show

Edits assets/js/contact.js in place, then re-runs the launch gate
(scripts/preflight.py). Stdlib only.

Why --verified exists
---------------------
A mailto: to an address that does not exist is worse than no transport at all:
the visitor's mail app opens, the mail bounces back to *them*, and the inquiry is
lost silently while the page looks like it works. hello@hummelllc.com was set on
2026-09-25 and then bounced twice with a hard "550 5.1.1 User does not exist"
from mx.zoho.com — so this script refuses to publish an address unless you say you
tested it. To test: send one mail to the address from any external account, wait
two minutes, confirm no mailer-daemon reply. (Outbound SMTP is blocked from this
machine, so the test has to go through a real mail client.)
"""

import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = "assets/js/contact.js"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[A-Za-z]{2,}$")


def read_config():
    with open(os.path.join(ROOT, CONFIG), encoding="utf-8") as fh:
        return fh.read()


def field(text, name):
    m = re.search(name + r':\s*"([^"]*)"', text)
    return m.group(1) if m else None


def set_field(text, name, value):
    old = re.search(name + r':\s*"[^"]*"', text)
    if not old:
        raise SystemExit(f"could not find `{name}` in {CONFIG} — refusing to guess.")
    return text[: old.start()] + f'{name}: "{value}"' + text[old.end():]


def die(msg):
    print(f"REFUSED: {msg}", file=sys.stderr)
    return 2


def main():
    ap = argparse.ArgumentParser(description="Set the Engage form's delivery config (Gate 1).")
    ap.add_argument("--email", help="mailbox to publish (mailto transport)")
    ap.add_argument("--endpoint", help="form-provider URL (POST transport)")
    ap.add_argument("--schedule", help="calendar URL for the 'Schedule a 30-minute intro call' button")
    ap.add_argument("--clear", action="store_true", help="reset all three to empty")
    ap.add_argument("--verified", action="store_true",
                    help="confirm you sent a real test mail to --email and saw no bounce")
    ap.add_argument("--show", action="store_true", help="print the current config and exit")
    ap.add_argument("--preflight", action="store_true", help="run scripts/preflight.py afterwards")
    args = ap.parse_args()

    text = read_config()

    if args.show:
        for name in ("endpoint", "email", "scheduleUrl"):
            print(f"  {name}: {field(text, name) or '(empty)'}")
        return 0

    if args.clear:
        for name in ("endpoint", "email", "scheduleUrl"):
            text = set_field(text, name, "")
        with open(os.path.join(ROOT, CONFIG), "w", encoding="utf-8") as fh:
            fh.write(text)
        print("cleared endpoint/email/scheduleUrl — form back in pre-launch mode")
        return 0

    if not (args.email or args.endpoint or args.schedule):
        return die("nothing to do — pass --email, --endpoint, --schedule, --show or --clear.")

    changed = []

    if args.email:
        addr = args.email.strip()
        if not EMAIL_RE.match(addr):
            return die(f"{addr!r} is not a valid email address.")
        if not addr.lower().endswith("@hummelllc.com"):
            print(f"NOTE: {addr} is off-domain — the site publishes a hummelllc.com address.")
        if not args.verified:
            return die(
                f"publishing mailto:{addr} requires --verified.\n"
                "  A mailto to a dead address silently loses every inquiry while the page looks\n"
                "  fine (that is exactly how hello@hummelllc.com failed: 550 5.1.1 from mx.zoho.com,\n"
                "  twice, on 2026-09-25). Send one test mail there from an external account, wait\n"
                "  two minutes, confirm no bounce — then re-run with --verified."
            )
        text = set_field(text, "email", addr)
        changed.append(f"email = {addr} (mailto transport live)")

    if args.endpoint:
        url = args.endpoint.strip()
        if not url.startswith("https://"):
            return die("endpoint must be an https:// URL (form providers are https-only).")
        if " " in url:
            return die("endpoint contains whitespace.")
        text = set_field(text, "endpoint", url)
        changed.append(f"endpoint = {url} (provider transport live — takes priority over mailto)")

    if args.schedule:
        url = args.schedule.strip()
        if not url.startswith("https://"):
            return die("schedule URL must be https://.")
        if " " in url:
            return die("schedule URL contains whitespace.")
        text = set_field(text, "scheduleUrl", url)
        changed.append(f"scheduleUrl = {url}")

    with open(os.path.join(ROOT, CONFIG), "w", encoding="utf-8") as fh:
        fh.write(text)

    for c in changed:
        print(f"set: {c}")
    print(f"wrote {CONFIG}")

    # Read back from disk — the file, not our intent, is the evidence.
    on_disk = read_config()
    for name, want in (("email", args.email), ("endpoint", args.endpoint), ("scheduleUrl", args.schedule)):
        if want and field(on_disk, name) != want.strip():
            print(f"FAIL: {name} did not land in {CONFIG}", file=sys.stderr)
            return 1
    print("verified: config read back from disk")

    if args.preflight:
        return subprocess.call([sys.executable, os.path.join(ROOT, "scripts", "preflight.py")], cwd=ROOT)
    print("next: python3 scripts/preflight.py --live <url>  (Gate 1 flips to ok), then commit + push")
    return 0


if __name__ == "__main__":
    sys.exit(main())