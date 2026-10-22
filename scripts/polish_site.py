#!/usr/bin/env python3
"""Apply the portfolio polish pass to every page:

  1. #matrix-bg gets pointer-events:none  (the fixed canvas was swallowing
     clicks on static content - the "VIEW ALL 20 WRITEUPS" button was unclickable)
  2. platform cards use inline SVG brand icons instead of emoji
  3. the HackTheBox platform card links to the real profile id again
  4. footer social pills use inline SVG icons instead of emoji/glyphs
  5. every footer on every page is identical
  6. each page points at its own og:image
"""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
ICON_DIR = "/home/zudio/.hermes/cache/scratch/icons"

PAGES = ["index.html", "blog.html", "posts/ohsint.html",
         "posts/hackathon-2026.html", "posts/kali-lab-setup.html"]

OG = {
    "index.html": "og-image.png",
    "blog.html": "og-blog.png",
    "posts/ohsint.html": "og-ohsint.png",
    "posts/hackathon-2026.html": "og-hackathon.png",
    "posts/kali-lab-setup.html": "og-lab.png",
    "404.html": "og-404.png",
}

# canonical footer, used on every page
FOOTER_LINKS = [
    ("github", "GitHub", "https://github.com/zudio-infosec"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/hasham-javed-a03424400/"),
    ("tryhackme", "TryHackMe", "https://tryhackme.com/p/zudio.infosec"),
    ("hackthebox", "Hack The Box", "https://www.hackthebox.com/profile/1961817"),
    ("instagram", "Instagram", "https://www.instagram.com/zudio.infosec"),
    ("youtube", "YouTube", "https://www.youtube.com/@zudio-infosec"),
    ("email", "Email", "mailto:zudio001@proton.me"),
    ("resume", "Resume", "/resume.pdf"),
]
FOOTER_DESC = "// HASHAM JAVED (ZUDIO) • OFFENSIVE SECURITY RESEARCHER • CTF PLAYER"
FOOTER_COPY = "© 2026 ZUDIO (HASHAM JAVED) • BUILT WITH CURIOSITY • OPEN TO REMOTE INTERNSHIPS"

PLATFORMS = [
    ("tryhackme", "TRYHACKME", "https://tryhackme.com/p/zudio.infosec", "ACTIVE — zudio.infosec", 1),
    ("portswigger", "PORTSWIGGER", "https://portswigger.net/web-security", "WEB SECURITY LABS", 2),
    ("picoctf", "PICOCTF", "https://picoctf.org", "CTF COMPETITIONS", 3),
    ("hackthebox", "HACKTHEBOX", "https://www.hackthebox.com/profile/1961817",
     "PROFILE ID 1961817", 4),
]


def icon(name, size=18, cls="plat-icon"):
    """Inline SVG for a brand / custom icon."""
    path = os.path.join(ICON_DIR, name + ".svg")
    with open(path) as f:
        svg = f.read()
    # keep only the inner markup, set our own sizing
    inner = re.sub(r"^.*?<svg[^>]*>", "", svg, flags=re.S)
    inner = re.sub(r"</svg>\s*$", "", inner, flags=re.S)
    inner = re.sub(r'<title>.*?</title>', "", inner, flags=re.S)
    inner = inner.replace('fill="none" stroke="currentColor"', 'fill="none" stroke="currentColor"')
    return ('<svg class="%s" viewBox="0 0 24 24" width="%d" height="%d" '
            'aria-hidden="true" focusable="false">%s</svg>' % (cls, size, size, inner))


def build_platforms():
    out = ['  <div class="platforms-grid">']
    for name, label, url, status, delay in PLATFORMS:
        out.append(
            '    <a href="%s" target="_blank" rel="me" class="platform-card reveal reveal-delay-%d">'
            % (url, delay))
        out.append('      <span class="platform-icon">%s</span>' % icon(name, 30, "plat-icon"))
        out.append('      <div class="platform-name">%s</div>' % label)
        out.append('      <div class="platform-status">%s</div>' % status)
        out.append('    </a>')
    out.append('  </div>')
    return "\n".join(out)


def build_footer_pills():
    out = []
    for name, label, url in FOOTER_LINKS:
        target = "" if url.startswith("mailto:") or url.startswith("/") else ' target="_blank"'
        rel = "" if url.startswith("mailto:") or url.startswith("/") else ' rel="me"'
        out.append('    <a href="%s"%s%s class="social-pill">%s %s</a>'
                   % (url, target, rel, icon(name, 15, "pill-icon"), label))
    return "\n".join(out)


def main():
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.isfile(path):
            print("SKIP missing:", page)
            continue
        src = open(path, encoding="utf-8").read()
        orig = src

        # ---- 1. matrix canvas must not eat clicks ----
        if "#matrix-bg {" in src and "pointer-events: none" not in src.split("#matrix-bg {")[1].split("}")[0]:
            src = src.replace(
                "  #matrix-bg {\n    position: fixed;\n    top: 0; left: 0;\n"
                "    width: 100%; height: 100%;\n    z-index: 0;\n    opacity: 0.07;\n  }",
                "  #matrix-bg {\n    position: fixed;\n    top: 0; left: 0;\n"
                "    width: 100%; height: 100%;\n    z-index: 0;\n    opacity: 0.07;\n"
                "    pointer-events: none;   /* decorative only - must never eat clicks */\n  }")
            print("  %-28s canvas pointer-events fixed" % page)

        # ---- 2 + 3. platform cards ----
        m = re.search(r'(  <div class="platforms-grid">)(.*?)(  </div>\n)', src, re.S)
        if m and "platform-icon" in m.group(2):
            src = src[:m.start()] + build_platforms() + "\n" + src[m.end():]
            print("  %-28s platform cards -> SVG icons + HTB profile id" % page)

        # ---- 4 + 5. footer ----
        fm = re.search(r'(<footer.*?</footer>)', src, re.S)
        if fm:
            foot = fm.group(1)
            # replace the pill block
            new_foot = re.sub(r'( *<div class="footer-links">)(.*?)( *</div>)',
                               lambda mm: mm.group(1) + "\n" + build_footer_pills() + "\n" + mm.group(3),
                               foot, count=1, flags=re.S)
            # unify the description line
            new_foot = re.sub(r'<div class="footer-desc">[^<]*</div>',
                              '<div class="footer-desc">%s</div>' % FOOTER_DESC, new_foot)
            new_foot = re.sub(r'<div class="footer-copy">[^<]*</div>',
                              '<div class="footer-copy">%s</div>' % FOOTER_COPY, new_foot)
            src = src[:fm.start()] + new_foot + src[fm.end():]
            print("  %-28s footer unified" % page)

        # ---- 6. per-page og:image ----
        if page in OG:
            want = "https://zudio-infosec.github.io/" + OG[page]
            src = re.sub(r'(<meta property="og:image" content=")[^"]*(")',
                         lambda mm: mm.group(1) + want + mm.group(2), src)
            src = re.sub(r'(<meta name="twitter:image" content=")[^"]*(")',
                         lambda mm: mm.group(1) + want + mm.group(2), src)
            src = re.sub(r'(<meta property="og:image:alt" content=")[^"]*(")',
                         lambda mm: mm.group(1) + og_alt(page) + mm.group(2), src)
            print("  %-28s og:image -> %s" % (page, OG[page]))

        if src != orig:
            open(path, "w", encoding="utf-8").write(src)


def og_alt(page):
    return {
        "index.html": "Hasham Javed (Zudio) - Offensive Security Researcher and CTF Player",
        "blog.html": "CTF writeups and security notes by Hasham Javed (Zudio)",
        "posts/ohsint.html": "OhSINT - TryHackMe OSINT walkthrough by Zudio",
        "posts/hackathon-2026.html": "Cybersecurity Hackathon 2026 - 11 challenges solved by Zudio",
        "posts/kali-lab-setup.html": "Building a Kali Linux and VirtualBox home security lab - Zudio",
        "404.html": "Page not found - Zudio",
    }.get(page, "Zudio")


if __name__ == "__main__":
    main()
