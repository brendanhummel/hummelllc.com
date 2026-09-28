#!/usr/bin/env python3
"""
Hummel LLC — header logo payload fix + markup wiring.

WHY: `assets/logo.png` is the 1083x1020 brand master (272 KB). The header renders
it at `height: 2.9rem` (~46 px), so every page view downloaded ~270 KB of pixels
that were thrown away on arrival. This script derives display-sized variants from
the master (which is never modified — it stays the brand source file) and wires
the header <img> on all pages to the right one.

    python3 scripts/optimize-logo.py            # generate variants + wire markup
    python3 scripts/optimize-logo.py --check     # verify only (exit 1 if stale/oversize)

Idempotent: re-running regenerates the same pixels and rewrites only if the
markup differs. Pillow is used when available; macOS `sips` is the fallback.
"""

import argparse
import os
import re
import struct
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MASTER = "assets/logo.png"
# Header logo box: site.css `.brand img { height: 2.9rem }` -> 46.4 px at 16px root.
VARIANT_HEIGHTS = {1: 46, 2: 93}
MAX_VARIANT_BYTES = 24 * 1024  # a display-sized logo has no business exceeding this

PAGES = [
    "index.html",
    "what-we-do/index.html",
    "who-its-for/index.html",
    "how-it-works/index.html",
    "about/index.html",
    "engage/index.html",
    "404.html",
]

IMG_RE = re.compile(r'<img src="(?P<prefix>[^"]*)assets/logo(?:-\d+)?\.png"(?: srcset="[^"]*")?'
                    r' alt="Hummel LLC" width="\d+" height="\d+">')


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def master_size():
    with open(os.path.join(ROOT, MASTER), "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"{MASTER}: not a PNG — cannot derive variants")
    return struct.unpack(">II", head[16:24])


def variant_path(scale):
    return f"assets/logo-{VARIANT_HEIGHTS[scale]}.png"


def variant_dims():
    w, h = master_size()
    dims = {}
    for scale, height in VARIANT_HEIGHTS.items():
        dims[scale] = (round(height * w / h), height)
    return dims


def generate():
    dims = variant_dims()
    made = []
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        Image = None
    for scale, (width, height) in dims.items():
        out = os.path.join(ROOT, variant_path(scale))
        if Image is not None:
            with Image.open(os.path.join(ROOT, MASTER)) as im:
                # Keep the master's own channel model: it is an opaque RGB mark, so
                # converting to RGBA would only add bytes and alpha-fringe risk.
                src = im.convert("RGBA") if (im.mode in ("RGBA", "LA", "P") and "transparency" in im.info) else im.convert("RGB")
                src.resize((width, height), Image.LANCZOS).save(out, format="PNG", optimize=True)
        else:  # macOS fallback: sips resamples and writes an optimized PNG
            subprocess.run(["sips", "-z", str(height), str(width), MASTER, "--out", out],
                           check=True, capture_output=True)
        made.append((variant_path(scale), os.path.getsize(out), width, height))
    return made


def expected_markup(prefix, dims):
    src = f"{prefix}{variant_path(1)}"
    srcset = f"{prefix}{variant_path(1)} 1x, {prefix}{variant_path(2)} 2x"
    width, height = dims[1]
    return (f'<img src="{src}" srcset="{srcset}" alt="Hummel LLC" '
            f'width="{width}" height="{height}">')


def wire_markup(check_only):
    dims = variant_dims()
    changed, mismatches = [], []
    for page in PAGES:
        text = read(page)
        found = IMG_RE.search(text)
        if found is None:
            sys.exit(f"{page}: header logo <img> not found — markup shape changed, update IMG_RE")
        want = expected_markup(found.group("prefix"), dims)
        if found.group(0) == want:
            continue
        if check_only:
            mismatches.append(page)
            continue
        new = IMG_RE.sub(lambda m: expected_markup(m.group("prefix"), dims), text)
        with open(os.path.join(ROOT, page), "w", encoding="utf-8") as fh:
            fh.write(new)
        changed.append(page)
    return changed, mismatches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="verify only, change nothing")
    args = ap.parse_args()

    master_bytes = os.path.getsize(os.path.join(ROOT, MASTER))
    dims = variant_dims()
    if not args.check:
        made = generate()
        for path, size, width, height in made:
            print(f"  wrote   {path}  {width}x{height}  {size:,} bytes")
    else:
        made = []
        for scale, (width, height) in dims.items():
            path = os.path.join(ROOT, variant_path(scale))
            if not os.path.exists(path):
                sys.exit(f"MISSING {variant_path(scale)} — run: python3 scripts/optimize-logo.py")
            made.append((variant_path(scale), os.path.getsize(path), width, height))

    changed, mismatches = wire_markup(args.check)
    if args.check and mismatches:
        sys.exit("stale logo markup in: " + ", ".join(mismatches) +
                 " — run: python3 scripts/optimize-logo.py")
    if changed:
        print(f"  updated {len(changed)} page(s): {', '.join(changed)}")

    biggest = max(s for _, s, _, _ in made)
    print(f"\nmaster  {MASTER}  {master_bytes:,} bytes (untouched — brand source)")
    for path, size, width, height in made:
        print(f"  served {path}  {width}x{height}  {size:,} bytes  "
              f"({100 - round(size * 100 / master_bytes)}% smaller)")
    print(f"header payload {master_bytes:,} -> {biggest:,} bytes per page view")
    if biggest > MAX_VARIANT_BYTES:
        sys.exit(f"FAIL: largest variant is {biggest:,} bytes (> {MAX_VARIANT_BYTES:,})")
    print("logo payload OK")


if __name__ == "__main__":
    main()