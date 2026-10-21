#!/usr/bin/env python3
"""Unify positioning across the portfolio: 'Cybersecurity Student' -> 'Offensive Security Researcher'.

Keeps one voice everywhere (site, GitHub, LinkedIn, TryHackMe):
    Offensive Security Researcher | CTF Player | Python Security Tooling

Factual statements about the hackathon (student teams, sponsors) are left alone.
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."

# ordered: longest / most specific first
REPLACEMENTS = [
    # meta description (index + blog)
    ('is a cybersecurity student and CTF player from Pakistan',
     'is an offensive security researcher and CTF player from Pakistan'),
    ('a cybersecurity student from Pakistan who builds Python security tools',
     'an offensive security researcher from Pakistan who builds Python security tools'),
    ('a cybersecurity student from Pakistan building Python security tools',
     'an offensive security researcher from Pakistan building Python security tools'),
    ('a cybersecurity student from Pakistan.',
     'an offensive security researcher from Pakistan.'),
    # visible hero / terminal / footer
    ('CYBERSECURITY STUDENT &amp; CTF PLAYER',
     'OFFENSIVE SECURITY RESEARCHER &amp; CTF PLAYER'),
    ('CYBERSECURITY STUDENT & CTF PLAYER',
     'OFFENSIVE SECURITY RESEARCHER & CTF PLAYER'),
    ('// CYBERSECURITY STUDENT • GUJRANWALA, PK → UK',
     '// OFFENSIVE SECURITY RESEARCHER • GUJRANWALA, PK → UK'),
    ('// HASHAM JAVED (ZUDIO) • CYBERSECURITY STUDENT • RED TEAMER',
     '// HASHAM JAVED (ZUDIO) • OFFENSIVE SECURITY RESEARCHER • CTF PLAYER'),
    ('zudio — cybersecurity student',
     'zudio — offensive security researcher'),
    ('"jobTitle": "Cybersecurity Student"',
     '"jobTitle": "Offensive Security Researcher"'),
    # keywords: keep "student" out of the primary intent but leave the phrase list alone
    ('Pakistan cybersecurity student, web security',
     'Pakistan offensive security researcher, web security'),
    ('Pakistan cybersecurity student">',
     'Pakistan offensive security researcher">'),
    ('cybersecurity student from Pakistan.',
     'offensive security researcher from Pakistan.'),
]


def process(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    orig = src
    hits = []
    for old, new in REPLACEMENTS:
        if old in src:
            n = src.count(old)
            src = src.replace(old, new)
            hits.append((old, new, n))
    if src != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
    return hits


def main():
    targets = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for n in filenames:
            if n.endswith((".html", ".md")):
                targets.append(os.path.join(dirpath, n))

    total = 0
    for t in sorted(targets):
        hits = process(t)
        if hits:
            rel = os.path.relpath(t, ROOT)
            print("%s:" % rel)
            for old, new, n in hits:
                print("   x%d  %s" % (n, old[:64]))
            total += len(hits)
    print("\n%d replacement group(s) applied." % total)


if __name__ == "__main__":
    main()
