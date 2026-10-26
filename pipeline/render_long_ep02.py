#!/usr/bin/env python3
"""
60fps 1080p Renderer for Video Long #02 (@SeorangSains):
'POV: Kamu Jadi Pejabat Korupsi di Indonesia (Cara Kerja Suap & Cuci Uang Miliaran)'
- Format: 1920x1080 @ 60.00 fps (16:9 Full HD)
- Audio: Pure Master VO (VO_Master_Long02_94_Adegan_16x9.mp3) — NO BACKGROUND MUSIC (per user instruction)
- Visuals:
  * 94 custom 16:9 scenes (#01..#94)
  * Calm 1.2% micro-zoom + smooth 0.25s (15-frame) cross-dissolves at exact silence midpoints
  * Non-subtitle Explanatory Motion Graphics & POV HUD overlays (animated ECG heart-rate/cortisol wave,
    PPATK/KPK radar scanner sweep, suspicion meter bar, and 3-stage TPPU flow node diagram)
"""

import json
import math
import os
import subprocess
import time
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

W, H = 1920, 1080
FPS = 60
CROSSFADE_FRAMES = 15  # 0.25s smooth cross-dissolve

# Mascot @SeorangSains explainer scenes (no POV visor brackets; show Science/Forensic Node Diagram HUD)
MASCOT_SCENES = {1, 2, 3, 9, 21, 34, 44, 54, 64, 77, 87, 94}


def build_hud_frames(stage_idx: int, is_mascot: bool, n_loop: int = 120):
    """
    Pre-render `n_loop` (2.0s @ 60fps) animated non-subtitle motion-graphics HUD patches:
    1) Top-left: 9-node stage progress & TPPU / Forensic flow diagram (380x76)
    2) Top-right: Animated PPATK/KPK Radar Sweep + Suspicion Meter + ECG Cortisol/Heart-rate wave (360x96)
    3) Bottom corners (for POV scenes): Subtle POV viewfinder brackets
    Returns a list of pre-rendered (patch_rgb, patch_alpha, x, y) tuples per frame index f in 0..n_loop-1.
    """
    # Suspicion level 0.0 -> 1.0 across stages 0..10
    susp_map = {
        0: 0.08,  # Intro
        1: 0.15,  # Tahap 1: Fraud Triangle
        2: 0.28,  # Tahap 2: Mark-Up & Tender
        3: 0.42,  # Tahap 3: Commitment Fee Tunai
        4: 0.54,  # Tahap 4: TPPU Placement
        5: 0.66,  # Tahap 5: TPPU Layering
        6: 0.80,  # Tahap 6: TPPU Integration & Flexing
        7: 0.92,  # Tahap 7: PPATK Follow The Money
        8: 1.00,  # Tahap 8: Sadapan & OTT KPK
        9: 1.00,  # Tahap 9: Rompi Oranye & Pembuktian Terbalik
        10: 0.10, # Outro
    }
    susp = susp_map.get(stage_idx, 0.5)

    # Choose accent color based on suspicion level
    if susp < 0.35:
        col_main = (0, 230, 180)
    elif susp < 0.75:
        col_main = (255, 195, 40)
    else:
        col_main = (255, 65, 75)

    top_left_frames = []
    top_right_frames = []

    tl_w, tl_h = 370, 68
    tr_w, tr_h = 340, 84

    for f in range(n_loop):
        phase = (f / n_loop) * 2.0 * math.pi

        # --- 1. TOP-LEFT MOTION GRAPHIC: 9-Node Forensic Flow Indicator (No text!) ---
        tl_img = Image.new("RGBA", (tl_w, tl_h), (0, 0, 0, 0))
        d_tl = ImageDraw.Draw(tl_img)
        # Sleek dark glass pill
        d_tl.rounded_rectangle([0, 0, tl_w - 1, tl_h - 1], radius=14, fill=(12, 16, 24, 175), outline=(col_main[0], col_main[1], col_main[2], 190), width=2)

        # Draw 9 connected stage nodes with animated data pulse traveling along the line
        n_nodes = 9
        x0, x1 = 28, tl_w - 28
        y_mid = tl_h // 2
        d_tl.line([(x0, y_mid), (x1, y_mid)], fill=(60, 75, 95, 200), width=4)

        # Animated pulse packet along active progress
        active_node = max(1, min(9, stage_idx if 1 <= stage_idx <= 9 else (1 if stage_idx == 0 else 9)))
        prog_x = x0 + (x1 - x0) * ((active_node - 1) / (n_nodes - 1))
        d_tl.line([(x0, y_mid), (int(prog_x), y_mid)], fill=(col_main[0], col_main[1], col_main[2], 230), width=4)

        pulse_t = (f % 60) / 60.0
        px = int(x0 + (prog_x - x0) * pulse_t)
        d_tl.ellipse([px - 5, y_mid - 5, px + 5, y_mid + 5], fill=(255, 255, 255, 240))

        for i in range(n_nodes):
            nx = int(x0 + (x1 - x0) * (i / (n_nodes - 1)))
            if i + 1 < active_node:
                d_tl.ellipse([nx - 7, y_mid - 7, nx + 7, y_mid + 7], fill=(col_main[0], col_main[1], col_main[2], 240), outline=(255, 255, 255, 210), width=2)
            elif i + 1 == active_node:
                r_pulse = int(9 + 2.5 * math.sin(phase * 2))
                d_tl.ellipse([nx - r_pulse - 3, y_mid - r_pulse - 3, nx + r_pulse + 3, y_mid + r_pulse + 3], fill=(col_main[0], col_main[1], col_main[2], 85))
                d_tl.ellipse([nx - r_pulse, y_mid - r_pulse, nx + r_pulse, y_mid + r_pulse], fill=(255, 255, 255, 255), outline=(col_main[0], col_main[1], col_main[2], 255), width=3)
            else:
                d_tl.ellipse([nx - 6, y_mid - 6, nx + 6, y_mid + 6], fill=(30, 40, 55, 220), outline=(90, 110, 135, 190), width=2)

        tl_arr = np.array(tl_img, dtype=np.uint8)
        top_left_frames.append((tl_arr[:, :, :3], tl_arr[:, :, 3:4].astype(np.float32) / 255.0))

        # --- 2. TOP-RIGHT MOTION GRAPHIC: Radar Sweep + Suspicion Bar + ECG Wave (No text!) ---
        tr_img = Image.new("RGBA", (tr_w, tr_h), (0, 0, 0, 0))
        d_tr = ImageDraw.Draw(tr_img)
        d_tr.rounded_rectangle([0, 0, tr_w - 1, tr_h - 1], radius=14, fill=(12, 16, 24, 175), outline=(col_main[0], col_main[1], col_main[2], 190), width=2)

        # Left side of TR panel: Animated Radar Circle (center 42, 42, radius 28)
        rcx, rcy, rr = 42, 42, 28
        d_tr.ellipse([rcx - rr, rcy - rr, rcx + rr, rcy + rr], fill=(18, 28, 40, 230), outline=(col_main[0], col_main[1], col_main[2], 210), width=2)
        d_tr.ellipse([rcx - rr // 2, rcy - rr // 2, rcx + rr // 2, rcy + rr // 2], outline=(col_main[0], col_main[1], col_main[2], 110), width=1)
        d_tr.line([(rcx - rr, rcy), (rcx + rr, rcy)], fill=(col_main[0], col_main[1], col_main[2], 90), width=1)
        d_tr.line([(rcx, rcy - rr), (rcx, rcy + rr)], fill=(col_main[0], col_main[1], col_main[2], 90), width=1)
        # Rotating radar hand
        ang = phase
        rx = int(rcx + rr * math.cos(ang))
        ry = int(rcy + rr * math.sin(ang))
        d_tr.line([(rcx, rcy), (rx, ry)], fill=(col_main[0], col_main[1], col_main[2], 255), width=3)
        # Blinking target blip inside radar when suspicion >= 0.4
        if susp >= 0.40:
            blip_a = int(140 + 115 * math.sin(phase * 3))
            d_tr.ellipse([rcx + 6, rcy - 14, rcx + 14, rcy - 6], fill=(255, 60, 70, blip_a))

        # Right side Top: Segmented Suspicion Meter Bar (x=86..320, y=16..34)
        bx0, by0, bx1, by1 = 86, 16, 320, 32
        n_segs = 12
        seg_w = (bx1 - bx0) // n_segs
        active_segs = int(round(susp * n_segs))
        for s_i in range(n_segs):
            sx0 = bx0 + s_i * seg_w + 1
            sx1 = sx0 + seg_w - 3
            if s_i < active_segs:
                if s_i < 4:
                    sc = (0, 230, 175, 235)
                elif s_i < 8:
                    sc = (255, 195, 40, 235)
                else:
                    sc = (255, 60, 75, 245)
                d_tr.rounded_rectangle([sx0, by0, sx1, by1], radius=3, fill=sc)
            else:
                d_tr.rounded_rectangle([sx0, by0, sx1, by1], radius=3, fill=(35, 45, 60, 190))

        # Right side Bottom: Animated ECG Heartbeat / Cortisol Wave (x=86..320, y=42..72)
        pts = []
        freq = 2.0 if susp < 0.7 else 3.5
        for ix in range(86, 320, 3):
            norm_x = (ix - 86) / (320 - 86)
            w_phase = (norm_x * freq * 2.0 * math.pi - phase * 2.0) % (2.0 * math.pi)
            # Sharp QRS ECG spike around w_phase == 3.0
            dist = abs(w_phase - 3.0)
            if dist < 0.22:
                val = math.cos((dist / 0.22) * (math.pi / 2.0)) * (14.0 if susp >= 0.7 else 10.0)
            elif 0.22 <= dist < 0.40:
                val = -5.0 * math.sin(((dist - 0.22) / 0.18) * math.pi)
            else:
                val = 1.5 * math.sin(w_phase)
            pts.append((ix, int(58 - val)))
        if len(pts) > 1:
            d_tr.line(pts, fill=(col_main[0], col_main[1], col_main[2], 240), width=2)

        tr_arr = np.array(tr_img, dtype=np.uint8)
        top_right_frames.append((tr_arr[:, :, :3], tr_arr[:, :, 3:4].astype(np.float32) / 255.0))

    return top_left_frames, top_right_frames, col_main


def apply_hud_inplace(frame: np.ndarray, tl_item, tr_item, is_pov: bool, col_main):
    """Fast in-place alpha blending of the small HUD patches + POV corner brackets."""
    # Top-left patch at (28, 24)
    tl_rgb, tl_a = tl_item
    th, tw, _ = tl_rgb.shape
    roi_tl = frame[24:24 + th, 28:28 + tw]
    frame[24:24 + th, 28:28 + tw] = (roi_tl * (1.0 - tl_a) + tl_rgb * tl_a).astype(np.uint8)

    # Top-right patch at (W - 28 - tw, 24)
    tr_rgb, tr_a = tr_item
    rh, rw, _ = tr_rgb.shape
    rx0 = W - 28 - rw
    roi_tr = frame[24:24 + rh, rx0:rx0 + rw]
    frame[24:24 + rh, rx0:rx0 + rw] = (roi_tr * (1.0 - tr_a) + tr_rgb * tr_a).astype(np.uint8)

    # Subtle POV viewfinder brackets at bottom-left and bottom-right on POV simulation scenes
    if is_pov:
        c = np.array(col_main, dtype=np.uint8)
        # Bottom-left L-bracket
        frame[H - 36:H - 32, 28:76] = c
        frame[H - 80:H - 32, 28:32] = c
        # Bottom-right L-bracket
        frame[H - 36:H - 32, W - 76:W - 28] = c
        frame[H - 80:H - 32, W - 32:W - 28] = c


def get_stage_idx(scene_num: int) -> int:
    if scene_num <= 3:
        return 0
    if scene_num == 94:
        return 10
    return (scene_num - 4) // 10 + 1


def load_zoom_lut(img_path: str, n_steps: int = 24):
    """
    Precompute 24 discrete calm micro-zoom steps (0.0% -> 1.2% zoom) for an image?
    Even faster and 8x lighter on RAM: pre-upscale the image ONCE by 1.25% to (1944, 1094),
    and during rendering simply slice a (1920, 1080) window out of it!
    Wait: slicing a (1920, 1080) crop from a pre-upscaled (1968, 1107) array takes 0.05 ms per frame!
    """
    im = Image.open(img_path).convert("RGB")
    up_w, up_h = 1968, 1107  # +2.5% margin for smooth pan/micro-zoom
    im_up = im.resize((up_w, up_h), Image.Resampling.LANCZOS)
    return np.array(im_up, dtype=np.uint8)


def crop_micro_zoom(up_arr: np.ndarray, progress: float, scene_num: int) -> np.ndarray:
    """
    Extract a (1080, 1920, 3) window from the (1107, 1968, 3) buffer with a smooth sinusoidal drift.
    """
    max_dx = 1968 - W  # 48 px
    max_dy = 1107 - H  # 27 px
    # Alternate pan direction smoothly between even and odd scenes
    if scene_num % 2 == 0:
        x0 = int(round(max_dx * progress))
        y0 = int(round(max_dy * (0.2 + 0.6 * progress)))
    else:
        x0 = int(round(max_dx * (1.0 - progress)))
        y0 = int(round(max_dy * (0.8 - 0.6 * progress)))
    return up_arr[y0:y0 + H, x0:x0 + W].copy()


def main():
    t0 = time.time()
    with open("output/long02_timeline_94_scenes.json", "r", encoding="utf-8") as f:
        timeline = json.load(f)

    assert len(timeline) == 94, f"Expected 94 scenes, got {len(timeline)}"
    total_sec = timeline[-1]["end"]
    total_frames = int(round(total_sec * FPS))
    print(f"Rendering Video Long #02: {len(timeline)} scenes, {total_sec:.2f}s ({total_frames} frames @ {FPS}fps) — NO BGM")

    # Precompute HUD animations for stages 0..10
    hud_cache = {}
    for s_idx in range(11):
        hud_cache[(s_idx, True)] = build_hud_frames(s_idx, True)
        hud_cache[(s_idx, False)] = build_hud_frames(s_idx, False)

    out_mp4 = "output/STICKMAN_long-02_pov-pejabat-korupsi-cuci-uang-miliaran_16x9.mp4"
    vo_path = "google_drive/VO_Master_Long02_94_Adegan_16x9.mp3"
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
        "-preset", "ultrafast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        out_mp4,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Convert scene boundaries to frame indices
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
        stage_idx = get_stage_idx(s_num)
        is_mascot = s_num in MASCOT_SCENES
        is_pov = not is_mascot
        tl_frames, tr_frames, col_main = hud_cache[(stage_idx, is_mascot)]

        for local_f in range(n_f):
            global_f = f_start + local_f
            prog = local_f / max(1, n_f - 1)
            frame = crop_micro_zoom(curr_up, prog, s_num)

            # Smooth 0.25s (15-frame) cross-dissolve into next scene at end of scene
            rem = (n_f - 1) - local_f
            if rem < CROSSFADE_FRAMES and idx + 1 < len(scene_frames):
                alpha = (CROSSFADE_FRAMES - rem) / float(CROSSFADE_FRAMES)
                # Smoothstep easing
                alpha = alpha * alpha * (3.0 - 2.0 * alpha)
                next_frame = crop_micro_zoom(next_up, 0.0, s_num + 1)
                frame = (frame.astype(np.float32) * (1.0 - alpha) + next_frame.astype(np.float32) * alpha).astype(np.uint8)

            # Apply 60fps Non-Subtitle Motion Graphics & POV HUD
            loop_i = global_f % 120
            apply_hud_inplace(frame, tl_frames[loop_i], tr_frames[loop_i], is_pov, col_main)

            proc.stdin.write(frame.tobytes())
            frames_written += 1

        # Advance scene buffers
        if idx + 1 < len(scene_frames):
            curr_up = next_up
            if idx + 2 < len(scene_frames):
                next_up = load_zoom_lut(scene_frames[idx + 2][1])

        if (idx + 1) % 10 == 0 or (idx + 1) == len(scene_frames):
            el = time.time() - t0
            fps_rate = frames_written / max(0.1, el)
            print(f"  Rendered {idx + 1}/94 scenes ({frames_written}/{total_frames} frames, {fps_rate:.1f} fps, {el:.1f}s elapsed)")

    proc.stdin.close()
    ret = proc.wait()
    assert ret == 0, f"FFmpeg exited with {ret}"
    sz_mb = os.path.getsize(out_mp4) / (1024 * 1024)
    print(f"SUCCESS: {out_mp4} ({sz_mb:.2f} MB) in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
