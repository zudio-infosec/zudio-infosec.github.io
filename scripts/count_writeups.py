#!/usr/bin/env python3
"""Count real writeups in the ctf-writeups repo and patch the portfolio's counter.

Rules (per repo owner):
  * count every *.md file in the repo, at ANY depth (root + all sub-folders)
  * subtract every README.md (they are index docs, not writeups)
  * write the total into index.html's "CTF WRITEUPS" stat card

Usage:
  count_writeups.py --repo <path-to-ctf-writeups-checkout> [--html index.html] [--check]
"""
import argparse
import os
import re
import sys


def count_writeups(repo_dir):
    """All .md at any depth, minus every README.md."""
    md_total = 0
    readmes = 0
    files = []
    for root, dirs, names in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in names:
            if not n.lower().endswith(".md"):
                continue
            md_total += 1
            if n.lower() == "readme.md":
                readmes += 1
            else:
                files.append(os.path.relpath(os.path.join(root, n), repo_dir))
    return md_total - readmes, md_total, readmes, sorted(files)


# Matches the stat card: <div class="stat-num">N</div>\n<div class="stat-label">CTF WRITEUPS</div>
STAT_RE = re.compile(
    r'(<div class="stat-num">)([^<]*)(</div>\s*<div class="stat-label">\s*CTF WRITEUPS\s*</div>)',
    re.IGNORECASE,
)


def patch_html(path, count):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    m = STAT_RE.search(src)
    if not m:
        return None, src
    old = m.group(2)
    new_src = src[:m.start()] + m.group(1) + str(count) + m.group(3) + src[m.end():]
    return old, new_src


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--html", default="index.html")
    ap.add_argument("--check", action="store_true", help="don't write, just report")
    ap.add_argument("--list", action="store_true", help="print counted files")
    a = ap.parse_args()

    count, md_total, readmes, files = count_writeups(a.repo)
    print("md files at any depth : %d" % md_total)
    print("README.md excluded    : %d" % readmes)
    print("WRITEUP COUNT         : %d" % count)
    if a.list:
        for f in files:
            print("   -", f)

    if not os.path.isfile(a.html):
        print("html not found: %s" % a.html, file=sys.stderr)
        return 2

    old, new_src = patch_html(a.html, count)
    if old is None:
        print("ERROR: could not locate the 'CTF WRITEUPS' stat card in %s" % a.html,
              file=sys.stderr)
        return 3

    if old.strip() == str(count):
        print("counter already accurate (%s) - nothing to do" % count)
        return 0

    print("counter: %s -> %d" % (old.strip(), count))
    if a.check:
        return 0
    with open(a.html, "w", encoding="utf-8") as f:
        f.write(new_src)
    print("patched %s" % a.html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
