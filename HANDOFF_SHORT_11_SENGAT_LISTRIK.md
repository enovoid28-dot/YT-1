# HANDOFF PROJECT — CHANNEL @SeorangSains (YouTube Shorts)

File ini berisi semua informasi yang diperlukan AI baru untuk melanjutkan proyek Video Short #11 dari titik onde saya berhenti.

---

## 1. RINGKASAN PROYEK

| Item | Detail |
|------|--------|
| **Channel** | @SeorangSains |
| **Platform** | YouTube Shorts (9:16 vertical) |
| **Bahasa** | Indonesian (narasi, judul, tag) |
| **Resolusi video** | 1080×1920 @ 60fps |
| **Format gambar scene** | JPG, 1080×1920, LANCZOS + UnsharpMask, TANPA teks/huruf/angka/watermark/logo |
| **Audio** | Voiceover only, TANPA musik, TANPA subtitle/caption |
| **Branch git** | `arena/8c1b4b22-yt-1` (repo: `enovoid28-dot/YT-1`) |
| **Short aktif** | #11 — "Apa yang Terjadi Jika Tubuh Tersengat Listrik Tegangan Tinggi?" (Benchmark 42 Juta Views) |

---

## 2. STRUKTUR FILE DI WORKSPACE (`/home/user/YT-1`)

```
script/
  14-SHORT-SENGAT-LISTRIK-TEGANGAN-TINGGI.md   <-- SKRIP LENGKAP 30 ADEGAN (SUDAH ADA)
  00-FORMAT-BAKU-NASKAH.md
  01-NASKAH-DI-MANA-SEMUANYA.md
  ... (skrip lama, tidak relevan untuk Short #11)
pipeline/
  render.py, render_short_ep02.py ... render_short_ep09.py   <-- Renderer lama, bisa dijadikan referensi
  render_long_ep01.py, render_long_ep02.py
  bgm_synthesizer.py, build_audio.py, ... (tools audio lama)
assets/
  images/   <-- KOSONG (menunggu 30 gambar Short #11)
output/     <-- KOSONG (menunggu ZIP, preview, VO, video)
```

**File terpenting yang sudah ada:**
- `script/14-SHORT-SENGAT-LISTRIK-TEGANGAN-TINGGI.md` — Skrip lengkap 30 adegan, 3 tahap, VO Bahasa Indonesia.

---

## 3. SKRIP SHORT #11 — RINGKASAN 30 ADEGAN (3 TAHAP)

**Judul:** "Apa yang Terjadi Jika Tubuh Tersengat Listrik Tegangan Tinggi?"  
**Benchmark:** ~42 Juta Views  
**Durasi target:** < 180 detik (~155–168 detik)  
**Karakter utama:** Stickman biasa (subjek uji coba di lokasi kejadian)  
**Mascot:** @SeorangSains (kacamata hitam, hanya di #01 dan #30)

### TAHAP 1: KONTRAKSI TETANIK — TANGAN TIDAK BISA LEPAS (`#01–#10`)
- #01: Mascot @SeorangSains di lab menunjuk hologram stickman di bawah tiang listrik
- #02: Stickman biasa bekerja di bawah tiang transmisi tegangan tinggi
- #03: Jempol tangan menyentuh ujung kabel listrik (spark biru)
- #04: Arus masuk saraf & otot tangan/lengan (penampang anatomi)
- #05: Otot fleksor berkontraksi, jari mencengkeram kabel erat
- #06: Tangan terkunci ke kabel, tidak bisa dilepas
- #07: Arus mengalir dari jari → lengan → bahu → dada
- #08: Sinyal listrik luar mengacaukan saraf di seluruh tubuh
- #09: Arus mencapai dada & sistem listrik jantung
- #10: Sistem listrik jantung terganggu oleh arus luar

### TAHAP 2: FIBRILASI VENTRIKEL — JANTUNG TERGANGO (`#11–#20`)
- #11: Detak alami digantikan percikan listrik acak di bilik jantung
- #12: Jantung bergetar lemah, tidak memompa darah
- #13: Fibrilasi ventrikel (denyut acak, tidak teratur)
- #14: Otak tidak menerima darah, stickman pingsan
- #15: Otot dada & diafragma terkunci, tidak bisa bernapas
- #16: Jari masih mencengkeram kabel, arus terus mengalir
- #17: Panas listrik merusak jaringan dalam (tangan → dada)
- #18: Jantung berhenti sepenuhnya, tidak ada aliran darah
- #19: Stickman pingsan di tanah, kondisi kritis
- #20: Teman mematikan saklar sumber listrik & memutus kabel

### TAHAP 3: PANAS JOULE & PENYELAMATAN AED (`#21–#30`)
- #21: Jaringan otot & saraf terbakar parah (panas listrik)
- #22: Luka bakar dalam kecil di luar, rusak parah di dalam
- #23: Tim medis tiba dengan defibrilator AED
- #24: Dua elektroda AED diletakkan dada kiri & kanan
- #25: AED memberikan kejutan listrik singkat
- #26: Detak jantung alami mulai kembali
- #27: Stickman bernapas lagi, kesadaran balik
- #28: Dibawa ke rumah sakit untuk perawatan lanjutan
- #29: Peringatan jangan menyentuh kabel tegangan tinggi
- #30: Mascot @SeorangSains di lab, layar hologram peringatan

**Lihat isi lengkap:** `script/14-SHORT-SENGAT-LISTRIK-TEGANGAN-TINGGI.md`

---

## 4. ATURAN VISUAL (WAJIB DIPATUHI)

### Karakter Stickman Biasa (digunakan di #02–#29)
- Kepala: bulat putih, outline tebal hitam
- Wajah: kartun ekspresif (mata, mulut)
- Tubuh: **satu garis hitam tipis tunggal** untuk badan, lengan, kaki (kurus)
- **TIDAK ada pakaian**
- **TIDAK ada lengan berdaging/fleshy arms**
- Tangan: kartun berwarna putih
- **TIDAK ada kacamata** (hanya mascot yang pakai kacamata hitam)
- **TIDAK ada halotan/outline putih di sekitar tubuh**

### Mascot @SeorangSains (hanya #01 dan #30)
- Sama seperti stickman tapi **menggunakan kacamata hitam detail**
- Digunakan di pembuka dan penutup saja

### Aturan Umum Semua Gambar Scene
- **TIDAK ADA teks, huruf, angka, watermark, atau logo** di dalam gambar
- Aspek rasio: 9:16 (1080×1920)
- Setiap adegan harus **urut secara kronologis** dan **fisik logis**
- Tidak ada AI slop / gambar cacat — periksa setiap gambar via `read_file`, regenerasi yang cacat
- Latar gelap untuk anatomi internal: `#1E293B` (dark slate)
- Normalisasi: `PIL.ImageOps.fit(..., (1080,1920), LANCZOS)` lalu `UnsharpMask(radius=1.2, percent=115, threshold=2)`
- Simpan JPG quality 96, subsampling 0

---

## 5. ATURAN VOICEOVER (VO)

- Bahasa Indonesia
- **12–13 kata per kalimat**, uniform di semua chunk
- Sintesis dalam **6 chunk** (`vo_short11_c1.mp3` … `c6.mp3`)
- Setiap chunk ~5 kalimat (~60–65 kata)
- **Jangan rapikan jeda intra-kalimat** (keep natural pauses) — agar tidak terdengar "seperti rapper"
- Jeda antar-kalimat ~0.25–0.30 detik
- Total durasi < 180 detik (target ~155–168 detik)
- **TANPA musik latar** (`"Jangan ada musik!"`)
- **TANPA subtitle / caption**
- Gabung 6 chunk jadi `VO_Master_Short11_30_Adegan_9x16.mp3`
- Buat `short11_timeline_30_scenes.json` dengan timing eksak setiap adegan
- Voice: `voice-00` (gunakan add_voice → generate_speech)

---

## 6. GOOGLE DRIVE STRUKTUR & FOLDER ID

```
Aset (1-jWwlAm-w_TI7t8B_b0jAtVp0LLEkXYZ)
  └── 01 - Aset Gambar (1Prb7PSiJc0IoGYppbc7besDRufXWRIGS)
        └── [Short #11 files go here]
  └── 02 - Aset Voiceover (1nxqZgfqmNqCpwmnrZK1_9aoZR6F5cjK_)
        └── [VO files go here]

YT 1 @SeorangSains (1sf3HBcPtHhvGOYLQMCsiqYGpRxHrw3xy)
  └── 02 - Video Short (1cVJ1GSdS4RiHy4F96bhD9FxOiAOMbNLr)
        └── [Final video goes here]
  └── 04 - Metadata & Naskah (1czF1Szh1F8CKmKXxcke79VtQAH01LGU6)
        └── [Script goes here]
```

**Catatan:** Gambar, audio, dan video diunggah ke Google Drive ONLY — TIDAK ke GitHub. Repo hanya berisi text/code/scripts.

---

## 7. STATUS SAAT INI (Tanggal 2026-10-30)

| Tugas | Status | Keterangan |
|-------|--------|------------|
| Skrip 30 adegan | ✅ SELESAI | `script/14-SHORT-SENGAT-LISTRIK-TEGANGAN-TINGGI.md` |
| Generate 30 gambar scene | ❌ BELUM | API generate_image menghasilkan error 403 Forbidden |
| Normalisasi gambar ke 1080×1920 | ❌ BELUM | Menunggu gambar berhasil di-generate |
| ZIP backup + preview grid | ❌ BELUM | Menunggu 30 gambar |
| Upload aset ke Google Drive | ❌ BELUM | Menunggu ZIP & preview |
| Sintesis VO 6 chunk | ❌ BELUM | Menunggu generate_speech |
| Gabung VO Master + timeline JSON | ❌ BELUM | Menunggu VO chunks |
| Render video final 1080×1920 @ 60fps | ❌ BELUM | Menunggu semua gambar + VO |
| Upload video ke Google Drive | ❌ BELUM | Menunggu render |

**Pembatasan saat ini:** API `generate_image` mengembalikan `403 Forbidden` ("account flagged for suspicious activity"). Ini terjadi sejak tengah sesi dan masih aktif. Perlu mencoba ulang setiap beberapa turn hingga pulih.

---

## 8. URUTAN KERJA SELANJUTNYA (AI BARU)

### Langkah 1: Coba generate gambar lagi
Coba `generate_image` untuk `assets/images/short11_intro_01.jpg`. Jika masih 403, tunggu beberapa turn dan coba lagi.

### Langkah 2: Generate 30 gambar (10 per turn, parallel)
**Batch 1 — #01–#10:** `short11_intro_01.jpg`, `_02.jpg`, `_03.jpg`, `short11_t1_01.jpg`…`07.jpg`  
**Batch 2 — #11–#20:** `short11_t2_01.jpg`…`10.jpg`  
**Batch 3 — #21–#30:** `short11_t3_01.jpg`…`10.jpg`

Setiap batch:
1. Generate 10 image secara parallel
2. Inspect semua via `read_file` — pastikan 100% bebas teks, cacat, dan urutan konsisten
3. Regenerasi yang cacat
4. Normalisasi semua ke `1080×1920` (LANCZOS + UnsharpMask)
5. Buat `BACKUP_Short11_Scenes_XX_to_YY.zip`
6. Buat `PREVIEW_Short11_BatchX_XX_to_YY_9x16.jpg` (grid 5×2)
7. Upload ZIP + preview ke Google Drive folder `1Prb7PSiJc0IoGYppbc7besDRufXWRIGS`

### Langkah 3: Sintesis VO
1. `add_voice` untuk registrasi speaker (kalau belum ada voice-00)
2. `generate_speech` 6 chunk (`vo_short11_c1.mp3` … `c6.mp3`), voice-00, bahasa Indonesia
3. Gabung jadi `VO_Master_Short11_30_Adegan_9x16.mp3`
4. Buat `short11_timeline_30_scenes.json` (total < 180s)
5. Upload VO Master ke Google Drive folder `1nxqZgfqmNqCpwmnrZK1_9aoZR6F5cjK_`

### Langkah 4: Render Video Final
- Gunakan renderer di `pipeline/` (referensi `render_short_ep02.py` … `ep09.py`) atau buat `render_short_ep11.py`
- Input: 30 gambar `1080×1920` + `VO_Master_Short11_30_Adegan_9x16.mp3` + timeline JSON
- Output: `output/VIDEO_SHORT_11_Sengat_Listrik_Tegangan_Tinggi_9x16_1080p_60fps.mp4`
- Tanpa subtitle, tanpa musik
- Upload ke Google Drive folder `1cVJ1GSdS4RiHy4F96bhD9FxOiAOMbNLr`

### Langkah 5: Push ke GitHub
- Hanya file teks/script (tidak ada image/audio/video)
- Commit ke branch `arena/8c1b4b22-yt-1`

---

## 9. CATATAN PENTING DARI PENGGUNA

- **"Cari topik atau judul yang berpotensi besar mendapatkan lebih banyak views! Bukan asal-asalan! Bukan asal menebak! Saya yang memilih!"** — Selalu riset data-driven dulu, biarkan pengguna memilih via `ask_user`.
- **"Gambar stickman yang memiliki tangan berdaging itu terlihat aneh"** — Setiap stickman: kepala bulat putih, outline tebal hitam, tubuh satu garis tipis, tangan putih, nol halotan putih.
- **"Lanjut, jangan ada musik!"** — Tidak ada musik latar di video.
- **"No subtitles / no captions"** — Tidak ada teks di video.
- **"Ulangi! Hasil gambar ada yang rusak, video seperti blur sedikit!"** — Tidak ever menggambar bentuk PIL di atas scene image. Regenerasi yang cacat secara bersih.
- Karakter stickman biasa menjadi subjek uji coba di lokasi kejadian di setiap tahap.

---

## 10. ERROR YANG PERLU DIINGAT

- `generate_image` 403 Forbidden — akun sedang dibatasi sementara. Coba ulang setiap turn.
- `generate_image` limit 10 per turn — baru bisa generate 10 gambar dalam satu turn.
- Jangan pernah memasukkan teks/angka/kegiatan medis grafis dalam prompt `generate_speech` yang dapat memicu moderasi (gunakan istilah klinis).

---

**File skrip utama:** `script/14-SHORT-SENGAT-LISTRIK-TEGANGAN-TINGGI.md`  
**Branch:** `arena/8c1b4b22-yt-1`  
**Tanggal handoff:** 2026-10-30

Selamat melanjutkan! Semua skrip sudah siap, tinggal generate gambar → VO → render video.