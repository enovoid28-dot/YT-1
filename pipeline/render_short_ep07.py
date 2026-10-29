#!/usr/bin/env python3
"""
Render Pipeline for Video Short #07 (30 Scenes, 3 Stages, 9:16 1080x1920 @ 60fps):
"Apa yang Terjadi Saat Amuba Pemakan Otak Masuk Lewat Hidungmu? (Naegleria fowleri)"
- 30 scenes across Pembuka Maskot (#01-#03), Tahap 1 (#04-#10), Tahap 2 (#11-#20), Tahap 3 (#21-#30)
- 100% True 1:1 Un-Stretched Aspect Ratio (ImageOps.fit 1080x1920)
- NO Top HUD, NO BGM, NO Subtitles
- Calm 1.2% micro-zoom & smooth 0.25s cross-dissolve transitions
"""
import os
import json
import zipfile
import subprocess
import numpy as np
from PIL import Image, ImageOps
import imageio_ffmpeg

W, H = 1080, 1920
FPS = 60

ALL_30_SCENES = (
    [f"assets/images/short07_intro_{i:02d}.jpg" for i in range(1, 4)] +
    [f"assets/images/short07_t1_{i:02d}.jpg" for i in range(1, 8)] +
    [f"assets/images/short07_t2_{i:02d}.jpg" for i in range(1, 11)] +
    [f"assets/images/short07_t3_{i:02d}.jpg" for i in range(1, 10)] +
    ["assets/images/short07_outro_01.jpg"]
)


def normalize_all_30_scenes():
    for p in ALL_30_SCENES:
        assert os.path.exists(p), f"Missing scene file: {p}"
        im = Image.open(p).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            im.save(p, quality=96)
    print("Verified and normalized all 30 scenes to 1080x1920 (9:16 un-stretched 1:1).")


def build_batches_and_previews():
    os.makedirs("output", exist_ok=True)
    batches = [
        ("Batch1_01_to_10", "01_to_10", ALL_30_SCENES[0:10]),
        ("Batch2_11_to_20", "11_to_20", ALL_30_SCENES[10:20]),
        ("Batch3_21_to_30", "21_to_30", ALL_30_SCENES[20:30]),
    ]
    cw, ch = 270, 480
    for preview_tag, zip_tag, scene_list in batches:
        zip_path = f"output/BACKUP_Short07_Scenes_{zip_tag}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in scene_list:
                zf.write(p, os.path.basename(p))
        sheet = Image.new("RGB", (cw * 5, ch * 2), (255, 255, 255))
        for idx, p in enumerate(scene_list):
            im = Image.open(p).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
            r, c = idx // 5, idx % 5
            sheet.paste(im, (c * cw, r * ch))
        preview_path = f"output/PREVIEW_Short07_{preview_tag}_9x16.jpg"
        sheet.save(preview_path, quality=93)
        print("Saved:", zip_path, "and", preview_path)


def render_video():
    with open("output/short07_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)
    assert len(timeline) == 30, f"Expected 30 scenes in timeline, got {len(timeline)}"

    total_dur = timeline[-1]["end"]
    total_frames = int(round(total_dur * FPS))
    print(f"Rendering 30-Scene Short #07: {total_dur:.2f}s ({total_frames} frames @ {FPS}fps)...")

    base_frames = []
    zoom_frames = []
    zw, zh = int(W * 1.012), int(H * 1.012)
    x0 = (zw - W) // 2
    y0 = (zh - H) // 2

    for item in timeline:
        im = Image.open(item["image"]).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS)
        base_frames.append(np.asarray(im, dtype=np.uint8))
        im_z = im.resize((zw, zh), Image.Resampling.BICUBIC).crop((x0, y0, x0 + W, y0 + H))
        zoom_frames.append(np.asarray(im_z, dtype=np.uint8))

    out_mp4 = "output/Short07_Amuba_Pemakan_Otak_Lewat_Hidung_9x16.mp4"
    vo_mp3 = "output/VO_Master_Short07_30_Adegan_9x16.mp3"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", vo_mp3,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    starts = [item["start"] for item in timeline]
    ends = [item["end"] for item in timeline]
    fade_sec = 0.25

    def get_scene_frame(sc_idx, local_prog):
        s = 0.5 - 0.5 * np.cos(np.pi * np.clip(local_prog, 0.0, 1.0))
        if sc_idx % 2 == 1:
            s = 1.0 - s
        b = base_frames[sc_idx]
        z = zoom_frames[sc_idx]
        w_z = int(round(s * 256))
        if w_z <= 0:
            return b
        if w_z >= 256:
            return z
        return ((b.astype(np.uint16) * (256 - w_z) + z.astype(np.uint16) * w_z) >> 8).astype(np.uint8)

    sc_idx = 0
    for f_idx in range(total_frames):
        t = f_idx / FPS
        while sc_idx < 29 and t >= ends[sc_idx]:
            sc_idx += 1
        sc_start = starts[sc_idx]
        sc_end = ends[sc_idx]
        sc_dur = max(0.1, sc_end - sc_start)
        prog = (t - sc_start) / sc_dur

        frame = get_scene_frame(sc_idx, prog)

        if sc_idx > 0 and (t - sc_start) < fade_sec:
            alpha = (t - sc_start) / fade_sec
            alpha_s = 0.5 - 0.5 * np.cos(np.pi * np.clip(alpha, 0.0, 1.0))
            w_cur = int(round(alpha_s * 256))
            prev_frame = get_scene_frame(sc_idx - 1, 1.0)
            frame = ((prev_frame.astype(np.uint16) * (256 - w_cur) + frame.astype(np.uint16) * w_cur) >> 8).astype(np.uint8)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr_out[-600:]}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: Rendered {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s @ 60fps)")


if __name__ == "__main__":
    normalize_all_30_scenes()
    build_batches_and_previews()
    render_video()
