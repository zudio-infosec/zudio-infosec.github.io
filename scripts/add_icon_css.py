#!/usr/bin/env python3
"""Inject the SVG-icon CSS and finish the 404 page's social meta."""
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
PAGES = ["index.html", "blog.html", "posts/ohsint.html",
         "posts/hackathon-2026.html", "posts/kali-lab-setup.html"]

CSS = """
  /* SVG brand icons (platform cards + footer pills) */
  .plat-icon {
    fill: currentColor;
    color: var(--green);
    display: block;
    margin: 0 auto;
    transition: transform 0.3s ease, color 0.3s ease;
  }
  .platform-card:hover .plat-icon { transform: scale(1.12); }
  .pill-icon {
    fill: currentColor;
    vertical-align: -2px;
    margin-right: 5px;
  }
  .social-pill {
    display: inline-flex;
    align-items: center;
    gap: 2px;
  }
  .social-pill:hover .pill-icon { color: var(--green); }
"""

OG_404 = """<meta property="og:title" content="Page Not Found | Zudio">
<meta property="og:description" content="This route does not exist on the network. Head back to the portfolio, the writeups, or the blog.">
<meta property="og:url" content="https://zudio-infosec.github.io/404.html">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Page Not Found | Zudio">
<meta name="twitter:description" content="This route does not exist on the network.">
<meta property="og:image" content="https://zudio-infosec.github.io/og-404.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Page not found - Zudio">
<meta name="twitter:image" content="https://zudio-infosec.github.io/og-404.png">
<meta name="twitter:image:alt" content="Page not found - Zudio">
"""


def main():
    for page in PAGES:
        path = os.path.join(ROOT, page)
        if not os.path.isfile(path):
            print("SKIP:", page)
            continue
        src = open(path, encoding="utf-8").read()
        orig = src

        if ".plat-icon {" not in src:
            # put it right before the closing of the <style> block
            m = re.search(r"</style>", src)
            if m:
                src = src[:m.start()] + CSS + src[m.start():]
                print("  %-28s icon CSS added" % page)

        if src != orig:
            open(path, "w", encoding="utf-8").write(src)

    # 404 page
    p404 = os.path.join(ROOT, "404.html")
    if os.path.isfile(p404):
        s = open(p404, encoding="utf-8").read()
        if "og:image" not in s:
            m = re.search(r"</head>", s)
            if m:
                s = s[:m.start()] + OG_404 + s[m.start():]
                open(p404, "w", encoding="utf-8").write(s)
                print("  %-28s og meta added" % "404.html")
        if ".plat-icon {" not in s:
            m = re.search(r"</style>", s)
            if m:
                s = s[:m.start()] + CSS + s[m.start():]
                open(p404, "w", encoding="utf-8").write(s)
                print("  %-28s icon CSS added" % "404.html")
    else:
        print("  404.html missing")


if __name__ == "__main__":
    main()
