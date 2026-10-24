# FORMAT BAKU NASKAH — CHANNEL STICKMAN

Dokumen ini dipakai untuk **semua** episode. Tujuannya: narator bisa langsung
baca, editor bisa langsung potong, dan caption bisa langsung tempel.

---

## 1. ATURAN DASAR PRODUKSI

| Item | Ketentuan |
|---|---|
| Musik | **TIDAK ADA.** Nol musik, nol jingle, nol stinger melodi. |
| Audio | Hanya VO + *room tone* (desis ruang tipis) + SFX netral (whoosh, klik, detak, letupan debu) maksimal −18 dB di bawah VO |
| Rasio | 9:16 vertikal untuk Shorts, 16:9 untuk episode panjang |
| Kecepatan VO | 145–155 kata/menit. Segmen tegang: 160. Segmen refleksi: 130 |
| Jeda | `[JEDA 0,6]` antar-beat, `[JEDA 1,2]` sebelum kalimat pembuka bab |
| Penekanan | Kata ditebalkan = ditekan, bukan diteriakkan |
| Nada | Santai, tegas, bersemangat. Boleh sarkastik sedikit. **Dilarang** menggurui. |

### Gaya bahasa yang dipakai
- Kalimat pendek. Satu ide per kalimat.
- Angka selalu dibandingkan dengan hal yang bisa dibayangkan ("sejauh 24 miliar kilometer — empat kali jarak Bumi–Matahari, dikali... sudah tidak masuk akal").
- Tidak ada kata "hadirin", "saudara-saudara", "pada kesempatan kali ini".
- Tidak ada klaim tanpa angka atau sumber. Kalau estimasi, bilang "perkiraan".

---

## 2. STRUKTUR WAJIB SATU EPISODE

| Urutan | Bagian | Durasi | Fungsi |
|---|---|---|---|
| 1 | **COLD OPEN** | 0:00–0:12 | Satu kalimat aneh/pertanyaan. Tanpa intro logo. |
| 2 | **INTRO** | 0:12–0:40 | Perkenalkan pertanyaan + janji episode ("kita akan lihat 5 bukti") |
| 3 | **BAB 1–4** | 0:40–6:30 | Isi, tiap bab 60–100 detik, selalu ditutup satu kalimat kait |
| 4 | **TITIK BALIK** | 6:30–7:10 | Bagian paling jujur/emosional, menjawab "kenapa ini penting" |
| 5 | **OUTRO** | 7:10–7:50 | Rangkum 3 poin, CTA lembut, teaser episode berikutnya |
| 6 | **END CARD** | 7:50–8:00 | Layar diam + teks, VO satu kalimat penutup |

**Aturan transisi:** setiap akhir bab pakai satu kalimat pengait yang
menyebut bab berikutnya. Contoh: "Masalahnya, semua hitungan itu berdiri di atas
satu asumsi yang rapuh."

---

## 3. ATURAN CAPTION / SUBTITLE

### Tampilan
| Elemen | Ketentuan |
|---|---|
| Font | Bold sans, tanpa serif (Bebas Neue / DejaVu Sans Bold / Montserrat Bold) |
| Ukuran | 9:16 → 58–64 px pada kanvas 1080×1920. 16:9 → 54 px pada 1920×1080 |
| Warna | Putih #FFFFFF. Kata kunci: kuning #FFD640 |
| Outline | Hitam 6–7 px agar terbaca di latar apa pun |
| Posisi | 9:16: 200 px dari bawah (aman dari UI YouTube). 16:9: 120 px dari bawah |
| Lebar maks | 88% lebar kanvas, **maksimal 2 baris**, 30–34 karakter per baris |
| Kapital | Kapital semua untuk penegasan; kalimat tanya tetap kapital |
| Animasi | *Pop-in* 3 frame (skala 0,94 → 1,0), keluar potong langsung. Tanpa fade panjang |
| Sinkron | Muncul ≤ 0,15 s setelah kata diucapkan, bertahan sampai kata terakhir |

### Aturan isi
1. Caption **bukan transkrip mentah.** Buang "eh", "jadi", "nah".
2. Satu caption = satu gagasan. Maksimal 7 kata.
3. Angka ditulis penuh kalau penting: "**5.900** PLANET", bukan "5900 planet".
4. Kata kunci **selalu kuning dan maksimal 2 kata per caption.**
5. Setiap pindah bab, muncul *label bab* kecil di kiri atas: `BAGIAN 3 — TANDA YANG TIDAK PERNAH TERULANG`.
6. Di bagian refleksi, caption diganti kalimat utuh tanpa kuning — lebih tenang.
7. Bar progres tipis 3 px di paling bawah (opsional, bantu retensi).

### Larangan
- Tidak ada caption yang menutupi wajah karakter.
- Tidak ada emoji di dalam video (hanya di deskripsi YouTube).
- Tidak ada karaoke word-by-word berwarna-warni — terlalu ramai.

---

## 4. ATURAN VISUAL (untuk animator)
- Karakter = stick figure kepala bulat putih, garis hitam 8–10 px, ekspresi jelas.
- Satu gagasan visual per 3–5 detik. Tidak ada adegan statis lebih dari 6 detik.
- Latar flat, 2–4 warna per adegan. Palet muted, bukan neon.
- Setiap angka besar yang disebut → tampilkan sebagai teks besar di latar.
- Saat narator bicara soal skala, gunakan zoom-out bertahap; saat bicara soal
  perasaan, gunakan close-up kepala.

---

## 5. CHECKLIST SEBELUM REKAM
- [ ] Naskah dibaca keras, dihitung durasinya (target ± 8 menit)
- [ ] Setiap kalimat maksimal 18 kata
- [ ] Semua angka sudah dicek ulang
- [ ] Ada cold open, intro, minimal 4 bab, titik balik, outro, end card
- [ ] Caption sudah ditulis per beat (bukan menunggu editing)
- [ ] Tidak ada musik di timeline
