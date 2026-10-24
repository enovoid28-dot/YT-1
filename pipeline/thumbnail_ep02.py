#!/usr/bin/env python3
"""Thumbnail EP02 (9:16, 1080x1920) dari shot 1."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets/images/ep02_s01.jpg")
OUT = os.path.join(ROOT, "output/thumbnail_ep02.jpg")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920
ACCENT = (255, 214, 64)
WHITE = (255, 255, 255)


def fit(d, text, path, max_w, start, floor=40, step=4):
    for size in range(start, floor, -step):
        f = ImageFont.truetype(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
    return ImageFont.truetype(path, floor)


def main():
    im = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
    # gelapkan atas & bawah agar teks menempel
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([0, 0, W, int(H * 0.42)], fill=135)
    md.rectangle([0, int(H * 0.70), W, H], fill=120)
    mask = mask.filter(ImageFilter.GaussianBlur(70))
    im = Image.composite(Image.new("RGB", (W, H), (6, 7, 11)), im, mask)
    d = ImageDraw.Draw(im)
    m = 76

    # kicker
    kf = ImageFont.truetype(FB, 40)
    kick = "STICKMAN  •  EPISODE 02"
    kw = d.textlength(kick, font=kf)
    d.rounded_rectangle([m, 110, m + kw + 56, 110 + 72], radius=14,
                        fill=ACCENT, outline=(0, 0, 0), width=5)
    d.text((m + 28, 122), kick, font=kf, fill=(12, 12, 12))

    # judul
    y = 250
    for text, color in [("KALAU", WHITE), ("MATAHARI", ACCENT), ("MATI", WHITE)]:
        f = fit(d, text, FB, W - 2 * m, 150)
        d.text((m, y), text, font=f, fill=color, stroke_width=10,
               stroke_fill=(0, 0, 0))
        y += int(f.size * 1.02)

    # subjudul
    sf = ImageFont.truetype(FB, 52)
    sub = "8 MENIT 20 DETIK"
    sw = d.textlength(sub, font=sf)
    d.rounded_rectangle([m, y + 26, m + sw + 64, y + 26 + 96], radius=10,
                        fill=(0, 0, 0), outline=ACCENT, width=4)
    d.text((m + 32, y + 46), sub, font=sf, fill=ACCENT)

    # footer
    ff = ImageFont.truetype(FR, 46)
    foot = "Tidak ada ledakan. Tidak ada alarm."
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, H - 200), foot, font=ff, fill=(235, 238, 245),
           stroke_width=6, stroke_fill=(0, 0, 0))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(OUT, quality=92, subsampling=1)
    print("thumbnail ->", OUT)


if __name__ == "__main__":
    main()
