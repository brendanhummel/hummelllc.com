#!/usr/bin/env python3
"""Prove the fixed engage gate can still FAIL — and passes on correct content.

Throwaway (run scratch, not committed): monkeypatches postcutover.fetch() so we
can feed it doctored HTML/JS without touching the live site.
"""
import importlib.util
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("pc", f"{REPO}/scripts/postcutover.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)

HTML_OK = '<form id="contact-form"></form><script src="../assets/js/contact.js"></script>'
JS_OK = 'const cfg = { endpoint: "", email: "hello@hummelllc.com", scheduleUrl: "" };'

CASES = [
    ("correct content (expect ok)",
     {"engage/": HTML_OK, "assets/js/contact.js": JS_OK}, True),
    ("wrong address (expect FAIL)",
     {"engage/": HTML_OK, "assets/js/contact.js": JS_OK.replace("hello@", "info@")}, False),
    ("no transport at all (expect FAIL)",
     {"engage/": HTML_OK, "assets/js/contact.js": 'const cfg = { endpoint: "", email: "", scheduleUrl: "" };'}, False),
    ("endpoint-only transport (expect ok)",
     {"engage/": HTML_OK, "assets/js/contact.js": 'const cfg = { endpoint: "https://formspree.io/f/x", email: "hello@hummelllc.com" };'}, True),
    ("page does not load contact.js (expect FAIL)",
     {"engage/": '<form id="contact-form"></form>', "assets/js/contact.js": JS_OK}, False),
    ("form markup missing (expect FAIL)",
     {"engage/": '<p>no form</p>', "assets/js/contact.js": JS_OK}, False),
    ("JS not fetchable (expect FAIL)",
     {"engage/": HTML_OK, "assets/js/contact.js": None}, False),
]

failures = 0
for name, pages, should_pass in CASES:
    pc.FAILS.clear(); pc.WARNS.clear(); pc.OKS.clear()

    def fake_fetch(url, method="GET", _pages=pages):
        if url.endswith("/engage/"):
            val = _pages.get("engage/")
        elif "contact.js" in url:
            val = _pages.get("assets/js/contact.js")
        else:
            val = None
        if val is None:
            return None, "", url, "URLError: simulated"
        return 200, val, url, None

    pc.fetch = fake_fetch
    pc.check_engage_form()
    passed = not pc.FAILS
    verdict = "ok" if passed else f"FAIL: {pc.FAILS[0][:70]}"
    match = "PASS" if passed == should_pass else "*** WRONG ***"
    if passed != should_pass:
        failures += 1
    print(f"  {match:14s} {name:42s} -> {verdict}")

print()
print("engage gate behaves correctly in all 7 cases" if failures == 0
      else f"{failures} case(s) wrong")
sys.exit(1 if failures else 0)
