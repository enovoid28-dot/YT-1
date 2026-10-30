#!/usr/bin/env python3
"""
Anti-Blur 1:1 Pixel-Exact Render Pipeline for Video Short #08 (30 Scenes, 3 Stages, 9:16 1080x1920 @ 60fps):
"Apa yang Terjadi Jika Bom Nuklir Dijatuhkan ke Gunung Berapi Aktif?"
- 100% Native AI Illustrations (Zero manual PIL patching, zero fleshy stickman arms)
- 1:1 Pixel-Exact 1080x1920 + UnsharpMask + x264 -crf 14 -tune animation (Zero blur)
- Crystal-Clear Psychoacoustic Voiceover (Zero vocal fry / zero snoring, 1.000x natural speed, no BGM)
"""
import os
import json
import subprocess
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import imageio_ffmpeg

W, H = 1080, 1920
FPS = 60

ALL_30_SCENES = (
    [f"assets/images/short08_intro_{i:02d}.jpg" for i in range(1, 4)] +
    [f"assets/images/short08_t1_{i:02d}.jpg" for i in range(1, 8)] +
    [f"assets/images/short08_t2_{i:02d}.jpg" for i in range(1, 11)] +
    [f"assets/images/short08_t3_{i:02d}.jpg" for i in range(1, 10)] +
    ["assets/images/short08_outro_01.jpg"]
)


def normalize_and_sharpen_all_30_scenes():
    for p in ALL_30_SCENES:
        assert os.path.exists(p), f"Missing scene file: {p}"
        im = Image.open(p).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            im = im.filter(ImageFilter.UnsharpMask(radius=1.3, percent=125, threshold=2))
            im.save(p, quality=97)
    print("Verified, normalized, and sharpened all 30 scenes to 1080x1920 (9:16 un-stretched 1:1).")


def load_sharp_native_scene(img_path):
    im = Image.open(img_path).convert("RGB")
    if im.size != (W, H):
        im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
    return np.asarray(im, dtype=np.uint8)


def render_video():
    with open("output/short08_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)
    assert len(timeline) == 30, f"Expected 30 scenes in timeline, got {len(timeline)}"

    total_dur = timeline[-1]["end"]
    total_frames = int(round(total_dur * FPS))
    print(f"Rendering 1:1 Pixel-Exact Razor-Sharp 30-Scene Short #08: {total_dur:.2f}s ({total_frames} frames @ {FPS}fps)...")

    out_mp4 = "output/Short08_Bom_Nuklir_Di_Gunung_Berapi_Aktif_9x16.mp4"
    vo_mp3 = "output/VO_Master_Short08_30_Adegan_9x16.mp3"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", vo_mp3,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "14", "-tune", "animation",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    starts = [item["start"] for item in timeline]
    ends = [item["end"] for item in timeline]
    fade_sec = 0.14

    cur_sc_idx = -1
    cur_frame = None
    prev_frame = None
    cur_bytes = None

    sc_idx = 0
    for f_idx in range(total_frames):
        t = f_idx / FPS
        while sc_idx < 29 and t >= ends[sc_idx]:
            sc_idx += 1
        if sc_idx != cur_sc_idx:
            if cur_frame is not None:
                prev_frame = cur_frame
            cur_frame = load_sharp_native_scene(timeline[sc_idx]["image"])
            cur_bytes = cur_frame.tobytes()
            cur_sc_idx = sc_idx

        sc_start = starts[sc_idx]
        if sc_idx > 0 and prev_frame is not None and (t - sc_start) < fade_sec:
            alpha = (t - sc_start) / fade_sec
            alpha_s = 0.5 - 0.5 * np.cos(np.pi * np.clip(alpha, 0.0, 1.0))
            w_cur = int(round(alpha_s * 256))
            blended = ((prev_frame.astype(np.uint16) * (256 - w_cur) + cur_frame.astype(np.uint16) * w_cur) >> 8).astype(np.uint8)
            proc.stdin.write(blended.tobytes())
        else:
            proc.stdin.write(cur_bytes)

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr_out[-600:]}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: Rendered {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s @ 60fps)")


if __name__ == "__main__":
    normalize_and_sharpen_all_30_scenes()
    render_video()
