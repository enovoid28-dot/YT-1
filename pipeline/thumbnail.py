#!/usr/bin/env python3
"""Buat thumbnail short 1080x1920 (judul di area atas yang kosong)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/images/t01.jpg")
OUT = os.path.join(ROOT, "output/thumbnail_short-01.jpg")
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920
ACCENT = (255, 214, 64)
WHITE = (255, 255, 255)


def fit(d, text, font_path, max_w, start, floor=40, step=4):
    for size in range(start, floor, -step):
        f = ImageFont.truetype(font_path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
    return ImageFont.truetype(font_path, floor)


def main():
    im = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
    # gelapkan sedikit area atas supaya teks menempel
    dark = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(dark)
    dd.rectangle([0, 0, W, int(H * 0.40)], fill=120)
    dd.rectangle([0, int(H * 0.72), W, H], fill=110)
    dark = dark.filter(ImageFilter.GaussianBlur(60))
    im = Image.composite(Image.new("RGB", (W, H), (5, 6, 12)), im, dark)

    d = ImageDraw.Draw(im)
    m = 76

    # kicker
    kf = ImageFont.truetype(FONT_B, 40)
    kick = "SAINS CORET"
    kw = d.textlength(kick, font=kf)
    d.rounded_rectangle([m, 120, m + kw + 56, 120 + 74], radius=14,
                        fill=(255, 214, 64), outline=(0, 0, 0), width=5)
    d.text((m + 28, 132), kick, font=kf, fill=(12, 12, 12))

    # judul besar 3 baris
    lines = [("DITARIK KE", WHITE), ("LUBANG HITAM", ACCENT)]
    y = 250
    for text, color in lines:
        f = fit(d, text, FONT_B, W - 2 * m, 132)
        d.text((m, y), text, font=f, fill=color, stroke_width=9,
               stroke_fill=(0, 0, 0))
        y += int(f.size * 1.06)

    # angka 33 besar di kanan atas
    nf = ImageFont.truetype(FONT_B, 150)
    d.text((W - m - d.textlength("33", font=nf), y + 10), "33",
           font=nf, fill=ACCENT, stroke_width=9, stroke_fill=(0, 0, 0))
    sf = ImageFont.truetype(FONT_R, 44)
    sub = "tempat paling gila\ndi tata surya"
    sy = y + 20
    for line in sub.split("\n"):
        d.text((m, sy), line, font=sf, fill=(236, 238, 245),
               stroke_width=6, stroke_fill=(0, 0, 0))
        sy += 54

    # footer
    ff = ImageFont.truetype(FONT_B, 46)
    foot = "FAKTA ASLI. BUKAN FIKSI."
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, H - 190), foot, font=ff, fill=WHITE,
           stroke_width=7, stroke_fill=(0, 0, 0))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT, quality=92, subsampling=1)
    print("thumbnail ->", OUT)


if __name__ == "__main__":
    main()
