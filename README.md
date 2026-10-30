# @SeorangSains — Shorts produksi

## Short 01: Kenapa membaca di mobil bikin mabuk?

- [Naskah dan storyboard 30 adegan](script/01-SHORT-KENAPA-MEMBACA-DI-MOBIL-BIKIN-MABUK.md)
- [Timeline estimasi 30 adegan](output/short01_timeline_30_scenes.json)
- [Pipeline render](pipeline/render_short_ep01.py)

Short vertikal 1080×1920 @ 60 fps, tanpa musik, subtitle, atau teks pada scene. Maskot berkacamata hanya adegan 01–03 dan 30; stickman penumpang biasa untuk sisanya. Riset dan sumber medis ada di bawah naskah.

### Menjalankan pipeline

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python pipeline/render_short_ep01.py validate
.venv/bin/python pipeline/render_short_ep01.py prepare    # memerlukan output/vo_short01_c1.mp3 … c6.mp3
.venv/bin/python pipeline/render_short_ep01.py normalize  # hanya menormalkan gambar yang ada
.venv/bin/python pipeline/render_short_ep01.py render     # wajib punya 30 gambar
```

Masukkan gambar hasil generasi yang telah diperiksa di `assets/images/` sesuai nama pada timeline. `normalize` mengubah ukuran dan menajamkan gambar, **tidak menggambar di atasnya**. `render` menolak gambar yang kurang/tidak sesuai spesifikasi, dan tidak membuat gambar pengganti. Durasi timeline per kalimat merupakan **perkiraan proporsional**, bukan forced alignment; sebelum publikasi periksa waktu potong adegan dengan mendengarkan VO dan koreksi jika perlu. File gambar/audio/video tidak disimpan di Git.

### Status saat ini

- Naskah 30 adegan lengkap, setiap kalimat 12–13 kata; telah diunggah ke folder Drive `04 - Metadata & Naskah`.
- Enam chunk VO selesai; VO master durasi 169,39 detik telah diunggah ke folder Drive `02 - Aset Voiceover (VO)`.
- **0/30 ilustrasi**: layanan generate gambar mengembalikan HTTP 403 (pembatasan akun). Tidak ada backup gambar atau video final yang diklaim selesai. Lanjutkan gambar saat akses pulih, inspeksi setiap scene, lalu render/uji/unggah video.
