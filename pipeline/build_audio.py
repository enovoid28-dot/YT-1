#!/usr/bin/env python3
"""Bangun narasi: gabung 10 segmen VO jadi satu track, sisipkan jeda kecil."""
import json, os, re, subprocess, sys
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()
AUD = os.path.join(ROOT, "assets/audio")


def dur(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    h, mnt, s = m.groups()
    return int(h) * 3600 + int(mnt) * 60 + float(s)


def main():
    segs = [f"s{i:02d}.mp3" for i in range(1, 11)]
    missing = [s for s in segs if not os.path.exists(os.path.join(AUD, s))]
    if missing:
        sys.exit(f"audio belum lengkap: {missing}")
    info = []
    for s in segs:
        p = os.path.join(AUD, s)
        info.append({"file": s, "dur": round(dur(p), 3)})
        print(f"{s}  {dur(p):.2f}s")

    # jeda antar segmen (detik) — beri nafas dokumenter
    gap = 0.45
    listfile = os.path.join(AUD, "_concat.txt")
    files = []
    silence = os.path.join(AUD, "_gap.wav")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi",
                    "-i", f"anullsrc=r=48000:cl=stereo", "-t", str(gap), silence], check=True)
    for i, s in enumerate(segs):
        files.append(os.path.join(AUD, s))
        if i < len(segs) - 1:
            files.append(silence)
    with open(listfile, "w") as f:
        for p in files:
            f.write(f"file '{p}'\n")

    out = os.path.join(AUD, "narasi.wav")
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", listfile,
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", out], check=True)

    total = dur(out)
    print(f"\nnarasi.wav  {total:.2f}s  ({int(total//60)}:{total%60:04.1f})")

    # timeline per segmen (mulai, selesai, durasi termasuk jeda)
    t = 0.0
    timeline = []
    for i, s in enumerate(info):
        d = s["dur"] + (gap if i < len(info) - 1 else 0.0)
        timeline.append({"segment": i + 1, "start": round(t, 3), "end": round(t + d, 3),
                         "dur": round(d, 3), "file": s["file"]})
        t += d
    tp = os.path.join(ROOT, "work/timeline.json")
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    json.dump({"total": round(total, 3), "gap": gap, "segments": timeline},
              open(tp, "w"), indent=2)
    print("timeline ->", tp)


if __name__ == "__main__":
    main()
