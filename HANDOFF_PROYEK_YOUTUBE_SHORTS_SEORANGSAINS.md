# PANDUAN LENGKAP PROYEK YOUTUBE SHORTS — @SeorangSains

Dokumen ini adalah panduan standalone untuk AI baru yang akan melanjutkan/membangun proyek YouTube Shorts channel **@SeorangSains** dari awal sampai akhir, tanpa referensi ke video apa pun yang pernah dibuat sebelumnya.

---

## 1. IDENTITAS CHANNEL

| Item | Detail |
|------|--------|
| Nama channel | @SeorangSains |
| Platform | YouTube Shorts |
| Bahasa | Indonesian (narasi, judul, tag, deskripsi) |
| Aspek rasio video | 9:16 vertical (1080×1920) |
| Frame rate | 60fps |
| Mascot utama | Stickman dengan kacamata hitam detail (hanya di pembuka dan penutup) |
| Karakter reguler | Stickman biasa (tanpa kacamata) sebagai subjek uji coba di lokasi kejadian |

---

## 2. ATURAN KARAKTER STICKMAN (WAJIB DIPATUHI)

### Stickman Biasa (digunakan di semua adegan kecuali pembuka & penutup)
- **Kepala:** bulat putih dengan outline tebal hitam
- **Wajah:** kartun ekspresif (mata dan mulut yang jelas)
- **Tubuh:** **satu garis hitam tipis tunggal** untuk badan, lengan, dan kaki (strictly kurus)
- **TIDAK ada pakaian** (tidak ada kemeja, jaket, celana, dll.)
- **TIDAK ada lengan berdaging / fleshy arms**
- **Tangan:** kartun berwarna putih
- **TIDAK ada kacamata** (hanya mascot yang pakai)
- **TIDAK ada halotan / outline putih di sekitar tubuh**

### Mascot @SeorangSains (hanya pembuka & penutup)
- Sama seperti stickman biasa tapi **menggunakan kacamata hitam detail**
- Digunakan hanya di adegan pertama dan terakhir sebagai pemandu narasi

---

## 3. ATURAN VISUAL GAMBAR SCENE (WAJIB)

- **Resolusi:** 1080×1920 (9:16)
- **Format:** JPG, quality 96, subsampling 0
- **Normalisasi:** `PIL.ImageOps.fit(..., (1080,1920), LANCZOS)` lalu `ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2)`
- **TIDAK ADA teks, huruf, angka, watermark, logo, atau caption di dalam gambar scene** (zero typography)
- Setiap adegan harus **urut secara kronologis** dan **fisik logis**
- Tidak ada AI slop / gambar cacat — periksa setiap gambar via `read_file`, regenerasi yang cacat
- Latar gelap untuk anatomi internal: `#1E293B` (dark slate)
- **Tidak pernah menggambar bentuk PIL di atas scene image** — regenerasi yang cacat secara bersih via `generate_image`

---

## 4. ATURAN VOICEOVER (VO)

- **Bahasa:** Indonesia
- **Jumlah kata per kalimat:** 12–13 kata, uniform di semua chunk
- **Jumlah chunk:** 6 chunk (`c1` … `c6`)
- **Pacing:** Normal, calm, tidak terlalu cepat (hindari nada "seperti rapper")
- **Jeda intra-kalimat:** Jangan rapikan — pertahankan jeda alami (natural pauses)
- **Jeda antar-kalimat:** ~0.25–0.30 detik
- **Durasi total:** < 180 detik (target ~155–168 detik)
- **TIDAK ada musik latar** (`"Jangan ada musik!"`)
- **TIDAK ada subtitle / caption**
- **Voice:** `voice-00` (hasil add_voice)
- **File output:** `VO_Master_ShortXX_30_Adegan_9x16.mp3` + `shortXX_timeline_30_scenes.json`

---

## 5. STRUKTUR STORYBOARD (30 ADEGAN, 3 TAHAP, 3 BATCH)

Setiap Short harus terdiri dari **30 adegan** dibagi menjadi **3 tahap**, setiap tahap 10 adegan:

| Batch | Adegan | Tahap | Contoh Fokus |
|-------|--------|-------|--------------|
| Batch 1 | #01–#03 | Pembuka / Intro | Mascot memperkenalkan fenomena |
| Batch 1 | #04–#10 | Tahap 1 | Intinya / mekanisme utama bagian 1 |
| Batch 2 | #11–#20 | Tahap 2 | Intinya / mekanisme utama bagian 2 |
| Batch 3 | #21–#30 | Tahap 3 | Konsekuensi, penanganan, dan penutup |

- Setiap batch terdiri dari **10 gambar**, generate secara **parallel**
- Nama file: `shortXX_intro_01.jpg` … `03.jpg`, `shortXX_t1_01.jpg` … `07.jpg`, dst.
- Setiap adegan harus punya VO dan deskripsi visual yang jelas di skrip

---

## 6. PROSES RISET & PEMILIHAN TOPIK (WAJIB)

Sebelum membuat skrip, AI baru harus:

1. **Lakukan riset data-driven** untuk mencari topik berpotensi views tinggi (mis. benchmarks dari Zack D. Films atau channel serupa)
2. **JANGAN menebak topik asal** — pengguna yang memilih
3. Tampilkan **4 opsi topik** ke pengguna via `ask_user` dengan label `opt_1` … `opt_4`
4. Tunggu pengguna memilih salah satu opsi
5. Baru setelah pilihan, buat skrip

**Aturan pengguna:** *"Cari topik atau judul yang berpotensi besar mendapatkan lebih banyak views! Bukan asal-asalan! Bukan asal menebak! Saya yang memilih!"*

---

## 7. STRUKTUR FILE & FOLDER DI WORKSPACE

```
/home/user/YT-1/ (repo git, branch arena/8c1b4b22-yt-1)
├── script/
│   └── XX-SHORT-JUDUL.md          ← Skrip lengkap 30 adegan (teks only)
├── pipeline/
│   └── render_short_epXX.py       ← Renderer video (opsional, bisa buat baru)
├── assets/
│   └── images/
│       ├── shortXX_intro_01.jpg   ← 30 gambar scene (1080×1920)
│       └── ...
└── output/
    ├── vo_shortXX_c1.mp3 .. c6.mp3 ← 6 chunk VO
    ├── VO_Master_ShortXX_30_Adegan_9x16.mp3
    ├── shortXX_timeline_30_scenes.json
    ├── BACKUP_ShortXX_Scenes_01_to_10.zip
    ├── PREVIEW_ShortXX_BatchX_01_to_10_9x16.jpg
    └── VIDEO_SHORT_XX_..._1080p_60fps.mp4
```

**Aturan:** Gambar, audio, dan video diunggah ke **Google Drive ONLY** — **TIDAK ke GitHub**. Repo git hanya berisi text/code/scripts.

---

## 8. STRUKTUR GOOGLE DRIVE

```
Aset (1-jWwlAm-w_TI7t8B_b0jAtVp0LLEkXYZ)
  └── 01 - Aset Gambar (1Prb7PSiJc0IoGYppbc7besDRufXWRIGS)
        └── [File ZIP backup + preview grid per batch]
  └── 02 - Aset Voiceover (VO) (1nxqZgfqmNqCpwmnrZK1_9aoZR6F5cjK_)
        └── [File VO Master mp3]

YT 1 @SeorangSains (1sf3HBcPtHhvGOYLQMCsiqYGpRxHrw3xy)
  └── 02 - Video Short (1cVJ1GSdS4RiHy4F96bhD9FxOiAOMbNLr)
        └── [File video final mp4]
  └── 04 - Metadata & Naskah (1czF1Szh1F8CKmKXxcke79VtQAH01LGU6)
        └── [File skrip md]
```

---

## 9. PIPELINE AKHIR DARI AWAL SAMPAI AKHIR

### Fase 1: Riset & Pilihan Topik
1. Cari 4 topik viral benchmark (YouTube Shorts, jutaan views)
2. `ask_user` kepada pengguna dengan 4 opsi
3. Tunggu pilihan pengguna

### Fase 2: Skrip 30 Adegan
1. Tulis skrip lengkap 30 adegan, 3 tahap, 3 batch
2. Setiap adegan: VO (Indonesia, 12–13 kata/kalimat) + deskripsi visual
3. Simpan sebagai `script/XX-SHORT-JUDUL.md`
4. Push ke GitHub + upload ke Google Drive `04 - Metadata & Naskah`

### Fase 3: Generate Gambar (30 file, 10 per turn)
1. Buat 10 prompt gambar per batch (parallel)
2. `generate_image` setiap file
3. Inspect semua via `read_file` — pastikan 100% bebas teks, cacat, dan urutan konsisten
4. Regenerasi yang cacat
5. Normalisasi semua ke `1080×1920` (LANCZOS + UnsharpMask)
6. Buat ZIP backup per batch: `BACKUP_ShortXX_Scenes_XX_to_YY.zip`
7. Buat preview grid 5×2 per batch: `PREVIEW_ShortXX_BatchX_XX_to_YY_9x16.jpg`
8. Upload ZIP + preview ke Google Drive `01 - Aset Gambar`

### Fase 4: Sintesis VO
1. `add_voice` untuk registrasi speaker (dapatkan `voice_id`)
2. `generate_speech` 6 chunk (`vo_shortXX_c1.mp3` … `c6.mp3`), bahasa Indonesia, voice-00
3. Gabung 6 chunk jadi `VO_Master_ShortXX_30_Adegan_9x16.mp3`
4. Buat `shortXX_timeline_30_scenes.json` (total < 180s)
5. Upload VO Master ke Google Drive `02 - Aset Voiceover (VO)`

### Fase 5: Render Video Final
1. Gabungkan 30 gambar + VO Master + timeline JSON
2. Render `1080×1920 @ 60fps`, tanpa subtitle, tanpa musik
3. Output: `VIDEO_SHORT_XX_Judul_9x16_1080p_60fps.mp4`
4. Upload ke Google Drive `02 - Video Short (9:16)`

### Fase 6: Push ke GitHub
1. Commit hanya file teks/script (tidak ada image/audio/video)
2. Push ke branch `arena/8c1b4b22-yt-1`

---

## 10. CATATAN PENTING DARI PENGGUNA (STANDING INSTRUCTIONS)

- *"Cari topik atau judul yang berpotensi besar mendapatkan lebih banyak views! Bukan asal-asalan! Bukan asal menebak! Saya yang memilih!"*
- *"Gambar stickman yang memiliki tangan berdaging itu terlihat aneh"* — Every stickman: pure white round circle head, bold black outline, bare thin single black line body/arms/legs, white cartoon hands, ZERO white halo outline.
- *"Lanjut, jangan ada musik!"* — No background music.
- *"No subtitles / no captions"* — No text overlay in video.
- *"Ulangi! Hasil gambar ada yang rusak, video seperti blur sedikit!"* — Never draw PIL shapes over scene images; regenerate defective images cleanly via `generate_image`.
- Mascot @SeorangSains (kacamata hitam) hanya di pembuka dan penutup; setelah itu pakai stickman biasa.
- *"Naskah saya ingin bukan dari permintaan saya atau tidak terpengaruh dari permintaan saya. Tapi naskah harus sesuai dengan topik atau judul, menjelaskan dan lain-lain apapun itu istilah-nya yang sesuai dengan sains, fakta, ilmiah"* — Never echo user meta-instructions or fake claims in narration.

---

## 11. ERROR YANG PERLU DIINGAT

- `generate_image` 403 Forbidden — akun sedang dibatasi sementara. Coba ulang setiap beberapa turn hingga pulih.
- `generate_image` limit 10 per turn — baru bisa generate 10 gambar dalam satu turn.
- Jangan pernah memasukkan istilah grafis/kekerasan dalam prompt `generate_speech` yang dapat memicu moderasi (gunakan istilah klinis/medis).

---

## 12. CHECKLIST SEBELUM SELESAI

- [ ] 4 opsi topik ditampilkan via `ask_user`, pengguna memilih
- [ ] Skrip 30 adegan (3 tahap) ditulis dan diupload ke Google Drive + GitHub
- [ ] 30 gambar scene tersedia di `assets/images/` dan Google Drive
- [ ] ZIP backup dan preview grid per batch diupload ke Google Drive
- [ ] VO Master (6 chunk digabung) diupload ke Google Drive
- [ ] `shortXX_timeline_30_scenes.json` tersedia
- [ ] Video final `1080×1920 @ 60fps` diupload ke Google Drive
- [ ] Semua file teks/script di-commit dan di-push ke branch `arena/8c1b4b22-yt-1`

---

**Dokumen ini adalah panduan lengkap untuk AI baru. Semua yang diperlukan untuk menjalankan proyek YouTube Shorts @SeorangSains dari awal sampai akhir sudah tercantum di atas.**

Branch git: `arena/8c1b4b22-yt-1`  
Tanggal dokumentasi: 2026-10-30