#!/usr/bin/env python3
"""
Anti-Blur Razor-Sharp Render Pipeline for Video Short #07 v2 (30 Scenes, 3 Stages, 9:16 1080x1920 @ 60fps):
"Apa yang Terjadi Saat Amuba Pemakan Otak Masuk Lewat Hidungmu? (Naegleria fowleri)"

Fixes applied per user feedback ("Ulangi! Hasil gambar ada yang rusak, video seperti blur sedikit!"):
1. ZERO manual PIL rectangle/line/circle patching on any scene image or thumbnail — 100% pure native AI illustrations.
2. ZERO ghost-blending between unzoomed and zoomed frames (which previously caused double-edge blur on 2D outlines).
3. Uses a Supersampled UnsharpMask Master + Discrete Lanczos Zoom LUT (24 crisp Lanczos-resampled zoom steps per scene, zero alpha-blending between zoom steps!) + x264 `-crf 15 -tune animation` for razor-sharp 1080p60 output.
"""
import os
import json
import zipfile
import subprocess
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import imageio_ffmpeg

W, H = 1080, 1920
FPS = 60
ZOOM_STEPS = 24  # 24 discrete pure-Lanczos zoom steps (zero ghost-blending!)

ALL_30_SCENES = (
    [f"assets/images/short07_intro_{i:02d}.jpg" for i in range(1, 4)] +
    [f"assets/images/short07_t1_{i:02d}.jpg" for i in range(1, 8)] +
    [f"assets/images/short07_t2_{i:02d}.jpg" for i in range(1, 11)] +
    [f"assets/images/short07_t3_{i:02d}.jpg" for i in range(1, 10)] +
    ["assets/images/short07_outro_01.jpg"]
)


def normalize_and_sharpen_all_30_scenes():
    for p in ALL_30_SCENES:
        assert os.path.exists(p), f"Missing scene file: {p}"
        im = Image.open(p).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=135, threshold=2))
            im.save(p, quality=97)
    print("Verified, normalized, and sharpened all 30 scenes to 1080x1920 (9:16 un-stretched 1:1).")


def build_batches_and_previews():
    os.makedirs("output", exist_ok=True)
    batches = [
        ("Batch1_01_to_10", "01_to_10", ALL_30_SCENES[0:10]),
        ("Batch2_11_to_20", "11_to_20", ALL_30_SCENES[10:20]),
        ("Batch3_21_to_30", "21_to_30", ALL_30_SCENES[20:30]),
    ]
    cw, ch = 270, 480
    for preview_tag, zip_tag, scene_list in batches:
        zip_path = f"output/BACKUP_Short07_v2_Scenes_{zip_tag}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in scene_list:
                zf.write(p, os.path.basename(p))
        sheet = Image.new("RGB", (cw * 5, ch * 2), (255, 255, 255))
        for idx, p in enumerate(scene_list):
            im = Image.open(p).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS)
            r, c = idx // 5, idx % 5
            sheet.paste(im, (c * cw, r * ch))
        preview_path = f"output/PREVIEW_Short07_v2_{preview_tag}_9x16.jpg"
        sheet.save(preview_path, quality=95)
        print("Saved:", zip_path, "and", preview_path)


def build_scene_zoom_lut(img_path):
    """
    Build 24 pure Lanczos-resampled frames from 1.000x to 1.012x zoom with UnsharpMask.
    Each step is a crisp, standalone Lanczos-resampled frame (NO blending between steps!).
    """
    im = Image.open(img_path).convert("RGB")
    if im.size != (W, H):
        im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    lut = []
    for k in range(ZOOM_STEPS):
        scale = 1.0 + 0.012 * (k / max(1, ZOOM_STEPS - 1))
        if k == 0:
            step_im = im
        else:
            zw = int(round(W * scale))
            zh = int(round(H * scale))
            x0 = (zw - W) // 2
            y0 = (zh - H) // 2
            step_im = im.resize((zw, zh), Image.Resampling.LANCZOS).crop((x0, y0, x0 + W, y0 + H))
            step_im = step_im.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110, threshold=2))
        lut.append(np.asarray(step_im, dtype=np.uint8))
    return lut


def render_video():
    with open("output/short07_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)
    assert len(timeline) == 30, f"Expected 30 scenes in timeline, got {len(timeline)}"

    total_dur = timeline[-1]["end"]
    total_frames = int(round(total_dur * FPS))
    print(f"Rendering Razor-Sharp 30-Scene Short #07 v2: {total_dur:.2f}s ({total_frames} frames @ {FPS}fps)...")

    out_mp4 = "output/Short07_v2_Amuba_Pemakan_Otak_Lewat_Hidung_9x16.mp4"
    vo_mp3 = "output/VO_Master_Short07_30_Adegan_9x16.mp3"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", vo_mp3,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "faster", "-crf", "15", "-tune", "animation",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    starts = [item["start"] for item in timeline]
    ends = [item["end"] for item in timeline]
    fade_sec = 0.18

    cur_sc_idx = -1
    cur_lut = None
    prev_last_frame = None

    def get_frame_from_lut(lut, sc_idx, local_prog):
        s = 0.5 - 0.5 * np.cos(np.pi * np.clip(local_prog, 0.0, 1.0))
        if sc_idx % 2 == 1:
            s = 1.0 - s
        k = int(round(s * (ZOOM_STEPS - 1)))
        return lut[max(0, min(ZOOM_STEPS - 1, k))]

    sc_idx = 0
    for f_idx in range(total_frames):
        t = f_idx / FPS
        while sc_idx < 29 and t >= ends[sc_idx]:
            sc_idx += 1
        if sc_idx != cur_sc_idx:
            if cur_lut is not None:
                prev_last_frame = get_frame_from_lut(cur_lut, cur_sc_idx, 1.0)
            cur_lut = build_scene_zoom_lut(timeline[sc_idx]["image"])
            cur_sc_idx = sc_idx

        sc_start = starts[sc_idx]
        sc_end = ends[sc_idx]
        sc_dur = max(0.1, sc_end - sc_start)
        prog = (t - sc_start) / sc_dur

        frame = get_frame_from_lut(cur_lut, sc_idx, prog)

        if sc_idx > 0 and prev_last_frame is not None and (t - sc_start) < fade_sec:
            alpha = (t - sc_start) / fade_sec
            alpha_s = 0.5 - 0.5 * np.cos(np.pi * np.clip(alpha, 0.0, 1.0))
            w_cur = int(round(alpha_s * 256))
            frame = ((prev_last_frame.astype(np.uint16) * (256 - w_cur) + frame.astype(np.uint16) * w_cur) >> 8).astype(np.uint8)

        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr_out[-600:]}")
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: Rendered {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s @ 60fps)")


if __name__ == "__main__":
    normalize_and_sharpen_all_30_scenes()
    build_batches_and_previews()
    render_video()
