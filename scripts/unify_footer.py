#!/usr/bin/env python3
"""Replace every page's footer with one identical, icon-based footer.

The container class is `.footer-social` (not `.footer-links`).
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
ICON_DIR = "/home/zudio/.hermes/cache/scratch/icons"
PAGES = ["index.html", "blog.html", "posts/ohsint.html",
         "posts/hackathon-2026.html", "posts/kali-lab-setup.html", "404.html"]

LINKS = [
    ("github", "GitHub", "https://github.com/zudio-infosec"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/hasham-javed-a03424400/"),
    ("tryhackme", "TryHackMe", "https://tryhackme.com/p/zudio.infosec"),
    ("hackthebox", "Hack The Box", "https://www.hackthebox.com/profile/1961817"),
    ("instagram", "Instagram", "https://www.instagram.com/zudio.infosec"),
    ("youtube", "YouTube", "https://www.youtube.com/@zudio-infosec"),
    ("email", "Email", "mailto:zudio001@proton.me"),
    ("resume", "Resume", "/resume.pdf"),
]

DESC = "// HASHAM JAVED (ZUDIO) • OFFENSIVE SECURITY RESEARCHER • CTF PLAYER"
COPY = "© 2026 ZUDIO (HASHAM JAVED) • BUILT WITH CURIOSITY • OPEN TO REMOTE INTERNSHIPS"


def icon(name, size=15):
    with open(os.path.join(ICON_DIR, name + ".svg")) as f:
        svg = f.read()
    inner = re.sub(r"^.*?<svg[^>]*>", "", svg, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    return ('<svg class="pill-icon" viewBox="0 0 24 24" width="%d" height="%d" '
            'aria-hidden="true" focusable="false">%s</svg>' % (size, size, inner))


def pills():
    out = []
    for name, label, url in LINKS:
        if url.startswith("mailto:") or url.startswith("/"):
            attrs = ""
        else:
            attrs = ' target="_blank" rel="me"'
        title = ' title="%s"' % url if url.startswith("mailto:") else ""
        out.append('    <a href="%s"%s%s class="social-pill">%s %s</a>'
                   % (url, attrs, title, icon(name), label))
    return "\n".join(out)


def main():
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.isfile(path):
            print("SKIP:", page)
            continue
        src = open(path, encoding="utf-8").read()
        orig = src

        m = re.search(r'<div class="footer-social">(.*?)</div>', src, re.S)
        if m:
            src = src[:m.start()] + '<div class="footer-social">\n' + pills() + "\n  </div>" + src[m.end():]
        else:
            print("  %-28s footer-social not found" % page)
            continue

        src = re.sub(r'<div class="footer-desc">[^<]*</div>',
                      '<div class="footer-desc">%s</div>' % DESC, src)
        src = re.sub(r'<div class="footer-copy">[^<]*</div>',
                      '<div class="footer-copy">%s</div>' % COPY, src)

        if src != orig:
            open(path, "w", encoding="utf-8").write(src)
            print("  %-28s footer -> %d icon pills, desc+copy unified" % (page, len(LINKS)))


if __name__ == "__main__":
    main()
