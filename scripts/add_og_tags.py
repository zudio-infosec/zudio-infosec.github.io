#!/usr/bin/env python3
"""Insert og:image / twitter:image (and the missing og:site_name, twitter:site)
into every page of the portfolio that lacks them.

The image is served from the GitHub Pages site itself, so there is no external
dependency and it always stays in sync with the repo.
"""
import os
import re
import sys

SITE = "https://zudio-infosec.github.io"
IMAGE = SITE + "/og-image.png"

PAGES = {
    "index.html": {
        "title": "Hasham Javed (Zudio) | Offensive Security Researcher & CTF Player",
        "desc": "Offensive security researcher and CTF player from Pakistan. "
                "20 authorized CTF writeups, Python security tooling, and recon automation.",
    },
    "blog.html": {
        "title": "Hasham Javed (Zudio) | CTF Writeups & Security Notes",
        "desc": "Authorized CTF writeups, OSINT walkthroughs, web-security notes, "
                "and Python security-tool breakdowns.",
    },
    "posts/ohsint.html": {
        "title": "OhSINT — TryHackMe Walkthrough | Zudio",
        "desc": "Full walkthrough of the TryHackMe OhSINT room: extracting GPS, "
                "username and a full OSINT trail from a single image file.",
    },
    "posts/kali-lab-setup.html": {
        "title": "Kali Linux Lab Setup | Zudio",
        "desc": "How I built a personal offensive-security lab with Kali Linux and "
                "VirtualBox, and the mistakes that cost me time.",
    },
    "posts/hackathon-2026.html": {
        "title": "Cybersecurity Hackathon 2026 — 11 Challenges Solved | Zudio",
        "desc": "3-day hackathon across web, network, crypto, Android reversing "
                "and DFIR — 11 challenges solved, with the full writeups.",
    },
}

# A page-specific image would be nicer but we ship one card for the whole site.
TEMPLATE = """<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Hasham Javed (Zudio) - Offensive Security Researcher and CTF Player">
<meta name="twitter:image" content="{img}">
<meta name="twitter:image:alt" content="Hasham Javed (Zudio) - Offensive Security Researcher and CTF Player">"""


def upsert(head, tag):
    """Insert tag if missing; if present, replace it."""
    if tag in head:
        return head, False
    # insert right before </head>
    idx = head.lower().rfind("</head>")
    if idx == -1:
        return head, False
    return head[:idx] + tag + "\n" + head[idx:], True


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    changed = []
    for rel, meta in PAGES.items():
        path = os.path.join(root, rel)
        if not os.path.isfile(path):
            print("SKIP (missing): %s" % rel)
            continue
        with open(path, encoding="utf-8") as f:
            src = f.read()

        # refresh title/description to the tighter researcher positioning
        src = re.sub(r'<title>[^<]*</title>',
                     '<title>%s</title>' % meta["title"], src, count=1)
        src = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                     lambda m: m.group(1) + meta["title"] + m.group(2), src, count=1)
        src = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
                     lambda m: m.group(1) + meta["title"] + m.group(2), src, count=1)
        src = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                     lambda m: m.group(1) + meta["desc"] + m.group(2), src, count=1)
        src = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")',
                     lambda m: m.group(1) + meta["desc"] + m.group(2), src, count=1)

        tag = TEMPLATE.format(img=IMAGE)
        src, added = upsert(src, tag)
        if not added:
            print("OK (already tagged): %s" % rel)
            continue

        # upgrade twitter:card from summary -> summary_large_image
        src = src.replace('<meta name="twitter:card" content="summary">',
                          '<meta name="twitter:card" content="summary_large_image">')

        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        changed.append(rel)
        print("PATCHED: %s" % rel)

    print("\n%d page(s) updated." % len(changed))


if __name__ == "__main__":
    main()
