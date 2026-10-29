#!/usr/bin/env python3
"""
RENDERER 40 GAMBAR REALISTIS (1080p 60FPS — 100% NATURAL 1.00x UNTOUCHED VO + ANTI-PUSING)
Judul: "Saat Matahari Mati: Tahap Demi Tahap Sebenarnya (Kronologi Sains Nyata)"

Perbaikan Kritis Sesuai Evaluasi User ("VO masih sedikit cepat, seperti terpotong, atau error!"):
1. 100% KECEPATAN ALAMI 1.00x TANPA PEMOTONGAN SUKU KATA (ZERO CHOPPING, ZERO ATEMPO):
   - Menghapus total fungsi `compact_sentence_pcm`, `silenceremove`, dan `atempo=1.20` yang
     sebelumnya memotong konsonan halus dan mempercepat suara hingga terdengar seperti terpotong/error.
   - Menggunakan 10 file audio baru (`vo_v5_01..10.mp3`) yang dari awalnya sudah berdurasi alami
     `177.00 detik` (`02:57.00`) pada kecepatan bicara **100% murni `1.000x` (0% percepatan)**.
   - Gelombang suara di dalam setiap segmen dibiarkan **100% utuh menyambung tanpa dipotong-potong**,
     dan transisi gambar dipicu tepat di titik tengah jeda hening alami antar kalimat (`MIDS_V5`).
2. 100% AKURAT SESUAI ISI VISUAL 40 GAMBAR (`real_t1_01.jpg` s/d `real_t4_10.jpg`)
3. TRANSISI TENANG & NYAMAN DI MATA (Smooth Cross-Dissolve 0.25s @ 60fps, Tanpa Whip-Pan/Goyang)
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
WORK = os.path.join(ROOT, "work/short02_60fps")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
FPS = 60
SR = 48000

OUT_VIDEO = os.path.join(OUT_DIR, "STICKMAN_short-02_kalau-matahari-mati_9x16.mp4")
OUT_THUMB = os.path.join(OUT_DIR, "thumbnail_short_ep02.jpg")

# ---------------------------------------------------------------------------
# DAFTAR 40 GAMBAR & 40 KALIMAT VO ALAMI 1.00x (100% SESUAI VISUAL GAMBAR #01-#40)
# ---------------------------------------------------------------------------
STAGES_40 = [
    # === TAHAP 1 (01-10) ===
    ("real_t1_01.jpg", "city_day",
     "Hari ini Matahari bersinar hangat menyinari jalanan kota."),
    ("real_t1_02.jpg", "water_hose",
     "Air selang masih mengalir deras menyirami rumput halaman."),
    ("real_t1_03.jpg", "space_hum",
     "Namun seiring menua Matahari bersinar makin terang."),
    ("real_t1_04.jpg", "city_day",
     "Panas teriknya mulai memanggang sawah dan saluran air."),
    ("real_t1_05.jpg", "heat_hiss",
     "Di perkotaan rumput mengering dan jalanan memancarkan panas."),
    ("real_t1_06.jpg", "dry_faucet",
     "Tanah retak dan keran hanya meneteskan sisa air."),
    ("real_t1_07.jpg", "water_rush",
     "Suhu panas mencairkan tebing es kutub menjadi air terjun."),
    ("real_t1_08.jpg", "water_rush",
     "Air laut pun naik merendam jalanan dan mobil."),
    ("real_t1_09.jpg", "dry_wind",
     "Sungai di bawah jembatan mengering hingga perahu terdampar."),
    ("real_t1_10.jpg", "steam_boil",
     "Di tepi pantai air laut mulai mendidih beruap."),

    # === TAHAP 2 (11-20) ===
    ("real_t2_01.jpg", "steam_boil",
     "Uap panas tebal langsung menyelimuti jalanan gedung kota."),
    ("real_t2_02.jpg", "dry_wind",
     "Air di bendungan tinggi lenyap menjadi tanah retak."),
    ("real_t2_03.jpg", "sand_storm",
     "Gundukan pasir gurun mulai menimbun jalan dan mobil."),
    ("real_t2_04.jpg", "dry_wind",
     "Di pelabuhan kapal besar berkarat di dasar laut kering."),
    ("real_t2_05.jpg", "heat_hiss",
     "Panas ekstrem melelehkan aspal dan membengkokkan tiang lampu."),
    ("real_t2_06.jpg", "volcano_roar",
     "Gunung berapi pun meletus memuntahkan lava dan abu."),
    ("real_t2_07.jpg", "dry_wind",
     "Kota akhirnya hancur di bawah langit kuning pekat."),
    ("real_t2_08.jpg", "space_hum",
     "Dari angkasa Bumi tampak menjadi planet gurun cokelat."),
    ("real_t2_09.jpg", "solar_roar",
     "Hidrogen habis dan Matahari membengkak menjadi Raksasa Merah."),
    ("real_t2_10.jpg", "solar_roar",
     "Dari sela gedung bola Matahari tampak membesar raksasa."),

    # === TAHAP 3 (21-30) ===
    ("real_t3_01.jpg", "solar_roar",
     "Di angkasa bintang Raksasa Merah mendidih membakar planet."),
    ("real_t3_02.jpg", "solar_roar",
     "Gelombang plasma Matahari langsung menghancurkan planet Merkurius."),
    ("real_t3_03.jpg", "solar_wind",
     "Angin surya ganas mengelupas habis atmosfer planet Venus."),
    ("real_t3_04.jpg", "solar_roar",
     "Lidah api Matahari menarik planet Venus ke dalamnya."),
    ("real_t3_05.jpg", "solar_roar",
     "Di Bumi bola api merah memenuhi ujung jalan."),
    ("real_t3_06.jpg", "volcano_roar",
     "Jalanan di antara gedung kota menjadi sungai lava."),
    ("real_t3_07.jpg", "volcano_roar",
     "Seluruh daratan akhirnya mencair menjadi samudra magma mendidih."),
    ("real_t3_08.jpg", "solar_roar",
     "Dari angkasa Bumi tampak hitam penuh retakan magma."),
    ("real_t3_09.jpg", "water_rush",
     "Namun panas itu mencairkan es di bulan Jupiter."),
    ("real_t3_10.jpg", "helium_boom",
     "Inti Matahari akhirnya memicu ledakan kilat cahaya terang."),

    # === TAHAP 4 (31-40) ===
    ("real_t4_01.jpg", "solar_roar",
     "Matahari mulai berdenyut melontarkan cincin gas api."),
    ("real_t4_02.jpg", "space_hum",
     "Lapisan luarnya terlepas dan menyingkap inti putih terang."),
    ("real_t4_03.jpg", "space_hum",
     "Awan gas itu membentuk Nebula Planeter yang indah."),
    ("real_t4_04.jpg", "space_hum",
     "Dari kejauhan pusaran nebula itu menerangi langit malam."),
    ("real_t4_05.jpg", "space_hum",
     "Tersisa bintang kecil Katai Putih dekat Bumi hangus."),
    ("real_t4_06.jpg", "dry_wind",
     "Tanpa panas lagi sisa kota membeku tertutup salju."),
    ("real_t4_07.jpg", "dry_wind",
     "Dari batu beku Matahari hanya tampak setitik bintang."),
    ("real_t4_08.jpg", "space_hum",
     "Triliunan tahun kemudian intinya padam menjadi Katai Hitam."),
    ("real_t4_09.jpg", "space_hum",
     "Namun sisa gasnya berkumpul melahirkan tata surya baru."),
    ("real_t4_10.jpg", "city_day",
     "Mari bersyukur selagi Matahari masih bersinar hangat hari ini."),
]

# Titik tengah presisi dari 3 jeda hening alami (~0.75s) di dalam setiap file vo_v5_01..10.mp3
MIDS_V5 = {
    1:  [4.510, 9.015, 13.195],
    2:  [5.185, 9.390, 13.820],
    3:  [4.270, 8.550, 13.025],
    4:  [3.795, 7.870, 12.590],
    5:  [4.045, 8.575, 13.500],
    6:  [5.795, 10.950, 16.055],
    7:  [4.055, 7.935, 12.885],
    8:  [4.160, 8.730, 13.025],
    9:  [3.980, 8.300, 12.430],
    10: [4.670, 9.525, 14.275],
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


def build_thumbnail():
    ai_thumb_path = os.path.join(IMG_DIR, "thumb_short02_ai_text.jpg")
    im = fit_crop_9x16(ai_thumb_path, W, H)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = ImageEnhance.Sharpness(im).enhance(1.08)
    im.save(OUT_THUMB, "JPEG", quality=96, subsampling=0)
    return OUT_THUMB


def prepare_40_stages_and_untouched_vo():
    """
    Gabungkan 10 file `vo_v5_01..10.mp3` pada kecepatan ALAMI 1.000x TANPA pemotongan
    suku kata (`compact_sentence_pcm` = OFF, `silenceremove` = OFF, `atempo` = OFF).
    Setiap segmen 4 kalimat tetap 100% utuh menyambung, dan durasi tampilan masing-masing
    gambar dihitung presisi dari jumlah sampel di antara titik tengah jeda kalimat (`MIDS_V5`).
    """
    assert len(STAGES_40) == 40
    OW, OH = int(W * 1.015), int(H * 1.015)

    seg_chunks_mono = []
    stage_list = []

    fade_len = int(0.025 * SR)  # 25ms smooth fade di ujung file (di dalam area hening)
    fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    for seg_idx in range(1, 11):
        mp3_path = os.path.join(AUD_DIR, f"vo_v5_{seg_idx:02d}.mp3")
        seg_wav = os.path.join(WORK, f"seg_v5_{seg_idx:02d}.wav")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", mp3_path,
             "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", seg_wav])

        seg_stereo, _ = read_wav_stereo_float(seg_wav)
        seg_mono = 0.5 * (seg_stereo[:, 0] + seg_stereo[:, 1])
        total_samples = len(seg_mono)

        # Titik potong segmen hanya di keheningan awal (0.10s) & keheningan akhir (d - 0.12s)
        s0 = int(round(0.10 * SR))
        s4 = max(s0 + SR, total_samples - int(round(0.12 * SR)))
        mids = MIDS_V5[seg_idx]
        s1 = int(round(mids[0] * SR))
        s2 = int(round(mids[1] * SR))
        s3 = int(round(mids[2] * SR))

        # Ambil gelombang suara utuh 100% menyambung dari s0 s/d s4 (TANPA dipotong di tengah!)
        whole_seg = seg_mono[s0:s4].copy()
        whole_seg[:fade_len] *= fade_in
        whole_seg[-fade_len:] *= fade_out
        seg_chunks_mono.append(whole_seg)

        # Hitung jumlah sampel presisi untuk masing-masing dari 4 kalimat di segmen ini
        sample_Points = [s0, s1, s2, s3, s4]
        for s_i in range(4):
            global_idx = (seg_idx - 1) * 4 + s_i
            src_name, sfx_kind, sentence = STAGES_40[global_idx]
            n_samp = sample_Points[s_i + 1] - sample_Points[s_i]
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

    # Gabungkan seluruh 10 segmen utuh menjadi 1 aliran kontinu 177.00 detik
    full_mono = np.concatenate(seg_chunks_mono)
    # Proses kejernihan telinga manusia (Zero-Phase ISO 226 EQ) pada aliran utuh sekaligus!
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

        if kind in ("city_day", "water_hose"):
            water = np.convolve(noise, np.ones(30) / 30, mode="same") * 0.020
            add_stereo(water, water * 0.95, cursor)
        elif kind in ("steam_boil", "heat_hiss", "water_rush"):
            hiss = np.convolve(noise, np.ones(22) / 22, mode="same") * 0.025
            add_stereo(hiss, hiss * 0.92, cursor)
        elif kind in ("volcano_roar", "solar_roar"):
            roar = np.convolve(noise, np.ones(70) / 70, mode="same") * 0.040
            sub = 0.035 * np.sin(2 * np.pi * 46 * t)
            add_stereo(roar + sub, roar * 0.92 + sub, cursor)
        elif kind == "helium_boom":
            boom = 0.055 * np.sin(2 * np.pi * (80 * np.exp(-t * 1.5) + 38) * t) * np.exp(-t * 1.1)
            add_stereo(boom, boom, cursor)
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

    # Transisi Cross-Dissolve lembut 15 frame (0.25 detik @ 60fps) tepat di tengah jeda hening antar kalimat
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
    print("1/5 Memastikan Thumbnail 9:16 ('output/thumbnail_short_ep02.jpg')...")
    build_thumbnail()
    print("2/5 Menggabungkan 40 kalimat VO pada kecepatan ALAMI 1.000x (TANPA pemotongan/atempo)...")
    stage_list, vo_master, total_dur = prepare_40_stages_and_untouched_vo()
    print(f"    Total durasi 40 kalimat 1.00x alami: {total_dur:.2f}s ({int(total_dur//60)}:{total_dur%60:05.2f}, rata-rata {total_dur/40:.2f}s/gambar)")
    print("3/5 Menyintesis Foley SFX halus dengan Vocal-Pocket Carving & Sidechain Auto-Ducking...")
    sfx_master = synth_sfx_40_human_ear(stage_list, vo_master, total_dur)
    print("4/5 Merender stream video 1080p 60fps (kamera tenang + Smooth Cross-Dissolve)...")
    v_only = render_video_stream_60fps(stage_list)

    print("5/5 Mastering audio akhir (100% Untouched 1.00x Human-Ear VO -14 LUFS + Ducked SFX)...")
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
