#!/usr/bin/env python3
"""verify-presence.py -- profile verification harness for Hummel LLC (M3-B, HUM-9).

Purpose: make the M3-B exit criterion mechanical. M3-B is not "the profiles were
created"; it is "each profile verified by opening the public URL and confirming it
loads with the correct link and description". This script does exactly that, per
profile, from the manifest, and prints one verdict line per profile.

Usage:
    python3 scripts/verify-presence.py scripts/presence-manifest.json          # verify every profile with a URL
    python3 scripts/verify-presence.py scripts/presence-manifest.json --all    # also list not-yet-published profiles
    python3 scripts/verify-presence.py scripts/presence-manifest.json gbp      # verify one profile by key

Exit code: 0 = every published profile passed, 1 = at least one FAIL.

Stdlib only. No credentials and no API tokens: every check is an anonymous read of
a public URL -- what a stranger (and Google) actually sees. Local file paths and
file:// URLs are also accepted, which is what makes the fault-injection self-test
(scripts/test-verify-presence.py) reproducible without network.

Expected values come from nap-doctrine section 5 (canonical strings) and
profile-copy rev 1 (HUM-10, the copy blocks). If this manifest and nap-doctrine
disagree, nap-doctrine wins and the manifest is wrong -- fix the manifest.

Durability note (2026-09-28): this file exists because the rev 1 harness was
written into run scratch, which Paperclip deletes when the run ends, leaving the
two documents that tell you to run it pointing at nothing. It lives in the repo
next to preflight.py / postcutover.py so it survives the run that wrote it.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

TIMEOUT = 20
UA = "HummelLLC-presence-verify/1.0 (profile verification; contact hello@hummelllc.com)"


def fetch(url: str) -> tuple[int, str]:
    """Return (status, body_text). (`status` 0 means the fetch itself failed.)"""
    p = url[7:] if url.startswith("file://") else url
    if not url.startswith(("http://", "https://")) and Path(p).exists():
        return 200, Path(p).read_text(encoding="utf-8", errors="replace")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:  # noqa: S310
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return 0, f"__FETCH_ERROR__ {type(e).__name__}: {e}"


def negated(body: str, start: int) -> bool:
    """True when a guardrail match is itself a negation ("is not an always-on,
    ticket-driven MSP"), which is approved copy, not a claim."""
    return re.search(r"\b(not|never|no|isn't|without)\b", body[max(0, start - 45):start], re.I) is not None


def check_profile(entry: dict, man: dict) -> list[str]:
    """Return failure strings; empty list means PASS."""
    url = entry["url"]
    exp = entry.get("expect", {})
    fails: list[str] = []

    status, body = fetch(url)
    if status == 0:
        return [f"unreachable: {body}"]
    if status != exp.get("status", 200):
        fails.append(f"HTTP {status} (expected {exp.get('status', 200)})")
    if status != 200:
        return fails

    for text in exp.get("must_contain", []):
        if text not in body:
            fails.append(f"missing required string: {text!r}")
    for pat in exp.get("must_not_contain", []):
        if re.search(pat, body, re.I):
            fails.append(f"forbidden pattern present: {pat!r}")
    for banned in man["staging_urls"]:
        if banned and banned in body:
            fails.append(f"STAGING URL LEAKED: {banned}")
    for pat in man["guardrail_patterns"]:
        for m in re.finditer(pat, body, re.I):
            if not negated(body, m.start()):
                fails.append(f"guardrail claim found: {pat!r} (offset {m.start()})")
                break
    return fails


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    show_all = "--all" in sys.argv
    manifest_path = args[0] if args else "scripts/presence-manifest.json"
    only = args[1] if len(args) > 1 else None

    man = json.loads(Path(manifest_path).read_text())
    canon = man["canonical"]
    published = [p for p in man["profiles"] if p.get("url") and (only is None or p["key"] == only)]

    print(f"presence-verify -- manifest {manifest_path}")
    print(f"canonical: {canon['name']} | {canon['website']} | {canon['email']}\n")
    failures_total = 0
    for p in published:
        fails = check_profile(p, man)
        failures_total += bool(fails)
        print(f"[{'PASS' if not fails else 'FAIL'}] {p['key']:<17} {p['url']}")
        for f in fails:
            print(f"          - {f}")
    unpublished = [p for p in man["profiles"] if not p.get("url")]
    if show_all:
        print("\nnot published yet (nothing to verify):")
        for p in unpublished:
            print(f"  - {p['key']:<17} {p['label']}  [{p.get('state', 'not created')}]")
    else:
        print(f"\n{len(unpublished)} profile(s) have no URL yet -- run with --all to list them.")
    print(f"\npublished checked: {len(published)}  failures: {failures_total}")
    return 1 if failures_total else 0


if __name__ == "__main__":
    sys.exit(main())