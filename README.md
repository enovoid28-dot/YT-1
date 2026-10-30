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

### Menghasilkan gambar dengan API Gemini Anda (di komputer sendiri)

Arena sandbox tidak dapat menghubungi API Gemini secara langsung. Jalankan generator ini pada komputer/runner milik Anda yang dapat mengakses `generativelanguage.googleapis.com`. **Jangan unggah atau tempel API key ke chat/GitHub.** Skrip hanya mengambil `GEMINI_API_KEY` dari environment variable, dan tidak mencetak atau menyimpannya. Aktifkan Gemini image model dan billing/kuota di proyek Anda; pemakaian API dapat dikenai biaya.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python pipeline/generate_images_gemini.py --batch 1 --dry-run
# Masukkan key secara tersembunyi pada terminal lokal, bukan dalam perintah atau file proyek:
read -rsp 'Gemini API key: ' GEMINI_API_KEY; export GEMINI_API_KEY; echo
.venv/bin/python pipeline/generate_images_gemini.py --batch 1
unset GEMINI_API_KEY
```

Lanjutkan `--batch 2` dan `--batch 3` setelah **setiap** scene batch sebelumnya diperiksa. Bisa juga `--scene 4` untuk satu scene; hanya `--force --scene 4` untuk mengganti berkas yang sudah ada. Model bawaan `gemini-2.5-flash-image`; pilih model image-capable lain dengan `--model MODEL` jika akses akun mendukung. Gambar disimpan langsung sebagai JPEG 1080×1920, quality 96, subsampling 0, tanpa gambar tambahan dari PIL. Keluaran model tetap perlu diperiksa manual karena larangan teks, keakuratan anatomi, dan konsistensi stickman tidak bisa dijamin dengan prompt saja. **Jangan `git add -f assets/images`**: aset biner hanya boleh masuk Google Drive, bukan GitHub.
