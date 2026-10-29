#!/usr/bin/env python3
"""Gaya caption bersama (dipakai EP01 & EP02).

Aturan baku (lihat docs/00-FORMAT-BAKU-NASKAH.md):
- putih #FFFFFF, kata kunci kuning #FFD640
- outline hitam, maks 2 baris, maks 88% lebar kanvas
- posisi 200 px dari bawah pada kanvas 1080x1920
- label kanal kanan atas
"""
import os
from PIL import Image, ImageDraw, ImageFont

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WHITE = (255, 255, 255, 248)
YELLOW = (255, 214, 64, 250)
STROKE = (0, 0, 0, 235)


def _fit(d, text, max_w, max_lines=2, start=62, floor=34):
    words = text.split()
    for size in range(start, floor, -2):
        f = ImageFont.truetype(FB, size)
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= max_w:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines and all(d.textlength(l, font=f) <= max_w for l in lines):
            return f, lines
    return ImageFont.truetype(FB, floor), [text]


def make_caption(caption, dst, size=(1080, 1920), label="STICKMAN",
                 highlight=None, bottom=200):
    """Buat overlay PNG transparan.

    highlight: kata kunci yang diwarnai kuning (maks 2 kata).
    """
    W, H = size
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    text = caption.upper()
    # caption pendek (angka/tokoh) dibuat jauh lebih besar agar jadi "hero number"
    if len(text) <= 10:
        start = int(H * 0.072)
    elif len(text) <= 18:
        start = int(H * 0.052)
    else:
        start = int(H * 0.0335)
    font, lines = _fit(d, text, int(W * 0.88), 2, start=start)
    asc, desc = font.getmetrics()
    lh = asc + desc + 10
    y0 = H - bottom - lh * len(lines)

    for i, line in enumerate(lines):
        w = d.textlength(line, font=font)
        x = (W - w) / 2
        if highlight and highlight.upper() in line:
            # gambar per kata supaya kata kunci bisa kuning
            cx = x
            for word in line.split(" "):
                fill = YELLOW if highlight.upper() in word.upper() else WHITE
                d.text((cx, y0 + i * lh), word, font=font, fill=fill,
                       stroke_width=6, stroke_fill=STROKE)
                cx += d.textlength(word + " ", font=font)
        else:
            d.text((x, y0 + i * lh), line, font=font, fill=WHITE,
                   stroke_width=6, stroke_fill=STROKE)

    if label:
        lf = ImageFont.truetype(FB, 30)
        lw = d.textlength(label, font=lf)
        d.text((W - lw - 46, 74), label, font=lf, fill=(255, 255, 255, 160),
               stroke_width=2, stroke_fill=(0, 0, 0, 130))

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    img.save(dst)
    return dst
