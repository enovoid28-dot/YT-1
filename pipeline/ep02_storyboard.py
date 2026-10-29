#!/usr/bin/env python3
"""Storyboard EP02 "Kalau Matahari Mati" — 45 shot + 8 kartu, format 9:16.

Struktur: satu segmen VO = beberapa shot. Kartu transisi disisipkan di antara
segmen sesuai naskah. Shot yang gambarnya belum ada otomatis dilewati
(durasi segmen dibagi rata ke shot yang tersedia).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets/images")
CARD = os.path.join(ROOT, "assets/cards")

# caption per shot (teks di layar, bukan transkrip)
CAP = {
    1: "12:00", 2: "MATAHARI HILANG", 3: "KAMU BELUM TAHU",
    4: "TIDAK ADA LEDAKAN", 5: "5 BAB", 6: "KALAU MATAHARI MATI",
    7: "KITA MULAI", 8: "SIAP?",
    9: "8 MENIT 20 DETIK", 10: "SEMUA MENDONGKAK", 11: "MASIH HIJAU",
    12: "BURUNG IKUT DIAM", 13: "CAHAYA MERAH", 14: "SIANG YANG SALAH",
    15: "LALU BUMI BERGERAK",
    16: "APAKAH BUMI JATUH?", 17: "TIDAK.", 18: "TERBANG LURUS",
    19: "DINGIN MULAI MASUK", 20: "MINGGU 1: 0 °C", 21: "DANAU MEMBEKU",
    22: "DINGIN ITU PELAN",
    23: "FOTOSINTESIS BERHENTI", 24: "RANTAI MAKANAN PUTUS",
    25: "KEHABISAN KALORI", 26: "TAHUN 1: −70 °C", 27: "LAUT MEMBEKU",
    28: "BINTANG DI SIANG HARI", 29: "LANGIT PENUH",
    30: "BERTAHAN ≠ HIDUP", 31: "GENERASI 1 INGAT", 32: "GENERASI 3 TIDAK",
    33: "TIGA GENERASI", 34: "APAKAH KITA WARAS?", 35: "TANPA PANTULAN",
    36: "DAN LAMPU PADAM",
    37: "+1 MILIAR TAHUN", 38: "LAUT MENDIDIH", 39: "RAKSASA MERAH",
    40: "LAPISAN TERLEPAS", 41: "KATAI PUTIH", 42: "TANPA PENONTON",
    43: "MATAHARI TIDAK BUTUH KITA", 44: "KITA SISA KEMATIAN BINTANG",
    45: "EPISODE BERIKUTNYA: DASAR JUPITER",
}

# shot per segmen + kartu setelah segmen
SEGMENTS = [
    {"audio": "ep02_coldopen.mp3", "shots": [1, 2, 3], "card_after": "k1"},
    {"audio": "ep02_intro.mp3",    "shots": [4, 5, 6, 7, 8]},
    {"audio": "ep02_bab1.mp3",     "shots": [9, 10, 11, 12, 13, 14, 15], "card_after": "k2"},
    {"audio": "ep02_bab2.mp3",     "shots": [16, 17, 18, 19, 20, 21, 22], "card_after": "k3"},
    {"audio": "ep02_bab3.mp3",     "shots": [23, 24, 25, 26, 27, 28, 29], "card_after": "k4"},
    {"audio": "ep02_bab4.mp3",     "shots": [30, 31, 32, 33, 34, 35, 36], "card_after": "k5"},
    {"audio": "ep02_bab5.mp3",     "shots": [37, 38, 39, 40, 41, 42], "card_after": "k6"},
    {"audio": "ep02_titikbalik.mp3", "shots": [43, 44], "card_after": None},
    {"audio": "ep02_outro.mp3",    "shots": [45], "card_after": None},
    {"audio": "ep02_endcard.mp3",  "shots": [], "card_after": None},
]

CARD_AT_START = "k0"
CARD_DUR = {"k0": 1.2, "k7": 2.6}
CARD_DUR_DEFAULT = 1.4

# gerak kamera per shot (vertikal dominan)
MOVE = {
    1: "in", 2: "out", 3: "in", 4: "up", 5: "in", 6: "in", 7: "down", 8: "in",
    9: "down", 10: "up", 11: "in", 12: "in", 13: "in", 14: "in", 15: "out",
    16: "in", 17: "down", 18: "up", 19: "in", 20: "in", 21: "in", 22: "in",
    23: "in", 24: "up", 25: "in", 26: "in", 27: "down", 28: "up", 29: "in",
    30: "in", 31: "in", 32: "in", 33: "down", 34: "in", 35: "in", 36: "out",
    37: "in", 38: "up", 39: "in", 40: "out", 41: "in", 42: "out",
    43: "in", 44: "in", 45: "in",
}


def shot_path(n):
    return os.path.join(IMG, f"ep02_s{n:02d}.jpg")


def card_path(c):
    return os.path.join(CARD, f"{c}.jpg")
