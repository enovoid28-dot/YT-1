import os
import json
import subprocess
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import imageio_ffmpeg

W, H = 1080, 1920
FPS = 60

def normalize_and_sharpen_all_30_scenes(timeline):
    for item in timeline:
        p = item["image"]
        assert os.path.exists(p), f"Missing scene file: {p}"
        im = Image.open(p).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
            im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
            im.save(p, quality=96, subsampling=0)

def render_short_ep10():
    with open("output/short10_timeline_30_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)

    assert len(timeline) == 30, f"Expected 30 scenes, got {len(timeline)}"
    normalize_and_sharpen_all_30_scenes(timeline)

    vo_path = "output/VO_Master_Short10_30_Adegan_9x16.mp3"
    out_mp4 = "output/VIDEO_SHORT_10_Jantung_Berdetak_Di_Luar_Tubuh_9x16_1080p_60fps.mp4"
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    total_dur = timeline[-1]["end"]
    total_frames = int(round(total_dur * FPS))
    print(f"Rendering {total_frames} frames ({total_dur:.2f}s @ {FPS}fps) -> {out_mp4} (1:1 Pixel-Exact Anti-Blur)")

    scene_frames = []
    for item in timeline:
        im = Image.open(item["image"]).convert("RGB")
        if im.size != (W, H):
            im = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        im_sharp = im.filter(ImageFilter.UnsharpMask(radius=1.1, percent=110, threshold=2))
        arr = np.asarray(im_sharp, dtype=np.uint8)
        scene_frames.append({
            "scene": item["scene"],
            "start": float(item["start"]),
            "end": float(item["end"]),
            "duration": float(item["duration"]),
            "frame": arr,
            "bytes": arr.tobytes(),
        })

    cmd = [
        ffmpeg, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", vo_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "14",
        "-tune", "animation",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS),
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-shortest",
        "-movflags", "+faststart",
        out_mp4
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    xfade_sec = 0.14
    s_idx = 0
    n_scenes = len(scene_frames)

    for f_idx in range(total_frames):
        t = f_idx / FPS
        while s_idx < n_scenes - 1 and t >= scene_frames[s_idx]["end"]:
            s_idx += 1

        cur = scene_frames[s_idx]

        if s_idx > 0 and (t - cur["start"]) < xfade_sec:
            alpha = (t - cur["start"]) / xfade_sec
            prev_f = scene_frames[s_idx - 1]["frame"].astype(np.float32)
            cur_f = cur["frame"].astype(np.float32)
            blended = np.clip(prev_f * (1.0 - alpha) + cur_f * alpha, 0, 255).astype(np.uint8)
            proc.stdin.write(blended.tobytes())
        else:
            proc.stdin.write(cur["bytes"])

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr_out[-1000:]}")

    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: {out_mp4} ({sz_mb:.2f} MB, {total_dur:.2f}s)")

if __name__ == "__main__":
    render_short_ep10()
