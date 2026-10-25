#!/usr/bin/env python3
"""
VO HUMAN-EAR PSYCHOACOUSTIC ENHANCER & MASTERING ENGINE (`vo_human_ear_enhancer.py`)
Dirancang khusus untuk memaksimalkan kejernihan (clarity), artikulasi konsonan,
kehangatan vokal, dan kenyamanan pendengaran telinga manusia berdasarkan kurva
sensitivitas telinga manusia ISO 226:2023 & resonansi saluran telinga (2.8 - 4.2 kHz).

PENTING (Anti-Cut / Anti-Glitch Architecture):
- Seluruh pemrosesan dilakukan secara KONTINU & LINEAR/ZERO-PHASE pada aliran audio utuh
  tanpa pemotongan frame internal, tanpa noise-gate yang memotong suku kata, dan tanpa
  time-stretching (`1.000x` kecepatan bicara alami).
"""
import wave
import numpy as np

SR = 48000


def read_wav_stereo_float(path):
    """Baca file WAV 16-bit menjadi array float32 stereo [-1.0, 1.0]."""
    with wave.open(path, "rb") as wf:
        nch = wf.getnchannels()
        sr = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if nch == 2:
        pcm = pcm.reshape(-1, 2)
    else:
        pcm = np.column_stack([pcm, pcm])
    return pcm, sr


def write_wav_stereo_float(path, stereo, sr=SR):
    """Simpan array float32 stereo [-1.0, 1.0] ke file WAV 16-bit."""
    clipped = np.clip(stereo, -0.99, 0.99)
    pcm = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def build_human_ear_eq_curve(freqs):
    """
    Kurva respons frekuensi (magnitude gain) berbasis ISO 226:2023 untuk vokal narator:
      - High-pass Butterworth orde-4 @ 80 Hz (buang sub-rumble)
      - Warmth bell @ 135 Hz (+1.4 dB, Q=1.4)
      - Mud cut bell @ 255 Hz (-3.2 dB, Q=1.6)
      - Boxy cut @ 520 Hz (-1.2 dB, Q=2.0)
      - Vowel definition boost @ 1850 Hz (+2.2 dB, Q=1.2)
      - Human Ear Canal Resonance Peak @ 3350 Hz (+3.8 dB, Q=1.15)
      - Gentle Sibilance Taming @ 7200 Hz (-1.5 dB, Q=2.2)
      - Condenser Air High-Shelf @ 9500 Hz (+2.4 dB)
    """
    f = np.maximum(freqs, 1.0)
    hp = 1.0 / np.sqrt(1.0 + (80.0 / f) ** 8)

    def bell_db(f0, gain_db, q):
        bw = f0 / q
        x = (f - f0) / (bw * 0.65 + 1e-6)
        return gain_db * np.exp(-0.5 * (x ** 2))

    db = np.zeros_like(f)
    db += bell_db(135.0, +1.4, 1.4)    # Kehangatan suara dada alami
    db += bell_db(255.0, -3.2, 1.6)    # Hilangkan suara mendem/keruh
    db += bell_db(520.0, -1.2, 2.0)    # Bersihkan resonansi kotak
    db += bell_db(1850.0, +2.2, 1.2)   # Kejelasan vokal & artikulasi tengah
    db += bell_db(3350.0, +3.8, 1.15)  # Puncak kepekaan saluran telinga manusia (ISO 226)
    db += bell_db(7200.0, -1.5, 2.2)   # Haluskan desis huruf 's' secara linear

    shelf = 2.4 / (1.0 + (9500.0 / f) ** 4)
    db += shelf

    lp = 1.0 / np.sqrt(1.0 + (f / 18000.0) ** 8)
    return hp * (10.0 ** (db / 20.0)) * lp


def fft_zero_phase_filter(x_1d, sr, gain_fn):
    """Terapkan filter kurva frekuensi zero-phase berbasis FFT pada sinyal 1D utuh."""
    n = len(x_1d)
    if n == 0:
        return x_1d
    n_fft = 1 << (n - 1).bit_length()
    spec = np.fft.rfft(x_1d, n=n_fft)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sr)
    gain = gain_fn(freqs)
    y = np.fft.irfft(spec * gain, n=n_fft)[:n]
    return y.astype(np.float32)


def enhance_vocal_for_human_ear(mono_sig, sr=SR):
    """
    Proses sinyal vokal mono secara kontinu & linear dengan Zero-Phase ISO 226 Human-Ear EQ
    dan soft-knee peak normalization tanpa memotong/mengubah amplop waktu suku kata.
    """
    eq_sig = fft_zero_phase_filter(mono_sig, sr, build_human_ear_eq_curve)
    peak = np.max(np.abs(eq_sig)) + 1e-8
    norm_sig = eq_sig / peak * 0.88
    out = np.where(
        np.abs(norm_sig) > 0.84,
        np.sign(norm_sig) * (0.84 + 0.06 * np.tanh((np.abs(norm_sig) - 0.84) / 0.06)),
        norm_sig
    )
    return out.astype(np.float32)


def carve_and_duck_sfx_for_human_ear(sfx_stereo, vo_stereo, sr=SR):
    """
    Lubangi frekuensi vokal utama (1.2 kHz - 4.5 kHz) sebesar -10 dB pada track SFX
    dan terapkan Sidechain Auto-Ducking halus agar SFX tidak pernah menutupi suara VO.
    """
    def sfx_vocal_pocket_curve(freqs):
        f = np.maximum(freqs, 1.0)
        bw = 2400.0
        x = (f - 2600.0) / (bw * 0.65)
        db = -10.0 * np.exp(-0.5 * (x ** 2))
        hp = 1.0 / np.sqrt(1.0 + (60.0 / f) ** 4)
        return hp * (10.0 ** (db / 20.0))

    carved_l = fft_zero_phase_filter(sfx_stereo[:, 0], sr, sfx_vocal_pocket_curve)
    carved_r = fft_zero_phase_filter(sfx_stereo[:, 1], sr, sfx_vocal_pocket_curve)

    vo_mono = 0.5 * (vo_stereo[:, 0] + vo_stereo[:, 1])
    n = min(len(carved_l), len(vo_mono))
    win = max(1, int(sr * 0.12))
    kernel = np.hanning(win * 2 + 1)
    kernel /= np.sum(kernel)
    vo_env = np.sqrt(np.convolve(vo_mono[:n] ** 2, kernel, mode="same") + 1e-10)
    speech_activity = np.clip(vo_env / 0.07, 0.0, 1.0)
    duck_gain = (0.75 - 0.52 * speech_activity).astype(np.float32)

    out = np.zeros_like(sfx_stereo)
    out[:n, 0] = carved_l[:n] * duck_gain
    out[:n, 1] = carved_r[:n] * duck_gain
    return out
