#!/usr/bin/env python3
"""
RENDERER 40 GAMBAR REALISTIS (1080p 60FPS — 100% NATURAL 1.00x UNTOUCHED VO + ANTI-PUSING)
Judul: "Saat Bumi Berhenti Berputar: Tahap Demi Tahap Sebenarnya (Kronologi Sains Nyata)"

Fitur Utama:
1. 100% KECEPATAN ALAMI 1.00x TANPA PEMOTONGAN SUKU KATA (ZERO CHOPPING, ZERO ATEMPO):
   - Menggunakan 10 file audio (`vo_ep03_v2_01..10.mp3`) berdurasi alami ~170 detik pada
     kecepatan bicara 100% murni `1.000x` (0% percepatan, 0% pemotongan internal).
   - Transisi gambar dipicu tepat di titik tengah jeda hening alami antar kalimat (`MIDS_EP03`).
2. 100% AKURAT SESUAI ISI VISUAL 40 GAMBAR (`ep03_t1_01.jpg` s/d `ep03_t4_10.jpg`)
3. TRANSISI TENANG & NYAMAN DI MATA (Smooth Cross-Dissolve 0.25s @ 60fps, Tanpa Whip-Pan/Goyang)
4. HUMAN-EAR VOCAL ENHANCER (Zero-Phase ISO 226:2023 EQ + Vocal-Pocket Sidechain SFX Ducking)
"""
import os
import re
import subprocess
import numpy as np
from PIL import Image, ImageEnhance
import imageio_ffmpeg

from pipeline.vo_human_ear_enhancer import (
    read_wav_stereo_float,
    write_wav_stereo_float,
    enhance_vocal_for_human_ear,
    carve_and_duck_sfx_for_human_ear,
)

ROOT = "/home/user/YT-1"
IMG_DIR = os.path.join(ROOT, "assets/images")
AUD_DIR = os.path.join(ROOT, "assets/audio")
WORK = os.path.join(ROOT, "work/short03_60fps")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
FPS = 60
SR = 48000

OUT_VIDEO = os.path.join(OUT_DIR, "STICKMAN_short-03_saat-bumi-berhenti-berputar_9x16.mp4")
OUT_THUMB = os.path.join(OUT_DIR, "thumbnail_short_ep03.jpg")

STAGES_40 = [
    # === TAHAP 1 (01-10) ===
    ("ep03_t1_01.jpg", "city_day",
     "Saat ini kita berjalan santai di atas Bumi."),
    ("ep03_t1_02.jpg", "jet_spin",
     "Padahal Bumi berputar seribu enam ratus kilometer sejam."),
    ("ep03_t1_03.jpg", "brake_boom",
     "Bayangkan jika tiba-tiba Bumi berhenti berputar mendadak."),
    ("ep03_t1_04.jpg", "supersonic_wind",
     "Tubuh kita langsung terlontar ke timur secepat peluru."),
    ("ep03_t1_05.jpg", "supersonic_wind",
     "Mobil dan bus di jalan ikut terlempar terbang."),
    ("ep03_t1_06.jpg", "sonic_boom",
     "Atmosfer Bumi menciptakan badai angin secepat gelombang suara."),
    ("ep03_t1_07.jpg", "supersonic_wind",
     "Angin supersonik itu mencabut pepohonan hingga beterbangan jauh."),
    ("ep03_t1_08.jpg", "crash_wind",
     "Atap dan dinding rumah warga langsung hancur berantakan."),
    ("ep03_t1_09.jpg", "quake_rumble",
     "Gedung pencakar langit di pusat kota ikut runtuh."),
    ("ep03_t1_10.jpg", "polar_wind",
     "Hanya warga di kutub Bumi yang tetap aman."),

    # === TAHAP 2 (11-20) ===
    ("ep03_t2_01.jpg", "fire_storm",
     "Gesekan angin panas di udara memicu badai api."),
    ("ep03_t2_02.jpg", "quake_rumble",
     "Hentakan kerak Bumi memicu gempa yang membelah jalanan."),
    ("ep03_t2_03.jpg", "quake_rumble",
     "Jembatan gantung raksasa pun putus akibat guncangan hebat."),
    ("ep03_t2_04.jpg", "water_draw",
     "Air laut di pantai tiba-tiba tersedot surut menjauh."),
    ("ep03_t2_05.jpg", "tsunami_roar",
     "Air samudra berubah menjadi dinding megatsunami setinggi langit."),
    ("ep03_t2_06.jpg", "tsunami_roar",
     "Gelombang raksasa itu langsung menenggelamkan seluruh kota pesisir."),
    ("ep03_t2_07.jpg", "tsunami_roar",
     "Air laut merangsek jauh hingga menenggelamkan daratan rendah."),
    ("ep03_t2_08.jpg", "volcano_roar",
     "Tekanan bawah tanah memicu gunung berapi meletus bersamaan."),
    ("ep03_t2_09.jpg", "space_hum",
     "Dari antariksa Bumi tampak tertutup pusaran badai debu."),
    ("ep03_t2_10.jpg", "polar_wind",
     "Saat badai mereda Matahari tampak diam di langit."),

    # === TAHAP 3 (21-30) ===
    ("ep03_t3_01.jpg", "space_hum",
     "Putaran Bumi tadinya menahan air laut di khatulistiwa."),
    ("ep03_t3_02.jpg", "water_draw",
     "Kini air samudra mengalir pindah menuju kedua kutub."),
    ("ep03_t3_03.jpg", "polar_wind",
     "Lautan khatulistiwa mengering menjadi satu daratan benua raksasa."),
    ("ep03_t3_04.jpg", "tsunami_roar",
     "Sebaliknya daratan utara dan selatan tenggelam menjadi samudra."),
    ("ep03_t3_05.jpg", "space_hum",
     "Satu hari di Bumi kini berlangsung satu tahun."),
    ("ep03_t3_06.jpg", "fire_storm",
     "Sisi yang menghadap Matahari terpanggang siang enam bulan."),
    ("ep03_t3_07.jpg", "fire_storm",
     "Panas ekstrem mengeringkan sungai dan membakar sisa hutan."),
    ("ep03_t3_08.jpg", "polar_wind",
     "Sisi belakang Bumi terjebak malam gelap enam bulan."),
    ("ep03_t3_09.jpg", "polar_wind",
     "Suhu malam yang beku menimbun kota dalam es."),
    ("ep03_t3_10.jpg", "supersonic_wind",
     "Di perbatasan siang dan malam badai terus mengamuk."),

    # === TAHAP 4 (31-40) ===
    ("ep03_t4_01.jpg", "quake_rumble",
     "Inti besi cair di pusat Bumi ikut berhenti."),
    ("ep03_t4_02.jpg", "space_hum",
     "Akibatnya perisai medan magnet pelindung Bumi menghilang total."),
    ("ep03_t4_03.jpg", "solar_rad",
     "Radiasi mematikan dari Matahari langsung menghantam permukaan Bumi."),
    ("ep03_t4_04.jpg", "solar_rad",
     "Langit di seluruh dunia berpendar merah penuh radiasi."),
    ("ep03_t4_05.jpg", "solar_rad",
     "Badai surya itu melumpuhkan satelit dan jaringan listrik."),
    ("ep03_t4_06.jpg", "polar_wind",
     "Manusia yang tersisa mengungsi ke perbatasan siang malam."),
    ("ep03_t4_07.jpg", "bunker_hum",
     "Demi menghindari radiasi manusia membangun bunker bawah tanah."),
    ("ep03_t4_08.jpg", "bunker_hum",
     "Makanan ditanam di bawah tanah memakai lampu buatan."),
    ("ep03_t4_09.jpg", "space_hum",
     "Wajah planet Bumi kini berubah menjadi dunia asing."),
    ("ep03_t4_10.jpg", "city_day",
     "Putaran Bumi setiap hari adalah penjaga kehidupan kita."),
]

# Titik tengah presisi dari 3 jeda hening alami di setiap file vo_ep03_v2_01..10.mp3
MIDS_EP03 = {
    1:  [3.535, 7.755, 11.260],
    2:  [3.855, 8.620, 13.280],
    3:  [3.695, 6.860, 10.765],
    4:  [4.450, 8.450, 13.695],
    5:  [4.790, 9.555, 14.620],
    6:  [3.885, 7.940, 12.860],
    7:  [4.105, 7.975, 12.520],
    8:  [3.830, 7.580, 11.080],
    9:  [4.860, 9.095, 13.030],
    10: [4.510, 8.200, 12.305],
}


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr[-1200:]}")
    return p


def dur(path):
    p = subprocess.run([FF, "-hide_banner", "-i", path],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if not m:
        raise RuntimeError(f"Cannot parse duration: {path}")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def fit_crop_9x16(img_path, tw=W, th=H):
    im = Image.open(img_path).convert("RGB")
    iw, ih = im.size
    target_ratio = tw / th
    cur_ratio = iw / ih
    if cur_ratio > target_ratio:
        nw = int(ih * target_ratio)
        x0 = (iw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, ih))
    elif cur_ratio < target_ratio:
        nh = int(iw / target_ratio)
        y0 = (ih - nh) // 2
        im = im.crop((0, y0, iw, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def prepare_40_stages_and_untouched_vo():
    assert len(STAGES_40) == 40
    OW, OH = int(W * 1.015), int(H * 1.015)

    seg_chunks_mono = []
    stage_list = []

    fade_len = int(0.025 * SR)
    fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    for seg_idx in range(1, 11):
        mp3_path = os.path.join(AUD_DIR, f"vo_ep03_v2_{seg_idx:02d}.mp3")
        seg_wav = os.path.join(WORK, f"seg_ep03_{seg_idx:02d}.wav")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", mp3_path,
             "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", seg_wav])

        seg_stereo, _ = read_wav_stereo_float(seg_wav)
        seg_mono = 0.5 * (seg_stereo[:, 0] + seg_stereo[:, 1])
        total_samples = len(seg_mono)

        s0 = int(round(0.08 * SR))
        s4 = max(s0 + SR, total_samples - int(round(0.10 * SR)))
        mids = MIDS_EP03[seg_idx]
        s1 = int(round(mids[0] * SR))
        s2 = int(round(mids[1] * SR))
        s3 = int(round(mids[2] * SR))

        whole_seg = seg_mono[s0:s4].copy()
        whole_seg[:fade_len] *= fade_in
        whole_seg[-fade_len:] *= fade_out
        seg_chunks_mono.append(whole_seg)

        sample_points = [s0, s1, s2, s3, s4]
        for s_i in range(4):
            global_idx = (seg_idx - 1) * 4 + s_i
            src_name, sfx_kind, sentence = STAGES_40[global_idx]
            n_samp = sample_points[s_i + 1] - sample_points[s_i]
            exact_d = n_samp / SR

            img_path = os.path.join(IMG_DIR, src_name)
            im = fit_crop_9x16(img_path, W, H)
            im = ImageEnhance.Contrast(im).enhance(1.02)
            im_over = im.resize((OW, OH), Image.LANCZOS)

            stage_list.append({
                "idx": global_idx + 1,
                "src": src_name,
                "im_over": im_over,
                "zoom_cache": None,
                "samples": n_samp,
                "dur": exact_d,
                "sfx": sfx_kind,
                "sentence": sentence,
            })

    full_mono = np.concatenate(seg_chunks_mono)
    enhanced_mono = enhance_vocal_for_human_ear(full_mono, sr=SR)
    master_stereo = np.column_stack([enhanced_mono, enhanced_mono])

    total_dur = len(master_stereo) / SR
    if total_dur >= 179.8:
        raise RuntimeError(f"Durasi melebihi batas 3 menit YouTube Shorts: {total_dur:.2f}s")

    vo_master = os.path.join(WORK, "vo_60fps_master.wav")
    write_wav_stereo_float(vo_master, master_stereo, sr=SR)
    return stage_list, vo_master, total_dur


def ensure_calm_frames(st):
    if st["zoom_cache"] is None:
        im_over = st["im_over"]
        OW, OH = im_over.size
        zc = []
        for k in range(12):
            e = k / 11.0
            scale = 1.0 - 0.012 * e
            cw = int(round(OW * scale))
            ch = int(round(OH * scale))
            x0 = (OW - cw) // 2
            y0 = (OH - ch) // 2
            sub = im_over.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
            zc.append(np.asarray(sub, dtype=np.uint8))
        st["zoom_cache"] = zc


def sample_calm_frame(st, u):
    ensure_calm_frames(st)
    k = int(round(np.clip(u, 0.0, 1.0) * (len(st["zoom_cache"]) - 1)))
    return st["zoom_cache"][k]


def smooth_crossfade(f_a, f_b, alpha):
    s = 0.5 - 0.5 * np.cos(np.pi * np.clip(alpha, 0.0, 1.0))
    return (f_a.astype(np.float32) * (1.0 - s) + f_b.astype(np.float32) * s).astype(np.uint8)


def synth_sfx_40_human_ear(stage_list, vo_master_wav, total_dur):
    n_total = int(total_dur * SR) + SR
    left = np.zeros(n_total, dtype=np.float32)
    right = np.zeros(n_total, dtype=np.float32)
    rng = np.random.default_rng(2026)

    def add_stereo(buf_l, buf_r, start_s):
        i0 = max(0, int(start_s * SR))
        i1 = min(n_total, i0 + len(buf_l))
        if i1 > i0:
            left[i0:i1] += buf_l[:i1 - i0]
            right[i0:i1] += buf_r[:i1 - i0]

    cursor = 0.0
    for st in stage_list:
        d = st["dur"]
        kind = st["sfx"]
        n = int(d * SR)
        t = np.linspace(0, d, n, endpoint=False)
        noise = rng.normal(0, 1.0, n)

        if kind in ("supersonic_wind", "sonic_boom", "crash_wind"):
            whoosh = np.convolve(noise, np.ones(18) / 18, mode="same") * 0.032
            sub = 0.025 * np.sin(2 * np.pi * 52 * t) * np.exp(-t * 0.4)
            add_stereo(whoosh + sub, whoosh * 0.90 + sub, cursor)
        elif kind in ("quake_rumble", "volcano_roar", "brake_boom"):
            roar = np.convolve(noise, np.ones(75) / 75, mode="same") * 0.042
            sub = 0.040 * np.sin(2 * np.pi * 42 * t)
            add_stereo(roar + sub, roar * 0.92 + sub, cursor)
        elif kind in ("tsunami_roar", "water_draw"):
            wave = np.convolve(noise, np.ones(40) / 40, mode="same") * 0.034
            low = 0.025 * np.sin(2 * np.pi * 58 * t)
            add_stereo(wave + low, wave * 0.94 + low, cursor)
        elif kind in ("fire_storm", "solar_rad"):
            hiss = np.convolve(noise, np.ones(24) / 24, mode="same") * 0.026
            add_stereo(hiss, hiss * 0.92, cursor)
        else:
            amb = np.convolve(noise, np.ones(50) / 50, mode="same") * 0.018
            add_stereo(amb, amb * 0.95, cursor)

        cursor += d

    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
    sfx_raw = np.stack([left / peak * 0.16, right / peak * 0.16], axis=1)

    vo_stereo, _ = read_wav_stereo_float(vo_master_wav)
    sfx_carved = carve_and_duck_sfx_for_human_ear(sfx_raw, vo_stereo, sr=SR)

    sfx_wav = os.path.join(WORK, "sfx_60fps_master.wav")
    write_wav_stereo_float(sfx_wav, sfx_carved, sr=SR)
    return sfx_wav


def render_video_stream_60fps(stage_list):
    v_only = os.path.join(WORK, "v_60fps_only.mp4")
    cmd = [
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS),
        v_only
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    TR_FRAMES = 15
    n_stages = len(stage_list)

    cum_samples = 0
    prev_f = 0
    for st in stage_list:
        cum_samples += st["samples"]
        exact_t = cum_samples / SR
        target_f = int(round(exact_t * FPS))
        st["frames"] = max(TR_FRAMES + 10, target_f - prev_f)
        prev_f = target_f

    for i, st in enumerate(stage_list):
        nf = st["frames"]
        has_next = (i < n_stages - 1)
        next_st = stage_list[i + 1] if has_next else None
        tr_len = TR_FRAMES if has_next else 0

        for f_idx in range(nf):
            u_curr = f_idx / max(1, nf - 1)
            frame_curr = sample_calm_frame(st, u_curr)

            if has_next and f_idx >= (nf - tr_len):
                k = f_idx - (nf - tr_len)
                alpha = (k + 1) / (tr_len + 1)
                frame_next = sample_calm_frame(next_st, 0.0)
                out_frame = smooth_crossfade(frame_curr, frame_next, alpha)
            else:
                out_frame = frame_curr

            proc.stdin.write(out_frame.tobytes())

        st["zoom_cache"] = None
        st["im_over"] = None
        if (i + 1) % 10 == 0 or i == 0:
            print(f"    [{i+1:02d}/40] {st['src']} ({st['dur']:.2f}s @ 1.00x alami) -> \"{st['sentence']}\"")

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg 60fps encode failed with code {ret}")
    return v_only


def main():
    print("1/4 Menggabungkan 40 kalimat VO pada kecepatan ALAMI 1.000x (TANPA pemotongan/atempo)...")
    stage_list, vo_master, total_dur = prepare_40_stages_and_untouched_vo()
    print(f"    Total durasi 40 kalimat 1.00x alami: {total_dur:.2f}s ({int(total_dur//60)}:{total_dur%60:05.2f}, rata-rata {total_dur/40:.2f}s/gambar)")
    print("2/4 Menyintesis Foley SFX halus dengan Vocal-Pocket Carving & Sidechain Auto-Ducking...")
    sfx_master = synth_sfx_40_human_ear(stage_list, vo_master, total_dur)
    print("3/4 Merender stream video 1080p 60fps (kamera tenang + Smooth Cross-Dissolve)...")
    v_only = render_video_stream_60fps(stage_list)

    print("4/4 Mastering audio akhir (100% Untouched 1.00x Human-Ear VO -14 LUFS + Ducked SFX)...")
    fc = (
        "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=9,volume=1.05[vo];"
        "[2:a]volume=0.25[sfx];"
        "[vo][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    run([
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-i", v_only,
        "-i", vo_master,
        "-i", sfx_master,
        "-filter_complex", fc,
        "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-ar", str(SR),
        "-t", f"{total_dur:.3f}",
        "-movflags", "+faststart",
        OUT_VIDEO
    ])
    final_d = dur(OUT_VIDEO)
    print(f"\nSELESAI: {OUT_VIDEO} ({final_d:.2f}s / {int(final_d//60)}:{final_d%60:05.2f}, 1080p 60fps, 1.00x Natural Untouched VO)")


if __name__ == "__main__":
    main()
