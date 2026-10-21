#!/usr/bin/env python3
"""Generate the portfolio's social share card (og:image, 1200x630).

Matches the site's dark hacker theme: near-black bg, green accent, monospace body.
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (4, 8, 5)
GREEN = (0, 255, 65)
DIM = (90, 150, 100)
GREY = (170, 185, 175)
CYAN = (0, 229, 255)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OUT = sys.argv[1] if len(sys.argv) > 1 else "og-image.png"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# ---- subtle grid ----
for x in range(0, W, 40):
    d.line([(x, 0), (x, H)], fill=(10, 22, 13), width=1)
for y in range(0, H, 40):
    d.line([(0, y), (W, y)], fill=(10, 22, 13), width=1)

# ---- green glow blob, top-left ----
glow = Image.new("RGB", (W, H), (0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([-260, -300, 620, 380], fill=(0, 60, 18))
glow = glow.filter(__import__("PIL.ImageFilter", fromlist=["ImageFilter"]).GaussianBlur(150))
img = Image.blend(img, Image.blend(img, glow, 0.0), 0.0)
img = Image.eval(img, lambda v: v)
base = img.copy()
img = Image.new("RGB", (W, H), BG)
img = Image.blend(base, glow, 0.35)
d = ImageDraw.Draw(img)

# ---- accent bar ----
d.rectangle([0, 0, W, 6], fill=GREEN)
d.rectangle([0, H - 6, W, H], fill=(0, 90, 30))

# ---- lightning mark ----
d.text((72, 62), "⚡", font=font(SANS_B, 74), fill=GREEN)

# ---- title ----
d.text((72, 176), "HASHAM JAVED", font=font(MONO_B, 76), fill=(255, 255, 255))
d.text((72, 272), "( ZUDIO )", font=font(MONO, 46), fill=GREEN)

# ---- rule ----
d.rectangle([72, 344, 300, 348], fill=GREEN)

# ---- subtitle ----
d.text((72, 372), "Offensive Security Researcher  |  CTF Player",
       font=font(MONO, 26), fill=GREY)
d.text((72, 412), "Python Security Tooling  |  Recon Automation",
       font=font(MONO, 26), fill=GREY)

# ---- chips ----
chips = ["CTF", "OSINT", "DFIR", "REVERSING", "WEB"]
cx = 72
cy = 468
for c in chips:
    f = font(MONO, 22)
    tw = d.textlength(c, font=f)
    d.rounded_rectangle([cx, cy, cx + tw + 30, cy + 40], radius=6,
                        outline=(0, 140, 50), width=2, fill=(0, 26, 12))
    d.text((cx + 15, cy + 9), c, font=f, fill=GREEN)
    cx += tw + 44

# ---- right-side stat panel ----
px = 830
d.rounded_rectangle([px, 150, px + 300, 480], radius=10,
                    outline=(0, 120, 45), width=2, fill=(6, 14, 8))
d.text((px + 28, 176), "20", font=font(MONO_B, 64), fill=GREEN)
d.text((px + 130, 202), "CTF", font=font(MONO, 24), fill=GREY)
d.text((px + 130, 228), "WRITEUPS", font=font(MONO, 24), fill=GREY)
d.line([px + 28, 290, px + 272, 290], fill=(0, 90, 35), width=2)
d.text((px + 28, 310), "OPEN TO", font=font(MONO, 22), fill=(110, 130, 118))
d.text((px + 28, 340), "JR RED TEAM", font=font(MONO_B, 26), fill=CYAN)
d.text((px + 28, 372), "& SEC ANALYST", font=font(MONO_B, 26), fill=CYAN)
d.text((px + 28, 414), "PAKISTAN", font=font(MONO, 24), fill=GREY)

# ---- footer ----
d.text((72, 556), "zudio-infosec.github.io", font=font(MONO_B, 28), fill=GREEN)
d.text((72, 590), "zudio001@proton.me", font=font(MONO, 20), fill=(100, 120, 108))

os.makedirs(os.path.dirname(os.path.abspath(OUT)) or ".", exist_ok=True)
img.save(OUT, "PNG", optimize=True)
print("wrote %s (%dx%d, %d bytes)" % (OUT, W, H, os.path.getsize(OUT)))
