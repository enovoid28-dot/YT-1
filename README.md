# SAINS CORET — Short #1: "Titik Putih di Tepi Lubang Hitam"

Channel YouTube berbahasa Indonesia: animasi stick figure 2D flat (gaya kartun
garis hitam tebal, karakter berkepala bulat putih ekspresif) dengan tema sains
antariksa. Nada: komedi tegang, fakta tetap akurat.

## Struktur repo
- `script/skrip-id.md` — naskah VO + 33 tahap storyboard + caption
- `pipeline/` — generator video (Python: PIL + numpy + ffmpeg imageio)
- `assets/` — gambar & audio mentah (besar) disimpan di Google Drive, tidak di Git
- `output/` — hasil final short (mp4) + thumbnail

## Catatan
Repo ini sengaja hanya berisi teks & skrip kecil. Aset biner (gambar 9:16,
audio narasi, render video) disimpan di Google Drive.

## Status produksi (short #1)
- [x] Nama channel & tone disetujui (SAINS CORET, komedi tegang)
- [x] Naskah VO 10 segmen + 33 tahap storyboard
- [x] Narasi pria Indonesia dirender (2:19 total)
- [x] Gambar tahap 1-23 selesai
- [x] Gambar tahap 24-33 selesai (33/33)
- [x] Render final 33 tahap -> 2:18, 1080x1920, audio -14 LUFS
- [x] Thumbnail 1080x1920 dengan judul

## Google Drive (aset)
Folder utama: `SAINS CORET`
https://drive.google.com/drive/folders/1eWA1AKTS_Z6ErPsN6fb6ilkvBbUIStUZ
- 01 - Thumbnail
- 02 - Video Short
- 03 - Judul Deskripsi Hashtag Tag
- 04 - Gambar Storyboard 33 Tahap
- 05 - Audio Narasi
- 06 - Naskah dan Acuan Produksi

## Cara render
```
python3 pipeline/build_audio.py     # gabung VO -> narasi.wav + timeline
python3 pipeline/thumbnail.py       # thumbnail 1080x1920
python3 pipeline/render.py          # render semua tahap yang gambarnya ada
python3 pipeline/render.py --preview 3   # uji cepat 3 klip
```

## Hasil akhir
- Video: `SAINS-CORET_short-01_titik-putih_1080x1920_FINAL.mp4` (Drive: 02 - Video Short)
  https://drive.google.com/file/d/1DDthPU8TKCVGB-d-3fB_GIDfZPamX_FE/view
- Thumbnail: https://drive.google.com/file/d/102mjBvapZ6ElnJBF6rkPIWtHBFykRVX_/view
- Judul/deskripsi/tag: folder 03 (Google Doc)

## Paket naskah & caption (tanpa musik)
- `script/00-FORMAT-BAKU-NASKAH.md` — aturan wajib semua episode
  (cold open, intro, 4-5 bab, titik balik, outro, end card; aturan caption; desain suara)
- `script/01-NASKAH-DI-MANA-SEMUANYA.md` — naskah utuh EP01 (8 menit) + versi Short 55 detik
- `pipeline/caption_style.py` — generator contoh caption 9:16 & 16:9
- Drive: folder `07 - Paket Naskah dan Caption`

## Karakter baku (final — Gaya *Mr Sticky*)
Stickman klasik polos **tanpa pakaian**: kepala bulat putih bersih + **hanya memakai kacamata hitam kotak** (badan, tangan, dan kaki murni garis hitam tipis sederhana tanpa baju/jas/dasi). Blok prompt & aturan ada di `docs/03-KARAKTER-BAKU.md`.
Model sheet: `assets/images/char/character-sheet-v2.jpg`

## Episode 02 — "Kalau Matahari Mati"
- Naskah 9:16 lengkap (45 shot, 8 kartu transisi, tanpa musik):
  `script/02-NASKAH-KALAU-MATAHARI-MATI.md`
- Gambar kunci tahap 1 (desain karakter baru): ep02_s01, s02, s03, s09, s10, s17, s21, s28
- Audio: ep02_coldopen.mp3, ep02_intro.mp3, ep02_bab1.mp3

## Aset EP02 (karakter baku "Si Profesional")
- 45 dari 45 shot SELESAI 100% (`ep02_s01.jpg` s/d `ep02_s45.jpg`, sudah di-QA & di-upload ke Google Drive)
- 8 kartu transisi final (programatik, bukan AI): `assets/cards/k0..k7.jpg` (`pipeline/cards.py`)
- 10 segmen audio narasi lengkap (`ep02_coldopen.mp3` s/d `ep02_endcard.mp3`)
- Thumbnail 9:16 (`pipeline/thumbnail_ep02.py`) + metadata siap upload (`docs/metadata-ep02.md`)

## Render EP02 (5:07, tanpa musik)
- `pipeline/render_ep02.py` — merakit 53 item (45 shot unik + 8 kartu transisi), audio diisi DIAM
  sepanjang durasi kartu sehingga video & narasi selalu sinkron
- `pipeline/capstyle.py` — gaya caption bersama (auto-fit, hero number)
- `pipeline/ep02_storyboard.py` — peta shot/segmen/kartu/gerak kamera
- Output: `output/STICKMAN_ep02_kalau-matahari-mati_9x16.mp4`
  (5:07, 1080x1920, audio -14 LUFS, room tone saja, TANPA musik)

## YouTube Short #2 — "8 Menit Terakhir Matahari" (57,47 detik, Gaya *Mr Sticky*, Tanpa Subtitle, Tanpa Musik)
- Naskah & peta Foley SFX: `script/03-SHORT-KALAU-MATAHARI-MATI.md`
- Engine render 20 beat dinamis + synthesizer Foley SFX fisik: `pipeline/render_short_ep02.py`
- 10 ilustrasi 9:16 gaya *Mr Sticky* (`short02_s01.jpg` s/d `short02_s10.jpg`, Stickman polos tanpa pakaian + kacamata hitam + balon *callout* / papan tulis edukatif) -> Google Drive
- Video final: `output/STICKMAN_short-02_kalau-matahari-mati_9x16.mp4` (57,47 detik, 1080x1920, 30 fps, VO -14 LUFS + Foley SFX, 0% musik, 0% subtitle) -> Google Drive
