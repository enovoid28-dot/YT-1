#!/usr/bin/env python3
"""
60fps 1080x1920 (9:16) Renderer for Video Short #04 (@SeorangSains):
'Apa yang Terjadi Jika Kamu Tidak Tidur Selama 11 Hari? (Saat Otak Memakan Dirinya Sendiri)'
- Format: 1080x1920 @ 60.00 fps (9:16 YouTube Shorts Full HD)
- Duration: 02:48.76 (168.76s, 30 scenes) — safely under 3:00 YouTube Shorts limit
- Audio: Pure Master VO (output/VO_Master_Short04_30_Adegan_9x16.mp3) — NO BACKGROUND MUSIC
- Visuals:
  * 30 custom 9:16 scenes (#01..#30)
  * Calm 1.2% micro-zoom + smooth 0.25s (15-frame) cross-dissolves at exact silence midpoints
  * Non-subtitle 60fps Explanatory Motion Graphics HUD at the top of the 9:16 frame:
    - 11-Day Progression Node Bar (Day 1 -> Day 11)
    - Brain Adenosine & Beta-Amyloid Toxicity Meter Bar
    - Animated EEG Brainwave Monitor Wave
"""

import json
import math
import os
import subprocess
import time
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
FPS = 60
CROSSFADE_FRAMES = 15  # 0.25s smooth cross-dissolve


def get_scene_state(scene_num: int):
    """
    Map scene_num (1..30) to:
    - day_node: 0..11 (which day node is active on the 11-day progression bar)
    - tox_level: 0.0..1.0 (brain adenosine / beta-amyloid toxicity bar)
    - wave_mode: 'normal', 'stress', 'microsleep', 'critical', 'recovery'
    """
    if scene_num <= 3:
        return 0, 0.10, "normal"
    elif scene_num <= 6:
        return 1, 0.30, "stress"
    elif scene_num == 7:
        return 2, 0.42, "stress"
    elif scene_num in (8, 9):
        return 2, 0.50, "microsleep"
    elif scene_num == 10:
        return 3, 0.62, "stress"
    elif scene_num == 11:
        return 4, 0.70, "critical"
    elif scene_num in (12, 13, 14, 15):
        return 5, 0.82, "critical"
    elif scene_num in (16, 17):
        return 6, 0.88, "critical"
    elif scene_num in (18, 19, 20):
        return 7, 0.94, "critical"
    elif scene_num == 21:
        return 9, 0.96, "critical"
    elif scene_num == 22:
        return 10, 0.98, "critical"
    elif scene_num in (23, 24):
        return 11, 1.00, "critical"
    elif scene_num in (25, 26, 27):
        return 11, 0.15, "recovery"
    elif scene_num in (28, 29):
        return 11, 0.55, "stress"
    else:
        return 0, 0.08, "recovery"


def build_hud_loop(day_node: int, tox_level: float, wave_mode: str, n_loop: int = 120):
    """
    Pre-render `n_loop` (2.0s @ 60fps) top HUD banner patches (1000 x 116) for vertical 9:16 screen.
    Contains ZERO text/letters/numbers — purely graphical/iconic explainers.
    """
    pw, ph = 1000, 116
    if wave_mode == "recovery":
        col_main = (0, 230, 195)
    elif tox_level < 0.35:
        col_main = (40, 220, 180)
    elif tox_level < 0.68:
        col_main = (255, 195, 40)
    else:
        col_main = (255, 60, 75)

    frames = []
    for f in range(n_loop):
        phase = (f / n_loop) * 2.0 * math.pi
        im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)

        # Sleek dark translucent glass panel
        d.rounded_rectangle([0, 0, pw - 1, ph - 1], radius=22, fill=(12, 16, 26, 180), outline=(col_main[0], col_main[1], col_main[2], 200), width=3)

        # Top row (y=32): 11-Node Day Progression Bar (x=42..620)
        x0, x1 = 42, 620
        y_top = 34
        d.line([(x0, y_top), (x1, y_top)], fill=(55, 70, 90, 210), width=5)
        n_nodes = 11
        act = max(1, min(11, day_node if day_node > 0 else 1))
        prog_x = x0 + (x1 - x0) * ((act - 1) / (n_nodes - 1))
        d.line([(x0, y_top), (int(prog_x), y_top)], fill=(col_main[0], col_main[1], col_main[2], 235), width=5)

        for i in range(n_nodes):
            nx = int(x0 + (x1 - x0) * (i / (n_nodes - 1)))
            if i + 1 < act:
                d.ellipse([nx - 8, y_top - 8, nx + 8, y_top + 8], fill=(col_main[0], col_main[1], col_main[2], 240), outline=(255, 255, 255, 210), width=2)
            elif i + 1 == act:
                rp = int(11 + 3.0 * math.sin(phase * 2))
                d.ellipse([nx - rp - 4, y_top - rp - 4, nx + rp + 4, y_top + rp + 4], fill=(col_main[0], col_main[1], col_main[2], 90))
                d.ellipse([nx - rp, y_top - rp, nx + rp, y_top + rp], fill=(255, 255, 255, 255), outline=(col_main[0], col_main[1], col_main[2], 255), width=3)
            else:
                d.ellipse([nx - 7, y_top - 7, nx + 7, y_top + 7], fill=(28, 38, 54, 220), outline=(85, 105, 130, 190), width=2)

        # Bottom row (y=72..94): Brain Toxicity / Adenosine Segmented Meter (x=42..620)
        bx0, by0, bx1, by1 = 42, 70, 620, 92
        n_segs = 18
        seg_w = (bx1 - bx0) // n_segs
        active_segs = int(round(tox_level * n_segs))
        for s_i in range(n_segs):
            sx0 = bx0 + s_i * seg_w + 2
            sx1 = sx0 + seg_w - 4
            if s_i < active_segs:
                if wave_mode == "recovery":
                    sc = (0, 230, 195, 235)
                elif s_i < 6:
                    sc = (40, 225, 175, 235)
                elif s_i < 12:
                    sc = (255, 195, 40, 235)
                else:
                    sc = (255, 55, 70, 245)
                d.rounded_rectangle([sx0, by0, sx1, by1], radius=4, fill=sc)
            else:
                d.rounded_rectangle([sx0, by0, sx1, by1], radius=4, fill=(32, 42, 58, 190))

        # Right side (x=655..968, y=18..98): Animated EEG Brainwave Monitor Box
        wx0, wy0, wx1, wy1 = 655, 18, 968, 98
        d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=12, fill=(16, 24, 38, 230), outline=(col_main[0], col_main[1], col_main[2], 180), width=2)
        wy_mid = (wy0 + wy1) // 2
        pts = []
        for ix in range(wx0 + 10, wx1 - 10, 3):
            norm_x = (ix - (wx0 + 10)) / float(wx1 - wx0 - 20)
            if wave_mode == "microsleep" and 0.35 <= norm_x <= 0.80:
                val = 0.0  # Sudden flatline during microsleep!
            elif wave_mode == "critical":
                w_p = norm_x * 6.0 * math.pi - phase * 3.0
                val = 22.0 * math.sin(w_p) * math.cos(w_p * 1.7)
            elif wave_mode == "stress":
                w_p = norm_x * 4.5 * math.pi - phase * 2.0
                val = 16.0 * math.sin(w_p)
            else:
                w_p = norm_x * 3.0 * math.pi - phase * 1.5
                val = 12.0 * math.sin(w_p)
            pts.append((ix, int(wy_mid - val)))
        if len(pts) > 1:
            d.line(pts, fill=(col_main[0], col_main[1], col_main[2], 245), width=3)

        arr = np.array(im, dtype=np.uint8)
        frames.append((arr[:, :, :3], arr[:, :, 3:4].astype(np.float32) / 255.0))
    return frames


def load_zoom_lut(img_path: str):
    im = Image.open(img_path).convert("RGB")
    up_w, up_h = 1108, 1970  # +2.5% margin for calm 1.2% micro-zoom/pan
    im_up = im.resize((up_w, up_h), Image.Resampling.LANCZOS)
    return np.array(im_up, dtype=np.uint8)


def crop_micro_zoom(up_arr: np.ndarray, progress: float, scene_num: int) -> np.ndarray:
    max_dx = 1108 - W  # 28 px
    max_dy = 1970 - H  # 50 px
    if scene_num % 2 == 0:
        x0 = int(round(max_dx * progress))
        y0 = int(round(max_dy * (0.2 + 0.6 * progress)))
    else:
        x0 = int(round(max_dx * (1.0 - progress)))
        y0 = int(round(max_dy * (0.8 - 0.6 * progress)))
    return up_arr[y0:y0 + H, x0:x0 + W].copy()


def main():
    t0 = time.time()
    with open("output/short04_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)

    assert len(timeline) == 30, f"Expected 30 scenes, got {len(timeline)}"
    total_sec = timeline[-1]["end"]
    total_frames = int(round(total_sec * FPS))
    print(f"Rendering Video Short #04: {len(timeline)} scenes, {total_sec:.2f}s ({total_frames} frames @ {FPS}fps) — NO BGM")

    last_st = None
    hud_frames = None

    out_mp4 = "output/STICKMAN_short-04_tidak-tidur-11-hari-otak-memakan-diri_9x16.mp4"
    vo_path = "output/VO_Master_Short04_30_Adegan_9x16.mp3"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}",
        "-r", str(FPS),
        "-i", "-",
        "-i", vo_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "animation",
        "-crf", "23",
        "-maxrate", "1200k",
        "-bufsize", "2400k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    scene_frames = []
    for i, item in enumerate(timeline):
        f_start = int(round(item["start"] * FPS))
        f_end = int(round(item["end"] * FPS)) if i < len(timeline) - 1 else total_frames
        scene_frames.append((i + 1, item["image"], f_start, f_end))

    curr_up = load_zoom_lut(scene_frames[0][1])
    next_up = load_zoom_lut(scene_frames[1][1])

    frames_written = 0
    for idx, (s_num, img_path, f_start, f_end) in enumerate(scene_frames):
        n_f = max(1, f_end - f_start)
        st = get_scene_state(s_num)
        if st != last_st:
            hud_frames = build_hud_loop(*st)
            last_st = st

        for local_f in range(n_f):
            global_f = f_start + local_f
            prog = local_f / max(1, n_f - 1)
            frame = crop_micro_zoom(curr_up, prog, s_num)

            rem = (n_f - 1) - local_f
            if rem < CROSSFADE_FRAMES and idx + 1 < len(scene_frames):
                alpha = (CROSSFADE_FRAMES - rem) / float(CROSSFADE_FRAMES)
                alpha = alpha * alpha * (3.0 - 2.0 * alpha)
                next_frame = crop_micro_zoom(next_up, 0.0, s_num + 1)
                frame = (frame.astype(np.float32) * (1.0 - alpha) + next_frame.astype(np.float32) * alpha).astype(np.uint8)

            # Overlay top non-subtitle motion-graphics HUD at (40, 36)
            h_rgb, h_a = hud_frames[global_f % 120]
            hh, hw, _ = h_rgb.shape
            roi = frame[36:36 + hh, 40:40 + hw]
            frame[36:36 + hh, 40:40 + hw] = (roi * (1.0 - h_a) + h_rgb * h_a).astype(np.uint8)

            proc.stdin.write(frame.tobytes())
            frames_written += 1

        if idx + 1 < len(scene_frames):
            curr_up = next_up
            if idx + 2 < len(scene_frames):
                next_up = load_zoom_lut(scene_frames[idx + 2][1])

        if (idx + 1) % 10 == 0 or (idx + 1) == len(scene_frames):
            el = time.time() - t0
            print(f"  Rendered {idx + 1}/30 scenes ({frames_written}/{total_frames} frames, {frames_written / max(0.1, el):.1f} fps, {el:.1f}s)")

    proc.stdin.close()
    ret = proc.wait()
    assert ret == 0, f"FFmpeg exited with {ret}"
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: {out_mp4} ({sz_mb:.2f} MB) in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
