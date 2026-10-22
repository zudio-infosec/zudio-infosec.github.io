#!/usr/bin/env python3
"""Generate a distinct social-share card (og:image) for every page of the
portfolio, all in one visual language.

The user's own Gemini-generated "ZUDIO" logo is the hero mark on every card.
All text is auto-fitted so nothing can ever overflow its column.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
BG = (4, 8, 5)
GREEN = (0, 255, 65)
CYAN = (0, 229, 255)
DIM = (120, 150, 132)
GREY = (188, 200, 192)
WHITE = (255, 255, 255)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
LOGO = "/home/zudio/Pictures/Gemini_Generated_Image_qsr1x9qsr1x9qsr1 (1).png"

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."

# layout columns
LOGO_SIZE = 250
LOGO_X, LOGO_Y = 54, 196
TEXT_X = 350
TEXT_W = 460          # text column width (must stay clear of the panel)
PANEL_X, PANEL_W = 856, 292

PAGES = {
    "og-image.png": dict(
        accent=GREEN,
        kicker="HASHAM JAVED  //  ZUDIO",
        title="HASHAM JAVED",
        sub=["Offensive Security Researcher", "CTF Player  ·  Python Security Tooling"],
        tags=["CTF", "OSINT", "DFIR", "REVERSING", "WEB"],
        badge=("20", "CTF", "WRITEUPS"),
        badge2=("OPEN TO", "JR RED TEAM", "& SEC ANALYST"),
    ),
    "og-blog.png": dict(
        accent=CYAN,
        kicker="WRITEUPS  //  NOTES",
        title="CTF WRITEUPS",
        sub=["Authorized walkthroughs", "Web · Crypto · Network · OSINT · DFIR"],
        tags=["PICOCTF", "TRYHACKME", "HACKATHON", "DFIR"],
        badge=("20", "CTF", "WRITEUPS"),
        badge2=("NEW", "EVERY", "FORTNIGHT"),
    ),
    "og-ohsint.png": dict(
        accent=GREEN,
        kicker="OSINT WALKTHROUGH",
        title="OhSINT",
        sub=["TryHackMe room — full breakdown", "ExifTool · GPS · Metadata · Social trails"],
        tags=["OSINT", "EXIFTOOL", "GEOINT", "RECON"],
        badge=("1", "IMAGE IN,", "1 TRAIL OUT"),
        badge2=("STEP BY", "STEP", "WALKTHROUGH"),
    ),
    "og-hackathon.png": dict(
        accent=CYAN,
        kicker="3-DAY WORKSHOP  //  2026",
        title="HACKATHON",
        sub=["11 challenges solved", "Web · Network · Crypto · Android · DFIR"],
        tags=["WEB", "NETWORK", "CRYPTO", "ANDROID", "DFIR"],
        badge=("11", "CHALLENGES", "SOLVED"),
        badge2=("FULL", "WRITEUPS", "PUBLISHED"),
    ),
    "og-lab.png": dict(
        accent=GREEN,
        kicker="LAB BUILD  //  KALI + VBOX",
        title="KALI LAB",
        sub=["Building a home security lab", "Windows 7/10/11 · VirtualBox · Kali"],
        tags=["KALI", "VIRTUALBOX", "LAB", "ISOLATION"],
        badge=("3", "VMs IN", "PERSONAL LAB"),
        badge2=("ISOLATED", "SAFE", "PRACTICE"),
    ),
    "og-404.png": dict(
        accent=(255, 92, 92),
        kicker="ERROR  //  404",
        title="NOT FOUND",
        sub=["This route does not exist", "Try the writeups, the blog, or head home"],
        tags=["404", "ZUDIO"],
        badge=("404", "ROUTE", "NOT FOUND"),
        badge2=("BACK TO", "INDEX", "PAGE"),
    ),
}


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def fit(d, text, path, max_w, max_size, min_size=12):
    """Largest font size (<= max_size) whose text fits in max_w."""
    for size in range(max_size, min_size - 1, -1):
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
    return font(path, min_size)


def load_logo(size):
    im = Image.open(LOGO).convert("RGBA").resize((size, size), Image.LANCZOS)
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if r < 26 and g < 30 and b < 28:
                px[x, y] = (r, g, b, 0)
    return im


def build(cfg, out_path):
    accent = cfg["accent"]

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(9, 20, 12), width=1)
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(9, 20, 12), width=1)

    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse([-120, -100, 460, 440], fill=(0, 72, 27))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    img = Image.blend(img, glow, 0.32)
    d = ImageDraw.Draw(img)

    logo = load_logo(LOGO_SIZE)
    img.paste(logo, (LOGO_X, LOGO_Y), logo)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 6], fill=accent)
    d.rectangle([0, H - 6, W, H], fill=(0, 80, 30) if accent == GREEN else
                ((0, 70, 80) if accent == CYAN else (90, 25, 25)))

    # kicker
    fk = fit(d, cfg["kicker"], MONO_B, TEXT_W, 24)
    d.text((TEXT_X, 112), cfg["kicker"], font=fk, fill=accent)
    d.rectangle([TEXT_X, 150, TEXT_X + 140, 154], fill=accent)

    # title
    ft = fit(d, cfg["title"], MONO_B, TEXT_W, 58)
    d.text((TEXT_X, 182), cfg["title"], font=ft, fill=WHITE)

    # subtitle lines
    y = 272
    for line in cfg["sub"]:
        fs = fit(d, line, MONO, TEXT_W, 24)
        d.text((TEXT_X, y), line, font=fs, fill=GREY)
        y += 36

    # tags (wrapped, auto-sized)
    tags = cfg["tags"]
    size = 20
    while size > 12:
        f = font(MONO, size)
        widths = [d.textlength(t, font=f) + 26 for t in tags]
        if sum(widths) + 12 * (len(tags) - 1) <= TEXT_W:
            break
        size -= 1
    f = font(MONO, size)
    cx, cy = TEXT_X, 366
    for t in tags:
        tw = d.textlength(t, font=f)
        if cx + tw + 26 > TEXT_X + TEXT_W:
            cx, cy = TEXT_X, cy + 44
        d.rounded_rectangle([cx, cy, cx + tw + 26, cy + 36], radius=6,
                            outline=accent, width=2, fill=(0, 24, 11))
        d.text((cx + 13, cy + 7), t, font=f, fill=accent)
        cx += tw + 38

    # right stat panel
    d.rounded_rectangle([PANEL_X, 112, PANEL_X + PANEL_W, 508], radius=10,
                        outline=(0, 105, 40), width=2, fill=(6, 14, 8))
    b1 = cfg["badge"]
    fb = fit(d, b1[0], MONO_B, PANEL_W - 48, 52)
    d.text((PANEL_X + 24, 134), b1[0], font=fb, fill=accent)
    d.text((PANEL_X + 24, 200), b1[1], font=fit(d, b1[1], MONO, PANEL_W - 48, 20), fill=GREY)
    d.text((PANEL_X + 24, 224), b1[2], font=fit(d, b1[2], MONO, PANEL_W - 48, 20), fill=GREY)
    d.line([PANEL_X + 24, 272, PANEL_X + PANEL_W - 24, 272], fill=(0, 85, 33), width=2)
    b2 = cfg["badge2"]
    d.text((PANEL_X + 24, 292), b2[0], font=fit(d, b2[0], MONO, PANEL_W - 48, 19), fill=(105, 125, 112))
    d.text((PANEL_X + 24, 322), b2[1], font=fit(d, b2[1], MONO_B, PANEL_W - 48, 25), fill=CYAN)
    d.text((PANEL_X + 24, 354), b2[2], font=fit(d, b2[2], MONO_B, PANEL_W - 48, 25), fill=CYAN)
    d.text((PANEL_X + 24, 398), "PAKISTAN", font=font(MONO, 21), fill=GREY)

    # footer
    d.text((TEXT_X, 486), "zudio-infosec.github.io", font=fit(d, "zudio-infosec.github.io", MONO_B, TEXT_W, 25), fill=accent)
    d.text((TEXT_X, 522), "zudio001@proton.me", font=font(MONO, 18), fill=(98, 118, 105))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return os.path.getsize(out_path)


if __name__ == "__main__":
    for name, cfg in PAGES.items():
        sz = build(cfg, os.path.join(OUT_DIR, name))
        print("  %-18s %7d bytes" % (name, sz))
