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
- [ ] Gambar tahap 24-33 (limit 10 gambar/turn)
- [ ] Render final 33 tahap
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
