#!/usr/bin/env python3
"""Kartu transisi full-screen 1080x1920 untuk episode (tanpa musik, fade 4 frame).

Jalankan: python3 pipeline/cards.py
Output: assets/cards/k0.jpg ... k7.jpg
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1080, 1920
BG = (9, 10, 14)
YELLOW = (255, 214, 64)
WHITE = (240, 240, 244)
DIM = (150, 150, 158)


def fit(d, text, max_w, start, floor=48):
    for size in range(start, floor, -4):
        f = ImageFont.truetype(FB, size)
        if d.textlength(text, font=f) <= max_w:
            return f
    return ImageFont.truetype(FB, floor)


def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(idx, big, small=None, rules=True, kicker=None):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)

    if rules:
        d.line([(120, 330), (W - 120, 330)], fill=(70, 70, 78), width=2)
        d.line([(120, H - 330), (W - 120, H - 330)], fill=(70, 70, 78), width=2)

    y = 600
    if kicker:
        kf = ImageFont.truetype(FB, 40)
        kw = d.textlength(kicker, font=kf)
        d.text(((W - kw) / 2, y - 130), kicker, font=kf, fill=DIM)
        # garis kuning kecil
        d.line([(W / 2 - kw / 2, y - 75), (W / 2 + kw / 2, y - 75)],
               fill=YELLOW, width=4)

    # teks utama: pilih ukuran terbesar yang muat dalam <= 2 baris
    font, lines = None, None
    for size in range(300, 90, -6):
        f = ImageFont.truetype(FB, size)
        ls = wrap(d, big, f, W - 190)
        if len(ls) <= 2 and all(d.textlength(l, font=f) <= W - 190 for l in ls):
            font, lines = f, ls
            break
    if font is None:
        font = ImageFont.truetype(FB, 96)
        lines = wrap(d, big, font, W - 190)
    asc, desc = font.getmetrics()
    lh = asc + desc + 12
    y0 = H / 2 - (lh * len(lines)) / 2 - 40
    for i, line in enumerate(lines):
        w = d.textlength(line, font=font)
        d.text(((W - w) / 2, y0 + i * lh), line, font=font, fill=YELLOW)

    if small:
        sf = ImageFont.truetype(FR, 44)
        slines = wrap(d, small, sf, W - 260)
        sy = y0 + lh * len(lines) + 50
        for line in slines:
            w = d.textlength(line, font=sf)
            d.text(((W - w) / 2, sy), line, font=sf, fill=DIM)
            sy += 62

    dst = os.path.join(ROOT, "assets/cards", f"k{idx}.jpg")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im.save(dst, quality=95)


CARDS = [
    (0, "STICKMAN", "EPISODE 02", False, None),
    (1, "08:20", None, True, "CAHAYA MATAHARI KE BUMI"),
    (2, "MENIT KE-9", None, True, "LANGIT BERUBAH"),
    (3, "HARI KE-7", None, True, "DINGIN MULAI BEKERJA"),
    (4, "TAHUN KE-1", None, True, "BUMI TANPA MUSIM"),
    (5, "5 MILIAR TAHUN", None, True, "CARA MATAHARI BERAKHIR"),
    (6, "YANG TAK TERHINDARI", None, True, "TITIK BALIK"),
    (7, "SUBSCRIBE", "STICKMAN — EPISODE 02", False, None),
]

if __name__ == "__main__":
    for c in CARDS:
        card(*c)
    print("8 kartu -> assets/cards/")
