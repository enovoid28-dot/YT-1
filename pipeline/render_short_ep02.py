#!/usr/bin/env python3
"""
Render YouTube Short #2: 'SAAT MATAHARI MATI: TAHAP DEMI TAHAP SEBENARNYA'
- 40 Gambar Mahakarya 2D Environmental Cross-Section Unik (batch1_01..10, batch2_01..10, batch3_01..10, batch4_01..10)
  tanpa duplikasi crop & tanpa diagram/panah AI slop.
- Durasi target: ~1:42 (102 detik, tepat di rentang 1:30 - 1:50 permintaan user).
- 12 segmen Voiceover Bahasa Indonesia kronologis dari awal hingga akhir kematian Matahari.
- 0% Subtitle di layar, 0% Musik, 100% Voiceover (-14 LUFS) + Foley SFX fisik 40 tahap.
"""
import os
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imageio_ffmpeg

ROOT = "/home/user/YT-1"
IMG = os.path.join(ROOT, "assets/images")
AUD = os.path.join(ROOT, "assets/audio")
WORK = os.path.join(ROOT, "work/short02_40")
OUT_VIDEO = os.path.join(ROOT, "output/STICKMAN_short-02_kalau-matahari-mati_9x16.mp4")
OUT_THUMB = os.path.join(ROOT, "output/thumbnail_short_ep02.jpg")
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30
SR = 48000

# 12 segmen VO kronologis dipetakan secara presisi ke 40 gambar unik (batch1_01 .. batch4_10)
SEGMENTS = [
    # 01: Kondisi Matahari & Bumi Hari Ini (3 gambar: batch1_01..03)
    ("sun50_01.mp3", (3.96, 18.20), " birds_day", [
        ("batch1_01.jpg", "zoom_in",  "Bumi hari ini: kota kanal yang damai di bawah sinar Matahari stabil"),
        ("batch1_02.jpg", "pan_down", "Observatorium gunung & ruang kontrol bawah tanah memantau fusi inti Matahari"),
        ("batch1_03.jpg", "zoom_out", "Lembah subur, bendungan air, dan kincir kayu di iklim Bumi yang ideal"),
    ]),
    # 02: Asal-usul Cahaya & Sabuk Layak Huni menuju Pemanasan Awal (3 gambar: tahap1_10 ref / batch1_04..06)
    ("sun50_09_origin.mp3", None, "lab_hum", [
        ("batch1_04.jpg", "zoom_in",  "+500 Juta Tahun: Matahari makin terik, warga mengantre air pendingin di kota batu"),
        ("batch1_05.jpg", "pan_up",   "+800 Juta Tahun: Tebing gletser es kutub runtuh mencair menenggelamkan menara"),
        ("batch1_06.jpg", "zoom_in",  "+1 Miliar Tahun: Sungai mengering, warga menggali sumur dalam di ngarai retak"),
    ]),
    # 03: +1 Miliar Tahun - Lautan Menguap & Pesisir Mendidih (3 gambar: batch1_07..09)
    ("sun50_02.mp3", (3.30, 15.28), "steam_boil", [
        ("batch1_07.jpg", "zoom_in",  "+1,1 Miliar Tahun: Air laut pelabuhan mendidih beruap, warga mengungsi ke truk"),
        ("batch1_08.jpg", "pan_down", "+1,2 Miliar Tahun: Badai uap air & petir menghantam pintu terowongan gunung"),
        ("batch1_09.jpg", "zoom_out", "+1,5 Miliar Tahun: Instalasi pipa penyulingan air raksasa di gua bawah tanah"),
    ]),
    # 04: +1,5 - 2,5 Miliar Tahun - Eksodus Bawah Tanah & Samudra Mengering (3 gambar: batch1_10, batch2_01, batch2_02)
    ("sun50_10_moist_uv.mp3", None, "wind_shelter", [
        ("batch1_10.jpg", "pan_down", "+2 Miliar Tahun: Permukaan 100°C, eksodus ke kota bunker & hidroponik bawah tanah"),
        ("batch2_01.jpg", "zoom_in",  "+2,5 Miliar Tahun: Samudra menguap habis menyisakan kapal kandas & kerangka paus"),
        ("batch2_02.jpg", "zoom_out", "+2,8 Miliar Tahun: Lempeng tektonik macet, gunung berapi meletus di atas bunker"),
    ]),
    # 05: +3 Miliar Tahun - Neraka Rumah Kaca Kembaran Venus (3 gambar: batch2_03..05)
    ("sun50_03.mp3", None, "venus_furnace", [
        ("batch2_03.jpg", "zoom_in",  "+3 Miliar Tahun: Awan asam pekat & gedung meleleh, Bumi menjadi kembaran Venus"),
        ("batch2_04.jpg", "pan_down", "+3,5 Miliar Tahun: Cadangan air gua bawah tanah terakhir mengering tersisa lumpur"),
        ("batch2_05.jpg", "zoom_out", "+4 Miliar Tahun: Silo gunung terbuka, pemuatan tanaman ke roket evakuasi bawah tanah"),
    ]),
    # 06: +4,5 Miliar Tahun - Tektonik & Hidrogen Inti Mulai Habis (3 gambar: batch2_06..08)
    ("sun50_11_tectonic_venus.mp3", None, "alarm_rumble", [
        ("batch2_06.jpg", "zoom_in",  "+4,5 Miliar Tahun: Dek observasi memantau gejolak Matahari saat hidrogen inti habis"),
        ("batch2_07.jpg", "pan_up",   "+5 Miliar Tahun: Matahari membengkak menjadi bintang Sub-Raksasa jingga raksasa"),
        ("batch2_08.jpg", "zoom_out", "+5,2 Miliar Tahun: Angin surya merobohkan menara radio, bunker dikunci rapat"),
    ]),
    # 07: +5,5 - 6,5 Miliar Tahun - Sub-Raksasa ke Raksasa Merah Menelan Merkurius (4 gambar: batch2_09, batch2_10, batch3_01, batch3_02)
    ("sun50_04.mp3", None, "solar_roar", [
        ("batch2_09.jpg", "zoom_in",  "+5,5 Miliar Tahun: Kerak planet Merkurius retak meleleh di bawah dinding api surya"),
        ("batch2_10.jpg", "zoom_out", "+6 Miliar Tahun: Planet Merkurius ditelan bulat-bulat oleh Raksasa Merah"),
        ("batch3_01.jpg", "pan_down", "+6,5 Miliar Tahun: Atmosfer pekat Venus terbakar menjadi ekor api raksasa"),
        ("batch3_02.jpg", "zoom_in",  "+6,8 Miliar Tahun: Planet Venus jatuh berpilin dan ditelan Raksasa Merah"),
    ]),
    # 08: +7 Miliar Tahun - Raksasa Merah 200x Lipat & Bumi Meleleh Jadi Samudra Lava (4 gambar: batch3_03..06)
    ("sun50_05.mp3", None, "lava_melt", [
        ("batch3_03.jpg", "zoom_in",  "+7 Miliar Tahun: Raksasa Merah 200x lipat memenuhi langit di atas jembatan membara"),
        ("batch3_04.jpg", "pan_down", "+7,1 Miliar Tahun: Tebing gunung batu Bumi meleleh menjadi air terjun magma pijar"),
        ("batch3_05.jpg", "zoom_out", "+7,2 Miliar Tahun: Seluruh kerak Bumi berubah menjadi samudra lava pijar 1500°C"),
        ("batch3_06.jpg", "zoom_in",  "+7,3 Miliar Tahun: Kapal induk evakuasi meninggalkan Bumi yang berpijar lava"),
    ]),
    # 09: +7,4 - 7,55 Miliar Tahun - Bulan Es Europa Mencair Menjadi Lautan Baru (3 gambar: batch3_07..09)
    ("sun50_06.mp3", (1.33, 16.68), "ice_thaw_water", [
        ("batch3_07.jpg", "pan_up",   "+7,4 Miliar Tahun: Pos teleskop di bulan Jupiter menyambut bergesernya zona hangat"),
        ("batch3_08.jpg", "zoom_in",  "+7,5 Miliar Tahun: Tebing gletser es bulan Europa mencair menjadi air terjun deras"),
        ("batch3_09.jpg", "zoom_out", "+7,55 Miliar Tahun: Permukiman terapung & kebun hijau di lautan hangat baru Europa"),
    ]),
    # 10: +7,6 - 7,8 Miliar Tahun - Kilatan Helium 100 Juta Derajat & Denyut Termal (3 gambar: batch3_10, batch4_01, batch4_02)
    ("sun50_12_helium_flash.mp3", None, "helium_blast", [
        ("batch3_10.jpg", "zoom_in",  "+7,6 Miliar Tahun: Kilatan Helium 100 juta derajat mengguncang ruang seismik bawah tanah"),
        ("batch4_01.jpg", "pan_up",   "+7,7 Miliar Tahun: Denyut termal raksasa melontarkan cincin gelombang gas Matahari"),
        ("batch4_02.jpg", "zoom_out", "+7,8 Miliar Tahun: Kulit gas luar Matahari terlepas membubung ke angkasa"),
    ]),
    # 11: +7,9 - 8,5 Miliar Tahun - Nebula Planeter & Inti Katai Putih Seukuran Bumi (4 gambar: batch4_03..06)
    ("sun50_07.mp3", None, "nebula_chime", [
        ("batch4_03.jpg", "zoom_in",  "+7,9 Miliar Tahun: Kelahiran Nebula Planeter zamrud-ungu di atas observatorium gunung"),
        ("batch4_04.jpg", "pan_down", "+8 Miliar Tahun: Nebula memudar menyisakan titik Katai Putih di atas es yang membeku"),
        ("batch4_05.jpg", "zoom_in",  "Kepadatan Katai Putih: derek baja mengangkat sampel inti padat yang meretakkan batu"),
        ("batch4_06.jpg", "zoom_out", "+9 Miliar Tahun: Sungai lava masa lalu membeku jadi ngarai obsidian di bawah Katai Putih"),
    ]),
    # 12: +10 Miliar Tahun+ - Katai Hitam & Kelahiran Bintang/Planet Baru dari Debu Bintang (4 gambar: batch4_07..10)
    ("sun50_08.mp3", None, "rebirth_finale", [
        ("batch4_07.jpg", "zoom_in",  "+10 Miliar Tahun: Katai Putih mendingin dan mengkristal menjadi berlian karbon redup"),
        ("batch4_08.jpg", "pan_down", "Akhir Abadi: Katai Hitam gelap di langit beku & kehidupan di bunker geotermal bawah tanah"),
        ("batch4_09.jpg", "zoom_in",  "Daur Ulang Kosmik: Abu nebula Matahari memadat melahirkan bintang-bintang muda baru"),
        ("batch4_10.jpg", "zoom_out", "Siklus Kehidupan Baru: Lembah hijau subur yang lahir dari debu bintang kuno"),
    ]),
]


def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{r.stderr[-1200:]}")
    return r


def dur(path):
    r = subprocess.run([FF, "-i", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in r.stderr.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Cannot parse duration: {path}")


def build_thumbnail():
    """Bangun Thumbnail 9:16 dari gabungan adegan environmental terbaik (batch1_01, batch1_10, batch3_04, batch4_03)."""
    W, H = 1080, 1920
    canvas = Image.new("RGB", (W, H), (15, 12, 10))
    # Gunakan batch3_04 (tebing gunung meleleh menjadi air terjun lava + stickman berlari di jembatan baja) sebagai hero utama
    hero = Image.open(os.path.join(IMG, "batch3_04.jpg")).convert("RGB")
    sw, sh = hero.size
    target_r = W / H
    if sw / sh > target_r:
        nw = int(sh * target_r)
        left = (sw - nw) // 2
        hero = hero.crop((left, 0, left + nw, sh))
    else:
        nh = int(sw / target_r)
        top = (sh - nh) // 2
        hero = hero.crop((0, top, sw, top + nh))
    hero = hero.resize((W, H), Image.LANCZOS)
    hero = ImageEnhance.Contrast(hero).enhance(1.06)
    canvas.paste(hero, (0, 0))

    # Tambahkan 4 panel progresi tahap di bagian atas (Bumi Cerah -> Bunker 100°C -> Lava 1500°C -> Nebula & Katai Hitam)
    strip_files = ["batch1_01.jpg", "batch1_10.jpg", "batch3_05.jpg", "batch4_03.jpg"]
    pw, ph = 248, 320
    gap = 12
    start_x = (W - (pw * 4 + gap * 3)) // 2
    y_top = 42
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle([start_x - 14, y_top - 14, start_x + pw * 4 + gap * 3 + 14, y_top + ph + 14],
                           radius=20, fill=(10, 10, 14, 215), outline=(255, 200, 60, 255), width=4)
    for idx, sf in enumerate(strip_files):
        im = Image.open(os.path.join(IMG, sf)).convert("RGB")
        iw, ih = im.size
        r = pw / ph
        if iw / ih > r:
            nw = int(ih * r)
            im = im.crop(((iw - nw) // 2, 0, (iw + nw) // 2, ih))
        else:
            nh = int(iw / r)
            im = im.crop((0, (ih - nh) // 2, iw, (ih + nh) // 2))
        im = im.resize((pw, ph), Image.LANCZOS)
        x = start_x + idx * (pw + gap)
        canvas.paste(im, (x, y_top))
        draw.rectangle([x, y_top, x + pw, y_top + ph], outline=(255, 255, 255, 230), width=3)

    # Banner judul kuning-putih tegas di bawah strip
    draw.rounded_rectangle([44, 392, W - 44, 625], radius=24, fill=(12, 12, 18, 225),
                           outline=(255, 195, 40, 255), width=5)
    f_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 76)
    f_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)

    t1 = "SAAT MATAHARI MATI"
    b1 = draw.textbbox((0, 0), t1, font=f_big)
    x1 = (W - (b1[2] - b1[0])) // 2
    draw.text((x1, 418), t1, font=f_big, fill=(255, 220, 45), stroke_width=8, stroke_fill=(0, 0, 0))

    t2 = "40 TAHAP KRONOLOGIS SEBENARNYA"
    b2 = draw.textbbox((0, 0), t2, font=f_sub)
    x2 = (W - (b2[2] - b2[0])) // 2
    draw.text((x2, 528), t2, font=f_sub, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))

    canvas.save(OUT_THUMB, quality=95)


def prepare_40_frames():
    """Siapkan 40 gambar 1080x1920 tajam tanpa crop berlebih dari batch1_01..batch4_10."""
    os.makedirs(WORK, exist_ok=True)
    W, H = 1080, 1920
    stage_list = []
    idx = 0
    for aud_f, sl, sfx_kind, items in SEGMENTS:
        for src_name, move, desc in items:
            idx += 1
            src_path = os.path.join(IMG, src_name)
            im = Image.open(src_path).convert("RGB")
            sw, sh = im.size
            target_r = W / H
            if sw / sh > target_r:
                nw = int(sh * target_r)
                left = (sw - nw) // 2
                im = im.crop((left, 0, left + nw, sh))
            else:
                nh = int(sw / target_r)
                top = (sh - nh) // 2
                im = im.crop((0, top, sw, top + nh))
            im = im.resize((W, H), Image.LANCZOS)
            im = ImageEnhance.Contrast(im).enhance(1.03)
            im = ImageEnhance.Sharpness(im).enhance(1.08)
            out_path = os.path.join(WORK, f"scene_{idx:02d}.jpg")
            im.save(out_path, quality=95)
            stage_list.append({
                "idx": idx,
                "src": src_name,
                "img": out_path,
                "move": move,
                "sfx": sfx_kind,
                "desc": desc,
            })
    return stage_list


def build_vo_and_assign_durations(stage_list):
    """Rapikan 12 segmen VO kronologis agar total durasi berada di ~102 detik (1:42, tepat di rentang 1:30 - 1:50)."""
    vo_wavs = []
    seg_idx = 0
    cursor = 0
    for aud_f, sl, sfx_kind, items in SEGMENTS:
        seg_idx += 1
        src = os.path.join(AUD, aud_f)
        dst = os.path.join(WORK, f"vo40_{seg_idx:02d}.wav")
        trim = f"atrim={sl[0]}:{sl[1]},asetpts=PTS-STARTPTS," if sl else ""
        fc = (f"[0:a]{trim}silenceremove=start_periods=1:start_silence=0.04:start_threshold=-34dB:"
              f"stop_periods=-1:stop_silence=0.06:stop_threshold=-34dB,"
              f"atempo=1.36,afade=t=in:st=0:d=0.02,apad=pad_dur=0.08[a]")
        run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
             "-filter_complex", fc, "-map", "[a]", "-ar", str(SR), "-ac", "2",
             "-c:a", "pcm_s16le", dst])
        d = dur(dst)
        vo_wavs.append(dst)
        n_items = len(items)
        per_item = d / n_items
        for k in range(n_items):
            stage_list[cursor + k]["dur"] = per_item
        cursor += n_items

    total_dur = sum(s["dur"] for s in stage_list)
    vo_list_txt = os.path.join(WORK, "vo40_list.txt")
    with open(vo_list_txt, "w") as f:
        for w in vo_wavs:
            f.write(f"file '{w}'\n")
    vo_master = os.path.join(WORK, "vo40_master.wav")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vo_list_txt, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", vo_master])
    return vo_master, total_dur


def synth_sfx_40(stage_list, total_dur):
    """Sintesis Foley SFX fisik diegetik untuk 40 adegan (tanpa musik sama sekali)."""
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

        # Transisi lembut antar gambar (paper/mechanical whoosh halus)
        w_len = min(int(0.14 * SR), n)
        wt = np.linspace(0, 0.14, w_len, endpoint=False)
        whoosh = rng.normal(0, 0.035, w_len) * np.sin(np.pi * wt / 0.14)
        add_stereo(whoosh, whoosh * 0.9, cursor)

        # Karakteristik suara fisik sesuai gambar
        noise = rng.normal(0, 1.0, n)
        if "day" in kind or "rebirth" in kind:
            # Gemericik air sungai & angin sepoi
            water = np.convolve(noise, np.ones(18) / 18, mode="same") * 0.045
            add_stereo(water, water * 0.95, cursor)
        elif "steam" in kind or "wind" in kind:
            # Desis uap air mendidih & angin badai
            hiss = np.convolve(noise, np.ones(8) / 8, mode="same") * 0.075
            rumble = 0.06 * np.sin(2 * np.pi * 58 * t)
            add_stereo(hiss + rumble, hiss * 0.9 + rumble, cursor)
        elif "lava" in kind or "solar" in kind or "venus" in kind:
            # Gemuruh magma pijar & api Raksasa Merah
            roar = np.convolve(noise, np.ones(45) / 45, mode="same") * 0.11
            sub = 0.08 * np.sin(2 * np.pi * 46 * t)
            add_stereo(roar + sub, roar * 0.92 + sub, cursor)
        elif "helium" in kind or "alarm" in kind:
            # Dentuman seismik & dering mekanis bunker
            boom = 0.12 * np.sin(2 * np.pi * (95 * np.exp(-t * 2.2) + 38) * t) * np.exp(-t * 1.4)
            add_stereo(boom, boom, cursor)
        else:
            # Atmosfer laboratorium/observatorium/air mencair
            amb = np.convolve(noise, np.ones(30) / 30, mode="same") * 0.055
            add_stereo(amb, amb * 0.95, cursor)

        cursor += d

    peak = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
    stereo = np.stack([left / peak * 0.28, right / peak * 0.28], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    sfx_wav = os.path.join(WORK, "sfx40_master.wav")
    with wave.open(sfx_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
    return sfx_wav


def render_clip(st):
    """Render setiap gambar 9:16 dengan kamera lembut (z=1.00..1.05) agar bagian atas & bawah gambar 100% utuh."""
    idx = st["idx"]
    d = st["dur"]
    frames = max(1, int(round(d * FPS)))
    out_mp4 = os.path.join(WORK, f"clip_{idx:02d}.mp4")
    move = st["move"]

    if move == "zoom_in":
        z_expr = f"1.00+0.045*on/{frames}"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif move == "zoom_out":
        z_expr = f"1.045-0.045*on/{frames}"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = "ih/2-(ih/zoom/2)"
    elif move == "pan_down":
        z_expr = "1.04"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"(ih-ih/zoom)*(on/{frames})"
    else:  # pan_up
        z_expr = "1.04"
        x_expr = "iw/2-(iw/zoom/2)"
        y_expr = f"(ih-ih/zoom)*(1-on/{frames})"

    vf = (
        f"scale=2160:3840:flags=lanczos,"
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s=1080x1920:fps={FPS},"
        f"format=yuv420p"
    )
    run([
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-i", st["img"],
        "-vf", vf,
        "-frames:v", str(frames),
        "-t", f"{d:.4f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_mp4
    ])
    return out_mp4


def main():
    print("1/5 Membangun Thumbnail 9:16 ('output/thumbnail_short_ep02.jpg')...")
    build_thumbnail()
    print("2/5 Menyiapkan 40 gambar mahakarya unik ('batch1_01..batch4_10')...")
    stage_list = prepare_40_frames()
    print("3/5 Merapikan 12 segmen VO kronologis & membagi durasi ke 40 gambar...")
    vo_master, total_dur = build_vo_and_assign_durations(stage_list)
    print(f"    Total durasi 40 gambar: {total_dur:.2f}s ({int(total_dur//60)}:{total_dur%60:05.2f}, rata-rata {total_dur/40:.2f}s/gambar)")
    print("4/5 Menyintesis track Foley SFX fisik 40 tahap & merender 40 klip video...")
    sfx_master = synth_sfx_40(stage_list, total_dur)

    clips = []
    for st in stage_list:
        c = render_clip(st)
        clips.append(c)
        if st["idx"] % 10 == 0 or st["idx"] == 1:
            print(f"    [{st['idx']:02d}/40] {st['src']} ({st['dur']:.2f}s) - {st['desc']}")

    vlist = os.path.join(WORK, "v40_list.txt")
    with open(vlist, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    v_concat = os.path.join(WORK, "v40_concat.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", vlist, "-c", "copy", v_concat])

    print("5/5 Mastering audio (VO -14 LUFS + Foley SFX 40 tahap, 0% musik, 0% subtitle) & muxing MP4...")
    fc = (
        "[1:a]loudnorm=I=-14:TP=-1.5:LRA=9,volume=1.05[vo];"
        "[2:a]volume=0.52[sfx];"
        "[vo][sfx]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
    )
    run([
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-i", v_concat,
        "-i", vo_master,
        "-i", sfx_master,
        "-filter_complex", fc,
        "-map", "0:v:0", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-t", f"{total_dur:.3f}",
        "-movflags", "+faststart",
        OUT_VIDEO
    ])
    final_d = dur(OUT_VIDEO)
    print(f"\nSELESAI: {OUT_VIDEO} ({final_d:.2f}s / {int(final_d//60)}:{final_d%60:05.2f}, 40 gambar unik)")


if __name__ == "__main__":
    main()
