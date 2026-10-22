#!/usr/bin/env python3
"""Validate the portfolio's HTML: tag balance + check that every referenced
local asset actually exists on disk."""
import os
import re
import sys
from html.parser import HTMLParser

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
VOID = {"meta", "link", "br", "img", "hr", "input", "source", "area", "base",
        "col", "embed", "param", "track", "wbr"}


class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        # self-closing (<meta ... />) - do not push onto the stack
        pass

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            self.errors.append("mismatched </%s> (open: %s)" % (tag, self.stack[-3:]))
            while self.stack and self.stack.pop() != tag:
                pass
        else:
            self.errors.append("stray </%s>" % tag)


def check(path):
    src = open(path, encoding="utf-8").read()
    p = P()
    p.feed(src)
    p.errors += ["unclosed <%s>" % t for t in p.stack]

    # local asset references
    missing = []
    for m in re.finditer(r'(?:src|href)="(/[^"#?]+)"', src):
        rel = m.group(1).lstrip("/")
        if rel and not os.path.exists(os.path.join(ROOT, rel)):
            missing.append(rel)
    for m in re.finditer(r'src="\./([^"]+)"', src):
        if not os.path.exists(os.path.join(ROOT, m.group(1))):
            missing.append(m.group(1))
    return p.errors, sorted(set(missing))


pages = ["index.html", "blog.html", "posts/ohsint.html",
         "posts/hackathon-2026.html", "posts/kali-lab-setup.html", "404.html"]
bad = 0
for page in pages:
    path = os.path.join(ROOT, page)
    if not os.path.isfile(path):
        print("  %-28s MISSING" % page)
        bad += 1
        continue
    errs, missing = check(path)
    status = "OK" if not errs and not missing else "ISSUES"
    print("  %-28s %-6s errors=%d missing-assets=%s"
          % (page, status, len(errs), missing or "none"))
    for e in errs[:3]:
        print("        %s" % e)
    bad += len(errs) + len(missing)

print("\n%s" % ("ALL PAGES VALID" if bad == 0 else "%d issue(s) found" % bad))
sys.exit(0 if bad == 0 else 1)
