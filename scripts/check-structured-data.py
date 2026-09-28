#!/usr/bin/env python3
"""
Hummel LLC — verify the site's JSON-LD against `nap-doctrine` rev 3, value by value.

Written for HUM-12 (findability): the acceptance was "the block validates in
Google's Rich Results Test, contains no key outside the fixed list, and the values
match nap-doctrine §5 character for character". A JSON syntax check proves none of
that, so this script compares the parsed node against scripts/doctrine_nap.py —
the module that quotes the doctrine — and prints one line per value.

    python3 scripts/check-structured-data.py                    # index.html on disk
    python3 scripts/check-structured-data.py --url https://hummelllc.com/   # production
    python3 scripts/check-structured-data.py --json             # print the node
                                                                 # (paste into Google's
                                                                 # Rich Results Test)

Exit 0 = the node matches the doctrine exactly; 1 = at least one FAIL.
"""

import argparse
import json
import os
import sys
import urllib.request

import doctrine_nap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = "index.html"


def read_source(url, path):
    if url:
        req = urllib.request.Request(url, headers={"User-Agent": "hummelllc-structured-data-check"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read(400000).decode("utf-8", "replace"), url
        except Exception as e:  # noqa: BLE001
            sys.exit(f"could not fetch {url}: {type(e).__name__}: {e}")
    path = path or os.path.join(ROOT, HOME)
    with open(path, encoding="utf-8") as fh:
        return fh.read(), path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="check a served page instead of the file on disk")
    ap.add_argument("--file", help="check this HTML file (default: index.html in the repo)")
    ap.add_argument("--json", action="store_true", help="print the canonical node and exit")
    args = ap.parse_args()

    if args.json:
        print(doctrine_nap.render())
        return 0

    html, source = read_source(args.url, args.file)
    print(f"structured data check — {source}")
    print(f"doctrine: nap-doctrine rev 3 §5 (+ §2 for the locality and the service area; "
          f"profile-inventory §3.1 for the place list)\n")

    problems, data = doctrine_nap.validate_html(html)
    if data is None:
        for p in problems:
            print(f"  FAIL  {p}")
        print(f"\nFAIL — 1 problem, node cannot be read")
        return 1

    fails = []
    top = list(data.keys())
    print(f"  node keys ({len(top)}): {', '.join(top)}")
    expected = ", ".join(doctrine_nap.TOP_KEYS)
    if set(top) == set(doctrine_nap.TOP_KEYS):
        print(f"  ok    key set is exactly the doctrine list: {expected}")
    else:
        extra = [k for k in top if k not in doctrine_nap.TOP_KEYS]
        missing = [k for k in doctrine_nap.TOP_KEYS if k not in top]
        for k in extra:
            why = doctrine_nap.FORBIDDEN.get(k, "a new key needs a doctrine revision first (nap-doctrine §6.1)")
            fails.append(f"key `{k}` is present but is not a doctrine value — {why}")
        for k in missing:
            fails.append(f"key `{k}` is missing")
    print()

    # value-by-value, so a reader can compare against the doctrine table by eye
    rows = [
        ("@context", data.get("@context"), "https://schema.org"),
        ("@type", data.get("@type"), "ProfessionalService"),
        ("name", data.get("name"), doctrine_nap.NAME),
        ("url", data.get("url"), doctrine_nap.URL),
        ("email", data.get("email"), doctrine_nap.EMAIL),
        ("areaServed", data.get("areaServed"), doctrine_nap.AREA_SERVED),
        ("address.addressLocality", (data.get("address") or {}).get("addressLocality"), doctrine_nap.LOCALITY),
        ("address.addressRegion", (data.get("address") or {}).get("addressRegion"), doctrine_nap.REGION),
    ]
    width = max(len(r[0]) for r in rows)
    for key, got, want in rows:
        if got == want:
            shown = got if not isinstance(got, list) else f"{len(got)} places: " + ", ".join(got)
            print(f"  ok    {key.ljust(width)}  {shown}")
        else:
            print(f"  FAIL  {key.ljust(width)}  found {got!r}, doctrine says {want!r}")
            fails.append(f"{key}: {got!r} != {want!r}")

    addr_keys = list((data.get("address") or {}).keys())
    if addr_keys == doctrine_nap.ADDRESS_KEYS:
        print(f"  ok    address keys exactly {', '.join(doctrine_nap.ADDRESS_KEYS)}")
    else:
        print(f"  FAIL  address keys {addr_keys}, expected {doctrine_nap.ADDRESS_KEYS}")
        fails.append(f"address keys {addr_keys}")

    for key in doctrine_nap.FORBIDDEN:
        if json.dumps(data).count(f'"{key}"'):
            fails.append(f"forbidden key `{key}` present — {doctrine_nap.FORBIDDEN[key]}")
    if not any("forbidden key" in f for f in fails):
        banned = ", ".join(sorted(doctrine_nap.FORBIDDEN))
        print(f"  ok    none of the banned keys present ({len(doctrine_nap.FORBIDDEN)}: {banned})")

    # problems from validate() that the tables above did not already surface
    for p in problems:
        if p not in fails:
            fails.append(p)

    print()
    if fails:
        print(f"FAIL — {len(fails)} problem(s):")
        for f in fails:
            print(f"  - {f}")
        print("\nValues come from scripts/doctrine_nap.py; change the doctrine first "
              "(nap-doctrine §6.1), then reinstall with scripts/set-social-meta.py.")
        return 1
    print(f"PASS — {len(rows) + 2} checks, 0 problems. Node matches nap-doctrine rev 3 exactly, "
          f"no key outside the fixed list.")
    print("Note: this proves the values and the key set. Google's Rich Results Test proves "
          "Google parses it — paste the --json output there (or the page URL once deployed).")
    return 0


if __name__ == "__main__":
    sys.exit(main())