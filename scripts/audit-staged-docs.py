#!/usr/bin/env python3
"""Pre-publish NAP consistency gate for the staged M3 presence documents.

Before the owner sitting that creates Hummel LLC's profiles, every value that
will be pasted is staged in Paperclip documents (`nap-doctrine`,
`profile-inventory`, `profile-copy`, `m3b-publish-pack`, ...). Those documents
are hand-maintained prose. If one of them still carries an old phone number, a
staging URL or a `www` form, the founder pastes it and the profile is wrong from
minute one — the exact NAP failure the presence work exists to prevent.

This script checks a directory of markdown files against the canonical values in
`scripts/presence-manifest.json` and reports two severities:

  FAIL    a value that must not be pasted anywhere (staging URL, wrong phone)
  REVIEW  something a human must look at in context (narrative mentions of a
          URL variant, the doctrine's own "never use this form" lists)

Only FAIL findings set the exit code, so REVIEW can never be tuned away by
weakening a rule until the check goes green.

Usage:
    python3 scripts/audit-staged-docs.py <dir> [<dir> ...]
    python3 scripts/audit-staged-docs.py --self-test
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "presence-manifest.json")

PHONE_RE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}\b")
URL_RE = re.compile(r"https?://[^\s)\]}`\"'<>]+")
STAGING_RE = re.compile(r"github\.io", re.I)
# Forbidden display-name forms (nap-doctrine section 1): matched case-sensitively
# for the run-together form so that the domain "hummelllc.com" never matches.
BAD_NAME_RE = re.compile(r"\bHummelLLC\b|\bHummel LLC,\s*Inc\.")
GUARD_RE = re.compile(
    r"\b(HIPAA|CJIS|NIST|24\s*/\s*7|24x7|always[-\s]?on|certified|EIN|"
    r"guarantee[ds]?|registered in SC|Inc\.)\b",
    re.I,
)


def digits(s):
    d = re.sub(r"\D", "", s)
    return d[1:] if len(d) == 11 and d.startswith("1") else d


def load_canonical(manifest=MANIFEST):
    with open(manifest) as fh:
        man = json.load(fh)
    c = man["canonical"]
    for key in ("name", "website", "email", "phone", "phone_e164"):
        if not c.get(key):
            raise SystemExit("manifest canonical block is missing %r" % key)
    return c


def audit_text(fn, text, canon):
    """Return (fails, reviews); each item is (line, kind, detail)."""
    fails, reviews = [], []
    site = canon["website"]
    want = {digits(canon["phone"]), digits(canon["phone_e164"])}
    for i, line in enumerate(text.splitlines(), 1):
        for m in PHONE_RE.finditer(line):
            if digits(m.group(0)) not in want:
                fails.append((i, "PHONE", "digits do not match the canonical number"))
        for m in URL_RE.finditer(line):
            url = m.group(0).rstrip(".,;:")
            if STAGING_RE.search(url):
                fails.append((i, "STAGING-URL", url[:70]))
            elif "hummelllc.com" in url and not url.startswith(site):
                reviews.append((i, "SITE-URL-VARIANT", url[:70]))
        for m in BAD_NAME_RE.finditer(line):
            reviews.append((i, "NAME-FORM", m.group(0)))
        for m in GUARD_RE.finditer(line):
            reviews.append((i, "GUARDRAIL-WORD", m.group(0)))
    return fails, reviews


def audit_dirs(dirs):
    canon = load_canonical()
    total_fail = 0
    files = 0
    for d in dirs:
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            files += 1
            path = os.path.join(d, fn)
            with open(path) as fh:
                fails, reviews = audit_text(fn, fh.read(), canon)
            total_fail += len(fails)
            print("--- %s: %d FAIL, %d review" % (fn, len(fails), len(reviews)))
            for line, kind, detail in fails:
                print("    FAIL   L%-4d %-16s %s" % (line, kind, detail))
            for line, kind, detail in reviews:
                print("    review L%-4d %-16s %s" % (line, kind, detail))
    print()
    print("staged-docs NAP audit: %d file(s), %d FAIL, exit %d"
          % (files, total_fail, 1 if total_fail else 0))
    return 1 if total_fail else 0


SELF_TEST_CASES = [
    # (label, text, expect_fail_kinds)
    ("clean line -> no FAIL",
     "Phone `(803) 816-2204` · website `https://hummelllc.com/`\n", []),
    ("staging URL -> FAIL",
     "see https://brendanhummel.github.io/hummelllc.com/ for staging\n",
     ["STAGING-URL"]),
    ("www variant -> FAIL on the phone rule, review on the URL",
     "Call (803) 555-0100 — https://www.hummelllc.com/\n", ["PHONE"]),
    ("wrong-area-code phone -> FAIL",
     "Phone (803) 816-2205\n", ["PHONE"]),
]


def self_test():
    canon = load_canonical()
    ok = 0
    for label, text, want in SELF_TEST_CASES:
        fails, _ = audit_text("fixture", text, canon)
        got = [k for _, k, _ in fails]
        good = sorted(got) == sorted(want)
        ok += good
        print("%s  %s  want=%s got=%s" % ("ok " if good else "BAD", label, want, got))
    print("\n%d/%d self-test cases behave correctly" % (ok, len(SELF_TEST_CASES)))
    return 0 if ok == len(SELF_TEST_CASES) else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "--self-test":
        return self_test()
    dirs = argv[1:]
    if not dirs:
        print(__doc__)
        return 2
    return audit_dirs(dirs)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
