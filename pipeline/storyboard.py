#!/usr/bin/env python3
"""Storyboard: peta tahap -> segmen, caption di layar, dan gaya gerak kamera."""
import os

# (tahap, segmen, gerakan kamera)  gerakan: in / out / left / right / up
STAGES = [
    (1, 1, "in"), (2, 1, "left"), (3, 1, "up"), (4, 1, "in"),
    (5, 2, "in"), (6, 2, "right"), (7, 2, "out"),
    (8, 3, "up"), (9, 3, "in"), (10, 3, "out"),
    (11, 4, "right"), (12, 4, "in"), (13, 4, "out"),
    (14, 5, "left"), (15, 5, "up"), (16, 5, "in"),
    (17, 6, "in"), (18, 6, "right"), (19, 6, "out"),
    (20, 7, "up"), (21, 7, "in"), (22, 7, "left"),
    (23, 8, "in"), (24, 8, "up"), (25, 8, "out"),
    (26, 9, "in"), (27, 9, "right"), (28, 9, "out"), (29, 9, "in"),
    (30, 10, "in"), (31, 10, "in"), (32, 10, "out"), (33, 10, "in"),
]

CAPTIONS = {
    1: "TITIK PUTIH DI TEPI LUBANG HITAM",
    2: "BUMI. GARIS START.",
    3: "1969: KELUAR DARI ATMOSFER",
    4: "MATAHARI: 5.500 °C",
    5: "KAPSUL 6 METER, 3 ORANG",
    6: "MERKURIUS, TANPA PELINDUNG",
    7: "KERIKIL = PELURU",
    8: "VENUS: 464 °C",
    9: "PAYUNG ASAM SULFAT",
    10: "TEKANAN 92 ATM",
    11: "MARS: DEBU MERAH, SUNYI",
    12: "ROVER TUA, MASIH SETIA",
    13: "OLYMPUS MONS: 22 KM",
    14: "SABUK ASTEROID",
    15: "JUPITER: STORM ABADI",
    16: "DITARIK KE DALAM",
    17: "PETIR SEBESAR NEGARA",
    18: "CINCIN = MILIARAN ES",
    19: "NONGKRONG DI CINCIN",
    20: "TITAN: KABUT ORANYE",
    21: "URANUS: 98° MIRING",
    22: "KITA IKUT MIRING",
    23: "HUJAN INTAN",
    24: "NEPTUNUS: 2.100 KM/JAM",
    25: "ANGIN TERCEPAT",
    26: "PLUTO: JANTUNG ES",
    27: "TOMBAUGH REGIO",
    28: "KUIPER BELT",
    29: "CAHAYA DIBELOKKAN",
    30: "SPAGHETTIFIKASI",
    31: "TITIK TANPA KEMBALI",
    32: "BANGUN. MASIH DI BUMI.",
    33: "SUBSCRIBE @SAINSCORET",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "assets/images")


def image_for(stage):
    return os.path.join(IMG_DIR, f"t{stage:02d}.jpg")


def available():
    return [s for s, _, _ in STAGES if os.path.exists(image_for(s))]
