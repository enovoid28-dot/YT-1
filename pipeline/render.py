#!/usr/bin/env python3
"""Render short vertikal 9:16 dari 33 frame + narasi.

Alur: tiap tahap -> klip Ken Burns (zoompan) + caption -> concat -> mux narasi + drone.
Jalankan: python3 pipeline/render.py [--preview N]
"""
import json, os, shutil, subprocess, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from storyboard import STAGES, CAPTIONS, image_for, available, ROOT

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
WORK = os.path.join(ROOT, "work")
CLIPS = os.path.join(WORK, "clips")
CAPS = os.path.join(WORK, "caps")
OUT = os.path.join(ROOT, "output")
BED = os.path.join(ROOT, "assets/audio/bed.wav")


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("ffmpeg gagal:\n" + p.stderr[-3000:])


def load_timeline():
    tp = os.path.join(WORK, "timeline.json")
    if not os.path.exists(tp):
        sys.exit("jalankan dulu: python3 pipeline/build_audio.py")
    return json.load(open(tp))


def plan(tl):
    """Kembalikan daftar {stage, dur, move, caption}."""
    stages = [s for s in STAGES if os.path.exists(image_for(s[0]))]
    per_seg = {}
    for st, seg, mv in stages:
        per_seg.setdefault(seg, []).append((st, mv))
    out = []
    for seg, items in sorted(per_seg.items()):
        row = next(r for r in tl["segments"] if r["segment"] == seg)
        each = row["dur"] / len(items)
        for st, mv in items:
            out.append({"stage": st, "dur": round(each, 3), "move": mv,
                        "caption": CAPTIONS[st], "img": image_for(st)})
    return out


def zoompan_expr(move, frames):
    """Ekspresi zoompan halus, tanpa goyang."""
    z = {
        "in": f"min(1+0.16*on/{frames},1.16)",
        "out": f"max(1.16-0.16*on/{frames},1.0)",
        "left": "1.14",
        "right": "1.14",
        "up": "1.14",
    }[move]
    if move == "left":
        x, y = f"(iw-iw/zoom)*(1-on/{frames})", "ih/2-ih/zoom/2"
    elif move == "right":
        x, y = f"(iw-iw/zoom)*(on/{frames})", "ih/2-ih/zoom/2"
    elif move == "up":
        x, y = "iw/2-iw/zoom/2", f"(ih-ih/zoom)*(1-on/{frames})"
    else:
        x, y = "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"
    return z, x, y


def _fit_lines(d, text, max_w, max_lines=2):
    """Cari ukuran font terbesar (<=62) yang membuat teks muat dalam max_lines baris."""
    words = text.split()
    for size in range(62, 33, -2):
        font = ImageFont.truetype(FONT, size)
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if d.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        if len(lines) <= max_lines and all(d.textlength(l, font=font) <= max_w for l in lines):
            return font, lines
    return ImageFont.truetype(FONT, 34), [text]


def caption_png(item):
    """Overlay transparan 1080x1920: caption bawah (auto-wrap) + label kanal."""
    os.makedirs(CAPS, exist_ok=True)
    dst = os.path.join(CAPS, f"cap{item['stage']:02d}.png")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    small = ImageFont.truetype(FONT, 30)
    max_w = W - 96
    font, lines = _fit_lines(d, item["caption"], max_w)
    asc, desc = font.getmetrics()
    lh = asc + desc + 8
    total_h = lh * len(lines)
    y0 = H - 200 - total_h
    for i, line in enumerate(lines):
        w = d.textlength(line, font=font)
        d.text(((W - w) / 2, y0 + i * lh), line, font=font,
               fill=(255, 255, 255, 248), stroke_width=6, stroke_fill=(0, 0, 0, 235))
    w = d.textlength("SAINS CORET", font=small)
    d.text((W - w - 46, 74), "SAINS CORET", font=small,
           fill=(255, 255, 255, 155), stroke_width=2, stroke_fill=(0, 0, 0, 130))
    img.save(dst)
    return dst


def build_clip(item, idx, total_items):
    dur = item["dur"]
    frames = max(int(round(dur * FPS)), 2)
    z, x, y = zoompan_expr(item["move"], frames)
    cap = caption_png(item)
    fc = (
        f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
        f"crop={W*2}:{H*2},setsar=1,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
        f"eq=contrast=1.04:saturation=1.02,"
        f"noise=alls=5:allf=t+u,"
        f"vignette=PI/4.6[bg];"
        f"[bg][1:v]overlay=0:0:format=auto,"
        f"fade=t=in:st=0:d=0.20:color=black,"
        f"fade=t=out:st={max(dur-0.20,0):.3f}:d=0.20:color=black[v]"
    )
    dst = os.path.join(CLIPS, f"c{idx:02d}.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", item["img"],
         "-loop", "1", "-i", cap,
         "-filter_complex", fc, "-map", "[v]", "-r", str(FPS),
         "-t", f"{dur:.3f}", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-an", dst])
    return dst


def make_bed(total):
    """Drone ambient tipis (sine rendah + noise halus) supaya tidak terlalu sepi."""
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i",
         f"sine=frequency=55:duration={total:.2f}",
         "-f", "lavfi", "-i",
         f"sine=frequency=82.5:duration={total:.2f}",
         "-f", "lavfi", "-i",
         f"anoisesrc=color=brown:duration={total:.2f}:amplitude=0.25",
         "-filter_complex",
         "[0:a]volume=0.55[a0];[1:a]volume=0.28[a1];"
         "[2:a]lowpass=f=420,highpass=f=45,volume=0.30[a2];"
         "[a0][a1][a2]amix=inputs=3:normalize=0,"
         "tremolo=f=0.1:d=0.35,volume=0.5,"
         "afade=t=in:st=0:d=3,afade=t=out:st=" + f"{max(total-3,0):.2f}" + ":d=3[out]",
         "-map", "[out]", "-ar", "48000", "-ac", "2", BED])


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = int(sys.argv[sys.argv.index("--preview") + 1])
    tl = load_timeline()
    items = plan(tl)
    if preview:
        items = items[:preview]
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    clips = []
    for i, it in enumerate(items):
        print(f"[{i+1}/{len(items)}] tahap {it['stage']:02d}  {it['dur']:.2f}s  {it['move']}")
        clips.append(build_clip(it, i, len(items)))

    # concat
    lst = os.path.join(WORK, "clips.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    video_only = os.path.join(WORK, "video_only.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", video_only])

    total = sum(i["dur"] for i in items)
    make_bed(total)
    narasi = os.path.join(ROOT, "assets/audio/narasi.wav")
    dst = os.path.join(OUT, "SAINS-CORET_short-01_titik-putih_9x16.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", video_only, "-i", narasi, "-i", BED,
         "-filter_complex",
         "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[v];"
         "[2:a]volume=0.22[bed];"
         "[v][bed]amix=inputs=2:duration=first:dropout_transition=2,"
         "alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", dst])
    print("\nselesai:", dst)


if __name__ == "__main__":
    main()
