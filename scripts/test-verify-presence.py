#!/usr/bin/env python3
"""test-verify-presence.py -- fault injection for scripts/verify-presence.py (M3-B, HUM-9).

Why this exists: a verifier that has only ever printed PASS is decoration. The
rev 1 harness claimed a four-fixture self-test in its document; the fixtures were
throwaway files in a run scratch dir that no longer exist, so the claim could not
be re-run. This makes the proof reproducible: `python3 scripts/test-verify-presence.py`
builds the four fixtures on the fly, runs the real checker against them, and
asserts the checker fails the broken ones and passes the correct ones.

    python3 scripts/test-verify-presence.py      # exit 0 = the checker behaves

Cases:
  1 fixture-clean     correct page                                   -> PASS
  2 fixture-leak      carries the staging URL                        -> FAIL (both patterns)
  3 fixture-claim     HIPAA/CJIS/24-7/always-on/certified/registered-in-SC
                                                                     -> FAIL (7 guardrail hits)
  4 fixture-name      wrong name form 'HummelLLC' only, no exact 'Hummel LLC'
                                                                     -> FAIL (the name check fires)
  5 fixture-negation  the site's own approved negation, verbatim     -> PASS (no false positive)

Note on case 4: it is a separate fixture on purpose. The rev 1 document claimed
case 3 also proved the name check, but that fixture's body contains "Hummel LLC,
Inc." — which includes the exact string "Hummel LLC", so the name rule was never
exercised. This one is.

Stdlib only, no network: the checker reads local paths.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

FIXTURES = {
    "fixture-clean": """<!doctype html><html><head><title>Hummel LLC — Your Part-Time IT Leader</title></head>
<body><h1>Hummel LLC</h1><p>Your part-time IT leader — senior IT leadership for small businesses.</p>
<p>Website: https://hummelllc.com/ · Columbia, SC · hello@hummelllc.com</p></body></html>
""",
    "fixture-leak": """<!doctype html><html><head><title>Hummel LLC</title></head>
<body><h1>Hummel LLC</h1><p>Website: https://brendanhummel.github.io/hummelllc.com/</p></body></html>
""",
    "fixture-claim": """<!doctype html><html><head><title>HummelLLC — IT Consulting Columbia SC</title></head>
<body><h1>HummelLLC</h1><p>Certified HIPAA and CJIS compliance experts with 24/7 always-on support. https://hummelllc.com/</p>
<p>Hummel LLC, Inc. — registered in SC.</p></body></html>
""",
    "fixture-negation": """<!doctype html><html><head><title>Hummel LLC</title></head>
<body><h1>Hummel LLC</h1><p>Hummel LLC is not an always-on, ticket-driven MSP. https://hummelllc.com/</p></body></html>
""",
    "fixture-name": """<!doctype html><html><head><title>HummelLLC — IT Consulting Columbia SC</title></head>
<body><h1>HummelLLC</h1><p>Senior IT leadership for small businesses. https://hummelllc.com/</p></body></html>
""",
}


def load_checker():
    spec = importlib.util.spec_from_file_location("verify_presence", HERE / "verify-presence.py")
    assert spec is not None and spec.loader is not None, "could not load scripts/verify-presence.py"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    checker = load_checker()
    manifest = json.loads((HERE / "presence-manifest.json").read_text())

    checks = []  # (label, condition, detail)

    with tempfile.TemporaryDirectory(prefix="presence-selftest-") as tmp:
        tmpdir = Path(tmp)
        for name, html in FIXTURES.items():
            (tmpdir / f"{name}.html").write_text(html, encoding="utf-8")

        def run(key: str) -> list[str]:
            entry = {
                "key": key,
                "url": str(tmpdir / f"{key}.html"),
                "expect": {"status": 200, "must_contain": ["Hummel LLC"], "must_not_contain": []},
            }
            return checker.check_profile(entry, manifest)

        # 1. correct page passes
        fails = run("fixture-clean")
        checks.append(("fixture-clean -> PASS", not fails, f"failures={fails}"))

        # 2. leaked staging URL caught, both patterns
        fails = run("fixture-leak")
        leaks = [f for f in fails if "STAGING URL LEAKED" in f]
        checks.append(("fixture-leak -> FAIL on both staging patterns", len(leaks) == 2, f"leaks={leaks}"))

        # 3. guardrail claims caught (>=6)
        fails = run("fixture-claim")
        guards = [f for f in fails if "guardrail claim found" in f]
        checks.append(("fixture-claim -> FAIL on >=6 guardrails", len(guards) >= 6, f"hits={len(guards)}"))

        # 4. wrong name form caught -- needs its own fixture: the claim fixture says
        #    "Hummel LLC, Inc.", which *contains* the exact string "Hummel LLC", so it
        #    never exercised the name check. (The rev 1 document claimed it did; it did not.)
        fails = run("fixture-name")
        missing = [f for f in fails if "missing required string" in f]
        checks.append(("fixture-name -> FAIL on wrong name form (no exact 'Hummel LLC')", bool(missing), f"{missing}"))

        # 5. approved negation is NOT a false positive
        fails = run("fixture-negation")
        checks.append(("fixture-negation -> PASS (approved copy not flagged)", not fails, f"failures={fails}"))

    print("test-verify-presence -- fault injection against scripts/verify-presence.py\n")
    bad = 0
    for label, ok, detail in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<58} {detail}")
        bad += not ok
    print(f"\n{len(checks) - bad}/{len(checks)} cases behave correctly"
          f"{' — checker is decoration' if bad else ' — checker fails things as designed'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())