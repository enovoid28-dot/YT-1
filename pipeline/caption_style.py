#!/usr/bin/env python3
"""Contoh tampilan caption/subtitle untuk channel Stickman (9:16 & 16:9).

Menghasilkan gambar uji supaya gaya caption bisa disetujui sebelum produksi.
Jalankan: python3 pipeline/caption_style.py
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE = (255, 255, 255)
YELLOW = (255, 214, 64)
OUT = os.path.join(ROOT, "output")


def fit(d, text, max_w, start, floor=34):
    for size in range(start, floor, -2):
        f = ImageFont.truetype(FB, size)
        if d.textlength(text, font=f) <= max_w:
            return f
    return ImageFont.truetype(FB, floor)


def caption(d, canvas_w, lines, y, big):
    """lines = [(teks, warna)] — tiap baris dirender dengan outline hitam tebal."""
    for text, color in lines:
        f = fit(d, text, canvas_w * 0.88, big)
        w = d.textlength(text, font=f)
        d.text(((canvas_w - w) / 2, y), text, font=f, fill=color,
               stroke_width=7, stroke_fill=(0, 0, 0))
        y += int(f.size * 1.18)
    return y


def chapter_label(d, text, w, x=70, y=120):
    f = ImageFont.truetype(FB, 34)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + tw + 44, y + 62], radius=10,
                        fill=(0, 0, 0), outline=YELLOW, width=3)
    d.text((x + 22, y + 13), text, font=f, fill=YELLOW)


def progress(d, w, h, ratio):
    d.rectangle([0, h - 3, w, h], fill=(255, 255, 255, 60))
    d.rectangle([0, h - 3, int(w * ratio), h], fill=YELLOW)


def v9x16():
    src = Image.open(os.path.join(ROOT, "assets/images/t04.jpg")).convert("RGB")
    W, H = 1080, 1920
    im = src.resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    chapter_label(d, "BAGIAN 1 — 1950", W)
    caption(d, W, [("BUKAN SOAL ALIEN", WHITE)], H - 430, 66)
    caption(d, W, [("DATANG BESOK", WHITE)], H - 350, 66)
    caption(d, W, [("10 JUTA TAHUN", YELLOW)], H - 250, 78)
    caption(d, W, [("ITU CUMA SEKEDAP", WHITE)], H - 160, 44)
    progress(d, W, H, 0.22)
    im.save(os.path.join(OUT, "contoh-caption-9x16.jpg"), quality=92)
    print("contoh-caption-9x16.jpg")


def v16x9():
    src = Image.open(os.path.join(ROOT, "assets/images/t15.jpg")).convert("RGB")
    W, H = 1920, 1080
    im = src.resize((W, H), Image.LANCZOS)
    # sedikit gelapkan sisi bawah agar teks terbaca
    grad = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grad)
    for i in range(300):
        gd.line([(0, H - 300 + i), (W, H - 300 + i)], fill=int(160 * i / 300))
    grad = grad.filter(ImageFilter.GaussianBlur(30))
    im = Image.composite(Image.new("RGB", (W, H), (4, 5, 9)), im, grad)
    d = ImageDraw.Draw(im)
    chapter_label(d, "BAGIAN 3 — PERSAMAAN DRAKE", W, x=80, y=80)
    caption(d, W, [("FAKTOR KE-7 BUKAN SOAL BINTANG", WHITE),
                   ("TAPI SOAL KITA", YELLOW)], H - 260, 62)
    progress(d, W, H, 0.46)
    im.save(os.path.join(OUT, "contoh-caption-16x9.jpg"), quality=92)
    print("contoh-caption-16x9.jpg")


if __name__ == "__main__":
    v9x16()
    v16x9()
