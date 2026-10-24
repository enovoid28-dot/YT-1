#!/usr/bin/env python3
"""Render YouTube Short #2 — 'Kalau Matahari Mati' (< 60 detik, 9:16, TANPA subtitle, TANPA musik).

Fitur utama:
  - Durasi wajib di bawah standar maksimal YouTube Shorts klasik (< 60,0 detik, ~55–57 detik)
  - 10 ilustrasi 9:16 Ligne-Claire / Kurzgesagt masterpiece dengan skala Stickman kecil (15–18%)
  - TIDAK ADA subtitle / teks di layar sama sekali (murni visual + sinematografi)
  - TIDAK ADA musik sama sekali — hanya Voiceover (-14 LUFS) + Foley & Sound Effects fisik
    multi-lapis yang disintesis presisi per shot.
"""
import os
import re
import wave
import subprocess
import numpy as np
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

# 10 shot: (image_file, audio_file, slice_ranges, camera_move, sfx_preset)
SHOTS = [
    ("short02_s01.jpg", "s02_01.mp3", [(0.28, 9.95)],                "in",   "hook_clock_blackout"),
    ("short02_s02.jpg", "s02_02.mp3", [(0.24, 5.58)],                "down", "photon_beam_whoosh"),
    ("short02_s03.jpg", "s02_03.mp3", [(3.62, 11.60)],               "out",  "cable_snap_orbit"),
    ("short02_s04.jpg", "s02_04.mp3", [(0.25, 5.20)],                "in",   "arctic_wind_frost"),
    ("short02_s05.jpg", "s02_05.mp3", [(0.20, 7.22)],                "down", "underwater_sonar"),
    ("short02_s06.jpg", "s02_06.mp3", [(0.22, 6.58)],                "out",  "glacier_crack_rumble"),
    ("short02_s07.jpg", "s02_07.mp3", [(0.26, 7.75)],                "down", "bunker_steam_turbine"),
    ("short02_s08.jpg", "s02_08.mp3", [(0.26, 2.60), (6.18, 11.80)], "up",   "red_giant_seismic"),
    ("short02_s09.jpg", "s02_09.mp3", [(0.62, 10.45)],               "out",  "nebula_heartbeat"),
    ("short02_s10.jpg", "s02_10.mp3", [(0.25, 12.00)],               "in",   "twilight_loop_ticks"),
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
    for idx, (img_f, aud_f, parts, move, sfx_kind) in enumerate(SHOTS, 1):
        src = os.path.join(AUD, aud_f)
        dst = os.path.join(WORK, f"vo_{idx:02d}.wav")
        if len(parts) == 1:
            a, b = parts[0]
            fc = (f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,"
                  f"silenceremove=stop_periods=-1:stop_silence=0.09:stop_threshold=-36dB,"
                  f"atempo=1.24,afade=t=in:st=0:d=0.025,afade=t=out:st=0:d=0.02,"
                  f"apad=pad_dur=0.10[a]")
        else:
            (a1, b1), (a2, b2) = parts
            fc = (f"[0:a]atrim={a1}:{b1},asetpts=PTS-STARTPTS[p1];"
                  f"[0:a]atrim={a2}:{b2},asetpts=PTS-STARTPTS[p2];"
                  f"[p1][p2]concat=n=2:v=0:a=1,"
                  f"silenceremove=stop_periods=-1:stop_silence=0.09:stop_threshold=-36dB,"
                  f"atempo=1.24,afade=t=in:st=0:d=0.025,"
                  f"apad=pad_dur=0.10[a]")
        # Catatan: jangan afade=out di st=0 pada kalimat tunggal
        fc = fc.replace(",afade=t=out:st=0:d=0.02", "")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
             "-filter_complex", fc, "-map", "[a]", "-ar", str(SR), "-ac", "2",
             "-c:a", "pcm_s16le", dst])
        d = dur(dst)
        seg_info.append({
            "idx": idx,
            "img": os.path.join(IMG, img_f),
            "vo": dst,
            "dur": round(d, 3),
            "move": move,
            "sfx": sfx_kind,
        })
    return seg_info


# ----------------- SINTESIS FOLEY & SOUND EFFECTS FISIK -----------------

def _lp_noise(rng, n, alpha=0.06):
    """Derau terfilter low-pass sederhana (tanpa nada musik)."""
    w = rng.standard_normal(n).astype(np.float64)
    out = np.zeros_like(w)
    acc = 0.0
    for i in range(n):
        acc += alpha * (w[i] - acc)
        out[i] = acc
    return out


def _bp_whoosh(rng, dur_s, f0=180.0, f1=620.0, pan_dir=1):
    """Efek suara hembusan udara / transisi kamera fisik (stereo pan)."""
    n = int(dur_s * SR)
    t = np.linspace(0, dur_s, n, endpoint=False)
    env = np.sin(np.pi * t / dur_s) ** 2.2
    raw = _lp_noise(rng, n, alpha=0.08) - _lp_noise(rng, n, alpha=0.015)
    mod = 0.65 + 0.35 * np.sin(2 * np.pi * np.linspace(f0, f1, n) * t * 0.02)
    sig = raw * env * mod
    pan = np.linspace(0.25, 0.75, n) if pan_dir > 0 else np.linspace(0.75, 0.25, n)
    return np.column_stack([sig * (1 - pan), sig * pan])


def _add_at(buf, start_s, clip_st):
    """Tempel sinyal stereo clip_st ke buf mulai start_s."""
    i0 = max(0, int(round(start_s * SR)))
    i1 = min(len(buf), i0 + len(clip_st))
    if i1 > i0:
        buf[i0:i1] += clip_st[: i1 - i0]


def _clock_tick(rng, high=True):
    """Satu klik mekanik jam saku / menara jam (non-musikal, transien tajam)."""
    n = int(0.045 * SR)
    t = np.linspace(0, 0.045, n, endpoint=False)
    f = 2400.0 if high else 1750.0
    click = np.exp(-t * 180.0) * (0.7 * np.sin(2 * np.pi * f * t) + 0.5 * rng.standard_normal(n))
    body = np.exp(-t * 65.0) * np.sin(2 * np.pi * 420.0 * t) * 0.35
    mono = (click + body) * 0.42
    return np.column_stack([mono * 0.95, mono * 1.05])


def _breaker_blackout(rng):
    """Bunyi sakelar gardu raksasa KLAK + sub-drop vakum saat Matahari padam."""
    n = int(0.95 * SR)
    t = np.linspace(0, 0.95, n, endpoint=False)
    # Transien logam KLAK di awal + +0.06s
    clack1 = np.exp(-t * 95.0) * rng.standard_normal(n) * 0.9
    t2 = np.maximum(0.0, t - 0.055)
    clack2 = (t >= 0.055) * np.exp(-t2 * 70.0) * rng.standard_normal(n) * 0.75
    # Vacuum sub drop 115 Hz -> 28 Hz (fisik, bukan musik)
    freq = 28.0 + 87.0 * np.exp(-t * 4.5)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    sub = np.sin(phase) * np.exp(-t * 3.2) * 0.85
    mono = (clack1 + clack2 + sub) * 0.55
    return np.column_stack([mono, mono])


def _cable_snap_boom(rng):
    """Bunyi kabel baja gravitasi tegang lalu PUTUS (SNAP + dentuman rendah)."""
    n = int(1.35 * SR)
    t = np.linspace(0, 1.35, n, endpoint=False)
    # Derit tegangan awal 0..0.35s
    creak = (t < 0.35) * np.sin(2 * np.pi * (190 + 140 * t) * t) * (t / 0.35) * 0.25
    # Cambukan baja putus di t=0.35s
    ts = np.maximum(0.0, t - 0.35)
    whip = (t >= 0.35) * np.exp(-ts * 28.0) * (
        0.8 * rng.standard_normal(n) + 0.6 * np.sin(2 * np.pi * (980 * np.exp(-ts * 9.0)) * ts)
    )
    # Gemuruh lepas orbit
    boom = (t >= 0.35) * np.exp(-ts * 2.8) * np.sin(2 * np.pi * 44.0 * ts) * 0.75
    mono = (creak + whip + boom) * 0.52
    return np.column_stack([mono * 1.05, mono * 0.95])


def _ice_crack(rng, dur_s=1.1):
    """Bunyi retakan es / kaca membeku tajam diikuti gemuruh gletser."""
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
    """Satu pasang detak jantung manusia fisik (lub-dub) di ruang hampa."""
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

    # 1) Room tone / atmosfer fisik sangat halus (-38 dB) agar tidak mati hampa
    base_air = _lp_noise(rng, total_n, alpha=0.008) * 0.022
    buf[:, 0] += base_air
    buf[:, 1] += _lp_noise(rng, total_n, alpha=0.008) * 0.022

    cursor = 0.0
    for seg in seg_info:
        d = seg["dur"]
        kind = seg["sfx"]
        idx = seg["idx"]

        # Transisi whoosh fisik halus di setiap pergantian shot (kecuali shot 1)
        if idx > 1:
            _add_at(buf, cursor - 0.16, _bp_whoosh(rng, 0.34, pan_dir=(1 if idx % 2 == 0 else -1)) * 0.38)

        if kind == "hook_clock_blackout":
            # Detak jam mekanik cepat di 0..1.5s -> sakelar padam di 1.55s -> detak pelan kembali
            for k in range(6):
                _add_at(buf, cursor + k * 0.24, _clock_tick(rng, high=(k % 2 == 0)) * 0.85)
            _add_at(buf, cursor + 1.50, _breaker_blackout(rng) * 0.90)
            for k in range(8):
                _add_at(buf, cursor + 2.85 + k * 0.48, _clock_tick(rng, high=(k % 2 == 0)) * 0.42)

        elif kind == "photon_beam_whoosh":
            # Desau berkas foton kecepatan tinggi + pulsa sonar teleskop
            _add_at(buf, cursor + 0.10, _bp_whoosh(rng, min(d - 0.2, 3.6), f0=240, f1=880, pan_dir=1) * 0.45)
            for k in range(5):
                _add_at(buf, cursor + 0.6 + k * 0.75, _clock_tick(rng, high=True) * 0.32)

        elif kind == "cable_snap_orbit":
            # Kabel gravitasi putus + dentuman lepas orbit
            _add_at(buf, cursor + 0.45, _cable_snap_boom(rng) * 0.95)
            _add_at(buf, cursor + 1.90, _bp_whoosh(rng, min(d - 2.0, 3.2), f0=120, f1=420, pan_dir=-1) * 0.42)

        elif kind == "arctic_wind_frost":
            # Badai angin kutub + kaca barometer retak membeku
            wind = _bp_whoosh(rng, d, f0=160, f1=520, pan_dir=1) * 0.50
            _add_at(buf, cursor, wind)
            _add_at(buf, cursor + 1.35, _ice_crack(rng, 0.85) * 0.75)

        elif kind == "underwater_sonar":
            # Hidrofon bawah laut + gelembung meredup + pintu baja lab
            n_seg = int(d * SR)
            sub_water = _lp_noise(rng, n_seg, alpha=0.005) * 0.18
            _add_at(buf, cursor, np.column_stack([sub_water, sub_water]))
            _add_at(buf, cursor + 0.30, _breaker_blackout(rng) * 0.45)

        elif kind == "glacier_crack_rumble":
            # Samudra membeku -70 C: gletser retak besar + angin kutub
            _add_at(buf, cursor + 0.25, _ice_crack(rng, 1.35) * 0.95)
            _add_at(buf, cursor + 2.10, _ice_crack(rng, 1.10) * 0.70)
            _add_at(buf, cursor, _bp_whoosh(rng, d, f0=140, f1=380, pan_dir=-1) * 0.38)

        elif kind == "bunker_steam_turbine":
            # Bunker bawah tanah: desis uap pipa panas bumi + klik relai + tetesan air
            n_seg = int(d * SR)
            steam = (_lp_noise(rng, n_seg, alpha=0.14) - _lp_noise(rng, n_seg, alpha=0.03)) * 0.08
            _add_at(buf, cursor, np.column_stack([steam, steam]))
            for k in range(4):
                _add_at(buf, cursor + 0.7 + k * 1.15, _clock_tick(rng, high=False) * 0.55)

        elif kind == "red_giant_seismic":
            # Raksasa merah & samudra mendidih: gemuruh termal rendah + desis uap panas
            n_seg = int(d * SR)
            t = np.linspace(0, d, n_seg, endpoint=False)
            roar = _lp_noise(rng, n_seg, alpha=0.009) * np.sin(np.pi * t / d) * 0.32
            hiss = (_lp_noise(rng, n_seg, alpha=0.18) - _lp_noise(rng, n_seg, alpha=0.04)) * 0.09
            _add_at(buf, cursor, np.column_stack([roar + hiss, roar * 0.95 + hiss]))

        elif kind == "nebula_heartbeat":
            # Nebula & katai putih mendingin: hembusan angin kosmik + detak jantung manusia
            _add_at(buf, cursor, _bp_whoosh(rng, d * 0.85, f0=110, f1=290, pan_dir=1) * 0.32)
            for k in range(5):
                _add_at(buf, cursor + 0.55 + k * 1.18, _heartbeat_pair(rng) * 0.85)

        elif kind == "twilight_loop_ticks":
            # Outro teras senja: angin sore tenang + detak jam di akhir agar loop ke Shot 1 mulus!
            _add_at(buf, cursor, _bp_whoosh(rng, d * 0.7, f0=150, f1=340, pan_dir=-1) * 0.25)
            # Detak jam kembali di 2,2 detik terakhir menyambung ke detik 0:00
            t_start = max(cursor + d - 2.2, cursor + 1.0)
            k = 0
            while t_start + k * 0.28 < cursor + d - 0.05:
                _add_at(buf, t_start + k * 0.28, _clock_tick(rng, high=(k % 2 == 0)) * 0.75)
                k += 1

        cursor += d

    # Potong sesuai panjang exact total_dur dan simpan sebagai WAV 16-bit
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


def zoompan_expr(move, frames):
    """Gerak kamera vertikal/zoom halus 30 fps (tanpa patah-patah)."""
    span = max(frames - 1, 1)
    if move == "in":
        z = f"1.0+0.11*on/{span}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif move == "out":
        z = f"1.12-0.11*on/{span}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif move == "up":
        z = "1.12"
        x = "iw/2-(iw/zoom/2)"
        y = f"(ih-ih/zoom)*(1-on/{span})"
    else:  # down
        z = "1.12"
        x = "iw/2-(iw/zoom/2)"
        y = f"(ih-ih/zoom)*(on/{span})"
    return z, x, y


def build_clip(seg):
    """Render 1 shot 9:16 1080x1920 TANPA subtitle/teks di layar, dengan transisi fade halus."""
    idx = seg["idx"]
    d = seg["dur"]
    frames = max(int(round(d * FPS)), 2)
    z, x, y = zoompan_expr(seg["move"], frames)
    fade_out_st = max(0.0, d - 0.18)
    fc = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
          f"crop={W*2}:{H*2},setsar=1,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.04:saturation=1.05,"
          f"noise=alls=3:allf=t+u,"
          f"vignette=PI/5.2,"
          f"fade=t=in:st=0:d=0.14,fade=t=out:st={fade_out_st:.3f}:d=0.16[v]")
    dst = os.path.join(CLIPS, f"s{idx:02d}.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", seg["img"],
         "-filter_complex", fc, "-map", "[v]", "-r", str(FPS),
         "-t", f"{d:.3f}", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", dst])
    return dst


def main():
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)

    print("1/4 Memotong & menyusun 10 segmen Voiceover (< 60 detik)...")
    seg_info = build_vo_segments()
    total_dur = sum(s["dur"] for s in seg_info)
    print(f"    Total durasi 10 shot: {total_dur:.2f}s (batas YouTube Shorts: 60.00s)")
    assert total_dur < 59.5, f"Durasi terlalu panjang ({total_dur:.2f}s >= 59.5s)!"

    # Gabungkan VO
    vo_list = os.path.join(WORK, "vo_list.txt")
    with open(vo_list, "w") as f:
        for s in seg_info:
            f.write(f"file '{s['vo']}'\n")
    vo_concat = os.path.join(WORK, "vo_master.wav")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vo_list, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", vo_concat])

    print("2/4 Menyintesis efek suara fisik & foley multi-lapis (TANPA musik)...")
    sfx_wav = build_sfx_track(seg_info, total_dur)

    print("3/4 Merender 10 klip visual 9:16 (TANPA subtitle, Stickman proporsional)...")
    clip_paths = []
    for s in seg_info:
        print(f"    [{s['idx']:02d}/10] {os.path.basename(s['img'])}  {s['dur']:5.2f}s  move={s['move']}  sfx={s['sfx']}")
        clip_paths.append(build_clip(s))

    vlist = os.path.join(WORK, "v_list.txt")
    with open(vlist, "w") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")
    vonly = os.path.join(WORK, "video_only.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vlist, "-c", "copy", vonly])

    print("4/4 Mastering audio (VO -14 LUFS + Foley SFX, 0% musik) & muxing MP4...")
    final_mp4 = os.path.join(OUT, "STICKMAN_short-02_kalau-matahari-mati_9x16.mp4")
    af = (f"[1:a]highpass=f=80,lowpass=f=14500,"
          f"loudnorm=I=-14:TP=-1.5:LRA=9[vo];"
          f"[2:a]volume=0.52[sfx];"
          f"[vo][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
          f"alimiter=limit=0.95[a]")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", vonly, "-i", vo_concat, "-i", sfx_wav,
         "-filter_complex", af, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
         "-t", f"{total_dur:.3f}", "-movflags", "+faststart", final_mp4])

    final_d = dur(final_mp4)
    print(f"\nSELESAI: {final_mp4} ({final_d:.2f}s)")


if __name__ == "__main__":
    main()
