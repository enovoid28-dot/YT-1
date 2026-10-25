#!/usr/bin/env python3
"""
100% COPYRIGHT-FREE CINEMATIC SPACE & INTERSTELLAR-STYLE MUSIC SYNTHESIZER
Generates 3 distinct studio-grade background music options for @SeorangSains:
  - Opsi 1: Cosmic Cathedral Pipe Organ & Relativity Arpeggio (Gaya Interstellar / Hans Zimmer)
  - Opsi 2: Deep Cosmos Warm Ambient Pad & Distant Felt Piano (Gaya Melodysheep / Kurzgesagt)
  - Opsi 3: Event Horizon Cinematic Strings, Organ Swell & Pulsar Heartbeat (Gaya Dark Sci-Fi Documentary)

Each option includes:
  - Silence during the first 3.0s of the video so the opening greeting is crystal clear
  - Smooth 5.5s cosine fade-in after the video starts
  - Warm low-passed mastering (< 3.2 kHz ceiling) + Vocal-Pocket Sidechain Ducking so the
    music never competes with the narrator's voice
  - Smooth 6.5s cosine fade-out at the end of the video
"""
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfiltfilt, fftconvolve
import imageio_ffmpeg

from pipeline.vo_human_ear_enhancer import (
    read_wav_stereo_float,
    write_wav_stereo_float,
)

SR = 48000
FF = imageio_ffmpeg.get_ffmpeg_exe()


def midi_to_hz(m):
    return 440.0 * (2.0 ** ((m - 69.0) / 12.0))


def _lowpass(x, f_cut, sr=SR, order=2):
    sos = butter(order, min(0.48 * sr, f_cut) / (0.5 * sr), btype="lowpass", output="sos")
    return sosfiltfilt(sos, x)


def _highpass(x, f_cut, sr=SR, order=2):
    sos = butter(order, max(15.0, f_cut) / (0.5 * sr), btype="highpass", output="sos")
    return sosfiltfilt(sos, x)


def _bandpass(x, f_lo, f_hi, sr=SR, order=2):
    sos = butter(order, [max(15.0, f_lo) / (0.5 * sr), min(0.48 * sr, f_hi) / (0.5 * sr)], btype="bandpass", output="sos")
    return sosfiltfilt(sos, x)


def make_cathedral_ir(rt60=4.2, sr=SR, seed=101):
    """
    Creates a lush, warm stereo cathedral impulse response with early reflections
    and low-passed diffuse decay (no metallic ringing).
    """
    rng = np.random.default_rng(seed)
    n = int(rt60 * sr)
    t = np.linspace(0.0, rt60, n, endpoint=False, dtype=np.float32)
    decay = np.exp(-6.9078 * t / rt60).astype(np.float32)
    # Soft attack over 45ms so reverb blooms smoothly like a large stone cathedral
    bloom = 1.0 - np.exp(-t / 0.045).astype(np.float32)
    env = decay * bloom

    ir_l = rng.normal(0.0, 1.0, n).astype(np.float32) * env
    ir_r = rng.normal(0.0, 1.0, n).astype(np.float32) * env

    # Early reflections (15ms .. 140ms)
    for delay_ms, gain in [(19, 0.35), (37, 0.28), (61, 0.22), (89, 0.18), (127, 0.14)]:
        idx_l = int(delay_ms * 0.001 * sr)
        idx_r = int((delay_ms + 4) * 0.001 * sr)
        if idx_l < n:
            ir_l[idx_l] += gain
        if idx_r < n:
            ir_r[idx_r] -= gain * 0.95

    # Warmth damping (cathedral stone absorbs > 2600 Hz)
    ir_l = _lowpass(_highpass(ir_l, 70.0, sr), 2400.0, sr)
    ir_r = _lowpass(_highpass(ir_r, 70.0, sr), 2400.0, sr)

    norm = max(float(np.sqrt(np.mean(ir_l ** 2))), 1e-6) * np.sqrt(n)
    return (ir_l / norm).astype(np.float32), (ir_r / norm).astype(np.float32)


def apply_cathedral_reverb(dry_l, dry_r, wet=0.52, rt60=4.2):
    ir_l, ir_r = make_cathedral_ir(rt60=rt60)
    n = len(dry_l)
    wet_l = fftconvolve(dry_l, ir_l, mode="full")[:n]
    wet_r = fftconvolve(dry_r, ir_r, mode="full")[:n]
    # Cross-feed 25% of reverb for wide stereo space
    w_l = 0.85 * wet_l + 0.25 * wet_r
    w_r = 0.85 * wet_r + 0.25 * wet_l
    out_l = (1.0 - wet * 0.45) * dry_l + wet * w_l
    out_r = (1.0 - wet * 0.45) * dry_r + wet * w_r
    return out_l.astype(np.float32), out_r.astype(np.float32)


def synth_pipe_organ_note(freq, dur, sr=SR, bright=1.0):
    """
    Warm Cathedral Pipe Organ voice (16', 8', 5-1/3', 4', 2-2/3', 2' flute/principal pipes)
    with stereo wind-chest detuning.
    """
    n = int(round(dur * sr))
    t = np.linspace(0.0, dur, n, endpoint=False, dtype=np.float32)

    # Smooth pipe-valve attack (75ms) and release (160ms)
    att = min(n // 3, int(0.075 * sr))
    rel = min(n // 3, int(0.160 * sr))
    env = np.ones(n, dtype=np.float32)
    if att > 0:
        env[:att] = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, att, dtype=np.float32))
    if rel > 0:
        env[-rel:] = 0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, rel, dtype=np.float32))

    # Subtle wind-pressure tremulant (5.2 Hz, +-0.12%)
    vib = 1.0 + 0.0011 * np.sin(2.0 * np.pi * 5.2 * t)
    phase_base = 2.0 * np.pi * freq * np.cumsum(vib) / sr

    drawbars = [
        (0.5, 0.28),          # 16' Bourdon sub-octave
        (1.0, 1.00),          # 8' Diapason fundamental
        (1.5, 0.14 * bright), # 5-1/3' Quint
        (2.0, 0.48 * bright), # 4' Octave flute
        (3.0, 0.16 * bright), # 2-2/3' Nazard
        (4.0, 0.18 * bright), # 2' Piccolo
        (6.0, 0.05 * bright), # 1-1/3' Larigot
    ]

    sig_l = np.zeros(n, dtype=np.float32)
    sig_r = np.zeros(n, dtype=np.float32)
    for mult, amp in drawbars:
        # Slight stereo rank detuning (+1.6 cents L, -1.6 cents R)
        det_l = 1.0009 * mult
        det_r = 0.9991 * mult
        sig_l += amp * (0.65 * np.sin(phase_base * det_l) + 0.35 * np.sin(phase_base * mult))
        sig_r += amp * (0.65 * np.sin(phase_base * det_r) + 0.35 * np.sin(phase_base * mult + 0.25))

    return (sig_l * env * 0.18).astype(np.float32), (sig_r * env * 0.18).astype(np.float32)


def synth_felt_piano_note(freq, dur, sr=SR):
    """
    Warm, intimate Cinematic Felt Piano note (soft hammer attack + natural string decay).
    """
    n = int(round(dur * sr))
    t = np.linspace(0.0, dur, n, endpoint=False, dtype=np.float32)
    att = min(n // 4, int(0.018 * sr))
    env = np.exp(-t * 1.35).astype(np.float32)
    if att > 0:
        env[:att] *= np.linspace(0.0, 1.0, att, dtype=np.float32)

    # Felt hammer damps higher partials faster than fundamental
    partials = [
        (1.0, 1.00, 1.0),
        (2.0005, 0.38, 1.8),
        (3.0018, 0.14, 2.7),
        (4.0040, 0.05, 3.8),
    ]
    sig_l = np.zeros(n, dtype=np.float32)
    sig_r = np.zeros(n, dtype=np.float32)
    for mult, amp, dec_mult in partials:
        p_env = np.exp(-t * 1.35 * dec_mult).astype(np.float32)
        if att > 0:
            p_env[:att] *= np.linspace(0.0, 1.0, att, dtype=np.float32)
        sig_l += amp * np.sin(2.0 * np.pi * freq * mult * t) * p_env
        sig_r += amp * np.sin(2.0 * np.pi * freq * (mult * 0.9996) * t + 0.3) * p_env

    return (sig_l * 0.22).astype(np.float32), (sig_r * 0.22).astype(np.float32)


def synth_warm_pad_chord(midi_notes, dur, sr=SR, swell=True):
    """
    Lush 6-voice detuned stereo space pad / string ensemble for a chord.
    """
    n = int(round(dur * sr))
    t = np.linspace(0.0, dur, n, endpoint=False, dtype=np.float32)
    if swell:
        env = np.maximum(0.0, np.sin(np.pi * np.linspace(0.0, 1.0, n, dtype=np.float32))) ** 1.2
    else:
        att = min(n // 3, int(0.6 * sr))
        rel = min(n // 3, int(0.8 * sr))
        env = np.ones(n, dtype=np.float32)
        env[:att] = 0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, att, dtype=np.float32))
        env[-rel:] = 0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, rel, dtype=np.float32))

    out_l = np.zeros(n, dtype=np.float32)
    out_r = np.zeros(n, dtype=np.float32)
    detunes = [-0.0028, -0.0011, 0.0009, 0.0026]
    for m in midi_notes:
        f0 = midi_to_hz(m)
        for idx, d in enumerate(detunes):
            f = f0 * (1.0 + d)
            vib = 0.0015 * np.sin(2.0 * np.pi * (4.2 + 0.3 * idx) * t + idx)
            ph = 2.0 * np.pi * f * (t + vib)
            wave = 0.70 * np.sin(ph) + 0.22 * np.sin(2.0 * ph) + 0.08 * np.sin(3.0 * ph)
            if idx % 2 == 0:
                out_l += wave
                out_r += 0.4 * wave
            else:
                out_r += wave
                out_l += 0.4 * wave

    out_l = _lowpass(out_l * env * 0.055, 1650.0, sr)
    out_r = _lowpass(out_r * env * 0.055, 1650.0, sr)
    return out_l.astype(np.float32), out_r.astype(np.float32)


def add_stereo(buf_l, buf_r, seg_l, seg_r, start_s, sr=SR):
    i0 = max(0, int(round(start_s * sr)))
    i1 = min(len(buf_l), i0 + len(seg_l))
    if i1 > i0:
        buf_l[i0:i1] += seg_l[:i1 - i0]
        buf_r[i0:i1] += seg_r[:i1 - i0]


def generate_option_1_interstellar_organ(dur_s, sr=SR):
    """
    Opsi 1: Cosmic Cathedral Pipe Organ & Relativity Arpeggio (Gaya Interstellar).
    4-bar loop (16s per cycle at 60 BPM):
      Chords: Fmaj7#11 (F2,C3,A3,E4) -> G6 (G2,D3,B3,E4) -> Am9 (A2,E3,B3,C4) -> Em7 (E2,B2,G3,D4)
      Hypnotic triplet arpeggio ostinato on upper organ flute pipe + soft relativity clock pulse.
    """
    n_total = int(round(dur_s * sr)) + sr * 4
    buf_l = np.zeros(n_total, dtype=np.float32)
    buf_r = np.zeros(n_total, dtype=np.float32)

    chords = [
        # (bass_midi, pad_chord_midis, arp_pattern_midis)
        (41, [53, 60, 64, 69], [76, 81, 76, 83, 76, 81, 76, 84, 76, 83, 76, 81]),  # Fmaj7#11
        (43, [55, 62, 64, 71], [76, 83, 76, 84, 76, 83, 76, 86, 76, 84, 76, 83]),  # G6
        (45, [57, 64, 69, 72], [76, 81, 76, 84, 76, 81, 76, 83, 76, 81, 76, 79]),  # Am9
        (40, [52, 59, 64, 67], [76, 79, 76, 83, 76, 79, 76, 81, 76, 79, 76, 78]),  # Em7
    ]

    bar_dur = 4.2  # ~57 BPM majestic tempo
    step_dur = bar_dur / 12.0
    t_cur = 0.0
    bar_idx = 0

    while t_cur < dur_s:
        bass_m, chord_ms, arp_ms = chords[bar_idx % len(chords)]
        # Breathing intensity wave across bars (0.55 .. 1.0)
        swell_bright = 0.65 + 0.35 * np.sin(2.0 * np.pi * (t_cur / 33.6))

        # 1. Deep Pipe Organ Pedal Bass + Sustained Organ Chord
        b_l, b_r = synth_pipe_organ_note(midi_to_hz(bass_m), bar_dur * 1.04, sr, bright=0.6)
        add_stereo(buf_l, buf_r, b_l * 0.90, b_r * 0.90, t_cur, sr)

        for cm in chord_ms:
            c_l, c_r = synth_pipe_organ_note(midi_to_hz(cm), bar_dur * 1.03, sr, bright=0.75 * swell_bright)
            add_stereo(buf_l, buf_r, c_l * 0.48, c_r * 0.48, t_cur, sr)

        # 2. Iconic Interstellar-style gentle organ flute arpeggio
        for s_i, am in enumerate(arp_ms):
            vel = (0.55 if (s_i % 2 == 0) else 0.78) * swell_bright
            a_l, a_r = synth_pipe_organ_note(midi_to_hz(am), step_dur * 1.35, sr, bright=0.85)
            # Pan alternating arpeggio notes slightly left/right for 3D space
            pan_l = 0.85 if (s_i % 2 == 0) else 0.55
            pan_r = 0.55 if (s_i % 2 == 0) else 0.85
            add_stereo(buf_l, buf_r, a_l * vel * pan_l * 0.42, a_r * vel * pan_r * 0.42, t_cur + s_i * step_dur, sr)

        # 3. Soft relativity clock pulse (4 beats per bar, warm muted felt tick)
        for beat in range(4):
            t_beat = t_cur + beat * (bar_dur / 4.0)
            n_tk = int(0.06 * sr)
            t_tk = np.linspace(0, 0.06, n_tk, endpoint=False, dtype=np.float32)
            tick = np.sin(2.0 * np.pi * (523.25 if beat == 0 else 392.0) * t_tk) * np.exp(-t_tk * 65.0) * 0.05
            add_stereo(buf_l, buf_r, tick, tick * 0.9, t_beat, sr)

        t_cur += bar_dur
        bar_idx += 1

    n_out = int(round(dur_s * sr))
    out_l, out_r = apply_cathedral_reverb(buf_l[:n_out], buf_r[:n_out], wet=0.58, rt60=4.5)
    # Warm low-pass so the organ sits like velvet behind the voiceover
    out_l = _lowpass(out_l, 2200.0, sr)
    out_r = _lowpass(out_r, 2200.0, sr)
    return np.column_stack([out_l, out_r])


def generate_option_2_deep_cosmos_piano_pad(dur_s, sr=SR):
    """
    Opsi 2: Deep Cosmos Warm Ambient Pad & Distant Felt Piano (Gaya Melodysheep / Kurzgesagt).
    Ultra-smooth floating space chords with sparse, contemplative felt piano notes.
    """
    n_total = int(round(dur_s * sr)) + sr * 5
    buf_l = np.zeros(n_total, dtype=np.float32)
    buf_r = np.zeros(n_total, dtype=np.float32)

    progression = [
        (38, [50, 57, 62, 65, 69], [(0.5, 74), (2.2, 76), (3.8, 81)]),   # Dm9
        (34, [46, 53, 58, 62, 65], [(0.8, 72), (2.6, 74), (4.1, 77)]),   # Bbmaj9
        (36, [48, 55, 60, 64, 67], [(0.6, 76), (2.4, 79), (3.9, 72)]),   # Cmaj9
        (33, [45, 52, 57, 60, 64], [(1.0, 69), (2.8, 72), (4.2, 76)]),   # Am7
    ]

    bar_dur = 5.2
    t_cur = 0.0
    bar_idx = 0

    while t_cur < dur_s:
        bass_m, pad_ms, piano_notes = progression[bar_idx % len(progression)]
        # Lush warm pad chord
        p_l, p_r = synth_warm_pad_chord([bass_m] + pad_ms, bar_dur * 1.18, sr, swell=True)
        add_stereo(buf_l, buf_r, p_l * 1.15, p_r * 1.15, t_cur, sr)

        # Distant felt piano notes
        for offset_s, pm in piano_notes:
            pl, pr = synth_felt_piano_note(midi_to_hz(pm), 3.4, sr)
            add_stereo(buf_l, buf_r, pl * 0.45, pr * 0.45, t_cur + offset_s, sr)

        t_cur += bar_dur
        bar_idx += 1

    n_out = int(round(dur_s * sr))
    out_l, out_r = apply_cathedral_reverb(buf_l[:n_out], buf_r[:n_out], wet=0.64, rt60=4.8)
    out_l = _lowpass(out_l, 2000.0, sr)
    out_r = _lowpass(out_r, 2000.0, sr)
    return np.column_stack([out_l, out_r])


def generate_option_3_event_horizon_strings_organ(dur_s, sr=SR):
    """
    Opsi 3: Event Horizon Tension Strings, Pipe Organ Swell & Pulsar Heartbeat.
    Darker, suspenseful cosmic documentary atmosphere (C minor -> Abmaj7 -> Fm9 -> G7sus4).
    """
    n_total = int(round(dur_s * sr)) + sr * 5
    buf_l = np.zeros(n_total, dtype=np.float32)
    buf_r = np.zeros(n_total, dtype=np.float32)

    progression = [
        (36, [48, 55, 60, 63, 67], [72, 75, 79, 75]),  # Cm9
        (32, [44, 51, 56, 60, 63], [72, 75, 80, 75]),  # Abmaj7
        (29, [41, 48, 53, 56, 60], [68, 72, 77, 72]),  # Fm9
        (31, [43, 50, 55, 58, 62], [67, 70, 74, 70]),  # Gm7
    ]

    bar_dur = 4.6
    t_cur = 0.0
    bar_idx = 0

    while t_cur < dur_s:
        bass_m, str_ms, motif_ms = progression[bar_idx % len(progression)]
        # 1. Cinematic String Ensemble + Organ Swell
        s_l, s_r = synth_warm_pad_chord(str_ms, bar_dur * 1.12, sr, swell=True)
        o_l, o_r = synth_pipe_organ_note(midi_to_hz(bass_m + 12), bar_dur * 1.05, sr, bright=0.65)
        add_stereo(buf_l, buf_r, s_l * 0.95, s_r * 0.95, t_cur, sr)
        add_stereo(buf_l, buf_r, o_l * 0.55, o_r * 0.55, t_cur, sr)

        # 2. Slow 4-note tension motif
        step = bar_dur / 4.0
        for k, mm in enumerate(motif_ms):
            ml, mr = synth_pipe_organ_note(midi_to_hz(mm), step * 1.15, sr, bright=0.7)
            add_stereo(buf_l, buf_r, ml * 0.30, mr * 0.30, t_cur + k * step, sr)

        # 3. Deep Pulsar Heartbeat (warm sub-bass thump twice per bar)
        for hb in [0.0, bar_dur * 0.5]:
            n_hb = int(0.45 * sr)
            t_hb = np.linspace(0, 0.45, n_hb, endpoint=False, dtype=np.float32)
            freq_env = 58.0 + 38.0 * np.exp(-t_hb * 18.0)
            thump = np.sin(2.0 * np.pi * np.cumsum(freq_env) / sr) * np.exp(-t_hb * 8.5) * 0.14
            add_stereo(buf_l, buf_r, thump, thump, t_cur + hb, sr)

        t_cur += bar_dur
        bar_idx += 1

    n_out = int(round(dur_s * sr))
    out_l, out_r = apply_cathedral_reverb(buf_l[:n_out], buf_r[:n_out], wet=0.56, rt60=4.4)
    out_l = _lowpass(out_l, 2100.0, sr)
    out_r = _lowpass(out_r, 2100.0, sr)
    return np.column_stack([out_l, out_r])


def apply_fade_in_out_and_normalize(stereo, start_delay_s=2.8, fade_in_s=5.0, fade_out_s=6.0, target_rms=0.055, sr=SR):
    """
    Applies:
      - Pure silence for the first `start_delay_s` seconds (so the video starts cleanly with VO first)
      - Smooth cosine fade-in over `fade_in_s` seconds
      - Target RMS normalization (soft, balanced background level)
      - Smooth cosine fade-out over the last `fade_out_s` seconds
    """
    out = stereo.astype(np.float32).copy()
    n = len(out)

    # Normalize active RMS first
    cur_rms = float(np.sqrt(np.mean(out ** 2) + 1e-12))
    out = out * (target_rms / cur_rms)

    # Envelope: delay -> cosine fade-in -> 1.0 -> cosine fade-out
    env = np.ones(n, dtype=np.float32)
    i_delay = min(n, int(round(start_delay_s * sr)))
    i_fi_end = min(n, i_delay + int(round(fade_in_s * sr)))
    i_fo_start = max(i_fi_end, n - int(round(fade_out_s * sr)))

    env[:i_delay] = 0.0
    if i_fi_end > i_delay:
        u = np.linspace(0.0, 1.0, i_fi_end - i_delay, dtype=np.float32)
        env[i_delay:i_fi_end] = 0.5 - 0.5 * np.cos(np.pi * u)
    if n > i_fo_start:
        u = np.linspace(0.0, 1.0, n - i_fo_start, dtype=np.float32)
        env[i_fo_start:] = 0.5 + 0.5 * np.cos(np.pi * u)

    out[:, 0] *= env
    out[:, 1] *= env
    return np.clip(out, -0.95, 0.95)


def duck_bgm_under_vo(bgm_stereo, vo_mono, sr=SR):
    """
    Carves mid-range vocal pocket (900-3800 Hz) and sidechain-ducks BGM smoothly whenever VO speaks
    so VO remains 100% dominant and effortless to hear, while BGM swells gently during pauses.
    """
    win = max(16, int(0.050 * sr))
    vo_sq = vo_mono[:len(bgm_stereo)].astype(np.float64) ** 2
    vo_rms = np.sqrt(np.convolve(vo_sq, np.ones(win) / win, mode="same") + 1e-12).astype(np.float32)
    speaking = np.clip((vo_rms - 0.008) / 0.030, 0.0, 1.0)
    # Smooth release (220ms) so music breathes naturally between sentences
    win_rel = int(0.220 * sr)
    speaking = np.convolve(speaking, np.ones(win_rel, dtype=np.float32) / win_rel, mode="same")

    # When VO speaks, BGM drops to 42% (-7.5 dB); in pauses, BGM rises to 100%
    gain = 1.0 - 0.58 * speaking
    out = np.zeros_like(bgm_stereo, dtype=np.float32)
    for ch in range(2):
        s = bgm_stereo[:, ch]
        pocket = _bandpass(s, 900.0, 3800.0, sr)
        s_carved = s - 0.55 * speaking * pocket
        out[:, ch] = s_carved * gain
    return out


def save_mp3(stereo, mp3_path, sr=SR):
    tmp_wav = mp3_path + ".tmp.wav"
    write_wav_stereo_float(tmp_wav, stereo, sr=sr)
    subprocess.check_call([
        FF, "-y", "-hide_banner", "-loglevel", "error",
        "-i", tmp_wav, "-c:a", "libmp3lame", "-b:a", "192k", mp3_path
    ])
    os.remove(tmp_wav)


def build_all_previews():
    os.makedirs("output", exist_ok=True)
    prev_dur = 45.0  # 45s per standalone option preview

    print("Menyintesis Opsi 1 (Cosmic Cathedral Organ & Relativity Arpeggio — Interstellar Style)...")
    opt1_raw = generate_option_1_interstellar_organ(prev_dur, SR)
    opt1 = apply_fade_in_out_and_normalize(opt1_raw, start_delay_s=2.5, fade_in_s=4.5, fade_out_s=5.0, target_rms=0.085)
    save_mp3(opt1, "output/BGM_Opsi_1_Cathedral_Space_Organ_Interstellar_Style.mp3")

    print("Menyintesis Opsi 2 (Deep Cosmos Warm Ambient Pad & Distant Felt Piano)...")
    opt2_raw = generate_option_2_deep_cosmos_piano_pad(prev_dur, SR)
    opt2 = apply_fade_in_out_and_normalize(opt2_raw, start_delay_s=2.5, fade_in_s=4.5, fade_out_s=5.0, target_rms=0.085)
    save_mp3(opt2, "output/BGM_Opsi_2_Deep_Cosmos_Ambient_Piano.mp3")

    print("Menyintesis Opsi 3 (Event Horizon Cinematic Strings & Organ Swell)...")
    opt3_raw = generate_option_3_event_horizon_strings_organ(prev_dur, SR)
    opt3 = apply_fade_in_out_and_normalize(opt3_raw, start_delay_s=2.5, fade_in_s=4.5, fade_out_s=5.0, target_rms=0.085)
    save_mp3(opt3, "output/BGM_Opsi_3_Event_Horizon_Strings_Organ.mp3")

    # Also build a 3-in-1 simulation preview mixed with the first 28s of @SeorangSains VO so the user can hear the exact VO+BGM balance!
    vo_mp3 = "output/VO_Master_Long01_84_Adegan_16x9.mp3"
    if os.path.exists(vo_mp3):
        tmp_vo_wav = "output/_tmp_vo_prev.wav"
        subprocess.check_call([
            FF, "-y", "-hide_banner", "-loglevel", "error",
            "-i", vo_mp3, "-t", "28", "-ar", str(SR), "-ac", "2", tmp_vo_wav
        ])
        vo_st, _ = read_wav_stereo_float(tmp_vo_wav)
        os.remove(tmp_vo_wav)
        vo_m = 0.5 * (vo_st[:, 0] + vo_st[:, 1])
        seg_n = len(vo_m)
        gap = np.zeros((int(1.8 * SR), 2), dtype=np.float32)

        sim_segs = []
        for raw_bgm in [opt1_raw[:seg_n], opt2_raw[:seg_n], opt3_raw[:seg_n]]:
            bgm_env = apply_fade_in_out_and_normalize(raw_bgm, start_delay_s=2.5, fade_in_s=4.5, fade_out_s=4.0, target_rms=0.052)
            bgm_ducked = duck_bgm_under_vo(bgm_env, vo_m, sr=SR)
            mixed = np.clip(vo_st * 0.92 + bgm_ducked, -0.98, 0.98)
            sim_segs.append(mixed)
            sim_segs.append(gap)

        full_sim = np.concatenate(sim_segs[:-1], axis=0)
        save_mp3(full_sim, "output/PREVIEW_Simulasi_3_Opsi_Musik_dengan_VO.mp3")
        print("Selesai membuat PREVIEW_Simulasi_3_Opsi_Musik_dengan_VO.mp3!")


if __name__ == "__main__":
    build_all_previews()
