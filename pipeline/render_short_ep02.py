#!/usr/bin/env python3
"""Render YouTube Short #2 — 'Kalau Matahari Mati' (< 60 detik, 9:16, TANPA subtitle, TANPA musik).

Gaya visual & editing mengacu pada 'Mr Sticky' (Las PEORES TORTURAS de la Historia de la Humanidad):
  - Karakter: Stickman klasik polos TANPA pakaian, kepala bulat putih bersih, HANYA memakai kacamata hitam.
  - Visual: 10 adegan 2D flat vector kartun eye-level + balon callout / papan tulis edukatif yang
    100% sesuai kalimat narator dan langsung mudah dibayangkan penonton.
  - Editing: 20 beat kamera dinamis (2 beat per shot: establishing + fokus callout/detail, ~2,8 detik/beat),
    warna cerah bersih TANPA vignette gelap, TANPA grain kasar, potongan tegas (crisp cuts).
  - Audio: Durasi < 60,0 detik (57,47 detik), TANPA subtitle, TANPA musik — hanya Voiceover (-14 LUFS)
    + Foley & Sound Effects fisik (pop callout, klik sakelar, ketukan papan tulis, angin, es retak,
    gelembung laut, api, detak jantung, jam).
"""
import os
import re
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
IMG = os.path.join(ROOT, "assets/images")
AUD = os.path.join(ROOT, "assets/audio")
WORK = os.path.join(ROOT, "work/short02")
CLIPS = os.path.join(WORK, "clips")
OUT = os.path.join(ROOT, "output")

W, H, FPS = 1080, 1920, 30
SR = 48000

# 10 shot:
# (image_file, audio_file, slice_ranges, split_ratio, beatA_cam, beatB_cam, sfx_preset)
# cam tuple: (z0, z1, cx, cy) where cx, cy in [0..1] are the normalized center point of the crop window
SHOTS = [
    # S01: Siang terang & jalan santai makan es krim -> fokus balon callout Matahari dicabut stekernya
    ("short02_s01.jpg", "s02_01.mp3", [(0.28, 9.95)], 0.54,
     (1.00, 1.05, 0.50, 0.48), (1.05, 1.00, 0.50, 0.50), "hook_clock_blackout"),

    # S02: Stickman menunjuk papan tulis -> zoom lembut ke diagram jarak Matahari-Bumi & stopwatch 8m20d
    ("short02_s02.jpg", "s02_02.mp3", [(0.24, 5.58)], 0.47,
     (1.00, 1.04, 0.50, 0.50), (1.04, 1.08, 0.52, 0.48), "whiteboard_tap_photon"),

    # S03: Langit klik gelap & stickman berpegangan tiang lampu -> callout Bumi lepas orbit lurus
    ("short02_s03.jpg", "s02_03.mp3", [(3.62, 11.60)], 0.50,
     (1.00, 1.05, 0.50, 0.50), (1.05, 1.00, 0.50, 0.46), "cable_snap_orbit"),

    # S04: Hari ke-7 suhu anjlok 0°C (termometer membeku) -> stickman menggigil di dekat tong api
    ("short02_s04.jpg", "s02_04.mp3", [(0.25, 5.20)], 0.48,
     (1.00, 1.05, 0.50, 0.48), (1.05, 1.01, 0.50, 0.52), "arctic_wind_fire"),

    # S05: Dermaga & pohon mati tanpa fotosintesis -> balon callout fitoplankton mati di laut
    ("short02_s05.jpg", "s02_05.mp3", [(0.20, 7.22)], 0.44,
     (1.00, 1.04, 0.50, 0.48), (1.04, 1.07, 0.52, 0.52), "underwater_plankton_pop"),

    # S06: Tahun 1 samudra membeku -70°C di atas -> ventilasi vulkanik & kepiting laut dalam
    ("short02_s06.jpg", "s02_06.mp3", [(0.22, 6.58)], 0.48,
     (1.05, 1.02, 0.50, 0.42), (1.02, 1.06, 0.50, 0.58), "glacier_crack_vent"),

    # S07: Permukaan beku -> bunker bawah tanah hangat dengan radiator panas bumi & lampu hidroponik
    ("short02_s07.jpg", "s02_07.mp3", [(0.26, 7.75)], 0.50,
     (1.00, 1.05, 0.50, 0.48), (1.05, 1.08, 0.52, 0.54), "bunker_steam_growlamp"),

    # S08: Matahari bengkak jadi Raksasa Merah menelan planet -> stickman keringatan & payung terbakar di laut mendidih
    ("short02_s08.jpg", "s02_08.mp3", [(0.26, 2.60), (6.18, 11.80)], 0.50,
     (1.05, 1.02, 0.50, 0.44), (1.02, 1.06, 0.50, 0.54), "red_giant_boil"),

    # S09: Nebula cincin warna-warni -> balon callout perbandingan Katai Putih seukuran Bumi
    ("short02_s09.jpg", "s02_09.mp3", [(0.62, 10.45)], 0.46,
     (1.00, 1.04, 0.50, 0.48), (1.04, 1.08, 0.52, 0.50), "nebula_heartbeat"),

    # S10: Callout tulang & sel darah dari debu bintang -> taman cerah & Matahari bersinar
    ("short02_s10.jpg", "s02_10.mp3", [(0.25, 12.00)], 0.53,
     (1.05, 1.08, 0.52, 0.50), (1.06, 1.00, 0.50, 0.50), "stardust_sunny_loop"),
]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg gagal:\n{r.stderr[-1200:]}")
    return r


def dur(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        raise RuntimeError(f"durasi tidak terbaca: {path}")
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


def build_vo_segments():
    """Potong & rapikan 10 segmen VO dengan tempo Shorts yang tegas (< 60 detik total)."""
    os.makedirs(WORK, exist_ok=True)
    seg_info = []
    for idx, (img_f, aud_f, parts, split_r, cam_a, cam_b, sfx_kind) in enumerate(SHOTS, 1):
        src = os.path.join(AUD, aud_f)
        dst = os.path.join(WORK, f"vo_{idx:02d}.wav")
        if len(parts) == 1:
            a, b = parts[0]
            fc = (f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                  f"silenceremove=stop_periods=-1:stop_silence=0.09:stop_threshold=-36dB,"
                  f"atempo=1.24,afade=t=in:st=0:d=0.025,"
                  f"apad=pad_dur=0.10[a]")
        else:
            (a1, b1), (a2, b2) = parts
            fc = (f"[0:a]atrim={a1}:{b1},asetpts=PTS-STARTPTS[p1];"
                  f"[0:a]atrim={a2}:{b2},asetpts=PTS-STARTPTS[p2];"
                  f"[p1][p2]concat=n=2:v=0:a=1,"
                  f"silenceremove=stop_periods=-1:stop_silence=0.09:stop_threshold=-36dB,"
                  f"atempo=1.24,afade=t=in:st=0:d=0.025,"
                  f"apad=pad_dur=0.10[a]")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
             "-filter_complex", fc, "-map", "[a]", "-ar", str(SR), "-ac", "2",
             "-c:a", "pcm_s16le", dst])
        d = dur(dst)
        seg_info.append({
            "idx": idx,
            "img": os.path.join(IMG, img_f),
            "vo": dst,
            "dur": round(d, 3),
            "split_r": split_r,
            "cam_a": cam_a,
            "cam_b": cam_b,
            "sfx": sfx_kind,
        })
    return seg_info


# ----------------- SINTESIS FOLEY & SOUND EFFECTS FISIK (GAYA MR STICKY) -----------------

def _lp_noise(rng, n, alpha=0.06):
    w = rng.standard_normal(n).astype(np.float64)
    out = np.zeros_like(w)
    acc = 0.0
    for i in range(n):
        acc += alpha * (w[i] - acc)
        out[i] = acc
    return out


def _bp_whoosh(rng, dur_s, f0=180.0, f1=620.0, pan_dir=1):
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, endpoint=False)
    env = np.sin(np.pi * t / dur_s) ** 2.2
    raw = _lp_noise(rng, n, alpha=0.08) - _lp_noise(rng, n, alpha=0.015)
    mod = 0.65 + 0.35 * np.sin(2 * np.pi * np.linspace(f0, f1, n) * t * 0.02)
    sig = raw * env * mod
    pan = np.linspace(0.25, 0.75, n) if pan_dir > 0 else np.linspace(0.75, 0.25, n)
    return np.column_stack([sig * (1 - pan), sig * pan])


def _callout_pop(rng):
    """Bunyi 'pop' fisik lembut khas balon callout / zoom-in Mr Sticky (non-musikal)."""
    n = int(0.065 * SR)
    t = np.linspace(0, 0.065, n, endpoint=False)
    freq = 280.0 + 520.0 * (1.0 - np.exp(-t * 45.0))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    pop = np.sin(phase) * np.exp(-t * 42.0) * 0.45
    thump = np.exp(-t * 95.0) * rng.standard_normal(n) * 0.18
    mono = (pop + thump) * 0.55
    return np.column_stack([mono, mono])


def _wood_tap(rng):
    """Ketukan tongkat kayu di papan tulis."""
    n = int(0.04 * SR)
    t = np.linspace(0, 0.04, n, endpoint=False)
    tap = np.exp(-t * 140.0) * (0.6 * np.sin(2 * np.pi * 1150.0 * t) + 0.5 * rng.standard_normal(n))
    mono = tap * 0.45
    return np.column_stack([mono * 0.9, mono * 1.1])


def _add_at(buf, start_s, clip_st):
    i0 = max(0, int(round(start_s * SR)))
    i1 = min(len(buf), i0 + len(clip_st))
    if i1 > i0:
        buf[i0:i1] += clip_st[: i1 - i0]


def _clock_tick(rng, high=True):
    n = int(0.045 * SR)
    t = np.linspace(0, 0.045, n, endpoint=False)
    f = 2400.0 if high else 1750.0
    click = np.exp(-t * 180.0) * (0.7 * np.sin(2 * np.pi * f * t) + 0.5 * rng.standard_normal(n))
    body = np.exp(-t * 65.0) * np.sin(2 * np.pi * 420.0 * t) * 0.35
    mono = (click + body) * 0.42
    return np.column_stack([mono * 0.95, mono * 1.05])


def _breaker_blackout(rng):
    n = int(0.95 * SR)
    t = np.linspace(0, 0.95, n, endpoint=False)
    clack1 = np.exp(-t * 95.0) * rng.standard_normal(n) * 0.9
    t2 = np.maximum(0.0, t - 0.055)
    clack2 = (t >= 0.055) * np.exp(-t2 * 70.0) * rng.standard_normal(n) * 0.75
    freq = 28.0 + 87.0 * np.exp(-t * 4.5)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(phase) * np.exp(-t * 3.2) * 0.85
    mono = (clack1 + clack2 + sub) * 0.55
    return np.column_stack([mono, mono])


def _cable_snap_boom(rng):
    n = int(1.35 * SR)
    t = np.linspace(0, 1.35, n, endpoint=False)
    creak = (t < 0.35) * np.sin(2 * np.pi * (190 + 140 * t) * t) * (t / 0.35) * 0.25
    ts = np.maximum(0.0, t - 0.35)
    whip = (t >= 0.35) * np.exp(-ts * 28.0) * (
        0.8 * rng.standard_normal(n) + 0.6 * np.sin(2 * np.pi * (980 * np.exp(-ts * 9.0)) * ts)
    )
    boom = (t >= 0.35) * np.exp(-ts * 2.8) * np.sin(2 * np.pi * 44.0 * ts) * 0.75
    mono = (creak + whip + boom) * 0.52
    return np.column_stack([mono * 1.05, mono * 0.95])


def _ice_crack(rng, dur_s=1.1):
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, endpoint=False)
    out = np.zeros(n)
    for offset, amp in [(0.02, 0.9), (0.14, 0.65), (0.31, 0.8), (0.48, 0.5)]:
        to = np.maximum(0.0, t - offset)
        mask = (t >= offset).astype(float)
        burst = mask * np.exp(-to * 55.0) * rng.standard_normal(n) * amp
        ping = mask * np.exp(-to * 38.0) * np.sin(2 * np.pi * (1650 - 700 * to) * to) * (amp * 0.5)
        out += burst + ping
    rumble = _lp_noise(rng, n, alpha=0.012) * np.exp(-t * 1.8) * 1.6
    mono = (out + rumble) * 0.48
    return np.column_stack([mono * 0.92, mono * 1.08])


def _heartbeat_pair(rng):
    n = int(0.75 * SR)
    t = np.linspace(0, 0.75, n, endpoint=False)
    lub = np.exp(-t * 18.0) * np.sin(2 * np.pi * 48.0 * t) * 0.85
    td = np.maximum(0.0, t - 0.24)
    dub = (t >= 0.24) * np.exp(-td * 22.0) * np.sin(2 * np.pi * 58.0 * td) * 0.65
    mono = (lub + dub) * 0.60
    return np.column_stack([mono, mono])


def build_sfx_track(seg_info, total_dur):
    """Bangun track Foley & SFX fisik sepanjang total_dur (TANPA musik)."""
    rng = np.random.default_rng(20261024)
    total_n = int(round(total_dur * SR)) + SR
    buf = np.zeros((total_n, 2), dtype=np.float64)

    # Room tone sangat halus (-40 dB)
    base_air = _lp_noise(rng, total_n, alpha=0.008) * 0.018
    buf[:, 0] += base_air
    buf[:, 1] += _lp_noise(rng, total_n, alpha=0.008) * 0.018

    cursor = 0.0
    for seg in seg_info:
        d = seg["dur"]
        split_t = cursor + d * seg["split_r"]
        kind = seg["sfx"]
        idx = seg["idx"]

        # Transisi whoosh fisik di setiap pergantian shot + pop halus saat ganti beat tengah shot
        if idx > 1:
            _add_at(buf, cursor - 0.14, _bp_whoosh(rng, 0.28, pan_dir=(1 if idx % 2 == 0 else -1)) * 0.36)
        _add_at(buf, split_t - 0.03, _callout_pop(rng) * 0.65)

        if kind == "hook_clock_blackout":
            _add_at(buf, cursor + 0.08, _callout_pop(rng) * 0.80)
            for k in range(6):
                _add_at(buf, cursor + k * 0.24, _clock_tick(rng, high=(k % 2 == 0)) * 0.85)
            _add_at(buf, cursor + 1.50, _breaker_blackout(rng) * 0.90)
            for k in range(6):
                _add_at(buf, cursor + 2.85 + k * 0.36, _wood_tap(rng) * 0.38)

        elif kind == "whiteboard_tap_photon":
            _add_at(buf, cursor + 0.25, _wood_tap(rng) * 0.75)
            _add_at(buf, cursor + 0.45, _wood_tap(rng) * 0.65)
            _add_at(buf, cursor + 1.40, _bp_whoosh(rng, min(d - 1.5, 3.4), f0=240, f1=880, pan_dir=1) * 0.42)
            for k in range(6):
                _add_at(buf, split_t + 0.15 + k * 0.38, _clock_tick(rng, high=(k % 2 == 0)) * 0.48)

        elif kind == "cable_snap_orbit":
            _add_at(buf, cursor + 2.05, _breaker_blackout(rng) * 0.75)
            _add_at(buf, split_t + 0.15, _cable_snap_boom(rng) * 0.92)
            _add_at(buf, split_t + 1.20, _bp_whoosh(rng, max(1.2, d - (split_t - cursor) - 1.2), f0=120, f1=420, pan_dir=-1) * 0.45)

        elif kind == "arctic_wind_fire":
            wind = _bp_whoosh(rng, d, f0=160, f1=520, pan_dir=1) * 0.46
            _add_at(buf, cursor, wind)
            _add_at(buf, cursor + 0.95, _ice_crack(rng, 0.85) * 0.75)
            for k in range(8):
                _add_at(buf, split_t + 0.2 + k * 0.26, _clock_tick(rng, high=True) * 0.28)

        elif kind == "underwater_plankton_pop":
            n_seg = int(d * SR)
            sub_water = _lp_noise(rng, n_seg, alpha=0.005) * 0.16
            _add_at(buf, cursor, np.column_stack([sub_water, sub_water]))
            for k in range(5):
                _add_at(buf, split_t + 0.20 + k * 0.55, _callout_pop(rng) * 0.50)

        elif kind == "glacier_crack_vent":
            _add_at(buf, cursor + 0.25, _ice_crack(rng, 1.35) * 0.92)
            _add_at(buf, split_t + 0.20, _ice_crack(rng, 1.00) * 0.65)
            _add_at(buf, cursor, _bp_whoosh(rng, d, f0=140, f1=380, pan_dir=-1) * 0.35)

        elif kind == "bunker_steam_growlamp":
            n_seg = int(d * SR)
            steam = (_lp_noise(rng, n_seg, alpha=0.14) - _lp_noise(rng, n_seg, alpha=0.03)) * 0.08
            _add_at(buf, cursor, np.column_stack([steam, steam]))
            for k in range(4):
                _add_at(buf, cursor + 0.7 + k * 1.15, _clock_tick(rng, high=False) * 0.55)

        elif kind == "red_giant_boil":
            n_seg = int(d * SR)
            t = np.linspace(0, d, n_seg, endpoint=False)
            roar = _lp_noise(rng, n_seg, alpha=0.009) * np.sin(np.pi * t / d) * 0.32
            hiss = (_lp_noise(rng, n_seg, alpha=0.18) - _lp_noise(rng, n_seg, alpha=0.04)) * 0.09
            _add_at(buf, cursor, np.column_stack([roar + hiss, roar * 0.95 + hiss]))
            for k in range(6):
                _add_at(buf, split_t + 0.15 + k * 0.42, _callout_pop(rng) * 0.45)

        elif kind == "nebula_heartbeat":
            _add_at(buf, cursor, _bp_whoosh(rng, d * 0.85, f0=110, f1=290, pan_dir=1) * 0.32)
            for k in range(4):
                _add_at(buf, split_t + 0.10 + k * 0.62, _heartbeat_pair(rng) * 0.85)

        elif kind == "stardust_sunny_loop":
            _add_at(buf, cursor + 0.15, _callout_pop(rng) * 0.75)
            _add_at(buf, cursor, _bp_whoosh(rng, d * 0.7, f0=150, f1=340, pan_dir=-1) * 0.25)
            t_start = max(cursor + d - 2.2, cursor + 1.0)
            k = 0
            while t_start + k * 0.28 < cursor + d - 0.05:
                _add_at(buf, t_start + k * 0.28, _clock_tick(rng, high=(k % 2 == 0)) * 0.75)
                k += 1

        cursor += d

    buf = buf[: int(round(total_dur * SR))]
    peak = np.max(np.abs(buf))
    if peak > 0.92:
        buf = buf * (0.92 / peak)
    pcm = np.clip(buf * 32767.0, -32768, 32767).astype(np.int16)

    sfx_path = os.path.join(WORK, "sfx_short02.wav")
    with wave.open(sfx_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return sfx_path


def _subclip_zoompan(img_path, out_path, dur_s, cam):
    """Render satu sub-beat (Beat A atau Beat B) dengan warna jernih gaya Mr Sticky (tanpa vignette/noise/fade gelap)."""
    z0, z1, cx, cy = cam
    frames = max(int(round(dur_s * FPS)), 2)
    span = max(frames - 1, 1)
    z_expr = f"{z0:.4f}+({z1 - z0:.4f})*on/{span}"
    x_expr = f"clip({cx:.3f}*iw-(iw/zoom/2),0,iw-iw/zoom)"
    y_expr = f"clip({cy:.3f}*ih-(ih/zoom/2),0,ih-ih/zoom)"
    fc = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
          f"crop={W*2}:{H*2},setsar=1,"
          f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.03:saturation=1.06[v]")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", img_path,
         "-filter_complex", fc, "-map", "[v]", "-r", str(FPS),
         "-t", f"{dur_s:.3f}", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", out_path])


def build_clip(seg):
    """Render 1 shot yang terdiri dari 2 beat kamera dinamis (Beat A -> Beat B) sesuai narasi."""
    idx = seg["idx"]
    d = seg["dur"]
    total_frames = max(int(round(d * FPS)), 4)
    frames_a = max(int(round(total_frames * seg["split_r"])), 2)
    frames_b = max(total_frames - frames_a, 2)
    dur_a = frames_a / FPS
    dur_b = frames_b / FPS

    part_a = os.path.join(CLIPS, f"s{idx:02d}_a.mp4")
    part_b = os.path.join(CLIPS, f"s{idx:02d}_b.mp4")
    _subclip_zoompan(seg["img"], part_a, dur_a, seg["cam_a"])
    _subclip_zoompan(seg["img"], part_b, dur_b, seg["cam_b"])

    dst = os.path.join(CLIPS, f"s{idx:02d}.mp4")
    pair_list = os.path.join(CLIPS, f"s{idx:02d}_pair.txt")
    with open(pair_list, "w") as f:
        f.write(f"file '{part_a}'\nfile '{part_b}'\n")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", pair_list, "-c", "copy", dst])
    return dst


def build_thumbnail_and_char_sheets():
    """Bangun ulang thumbnail Short #2 dan lembar karakter baku dengan Stickman polos berkacamata hitam."""
    # 1. Thumbnail Short #2 (1080x1920) dari short02_s01.jpg + short02_s08.jpg
    s01 = Image.open(os.path.join(IMG, "short02_s01.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    draw = ImageDraw.Draw(s01)
    # Banner judul kuning-hitam kontras tinggi di bagian bawah (aman untuk thumbnail Shorts)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f_big = ImageFont.truetype(font_path, 86)
    f_sub = ImageFont.truetype(font_path, 52)
    draw.rounded_rectangle((54, 1500, 1026, 1840), radius=28, fill=(16, 18, 24), outline=(255, 214, 64), width=8)
    draw.text((540, 1605), "8 MENIT 20 DETIK", font=f_big, fill=(255, 214, 64), anchor="mm")
    draw.text((540, 1735), "KALAU MATAHARI PADAM", font=f_sub, fill=(255, 255, 255), anchor="mm")
    thumb_path = os.path.join(OUT, "thumbnail_short_ep02.jpg")
    s01.save(thumb_path, quality=95)

    # 2. Contoh adegan 9:16 karakter baru (tanpa pakaian, hanya kacamata hitam)
    os.makedirs(os.path.join(IMG, "char"), exist_ok=True)
    s02 = Image.open(os.path.join(IMG, "short02_s02.jpg")).convert("RGB").resize((W, H), Image.LANCZOS)
    s02.save(os.path.join(IMG, "char/karakter-contoh-adegan-9x16.jpg"), quality=94)

    # 3. Model sheet 5 pose dari 5 adegan terbaik karakter polos berkacamata hitam
    sheet_w, sheet_h = 1800, 1000
    sheet = Image.new("RGB", (sheet_w, sheet_h), (245, 242, 235))
    sd = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype(font_path, 40)
    f_lbl = ImageFont.truetype(font_path, 24)
    sd.text((900, 48), "KARAKTER BAKU — STICKMAN POLOS BERKACAMATA HITAM (GAYA MR STICKY)", font=f_title, fill=(20, 20, 20), anchor="mm")
    poses = [
        ("short02_s01.jpg", "1. Santai / Jalan"),
        ("short02_s02.jpg", "2. Edukasi / Papan Tulis"),
        ("short02_s03.jpg", "3. Terhempas / Darurat"),
        ("short02_s04.jpg", "4. Menggigil / Dingin"),
        ("short02_s08.jpg", "5. Kepanasan Ekstrem"),
    ]
    cw, ch = 320, 580
    for i, (fn, lbl) in enumerate(poses):
        im = Image.open(os.path.join(IMG, fn)).convert("RGB").resize((cw, ch), Image.LANCZOS)
        x0 = 50 + i * 345
        y0 = 110
        sheet.paste(im, (x0, y0))
        sd.rectangle((x0, y0, x0 + cw, y0 + ch), outline=(20, 20, 20), width=4)
        sd.text((x0 + cw // 2, y0 + ch + 32), lbl, font=f_lbl, fill=(20, 20, 20), anchor="mm")
    sd.text((900, 820), "Aturan mutlak: Kepala bulat putih bersih + kacamata hitam kotak. Badan/tangan/kaki murni garis hitam TANPA pakaian.", font=f_lbl, fill=(40, 40, 40), anchor="mm")
    sheet.save(os.path.join(IMG, "char/character-sheet-v2.jpg"), quality=94)


def main():
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    print("1/5 Memotong & menyusun 10 segmen Voiceover (< 60 detik)...")
    seg_info = build_vo_segments()
    total_dur = sum(s["dur"] for s in seg_info)
    print(f"    Total durasi 10 shot: {total_dur:.2f}s (batas YouTube Shorts: 60.00s)")
    assert total_dur < 59.5, f"Durasi terlalu panjang ({total_dur:.2f}s >= 59.5s)!"

    vo_list = os.path.join(WORK, "vo_list.txt")
    with open(vo_list, "w") as f:
        for s in seg_info:
            f.write(f"file '{s['vo']}'\n")
    vo_concat = os.path.join(WORK, "vo_master.wav")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vo_list, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", vo_concat])

    print("2/5 Menyintesis efek suara fisik & foley multi-lapis gaya Mr Sticky (TANPA musik)...")
    sfx_wav = build_sfx_track(seg_info, total_dur)

    print("3/5 Merender 10 shot (20 beat kamera dinamis, TANPA subtitle, warna cerah bersih)...")
    clip_paths = []
    for s in seg_info:
        print(f"    [{s['idx']:02d}/10] {os.path.basename(s['img'])}  {s['dur']:5.2f}s  sfx={s['sfx']}")
        clip_paths.append(build_clip(s))

    vlist = os.path.join(WORK, "v_list.txt")
    with open(vlist, "w") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")
    vonly = os.path.join(WORK, "video_only.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vlist, "-c", "copy", vonly])

    print("4/5 Mastering audio (VO -14 LUFS + Foley SFX, 0% musik) & muxing MP4...")
    final_mp4 = os.path.join(OUT, "STICKMAN_short-02_kalau-matahari-mati_9x16.mp4")
    af = (f"[1:a]highpass=f=80,lowpass=f=14500,"
          f"loudnorm=I=-14:TP=-1.5:LRA=9[vo];"
          f"[2:a]volume=0.55[sfx];"
          f"[vo][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
          f"alimiter=limit=0.95[a]")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", vonly, "-i", vo_concat, "-i", sfx_wav,
         "-filter_complex", af, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
         "-t", f"{total_dur:.3f}", "-movflags", "+faststart", final_mp4])

    print("5/5 Memperbarui thumbnail Short #2 & character sheet baku...")
    build_thumbnail_and_char_sheets()

    final_d = dur(final_mp4)
    print(f"\nSELESAI: {final_mp4} ({final_d:.2f}s)")


if __name__ == "__main__":
    main()
