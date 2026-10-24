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

## Karakter baku (final)
Stickman klasik: kepala bulat putih + kacamata hitam + kemeja putih + dasi hitam
+ jas abu tua. Blok prompt & aturan ada di `docs/03-KARAKTER-BAKU.md`.
Model sheet: `assets/images/char/character-sheet-v2.jpg`

## Episode 02 — "Kalau Matahari Mati"
- Naskah 9:16 lengkap (45 shot, 8 kartu transisi, tanpa musik):
  `script/02-NASKAH-KALAU-MATAHARI-MATI.md`
- Gambar kunci tahap 1 (desain karakter baru): ep02_s01, s02, s03, s09, s10, s17, s21, s28
- Audio: ep02_coldopen.mp3, ep02_intro.mp3, ep02_bab1.mp3

## Aset EP02 (karakter baku "Si Profesional")
- 37 dari 45 shot selesai (s16 sudah diregenerasi, bersih)
- 8 kartu transisi final (programatik, bukan AI): `assets/cards/k0..k7.jpg`
  generator: `pipeline/cards.py`
- Sisa: s06, s31, s33, s35, s36, s38, s40, s42

## Render EP02 (5:07, tanpa musik)
- `pipeline/render_ep02.py` — merakit 45 item (kartu + shot), audio diisi DIAM
  sepanjang durasi kartu sehingga video & narasi selalu sinkron
- `pipeline/capstyle.py` — gaya caption bersama (auto-fit, hero number)
- `pipeline/ep02_storyboard.py` — peta shot/segmen/kartu/gerak kamera
- Output: `output/STICKMAN_ep02_kalau-matahari-mati_9x16.mp4`
  (5:07, 1080x1920, audio -14 LUFS, room tone saja, TANPA musik)
