#!/usr/bin/env python3
"""
Hummel LLC — share-card + structured-data meta.

WHY: every page carries og:title/description/image/url, but nothing told X/Slack/
Teams to render the image (no twitter:card) and nothing told a search engine what
the business entity is (no JSON-LD). The share-card tags are derived from copy
already on the page. The structured-data node is NOT derived from anything here:
it is installed verbatim from scripts/doctrine_nap.py, which quotes `nap-doctrine`
rev 3 field by field — a crawler reading the node must get the doctrine value, not
a paraphrase of the page copy.

    python3 scripts/set-social-meta.py            # add/refresh the tags
    python3 scripts/set-social-meta.py --check     # verify only (exit 1 if missing)

Idempotent: existing tags are refreshed in place, missing ones are inserted after
the og:image tag, and a second run makes no change.
"""

import argparse
import os
import re
import sys

import doctrine_nap

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
    """The entity node for the home page.

    Values come from scripts/doctrine_nap.py, which quotes `nap-doctrine` rev 3
    field by field — nothing here is written from scratch, and the block is a
    closed key set. This function deliberately does NOT derive anything from the
    page copy: the node must not drift when marketing copy is edited.
    """
    # Guard: the published email lives in the doctrine and in contact.js. If the
    # site's own contact address ever changes, the doctrine changes first and this
    # stops the build rather than publishing two different addresses.
    site_email = req(r'email:\s*"([^"]+)"', read("assets/js/contact.js"), "assets/js/contact.js", "contact email")
    if site_email != doctrine_nap.EMAIL:
        sys.exit(f"assets/js/contact.js publishes {site_email!r} but nap-doctrine §5 says "
                 f"{doctrine_nap.EMAIL!r} — fix the doctrine first (nap-doctrine §6.1), then this.")
    return (
        '<script type="application/ld+json">\n'
        + "\n".join("  " + line for line in doctrine_nap.render().splitlines())
        + "\n</script>"
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
    problems, _ = doctrine_nap.validate_html(read(HOME))
    if problems:
        sys.exit(f"  structured data: {HOME} does not match nap-doctrine rev 3:\n    - " +
                 "\n    - ".join(problems))
    print(f"  structured data: {doctrine_nap.NODE['@type']} node on {HOME} — "
          f"{len(doctrine_nap.TOP_KEYS)} keys, all values from nap-doctrine §5")


if __name__ == "__main__":
    main()