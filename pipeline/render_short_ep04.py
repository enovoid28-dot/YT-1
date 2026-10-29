#!/usr/bin/env python3
"""
60fps 1080x1920 (9:16) Renderer for Video Short #04 (@SeorangSains):
'Apa yang Terjadi Jika Kamu Tidak Tidur Selama 11 Hari? (Saat Otak Memakan Dirinya Sendiri)'
- Format: 1080x1920 @ 60.00 fps (9:16 YouTube Shorts Full HD)
- Duration: 02:48.76 (168.76s, 30 scenes) — safely under 3:00 YouTube Shorts limit
- Audio: Pure Master VO (output/VO_Master_Short04_30_Adegan_9x16.mp3) — NO BACKGROUND MUSIC
- Visuals:
  * 30 custom realistic-situation 9:16 scenes (#01..#30)
  * Calm 1.2% micro-zoom + smooth 0.25s (15-frame) cross-dissolves at exact silence midpoints
  * NO top HUD / NO subtitles (100% clean full-frame visuals per user instruction)
"""

import json
import os
import subprocess
import time
import imageio_ffmpeg
import numpy as np
from PIL import Image

W, H = 1080, 1920
FPS = 60
CROSSFADE_FRAMES = 15  # 0.25s smooth cross-dissolve


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
    return up_arr[y0:y0 + H, x0:x0 + W]


def main():
    t0 = time.time()
    with open("output/short04_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)

    assert len(timeline) == 30, f"Expected 30 scenes, got {len(timeline)}"
    total_sec = timeline[-1]["end"]
    total_frames = int(round(total_sec * FPS))
    print(f"Rendering Clean Video Short #04 (No Top HUD, No BGM): {len(timeline)} scenes, {total_sec:.2f}s ({total_frames} frames @ {FPS}fps)")

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

        for local_f in range(n_f):
            prog = local_f / max(1, n_f - 1)
            frame = crop_micro_zoom(curr_up, prog, s_num)

            rem = (n_f - 1) - local_f
            if rem < CROSSFADE_FRAMES and idx + 1 < len(scene_frames):
                alpha = (CROSSFADE_FRAMES - rem) / float(CROSSFADE_FRAMES)
                alpha = alpha * alpha * (3.0 - 2.0 * alpha)
                next_frame = crop_micro_zoom(next_up, 0.0, s_num + 1)
                frame = (frame.astype(np.float32) * (1.0 - alpha) + next_frame.astype(np.float32) * alpha).astype(np.uint8)
            else:
                frame = np.ascontiguousarray(frame)

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
