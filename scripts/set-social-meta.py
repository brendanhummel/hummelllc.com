#!/usr/bin/env python3
"""
Hummel LLC — share-card + structured-data meta.

WHY: every page carries og:title/description/image/url, but nothing told X/Slack/
Teams to render the image (no twitter:card) and nothing told a search engine what
the business entity is (no JSON-LD). Both are add-only tags built from copy that is
already on the page — no new business claims are introduced here.

    python3 scripts/set-social-meta.py            # add/refresh the tags
    python3 scripts/set-social-meta.py --check     # verify only (exit 1 if missing)

Idempotent: existing tags are refreshed in place, missing ones are inserted after
the og:image tag, and a second run makes no change.
"""

import argparse
import os
import re
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
# 404.html is deliberately excluded: it is a noindex error page with no og tags,
# so a share card and an Organization node would add nothing.
HOME = "index.html"

SITE_NAME = "Hummel LLC"
OG_IMAGE = "https://hummelllc.com/assets/og-image.png"
OG_IMAGE_W, OG_IMAGE_H = 1200, 630

MARKER_BEGIN = "  <!-- social / structured data — installed by scripts/set-social-meta.py -->"
MARKER_END = "  <!-- end social / structured data -->"


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as fh:
        fh.write(text)


def req(pattern, text, path, what):
    m = re.search(pattern, text, re.S)
    if m is None:
        sys.exit(f"{path}: {what} not found — page head shape changed, update set-social-meta.py")
    return m.group(1).strip()


def meta_tags(text, path):
    """The tags this script owns, derived from the page's own title/description."""
    title = req(r"<title>(.*?)</title>", text, path, "title")
    desc = req(r'name="description" content="([^"]*)"', text, path, "meta description")
    return [
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{desc}">',
        f'<meta name="twitter:image" content="{OG_IMAGE}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:image:width" content="{OG_IMAGE_W}">',
        f'<meta property="og:image:height" content="{OG_IMAGE_H}">',
    ]


def jsonld(text, path):
    """Organization node for the home page — every value is already public on-page."""
    desc = req(r'name="description" content="([^"]*)"', text, path, "meta description")
    email = req(r'email:\s*"([^"]+)"', read("assets/js/contact.js"), "assets/js/contact.js", "contact email")
    return (
        '<script type="application/ld+json">\n'
        + "{\n"
        + '  "@context": "https://schema.org",\n'
        + '  "@type": "Organization",\n'
        + f'  "name": "{SITE_NAME}",\n'
        + '  "url": "https://hummelllc.com/",\n'
        + f'  "logo": "https://hummelllc.com/assets/logo.png",\n'
        + f'  "email": "{email}",\n'
        + f'  "description": "{desc}"\n'
        + "}\n"
        + "</script>"
    )


def block_for(page, text):
    body = "\n".join("  " + line for line in meta_tags(text, page))
    if page == HOME:
        body += "\n\n" + "\n".join("  " + line for line in jsonld(text, page).splitlines())
    return f"{MARKER_BEGIN}\n{body}\n{MARKER_END}"


def strip_managed(text):
    """Remove any previously installed block plus the individual tags it owns."""
    text = re.sub(re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END) + r"\n?", "", text, flags=re.S)
    owned = [
        r'\s*<meta name="twitter:(?:card|title|description|image)" content="[^"]*">',
        r'\s*<meta property="og:site_name" content="[^"]*">',
        r'\s*<meta property="og:image:(?:width|height)" content="[^"]*">',
    ]
    for pat in owned:
        text = re.sub(pat, "", text)
    return text


def apply(check_only):
    changed, missing = [], []
    for page in PAGES:
        raw = read(page)
        want = block_for(page, raw)
        clean = strip_managed(raw)
        # anchor: straight after og:image (the last og tag every page shares)
        anchor = re.search(r'^\s*<meta property="og:image"[^\n]*\n', clean, re.M)
        if not anchor:
            sys.exit(f"{page}: no og:image tag to anchor to — page head shape changed")
        new = clean[:anchor.end()] + want + "\n" + clean[anchor.end():]
        if raw == new:
            continue
        if check_only:
            missing.append(page)
            continue
        write(page, new)
        changed.append(page)
    return changed, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    changed, missing = apply(args.check)
    if args.check and missing:
        sys.exit("missing/stale share-card meta on: " + ", ".join(missing) +
                 " — run: python3 scripts/set-social-meta.py")
    if changed:
        print(f"  updated {len(changed)} page(s): {', '.join(changed)}")
    else:
        print("  already current — no change")
    print(f"  share card: summary_large_image + {OG_IMAGE_W}x{OG_IMAGE_H} og image on {len(PAGES)} pages")
    print(f"  structured data: Organization JSON-LD on {HOME}")


if __name__ == "__main__":
    main()