#!/usr/bin/env python3
"""
Hummel LLC — the canonical entity node for the site's JSON-LD, with citations.

Structured data is markup nobody reads on the page, so it is the one place where
an invented value would go unnoticed. Therefore every string in ``NODE`` below is
quoted from a governing document instead of written here, and the docstring of
each value says which one — copy-paste is the only allowed direction:

    name           -> `nap-doctrine` rev 3 §5 "Display name | `Hummel LLC` | FINAL"
    url            -> `nap-doctrine` rev 3 §4/§5 "Website | `https://hummelllc.com/` | FINAL"
                      (cutover verified 2026-09-28; the apex https form only)
    email          -> `nap-doctrine` rev 3 §5 "Contact email | `hello@hummelllc.com` | FINAL"
    addressLocality-> `nap-doctrine` rev 3 §2 "Where a field demands a location and the
                      address is hidden: `Columbia, SC`"  -> city `Columbia`, state `SC`
    areaServed     -> `nap-doctrine` rev 3 §2 "Service area ... is a list of named
                      places, not a radius" + `profile-inventory` §3.1, the approved
                      list that "must be identical in every platform's service-area field"

Deliberately absent — and enforced, not merely omitted (each ban is a doctrine rule):

    telephone       §3  status PENDING; "do not publish a phone number until it is in
                        this document". Founder input is the unblock.
    streetAddress   §2  the address is never displayed: service-area business.
    addressCountry  §2  the locality form published is `Columbia, SC`; the doctrine
                        defines no country field, so none is published.
    postalCode      §5  "undecided ... PENDING" — a form demanding it comes first.
    openingHours    §4  "Hours: none published" (`brief` §6 bans 24/7 / always-on).
    legalName       §1  the LLC is not filed; no incorporated-entity claim.
    foundingDate    §1  same rule — no entity metadata while the entity is unfiled.
    aggregateRating §5/`brief` §6  no clients yet; no rating or review may be implied.
    review          same.
    logo            the entity node is not a place to publish brand assets; the logo
                    lives on-page and in the favicons. (Not a doctrine value.)
    description     would duplicate the meta description as a second, silently
                    drifting copy of marketing copy. The page's own text is the
                    description; `site-copy` remains its single source.

Rule (nap-doctrine §6.1 "change here first"): a new value — a phone, a street
address, hours — is added to the doctrine, then to this file, never the reverse.
If a value is missing from the doctrine, it does not get published.

Consumers: scripts/set-social-meta.py installs ``render()`` into index.html,
scripts/check-structured-data.py and scripts/preflight.py validate a page (or a
live URL) against ``validate()``.
"""

import json
import re

BLOCK_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

NAME = "Hummel LLC"
URL = "https://hummelllc.com/"
EMAIL = "hello@hummelllc.com"
LOCALITY = "Columbia"
REGION = "SC"
AREA_SERVED = [
    "Columbia",
    "West Columbia",
    "Cayce",
    "Lexington",
    "Irmo",
    "Chapin",
    "Blythewood",
    "Newberry",
    "Camden",
    "Sumter",
]

# `ProfessionalService` (a LocalBusiness type) rather than `Organization`: the
# useful answer for a one-person practice is "who serves this locality", and only
# the LocalBusiness family carries the service area. The type is fixed by the
# engineering decision on HUM-12 and adds no claim the doctrine does not already
# publish — no hours, no address, no rating (see the bans above).
NODE = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "name": NAME,
    "url": URL,
    "email": EMAIL,
    "areaServed": list(AREA_SERVED),
    "address": {
        "@type": "PostalAddress",
        "addressLocality": LOCALITY,
        "addressRegion": REGION,
    },
}

# The complete, closed set of keys. A key outside this list is a failure, not a
# bonus: every extra key is an unpublished claim (or a second source of truth).
TOP_KEYS = ["@context", "@type", "name", "url", "email", "areaServed", "address"]
ADDRESS_KEYS = ["@type", "addressLocality", "addressRegion"]

# Named bans, so a failure explains itself. Each maps to the doctrine rule it breaks.
FORBIDDEN = {
    "telephone": "nap-doctrine §3 — phone is PENDING founder input; nothing publishes it yet",
    "streetAddress": "nap-doctrine §2 — service-area business; the address is never displayed",
    "postalCode": "nap-doctrine §5 — postal code is PENDING; no form has demanded it yet",
    "addressCountry": "nap-doctrine §2/§5 — the published locality form is `Columbia, SC` only",
    "openingHours": "nap-doctrine §4 + brief §6 — no hours are published (year one is ~5 hrs/wk)",
    "openingHoursSpecification": "nap-doctrine §4 — no hours, in any encoding",
    "legalName": "nap-doctrine §1 — the LLC is not filed; no entity claim may be made",
    "foundingDate": "nap-doctrine §1 — no entity metadata while the entity is unfiled",
    "aggregateRating": "brief §6 — no clients yet, so no rating may be implied",
    "review": "brief §6 — no clients yet, so no review may be implied",
    "logo": "brand assets live on-page; the doctrine defines no logo value for NAP",
    "description": "would duplicate the meta description as a silently drifting second copy",
    "priceRange": "no published pricing claim exists in `brief`/`site-copy`",
    "sameAs": "no profile URLs exist yet (M3-B); doctrine defines none",
}


def render():
    """The installed block body — character-for-character the doctrine values."""
    return json.dumps(NODE, indent=2, ensure_ascii=False)


def validate(data):
    """Return a list of problems ([] = the node matches the doctrine exactly).

    ``data`` is the parsed JSON of a page's application/ld+json block.
    """
    problems = []
    if not isinstance(data, dict):
        return ["JSON-LD root is not an object"]

    top = list(data.keys())
    for key in TOP_KEYS:
        if key not in data:
            problems.append(f"missing key `{key}` (doctrine requires it)")
    for key in top:
        if key not in TOP_KEYS:
            why = FORBIDDEN.get(key)
            problems.append(
                f"key `{key}` is not in the doctrine value list"
                + (f" — {why}" if why else " — a new key needs a doctrine revision first (nap-doctrine §6.1)")
            )

    if data.get("@context") != "https://schema.org":
        problems.append(f"@context is {data.get('@context')!r}, expected 'https://schema.org'")
    if data.get("@type") != "ProfessionalService":
        problems.append(f"@type is {data.get('@type')!r}, expected 'ProfessionalService'")
    if data.get("name") != NAME:
        problems.append(f"name is {data.get('name')!r}, doctrine §5 says {NAME!r}")
    if data.get("url") != URL:
        problems.append(f"url is {data.get('url')!r}, doctrine §5 says {URL!r} (apex https, trailing slash)")
    if data.get("email") != EMAIL:
        problems.append(f"email is {data.get('email')!r}, doctrine §5 says {EMAIL!r}")
    if data.get("areaServed") != AREA_SERVED:
        problems.append(
            f"areaServed is {data.get('areaServed')!r}, expected the profile-inventory §3.1 "
            f"list in order: {AREA_SERVED!r}"
        )

    addr = data.get("address")
    if not isinstance(addr, dict):
        problems.append("address is not an object with addressLocality/addressRegion")
    else:
        for key in ADDRESS_KEYS:
            if key not in addr:
                problems.append(f"address is missing `{key}`")
        for key in addr:
            if key not in ADDRESS_KEYS:
                why = FORBIDDEN.get(key)
                problems.append(
                    f"address key `{key}` is not in the doctrine value list"
                    + (f" — {why}" if why else " — a new key needs a doctrine revision first")
                )
        if addr.get("@type") != "PostalAddress":
            problems.append(f"address @type is {addr.get('@type')!r}, expected 'PostalAddress'")
        if addr.get("addressLocality") != LOCALITY:
            problems.append(f"addressLocality is {addr.get('addressLocality')!r}, doctrine §2 says {LOCALITY!r}")
        if addr.get("addressRegion") != REGION:
            problems.append(f"addressRegion is {addr.get('addressRegion')!r}, doctrine §2 says {REGION!r}")
    return problems


def validate_html(html):
    """Convenience for a whole page: extract the block, then validate it.

    Returns (problems, data) — ``data`` is None when no block is present or it
    does not parse.
    """
    m = BLOCK_RE.search(html)
    if m is None:
        return ["no <script type=\"application/ld+json\"> block on the page"], None
    try:
        data = json.loads(m.group(1))
    except ValueError as e:
        return [f"the JSON-LD block does not parse ({e}) — structured data is inert to crawlers"], None
    return validate(data), data


if __name__ == "__main__":  # pragma: no cover - manual inspection only
    print(render())