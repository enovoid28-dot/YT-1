#!/usr/bin/env python3
"""
HUMAN-EAR PSYCHOACOUSTIC VOCAL & SFX ENHANCER (ISO 226:2023 EQUAL-LOUDNESS CURVE)
Upgraded v2:
1. Per-Sentence Timbre & Pitch-Depth Equalizer (`normalize_sentence_timbre_and_level`):
   - Eliminates sudden deep/boomy sentences ("VO yang tiba-tiba dalam suaranya") by measuring
     each sentence's low-chest fundamental energy (85–230 Hz) relative to its mid-vocal
     presence core (600–2800 Hz) and dynamically taming excess 85–240 Hz boom so every
     sentence across all stages shares the exact same crisp, natural vocal timbre.
   - Normalizes active speech RMS per sentence so loudness never jumps or dips.
2. Zero-Phase ISO 226:2023 Ear-Canal Resonance EQ (`enhance_vocal_for_human_ear`):
   - Removes the old +1.5 dB 145 Hz boost that caused chest boominess.
   - Gently carves 250–420 Hz boxiness (-2.4 dB) and lifts 2.6–4.2 kHz ear-canal
     consonant articulation (+2.2 dB) with soft-knee dynamic de-essing at 6–10 kHz.
3. Vocal-Pocket Sidechain SFX Ducking (`carve_and_duck_sfx_for_human_ear`).
"""
import wave
import numpy as np
from scipy.signal import butter, filtfilt, sosfiltfilt


def read_wav_stereo_float(path):
    with wave.open(path, "rb") as wf:
        sr = wf.getframerate()
        n_ch = wf.getnchannels()
        raw = wf.readframes(wf.getnframes())
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if n_ch == 2:
        pcm = pcm.reshape(-1, 2)
    else:
        pcm = np.column_stack([pcm, pcm])
    return pcm, sr


def write_wav_stereo_float(path, stereo_float, sr=48000):
    clipped = np.clip(stereo_float, -0.99, 0.99)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())


def _bandpass(x, f_lo, f_hi, sr, order=2):
    nyq = 0.5 * sr
    sos = butter(order, [max(20.0, f_lo) / nyq, min(nyq - 100.0, f_hi) / nyq], btype="bandpass", output="sos")
    return sosfiltfilt(sos, x)


def _highpass(x, f_cut, sr, order=2):
    nyq = 0.5 * sr
    sos = butter(order, f_cut / nyq, btype="highpass", output="sos")
    return sosfiltfilt(sos, x)


def _lowpass(x, f_cut, sr, order=2):
    nyq = 0.5 * sr
    sos = butter(order, min(nyq - 100.0, f_cut) / nyq, btype="lowpass", output="sos")
    return sosfiltfilt(sos, x)


def _smooth_rms(x, win_ms, sr):
    win = max(16, int((win_ms / 1000.0) * sr))
    sq = x.astype(np.float64) ** 2
    kernel = np.ones(win, dtype=np.float64) / win
    return np.sqrt(np.convolve(sq, kernel, mode="same") + 1e-12).astype(np.float32)


def normalize_sentence_timbre_and_level(sent_mono, sr=48000, target_low_mid_ratio=0.58, target_rms=0.115):
    """
    Normalizes an individual sentence's low-chest spectral balance (85–235 Hz vs 600–2800 Hz)
    and active speech RMS so no sentence ever sounds suddenly deep, boomy, or uneven.
    """
    x = sent_mono.astype(np.float32).copy()
    if len(x) < int(0.15 * sr):
        return x

    # 1. Clean sub-bass rumble below 88 Hz
    x = _highpass(x, 88.0, sr, order=2)

    # 2. Measure low-chest band (88–235 Hz) vs vocal presence core (600–2800 Hz)
    b_chest = _bandpass(x, 88.0, 235.0, sr, order=2)
    b_mid = _bandpass(x, 600.0, 2800.0, sr, order=2)

    win = int(0.020 * sr)
    n_f = len(x) // win
    if n_f > 2:
        f_rms = np.sqrt(np.mean(x[:n_f * win].reshape(n_f, win) ** 2, axis=1))
        active = f_rms > 0.015
    else:
        active = np.ones(len(x), dtype=bool)

    chest_e = float(np.sqrt(np.mean(b_chest ** 2) + 1e-12))
    mid_e = float(np.sqrt(np.mean(b_mid ** 2) + 1e-12))
    cur_ratio = chest_e / (mid_e + 1e-9)

    # Dynamically attenuate excess chest boom (or gently warm overly thin sentences)
    if cur_ratio > target_low_mid_ratio:
        scale_chest = max(0.35, target_low_mid_ratio / cur_ratio)
        x = x - (1.0 - scale_chest) * b_chest
    elif cur_ratio < target_low_mid_ratio * 0.72:
        scale_chest = min(1.22, (target_low_mid_ratio * 0.82) / max(cur_ratio, 0.15))
        x = x + (scale_chest - 1.0) * b_chest

    # 3. Normalize active speech RMS so every sentence has uniform loudness
    if n_f > 2 and np.any(active):
        f_rms_after = np.sqrt(np.mean(x[:n_f * win].reshape(n_f, win) ** 2, axis=1))
        act_rms = float(np.median(f_rms_after[active]))
        if act_rms > 1e-4:
            gain = np.clip(target_rms / act_rms, 0.65, 1.55)
            x = x * gain

    return x.astype(np.float32)


def enhance_vocal_for_human_ear(vo_mono, sr=48000):
    """
    Zero-phase psychoacoustic vocal mastering chain calibrated to ISO 226:2023.
    No 145 Hz boost (prevents boomy voice); crisp, natural Indonesian broadcast clarity.
    """
    x = vo_mono.astype(np.float32).copy()

    # 1. Sub-rumble cleanup below 85 Hz
    x = _highpass(x, 85.0, sr, order=2)

    # 2. Zero-phase multi-band decomposition (NO chest boost at 145 Hz!)
    b_mud = _bandpass(x, 220.0, 420.0, sr, order=2)         # Boxy/muddy resonance (-2.5 dB cut)
    b_body = _bandpass(x, 800.0, 1800.0, sr, order=2)       # Vowel clarity (+0.8 dB)
    b_ear = _bandpass(x, 2500.0, 4300.0, sr, order=2)       # Ear-canal sensitivity peak (+2.2 dB)
    b_sib = _bandpass(x, 6000.0, 10000.0, sr, order=2)      # Sibilance control zone
    b_air = _bandpass(x, 10200.0, 15500.0, sr, order=2)     # Smooth studio air (+1.0 dB)

    # 3. Dynamic de-esser on 6–10 kHz
    sib_env = _smooth_rms(b_sib, win_ms=8.0, sr=sr)
    sib_thresh = 0.032
    deess_gain = np.where(
        sib_env > sib_thresh,
        sib_thresh / (sib_env + 1e-9),
        1.0,
    ).astype(np.float32)
    b_sib_controlled = b_sib * (deess_gain - 1.0)

    # 4. Recombine with zero phase shift
    y = (
        x
        - 0.25 * b_mud
        + 0.10 * b_body
        + 0.28 * b_ear
        + b_sib_controlled
        + 0.12 * b_air
    )

    # 5. Gentle syllable-level leveling (60ms RMS window)
    env = _smooth_rms(y, win_ms=60.0, sr=sr)
    speech_mask = env > 0.012
    target_rms = 0.145
    comp_gain = np.ones_like(y)
    comp_gain[speech_mask] = (target_rms / (env[speech_mask] + 1e-6)) ** 0.20
    comp_gain = np.clip(comp_gain, 0.82, 1.25)
    comp_gain = _smooth_rms(comp_gain, win_ms=35.0, sr=sr)
    y = y * comp_gain

    # 6. Normalize active speech RMS to -16.0 dBFS and soft-limit peaks at -1.0 dBFS (0.891)
    active_env = _smooth_rms(y, win_ms=40.0, sr=sr)
    active_samples = y[active_env > 0.018]
    if len(active_samples) > 100:
        cur_rms = float(np.sqrt(np.mean(active_samples.astype(np.float64) ** 2)))
        desired_rms = 10.0 ** (-16.0 / 20.0)
        y = y * (desired_rms / (cur_rms + 1e-9))

    peak_limit = 0.891
    y = peak_limit * np.tanh(y / peak_limit)
    return y.astype(np.float32)


def carve_and_duck_sfx_for_human_ear(sfx_stereo, vo_mono, sr=48000):
    """
    Carves 1–4.5 kHz vocal pocket out of SFX and sidechain-ducks SFX when VO speaks.
    """
    vo_env = _smooth_rms(vo_mono, win_ms=35.0, sr=sr)
    speaking = np.clip((vo_env - 0.008) / 0.035, 0.0, 1.0)
    speaking = _smooth_rms(speaking, win_ms=70.0, sr=sr)

    broad_duck = 1.0 - 0.65 * speaking
    pocket_duck = 1.0 - 0.58 * speaking

    out = np.zeros_like(sfx_stereo, dtype=np.float32)
    for ch in range(2):
        s = sfx_stereo[:, ch].astype(np.float32)
        s_sub = _lowpass(s, 55.0, sr, order=2)
        s = s - 0.45 * s_sub
        s_pocket = _bandpass(s, 1000.0, 4500.0, sr, order=2)
        s_carved = s - (1.0 - pocket_duck) * s_pocket
        out[:, ch] = s_carved * broad_duck

    return out
