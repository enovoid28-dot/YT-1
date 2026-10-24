#!/usr/bin/env python3
"""Rakit video EP02 "Kalau Matahari Mati" (9:16, tanpa musik).

Cara kerja:
1. Baca durasi tiap segmen VO.
2. Sisipkan kartu transisi sebagai DIAM di trek audio, supaya video & audio
   selalu sinkron walau ada kartu.
3. Render tiap shot dengan gerak kamera vertikal + caption.
4. Gabung, campur dengan room tone (BUKAN musik), loudnorm -14 LUFS.

Jalankan: python3 pipeline/render_ep02.py [--preview N]
"""
import json, os, subprocess, sys
import imageio_ffmpeg
from PIL import ImageFont
from capstyle import make_caption
from ep02_storyboard import (SEGMENTS, CAP, MOVE, CARD_DUR, CARD_DUR_DEFAULT,
                            CARD_AT_START, shot_path, card_path, ROOT)

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
WORK = os.path.join(ROOT, "work/ep02")
CLIPS = os.path.join(WORK, "clips")
CAPS = os.path.join(WORK, "caps")
OUT = os.path.join(ROOT, "output")
AUD = os.path.join(ROOT, "assets/audio")
FALLBACK_SHOTS = [6, 42, 35, 33, 1]
shots_all = []


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("ffmpeg gagal:\n" + p.stderr[-2500:])


def dur(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    import re
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if not m:
        sys.exit(f"tidak bisa baca durasi: {path}")
    h, mn, s = m.groups()
    return int(h) * 3600 + int(mn) * 60 + float(s)


def plan():
    """Bangun urutan item: kartu + shot, lengkap dengan durasi."""
    items = []

    def add_card(c, d=None):
        p = card_path(c)
        if not os.path.exists(p):
            print(f"  ! kartu {c} tidak ada, dilewati")
            return
        items.append({"kind": "card", "path": p, "dur": d or CARD_DUR.get(c, CARD_DUR_DEFAULT),
                      "caption": None, "move": "in"})

    add_card(CARD_AT_START)
    for seg in SEGMENTS:
        audio = os.path.join(AUD, seg["audio"])
        if not os.path.exists(audio):
            print(f"  ! audio {seg['audio']} tidak ada, dilewati")
            continue
        sd = dur(audio)
        shots = [n for n in seg["shots"] if os.path.exists(shot_path(n))]
        missing = [n for n in seg["shots"] if not os.path.exists(shot_path(n))]
        if missing:
            print(f"  ! shot belum ada: {missing} (dialihkan ke shot lain)")
        if shots:
            each = sd / len(shots)
            for j, n in enumerate(shots):
                items.append({"kind": "shot", "path": shot_path(n), "dur": round(each, 3),
                              "caption": CAP.get(n, ""), "move": MOVE.get(n, "in"),
                              "shot": n, "first": j == 0, "audio": audio})
        else:
            # tidak ada shot tersedia
            if os.path.basename(seg["audio"]).startswith("ep02_endcard"):
                items.append({"kind": "card", "path": card_path("k7"), "dur": round(sd, 3),
                              "caption": None, "move": "in", "audio": audio})
            else:
                # pakai shot cadangan (atmosfer) supaya tidak ada kartu statis panjang
                pool = [n for n in FALLBACK_SHOTS if os.path.exists(shot_path(n))] or \
                       ([shots_all[0]] if shots_all else [])
                if not pool:
                    items.append({"kind": "card", "path": card_path("k1"),
                                  "dur": round(sd, 3), "caption": None,
                                  "move": "in", "audio": audio})
                else:
                    each = sd / len(pool)
                    for j, n in enumerate(pool):
                        items.append({"kind": "shot", "path": shot_path(n),
                                      "dur": round(each, 3),
                                      "caption": CAP.get(n, ""), "move": "up",
                                      "shot": n, "first": j == 0, "audio": audio})
        if seg.get("card_after"):
            add_card(seg["card_after"])
    return items


def build_narration(items):
    """Gabung audio mengikuti urutan item.

    Aturan: setiap segmen VO ditempel TEPAT SEKALI, pada item pertama segmen itu.
    Item lain (shot lanjutan / kartu) diisi DIAM sepanjang durasinya -> video dan
    audio selalu sinkron.
    """
    os.makedirs(WORK, exist_ok=True)
    used = set()
    entries = []  # (path or None, dur)
    for it in items:
        audio = it.get("audio")
        if audio and audio not in used:
            used.add(audio)
            entries.append(("audio", audio, None))
        elif it["kind"] in ("card", "silent"):
            entries.append(("silence", None, it["dur"]))
        # shot lanjutan dalam satu segmen: tidak menambah audio apa pun

    # semua input dinormalkan ke WAV 48k stereo dulu (mp3 TTS kadang punya
    # header durasi yang bikin concat demuxer memotong)
    lst = os.path.join(WORK, "audio_list.txt")
    with open(lst, "w") as f:
        for i, (kind, path, d) in enumerate(entries):
            wav = os.path.join(WORK, f"seg_{i:03d}.wav")
            want = dur(path) if kind == "audio" else d
            if (not os.path.exists(wav)) or abs(dur(wav) - want) > 0.05:
                if kind == "audio":
                    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", path,
                         "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", wav])
                else:
                    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                         "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{d:.3f}",
                         "-c:a", "pcm_s16le", wav])
            f.write(f"file '{wav}'\n")

    out = os.path.join(WORK, "narasi_ep02.wav")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out])
    return out, dur(out)


def zoompan(move, frames):
    if move == "in":
        z = f"min(1+0.10*on/{frames},1.10)"
        x, y = "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"
    elif move == "out":
        z = f"max(1.10-0.10*on/{frames},1.0)"
        x, y = "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"
    elif move == "up":
        z = "1.10"
        x, y = "iw/2-iw/zoom/2", f"(ih-ih/zoom)*(1-on/{frames})"
    elif move == "down":
        z = "1.10"
        x, y = "iw/2-iw/zoom/2", f"(ih-ih/zoom)*(on/{frames})"
    else:
        z, x, y = "1.0", "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"
    return z, x, y


def build_clip(it, idx):
    d = it["dur"]
    frames = max(int(round(d * FPS)), 2)
    z, x, y = zoompan(it["move"], frames)
    inputs = ["-i", it["path"]]
    fc = (f"[0:v]scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
          f"crop={W*2}:{H*2},setsar=1,"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
          f"eq=contrast=1.03:saturation=1.02,noise=alls=4:allf=t+u,vignette=PI/4.8[bg]")
    if it.get("caption"):
        cap = make_caption(it["caption"], os.path.join(CAPS, f"c{idx:03d}.png"))
        inputs += ["-loop", "1", "-i", cap]
        fc += ";[bg][1:v]overlay=0:0:format=auto[v]"
        vmap = "[v]"
    else:
        vmap = "[bg]"
    dst = os.path.join(CLIPS, f"c{idx:03d}.mp4")
    if os.path.exists(dst) and abs(dur(dst) - d) < 0.05:
        return dst
    run([FF, "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", fc, "-map", vmap, "-r", str(FPS),
         "-t", f"{d:.3f}", "-frames:v", str(frames),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", "-an", dst])
    return dst


def main():
    preview = int(sys.argv[sys.argv.index("--preview") + 1]) if "--preview" in sys.argv else None
    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    items = plan()
    if preview:
        items = items[:preview]
    print(f"total item: {len(items)}")

    narasi, audio_total = build_narration(items)
    print(f"narasi: {audio_total:.1f}s")

    clips = []
    for i, it in enumerate(items):
        name = it.get("shot") or os.path.basename(it.get("path", "silent"))
        print(f"[{i+1}/{len(items)}] {it['kind']:6s} {str(name):>6s} {it['dur']:.2f}s")
        clips.append(build_clip(it, i))

    lst = os.path.join(WORK, "clips.txt")
    with open(lst, "w") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    vo = os.path.join(WORK, "video_only.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", lst, "-c", "copy", vo])

    # room tone (bukan musik): desis sangat tipis
    tone = os.path.join(WORK, "room.wav")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", f"anoisesrc=color=brown:duration={audio_total:.2f}:amplitude=0.35",
         "-af", "lowpass=f=180,highpass=f=40,volume=0.035,"
                f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(audio_total-2,0):.2f}:d=2",
         "-ar", "48000", "-ac", "2", tone])

    dst = os.path.join(OUT, "STICKMAN_ep02_kalau-matahari-mati_9x16.mp4")
    run([FF, "-y", "-hide_banner", "-loglevel", "error",
         "-i", vo, "-i", narasi, "-i", tone,
         "-filter_complex",
         "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[v];"
         "[2:a]volume=1.0[room];"
         "[v][room]amix=inputs=2:duration=first:dropout_transition=2,"
         "alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", dst])
    print("\nselesai:", dst, f"({dur(dst):.1f}s)")


if __name__ == "__main__":
    main()
