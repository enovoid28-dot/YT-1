#!/usr/bin/env python3
"""
RENDERER 84 ADEGAN WIDESCREEN 16:9 FULL HD (1920x1080 @ 60FPS — v2 UPGRADE)
Judul: "Apa yang Terjadi pada Tubuhmu di Tiap Planet hingga Lubang Hitam? (Eksperimen Sains Nyata)"

Fitur Utama v2:
1. STRUKTUR VIDEO LENGKAP DENGAN MASKOT CHANNEL `@SeorangSains` (84 ADEGAN):
   - Pembuka (3 adegan, `long01_intro_01..03.jpg` + `vo_long01_intro.mp3`): Maskot utama channel
     `@SeorangSains` (stickman berkacamata hitam detail) menyapa penonton, memperkenalkan tur
     Tata Surya hingga Lubang Hitam, dan menunjuk karakter stickman subjek uji (tanpa kacamata).
   - Isi Eksperimen & Penjelasan Istilah Sains (80 adegan, `long01_t1_01..t8_10.jpg` + `vo_long01_t1..t8.mp3`):
     Subjek uji stickman biasa mengalami kondisi ekstrem tiap planet, sementara Maskot `@SeorangSains`
     (berkacamata hitam detail) hadir menjelaskan istilah sains penting: Efek Rumah Kaca Ekstrem
     (`long01_t2_06.jpg`), Fenomena Hujan Berlian (`long01_t6_05.jpg`), dan Fenomena Spagetifikasi
     (`long01_t8_08.jpg`).
   - Penutup (1 adegan, `long01_outro_01.jpg` + `vo_long01_outro.mp3`): Maskot `@SeorangSains`
     menyimpulkan eksperimen di Bumi dan mengajak penonton berlangganan serta berdiskusi di kolom komentar.
2. 100% BEBAS POTONGAN KONSONAN & BEBAS SUARA DALAM/MENDEM (ZERO INTERNAL TRIMMING + TIMBRE NORMALIZER):
   - Tidak ada lagi pemangkasan `c_env > 0.008` di dalam kalimat sehingga akhiran konsonan halus
     (`s`, `h`, `k`, `t`, `p`) utuh 100%.
   - Setiap kalimat dinormalisasi keseimbangan spektral dada/vokalnya (`normalize_sentence_timbre_and_level`)
     sehingga tidak ada kalimat yang tiba-tiba terdengar dalam/berat.
3. TRANSISI TENANG & NYAMAN DI MATA (Smooth Cross-Dissolve 0.25s @ 60fps, Tanpa Whip-Pan/Goyang)
4. TANPA MUSIK & TANPA SUBTITLE (Hanya Voiceover & Diegetic Sound Effects).
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
    normalize_sentence_timbre_and_level,
    enhance_vocal_for_human_ear,
    carve_and_duck_sfx_for_human_ear,
)

ROOT = "/home/user/YT-1"
IMG_DIR = os.path.join(ROOT, "assets/images")
AUD_DIR = os.path.join(ROOT, "assets/audio")
WORK = os.path.join(ROOT, "work/long01_60fps")
OUT_DIR = os.path.join(ROOT, "output")
os.makedirs(WORK, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
FPS = 60
SR = 48000

OUT_VIDEO = os.path.join(OUT_DIR, "STICKMAN_long-01_tubuh-di-tiap-planet-dan-lubang-hitam_16x9.mp4")

STAGES_84 = [
    # === PEMBUKA (01-03): Maskot @SeorangSains Membuka Eksperimen ===
    ("long01_intro_01.jpg", "space_hum",
     "Halo sobat sains selamat datang kembali bersama Seorang Sains. Pernahkah kamu membayangkan apa yang sebenarnya terjadi jika tubuh manusia dilepas ke luar angkasa tanpa baju astronaut?"),
    ("long01_intro_02.jpg", "space_hum",
     "Dalam eksperimen pikiran kali ini kita akan menguji ketahanan fisik manusia di setiap tempat paling ekstrem mulai dari planet di Tata Surya hingga ke dalam Lubang Hitam."),
    ("long01_intro_03.jpg", "earth_breeze",
     "Tentu saja bukan aku yang akan melompat ke sana melainkan teman uji coba kita ini. Mari kita mulai perjalanan kita dari rumah kita sendiri yaitu planet Bumi."),

    # === TAHAP 1 (04-13): Bumi, Ruang Hampa, Bulan, Matahari, Merkurius ===
    ("long01_t1_01.jpg", "earth_breeze",
     "Di Bumi tubuh kita hidup nyaman terlindung atmosfer yang hangat."),
    ("long01_t1_02.jpg", "space_hum",
     "Namun apa jadinya jika tubuhmu berada di tiap planet tanpa pelindung?"),
    ("long01_t1_03.jpg", "vacuum_hiss",
     "Di ruang hampa antariksa udara di paru-parumu langsung tersedot keluar."),
    ("long01_t1_04.jpg", "boil_fizz",
     "Tanpa tekanan udara air liur dan cairan matamu mendidih seketika."),
    ("long01_t1_05.jpg", "space_hum",
     "Gas dalam darah mengembang membuat tubuhmu membengkak sebelum pingsan."),
    ("long01_t1_06.jpg", "dust_cough",
     "Di permukaan Bulan debu tajam regolith langsung menggores paru-parumu."),
    ("long01_t1_07.jpg", "thermal_crack",
     "Siang di Bulan memanggangmu seratus dua puluh derajat sementara malamnya membeku."),
    ("long01_t1_08.jpg", "solar_roar",
     "Jika mendekati Matahari panas jutaan derajat langsung menguapkan tubuhmu."),
    ("long01_t1_09.jpg", "fire_sizzle",
     "Di planet Merkurius sisi siangnya memanggangmu empat ratus tiga puluh derajat."),
    ("long01_t1_10.jpg", "ice_crack",
     "Tetapi saat malam tiba di Merkurius tubuhmu langsung membeku jadi es."),

    # === TAHAP 2 (14-23): Neraka Planet Venus & Istilah Efek Rumah Kaca ===
    ("long01_t2_01.jpg", "heavy_wind",
     "Sekarang kita turun menembus awan kuning pekat di planet Venus."),
    ("long01_t2_02.jpg", "acid_sizzle",
     "Awan Venus dipenuhi uap asam sulfat pekat yang membakar kulit."),
    ("long01_t2_03.jpg", "thunder_strike",
     "Petir raksasa terus menyambar ganas di balik awan beracun Venus."),
    ("long01_t2_04.jpg", "acid_sizzle",
     "Hujan asam sulfat turun dari langit namun menguap sebelum menyentuh tanah."),
    ("long01_t2_05.jpg", "fire_sizzle",
     "Begitu mendarat kamu disambut daratan batu membara yang sangat gersang."),
    ("long01_t2_06.jpg", "solar_roar",
     "Efek rumah kaca ekstrem membuat Venus lebih panas daripada Merkurius."),
    ("long01_t2_07.jpg", "fire_sizzle",
     "Suhu empat ratus tujuh puluh lima derajat langsung memanggang tubuhmu."),
    ("long01_t2_08.jpg", "crush_rumble",
     "Bukan cuma panas tekanan udara Venus sembilan puluh kali lipat Bumi."),
    ("long01_t2_09.jpg", "crush_rumble",
     "Tekanan mengerikan itu setara berada sembilan ratus meter di bawah laut."),
    ("long01_t2_10.jpg", "volcano_boom",
     "Di Venus tubuhmu akan terbakar dan remuk dalam waktu satu detik."),

    # === TAHAP 3 (24-33): Planet Merah Mars ===
    ("long01_t3_01.jpg", "mars_wind",
     "Dari neraka Venus kita pindah ke gurun merah planet Mars."),
    ("long01_t3_02.jpg", "mars_wind",
     "Sekilas Mars tampak tenang mirip gurun pasir di Bumi kita."),
    ("long01_t3_03.jpg", "dust_cough",
     "Namun udara Mars sembilan puluh lima persen berisi karbon dioksida beracun."),
    ("long01_t3_04.jpg", "vacuum_hiss",
     "Tanpa oksigen kamu akan langsung pingsan hanya dalam lima belas detik."),
    ("long01_t3_05.jpg", "boil_fizz",
     "Tekanan udara Mars yang sangat tipis membuat darahmu mendidih."),
    ("long01_t3_06.jpg", "ice_crack",
     "Selain itu suhu rata-rata Mars mencapai minus enam puluh derajat Celsius."),
    ("long01_t3_07.jpg", "mars_wind",
     "Gravitasi Mars yang ringan memang membuatmu bisa melompat tiga kali lebih tinggi."),
    ("long01_t3_08.jpg", "supersonic_wind",
     "Namun badai debu raksasa Mars bisa menelan seluruh permukaan planet."),
    ("long01_t3_09.jpg", "dust_cough",
     "Debu halus Mars mengandung zat kimia beracun yang merusak organ tubuh."),
    ("long01_t3_10.jpg", "ice_crack",
     "Tanpa baju astronaut kamu hanya bertahan dua menit di planet Mars."),

    # === TAHAP 4 (34-43): Sabuk Asteroid & Raksasa Gas Jupiter ===
    ("long01_t4_01.jpg", "space_hum",
     "Melewati Mars kita melintasi Sabuk Asteroid menuju raksasa gas Jupiter."),
    ("long01_t4_02.jpg", "ice_crack",
     "Di planet kerdil Ceres kamu melayang nyaris tanpa gravitasi di atas gunung es."),
    ("long01_t4_03.jpg", "deep_gravity",
     "Lalu di hadapanmu berdiri Jupiter planet terbesar di Tata Surya."),
    ("long01_t4_04.jpg", "heavy_wind",
     "Masalahnya Jupiter sama sekali tidak memiliki daratan padat untuk dipijak."),
    ("long01_t4_05.jpg", "supersonic_wind",
     "Tubuhmu akan terjun bebas menembus awan gas dengan kecepatan ratusan kilometer per jam."),
    ("long01_t4_06.jpg", "deep_gravity",
     "Gravitasi Jupiter dua setengah kali lebih berat daripada gravitasi Bumi."),
    ("long01_t4_07.jpg", "supersonic_wind",
     "Di lapisan atas kamu dihantam badai Bintik Merah Besar seukuran Bumi."),
    ("long01_t4_08.jpg", "thunder_strike",
     "Kecepatan angin badai di sana mencapai enam ratus kilometer per jam."),
    ("long01_t4_09.jpg", "crush_rumble",
     "Semakin jauh kamu jatuh tekanan gas meningkat ribuan kali lipat."),
    ("long01_t4_10.jpg", "thunder_strike",
     "Sebelum menyentuh lautan hidrogen metalik tubuhmu sudah hancur oleh tekanan."),

    # === TAHAP 5 (44-53): Cincin Saturnus, Bulan Titan & Planet Es Uranus ===
    ("long01_t5_01.jpg", "space_hum",
     "Berikutnya kita tiba di planet bercincin paling indah yaitu Saturnus."),
    ("long01_t5_02.jpg", "ice_crack",
     "Cincin Saturnus ternyata tersusun dari miliaran bongkahan es dan batu."),
    ("long01_t5_03.jpg", "supersonic_wind",
     "Bongkahan es itu melesat mengelilingi Saturnus lebih cepat dari peluru."),
    ("long01_t5_04.jpg", "heavy_wind",
     "Sama seperti Jupiter planet Saturnus juga tidak memiliki daratan padat."),
    ("long01_t5_05.jpg", "supersonic_wind",
     "Angin di ekuator Saturnus berembus hingga seribu delapan ratus kilometer per jam."),
    ("long01_t5_06.jpg", "supersonic_wind",
     "Di kutub utaranya berputar badai raksasa berbentuk segi enam."),
    ("long01_t5_07.jpg", "ice_crack",
     "Di bulan terbesarnya yaitu Titan mengalir sungai metana cair yang sangat dingin."),
    ("long01_t5_08.jpg", "space_hum",
     "Lanjut ke Uranus planet es raksasa yang berputar miring ke samping."),
    ("long01_t5_09.jpg", "acid_sizzle",
     "Atmosfer Uranus berbau telur busuk karena penuh gas hidrogen sulfida."),
    ("long01_t5_10.jpg", "ice_crack",
     "Suhu minus dua ratus dua puluh empat derajat Uranus menjadikannya planet terdingin."),

    # === TAHAP 6 (54-63): Badai Supersonik Neptunus, Istilah Hujan Berlian & Pluto ===
    ("long01_t6_01.jpg", "space_hum",
     "Di ujung Tata Surya berdiri raksasa biru gelap bernama Neptunus."),
    ("long01_t6_02.jpg", "thunder_strike",
     "Neptunus memiliki badai angin paling ganas di seluruh Tata Surya."),
    ("long01_t6_03.jpg", "supersonic_wind",
     "Angin di Neptunus menderu dua ribu seratus kilometer per jam melebihi kecepatan suara."),
    ("long01_t6_04.jpg", "supersonic_wind",
     "Tubuhmu akan terkoyak oleh gelombang kejut supersonik di atmosfernya."),
    ("long01_t6_05.jpg", "crystal_chime",
     "Namun jauh di kedalaman Uranus dan Neptunus terjadi fenomena menakjubkan."),
    ("long01_t6_06.jpg", "crystal_chime",
     "Tekanan ekstrem di sana memadatkan karbon metana menjadi hujan berlian asli."),
    ("long01_t6_07.jpg", "fire_sizzle",
     "Sayangnya berlian tajam itu menghujani tubuhmu di tengah lautan super panas."),
    ("long01_t6_08.jpg", "vacuum_hiss",
     "Di bulan Neptunus yaitu Triton semburan nitrogen cair menyembur delapan kilometer ke langit."),
    ("long01_t6_09.jpg", "space_hum",
     "Lebih jauh lagi di planet kerdil Pluto Matahari tampak hanya seperti bintang terang."),
    ("long01_t6_10.jpg", "ice_crack",
     "Di dataran es nitrogen Pluto tubuhmu langsung membeku keras seperti patung kaca."),

    # === TAHAP 7 (64-73): Eksoplanet Paling Ekstrem & Bintang Neutron ===
    ("long01_t7_01.jpg", "space_hum",
     "Sekarang mari kita keluar dari Tata Surya menuju eksoplanet paling ekstrem."),
    ("long01_t7_02.jpg", "crystal_chime",
     "Di planet biru HD 189733b turun hujan pecahan kaca cair secara menyamping."),
    ("long01_t7_03.jpg", "supersonic_wind",
     "Angin delapan ribu kilometer per jam melontarkan kaca tajam menembus tubuhmu."),
    ("long01_t7_04.jpg", "volcano_boom",
     "Di planet CoRoT-7b separuh permukaannya adalah samudra lava mendidih."),
    ("long01_t7_05.jpg", "fire_sizzle",
     "Awan di sana menguapkan batu lalu menjatuhkan hujan kerikil panas dari langit."),
    ("long01_t7_06.jpg", "pulsar_hum",
     "Lalu kita mendekati Bintang Neutron yaitu sisa ledakan bintang raksasa."),
    ("long01_t7_07.jpg", "crush_rumble",
     "Satu sendok teh materi Bintang Neutron beratnya setara Gunung Everest."),
    ("long01_t7_08.jpg", "deep_gravity",
     "Gravitasi Bintang Neutron dua ratus miliar kali lebih kuat daripada Bumi."),
    ("long01_t7_09.jpg", "supersonic_wind",
     "Tubuhmu akan jatuh menghantam permukaannya dengan kecepatan mendekati cahaya."),
    ("long01_t7_10.jpg", "volcano_boom",
     "Seketika tubuhmu penyek menjadi lapisan atom setipis kertas."),

    # === TAHAP 8 (74-83): Lubang Hitam, Istilah Spagetifikasi & Kembali ke Bumi ===
    ("long01_t8_01.jpg", "deep_gravity",
     "Dan inilah tujuan terakhir paling mengerikan yaitu Lubang Hitam."),
    ("long01_t8_02.jpg", "solar_roar",
     "Di sekelilingnya berputar piringan gas pijar dengan suhu jutaan derajat."),
    ("long01_t8_03.jpg", "deep_gravity",
     "Gravitasi Lubang Hitam begitu ekstrem hingga cahaya pun tidak bisa kabur."),
    ("long01_t8_04.jpg", "pulsar_hum",
     "Saat mendekati batas cakrawala peristiwa waktu di sekitarmu melambat drastis."),
    ("long01_t8_05.jpg", "space_hum",
     "Bagi pengamat dari jauh tubuhmu tampak membeku diam di tepi jurang gelap."),
    ("long01_t8_06.jpg", "deep_gravity",
     "Namun bagi dirimu sendiri tarikan gravitasi di kakimu jauh lebih kuat daripada di kepalamu."),
    ("long01_t8_07.jpg", "crush_rumble",
     "Tubuhmu pun ditarik memanjang secara vertikal seperti sehelai mi spageti."),
    ("long01_t8_08.jpg", "deep_gravity",
     "Para ilmuwan menyebut proses mengerikan ini sebagai fenomena spagetifikasi."),
    ("long01_t8_09.jpg", "pulsar_hum",
     "Akhirnya seluruh atom tubuhmu lenyap ditelan menuju titik singularitas."),
    ("long01_t8_10.jpg", "earth_breeze",
     "Dari seluruh alam semesta hanya Bumi rumah satu-satunya yang ramah bagi tubuh manusia."),

    # === PENUTUP (84): Maskot @SeorangSains Menutup Eksperimen ===
    ("long01_outro_01.jpg", "earth_breeze",
     "Itulah yang terjadi pada tubuh manusia di setiap planet hingga Lubang Hitam. Kalau kamu suka pembahasan sains seperti ini jangan lupa klik tombol suka dan berlangganan di channel Seorang Sains. Planet atau fenomena ekstrem apa lagi yang ingin kita bedah selanjutnya? Tulis di kolom komentar dan sampai jumpa di eksperimen berikutnya!"),
]

# Audio file -> (t_start, t_end, [exact inter-sentence silence midpoints in seconds])
STAGE_VO_CONFIG = [
    ("vo_long01_intro.mp3", 3, 0.05, 28.20, [8.01, 16.89]),
    ("vo_long01_t1.mp3",   10, 0.05, 52.54, [5.38, 10.33, 15.68, 20.84, 25.70, 30.78, 36.69, 42.36, 47.69]),
    ("vo_long01_t2.mp3",   10, 0.05, 54.82, [5.38, 10.71, 16.54, 21.74, 27.45, 33.45, 38.41, 43.95, 49.31]),
    ("vo_long01_t3.mp3",   10, 0.05, 49.18, [5.06, 9.86, 15.31, 20.08, 24.66, 29.86, 34.81, 39.92, 44.56]),
    ("vo_long01_t4.mp3",   10, 0.02, 54.05, [5.95, 11.93, 17.66, 22.66, 29.00, 33.80, 39.09, 43.69, 48.80]),
    ("vo_long01_t5.mp3",   10, 0.05, 51.88, [5.94, 10.95, 15.83, 20.65, 25.94, 30.60, 36.42, 41.42, 46.35]),
    ("vo_long01_t6.mp3",   10, 0.05, 58.14, [5.78, 10.56, 16.96, 21.84, 27.75, 34.09, 40.05, 46.55, 52.16]),
    ("vo_long01_t7.mp3",   10, 0.04, 58.98, [6.31, 15.40, 21.30, 27.62, 33.35, 39.32, 44.29, 49.28, 54.23]),
    ("vo_long01_t8.mp3",   10, 0.00, 54.75, [4.69, 9.87, 15.33, 21.05, 26.23, 32.16, 37.46, 42.45, 48.30]),
    ("vo_long01_outro.mp3", 1, 0.08, 18.42, []),
]


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


def fit_crop_16x9(img_path, tw=W, th=H):
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
    return im.resize((tw, th), Image.Resampling.LANCZOS)


def prepare_84_stages_and_untouched_vo():
    assert len(STAGES_84) == 84
    all_sent_mono = []
    stage_list = []

    fade_len = int(0.015 * SR)
    fade_in = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
    fade_out = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)

    # Jeda tambahan lembut di ujung blok tahap (80ms)
    pad_pause = np.zeros(int(0.080 * SR), dtype=np.float32)

    global_idx = 0
    for seg_i, (mp3_name, n_sent, t_start, t_end, mids) in enumerate(STAGE_VO_CONFIG):
        mp3_path = os.path.join(AUD_DIR, mp3_name)
        seg_wav = os.path.join(WORK, f"seg_{seg_i:02d}.wav")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", mp3_path,
             "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", seg_wav])

        seg_stereo, _ = read_wav_stereo_float(seg_wav)
        seg_mono = 0.5 * (seg_stereo[:, 0] + seg_stereo[:, 1])
        total_samples = len(seg_mono)

        pts = (
            [int(round(t_start * SR))]
            + [int(round(m * SR)) for m in mids]
            + [min(total_samples, int(round(t_end * SR)))]
        )

        for s_i in range(n_sent):
            src_name, sfx_kind, sentence = STAGES_84[global_idx]
            raw_chunk = seg_mono[pts[s_i]:pts[s_i + 1]].copy()

            # ZERO INTERNAL TRIMMING: Tidak ada pemangkasan c_env > 0.008 sama sekali!
            # Kita hanya menormalisasi warna suara (timbre/chest boom) per kalimat agar
            # tidak ada kalimat yang tiba-tiba terdengar dalam/berat.
            core = normalize_sentence_timbre_and_level(raw_chunk, sr=SR)

            if len(core) > 2 * fade_len:
                core[:fade_len] *= fade_in
                core[-fade_len:] *= fade_out

            if s_i == 0 and s_i == n_sent - 1:
                sent_audio = np.concatenate([pad_pause, core, pad_pause])
            elif s_i == 0:
                sent_audio = np.concatenate([pad_pause, core])
            elif s_i == n_sent - 1:
                sent_audio = np.concatenate([core, pad_pause])
            else:
                sent_audio = core

            all_sent_mono.append(sent_audio)
            n_samp = len(sent_audio)
            exact_d = n_samp / SR

            stage_list.append({
                "idx": global_idx + 1,
                "src": src_name,
                "img_path": os.path.join(IMG_DIR, src_name),
                "zoom_cache": None,
                "samples": n_samp,
                "dur": exact_d,
                "sfx": sfx_kind,
                "sentence": sentence,
            })
            global_idx += 1

    full_mono = np.concatenate(all_sent_mono)
    enhanced_mono = enhance_vocal_for_human_ear(full_mono, sr=SR)
    master_stereo = np.column_stack([enhanced_mono, enhanced_mono])

    total_dur = len(master_stereo) / SR
    vo_master = os.path.join(WORK, "vo_long01_60fps_master.wav")
    write_wav_stereo_float(vo_master, master_stereo, sr=SR)
    return stage_list, vo_master, total_dur


def ensure_calm_frames(st):
    if st["zoom_cache"] is None:
        OW, OH = int(W * 1.015), int(H * 1.015)
        im = fit_crop_16x9(st["img_path"], W, H)
        im = ImageEnhance.Contrast(im).enhance(1.02)
        im_over = im.resize((OW, OH), Image.Resampling.LANCZOS)
        zc = []
        for k in range(10):
            e = k / 9.0
            scale = 1.0 - 0.012 * e
            cw = int(round(OW * scale))
            ch = int(round(OH * scale))
            x0 = (OW - cw) // 2
            y0 = (OH - ch) // 2
            sub = im_over.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.BILINEAR)
            zc.append(np.asarray(sub, dtype=np.uint8))
        st["zoom_cache"] = zc


def sample_calm_frame(st, u):
    ensure_calm_frames(st)
    k = int(round(np.clip(u, 0.0, 1.0) * (len(st["zoom_cache"]) - 1)))
    return st["zoom_cache"][k]


def smooth_crossfade(f_a, f_b, alpha):
    s = 0.5 - 0.5 * np.cos(np.pi * np.clip(alpha, 0.0, 1.0))
    return (f_a.astype(np.float32) * (1.0 - s) + f_b.astype(np.float32) * s).astype(np.uint8)


def synth_sfx_84_human_ear(stage_list, vo_master_wav, total_dur):
    n_total = int(total_dur * SR) + SR
    left = np.zeros(n_total, dtype=np.float32)
    right = np.zeros(n_total, dtype=np.float32)
    rng = np.random.default_rng(20261025)

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
        t = np.linspace(0, d, n, endpoint=False, dtype=np.float32)
        noise = rng.normal(0, 1.0, n).astype(np.float32)

        if kind in ("supersonic_wind", "heavy_wind", "mars_wind"):
            whoosh = np.convolve(noise, np.ones(22, dtype=np.float32) / 22, mode="same") * 0.030
            sub = 0.022 * np.sin(2 * np.pi * 54 * t) * np.exp(-t * 0.35)
            add_stereo(whoosh + sub, whoosh * 0.90 + sub, cursor)
        elif kind in ("crush_rumble", "volcano_boom", "thunder_strike", "deep_gravity"):
            roar = np.convolve(noise, np.ones(80, dtype=np.float32) / 80, mode="same") * 0.038
            sub = 0.036 * np.sin(2 * np.pi * 40 * t)
            add_stereo(roar + sub, roar * 0.92 + sub, cursor)
        elif kind in ("fire_sizzle", "acid_sizzle", "solar_roar", "boil_fizz"):
            sizzle = np.convolve(noise, np.ones(14, dtype=np.float32) / 14, mode="same") * 0.024
            low = 0.020 * np.sin(2 * np.pi * 62 * t)
            add_stereo(sizzle + low, sizzle * 0.92 + low, cursor)
        elif kind in ("crystal_chime", "ice_crack", "thermal_crack"):
            crisp = np.convolve(noise, np.ones(8, dtype=np.float32) / 8, mode="same") * 0.018
            chime = 0.012 * np.sin(2 * np.pi * 880 * t) * np.exp(-t * 1.4)
            add_stereo(crisp + chime, crisp * 0.90 + chime, cursor)
        elif kind in ("pulsar_hum", "space_hum", "vacuum_hiss"):
            hum = 0.022 * np.sin(2 * np.pi * 68 * t) + 0.010 * np.sin(2 * np.pi * 136 * t)
            amb = np.convolve(noise, np.ones(60, dtype=np.float32) / 60, mode="same") * 0.015
            add_stereo(hum + amb, hum + amb * 0.94, cursor)
        else:
            breeze = np.convolve(noise, np.ones(45, dtype=np.float32) / 45, mode="same") * 0.016
            add_stereo(breeze, breeze * 0.95, cursor)

        cursor += d

    peak = max(float(np.max(np.abs(left))), float(np.max(np.abs(right))), 1e-6)
    sfx_raw = np.stack([left[:int(total_dur * SR)] / peak * 0.16, right[:int(total_dur * SR)] / peak * 0.16], axis=1)

    vo_stereo, _ = read_wav_stereo_float(vo_master_wav)
    vo_mono = 0.5 * (vo_stereo[:, 0] + vo_stereo[:, 1])
    n_min = min(len(sfx_raw), len(vo_mono))
    sfx_carved = carve_and_duck_sfx_for_human_ear(sfx_raw[:n_min], vo_mono[:n_min], sr=SR)

    sfx_wav = os.path.join(WORK, "sfx_long01_60fps_master.wav")
    write_wav_stereo_float(sfx_wav, sfx_carved, sr=SR)
    return sfx_wav


def render_video_stream_60fps(stage_list):
    v_only = os.path.join(WORK, "v_long01_60fps_only.mp4")
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

    TR_FRAMES = 15  # 0.25s smooth crossfade @ 60fps
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
        if (i + 1) % 10 == 0 or i == 0 or i == n_stages - 1:
            print(f"    [{i+1:02d}/{n_stages}] {st['src']} ({st['dur']:.2f}s @ 1.00x alami) -> \"{st['sentence'][:65]}...\"")

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"FFmpeg 60fps encode failed with code {ret}")
    return v_only


def main():
    print("1/4 Menggabungkan 84 adegan VO (Pembuka + 80 Isi + Penutup) pada kecepatan ALAMI 1.000x...")
    stage_list, vo_master, total_dur = prepare_84_stages_and_untouched_vo()
    print(f"    Total durasi 84 adegan 1.00x alami: {total_dur:.2f}s ({int(total_dur//60):02d}:{total_dur%60:05.2f}, rata-rata {total_dur/84:.2f}s/adegan)")
    print("2/4 Menyintesis Foley SFX halus dengan Vocal-Pocket Carving & Sidechain Auto-Ducking...")
    sfx_master = synth_sfx_84_human_ear(stage_list, vo_master, total_dur)
    print("3/4 Merender stream video Widescreen 1920x1080 60fps (kamera tenang + Smooth Cross-Dissolve)...")
    v_only = render_video_stream_60fps(stage_list)

    print("4/4 Mastering audio akhir (100% Untouched 1.00x Human-Ear VO -14 LUFS + Ducked SFX)...")
    fc = (
        "[1:a]loudnorm=I=-14.0:TP=-1.0:LRA=7,volume=1.05[vo];"
        "[2:a]volume=0.22[sfx];"
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
    print(f"\nSELESAI: {OUT_VIDEO} ({final_d:.2f}s / {int(final_d//60):02d}:{final_d%60:05.2f}, 1920x1080 60fps, 84 Adegan Lengkap)")


if __name__ == "__main__":
    main()
