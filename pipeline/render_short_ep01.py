"""Short 01 production: validate storyboard, assemble VO, normalize images, render.

Run from repo root after installing requirements.txt into a virtual environment.
Master timeline uses estimated per-sentence boundaries (TTS chunk has no word timestamps).
Check scene cuts by ear before publishing; no generated captions or music.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from mutagen.mp3 import MP3
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'script/01-SHORT-KENAPA-MEMBACA-DI-MOBIL-BIKIN-MABUK.md'
OUTPUT = ROOT / 'output'
IMAGES = ROOT / 'assets/images'
MASTER = OUTPUT / 'VO_Master_Short01_30_Adegan_9x16.mp3'
TIMELINE = OUTPUT / 'short01_timeline_30_scenes.json'
VIDEO = OUTPUT / 'VIDEO_SHORT_01_Kenapa_Membaca_di_Mobil_Bikin_Mabuk_9x16_1080p_60fps.mp4'
GAP = 0.28  # added only between chunks; natural intra-chunk pauses are left intact


def scenes():
    result = []
    for line in SCRIPT.read_text(encoding='utf-8').splitlines():
        if not re.match(r'^\| \d\d \|', line):
            continue
        columns = [x.strip() for x in line.split('|')[1:-1]]
        if len(columns) != 4:
            raise ValueError(f'Malformed storyboard row: {line}')
        number, chunk, voice, visual = columns
        number = int(number)
        words = len(voice.split())
        if words not in (12, 13):
            raise ValueError(f'Scene {number}: expected 12–13 VO words, found {words}')
        if chunk != f'c{(number-1)//5+1}':
            raise ValueError(f'Scene {number}: unexpected chunk {chunk}')
        if number <= 3:
            name = f'short01_intro_{number:02d}.jpg'
        elif number <= 10:
            name = f'short01_t1_{number-3:02d}.jpg'
        elif number <= 20:
            name = f'short01_t2_{number-10:02d}.jpg'
        else:
            name = f'short01_t3_{number-20:02d}.jpg'
        result.append(dict(scene=number, chunk=chunk, vo=voice, visual=visual,
                           image=str(Path('assets/images') / name)))
    if [s['scene'] for s in result] != list(range(1, 31)):
        raise ValueError('Storyboard must contain precisely ordered scenes 01–30')
    return result


def run(*args):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y',
                    *map(str, args)], check=True)


def prepare():
    rows = scenes()
    OUTPUT.mkdir(exist_ok=True)
    clips = [OUTPUT / f'vo_short01_c{i}.mp3' for i in range(1, 7)]
    missing = [str(p) for p in clips if not p.is_file()]
    if missing:
        raise FileNotFoundError('Missing VO: ' + ', '.join(missing))
    durations = [MP3(str(p)).info.length for p in clips]
    # Keep each TTS chunk whole, including natural pauses; add silence only at chunk boundaries.
    inputs = []
    parts = []
    for i, clip in enumerate(clips):
        inputs += ['-i', clip]
        parts += [f'[{i}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono[a{i}]']
    for i in range(5):
        parts += [f'anullsrc=r=24000:cl=mono,atrim=duration={GAP}[g{i}]']
    order = ''.join(f'[a{i}]' + (f'[g{i}]' if i < 5 else '') for i in range(6))
    parts += [f'{order}concat=n=11:v=0:a=1[voice]']
    run(*inputs, '-filter_complex', ';'.join(parts), '-map', '[voice]', '-c:a', 'libmp3lame',
        '-q:a', '2', MASTER)
    master_duration = MP3(str(MASTER)).info.length
    # Proportional sentence timing is approximate without forced alignment.
    estimated_total = sum(durations) + 5 * GAP
    scale = master_duration / estimated_total
    cursor = 0.0
    for group, duration in enumerate(durations):
        subset = rows[group*5:group*5+5]
        weights = [len(s['vo']) for s in subset]
        total_weight = sum(weights)
        for scene in subset:
            scene_duration = duration * len(scene['vo']) / total_weight * scale
            scene['start'] = round(cursor, 4)
            cursor += scene_duration
            scene['end'] = round(cursor, 4)
        if group < 5:
            cursor += GAP * scale
            # the gap is displayed on the last image of the preceding chunk
            subset[-1]['end'] = round(cursor, 4)
    rows[-1]['end'] = round(master_duration, 4)
    if master_duration >= 180:
        raise ValueError(f'VO too long for this plan: {master_duration:.2f}s >= 180s')
    payload = dict(title='Kenapa membaca di mobil bikin mabuk?', fps=60,
                   resolution=[1080, 1920], duration=round(master_duration, 4),
                   voiceover=str(MASTER.relative_to(ROOT)),
                   timing_note='Estimated scene cuts, proportional to character length within each 5-scene VO chunk; verify by listening before publish.',
                   scenes=rows)
    TIMELINE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Master: {MASTER} ({master_duration:.2f}s); timeline: {TIMELINE}')


def normalize():
    rows = scenes()
    found = 0
    for row in rows:
        path = ROOT / row['image']
        if not path.is_file():
            continue
        # Normalize only the actual generated scene. Never draw or paint over its contents.
        with Image.open(path) as original:
            rgb = ImageOps.fit(original.convert('RGB'), (1080, 1920), method=Image.Resampling.LANCZOS)
            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
            rgb.save(path, 'JPEG', quality=96, subsampling=0)
        found += 1
    print(f'Normalized {found}/30 images; missing scenes have NOT been fabricated.')


def render():
    if not TIMELINE.is_file() or not MASTER.is_file():
        raise FileNotFoundError('Run --prepare first to assemble voiceover and timeline')
    data = json.loads(TIMELINE.read_text(encoding='utf-8'))
    if len(data['scenes']) != 30:
        raise ValueError('Timeline must contain 30 scenes')
    missing = [s['image'] for s in data['scenes'] if not (ROOT / s['image']).is_file()]
    if missing:
        raise FileNotFoundError('Cannot render; missing original images: ' + ', '.join(missing))
    for s in data['scenes']:
        with Image.open(ROOT / s['image']) as im:
            if im.size != (1080, 1920) or im.format != 'JPEG':
                raise ValueError(f'Image not normalized to 1080x1920 JPEG: {s["image"]}')
    # Concat demuxer holds each original sharp image for its scene duration.
    # Escape single quotes for the concat demuxer's quoted file syntax.
    with tempfile.TemporaryDirectory() as folder:
        listing = Path(folder) / 'frames.txt'
        def entry(s):
            filename = str((ROOT / s['image']).resolve()).replace("'", "'\\''")
            return "file '" + filename + "'\n"
        text = ''.join(entry(s) + f"duration {s['end']-s['start']:.6f}\n" for s in data['scenes'])
        text += entry(data['scenes'][-1])  # concat demuxer needs final file repeated
        listing.write_text(text, encoding='utf-8')
        run('-f', 'concat', '-safe', '0', '-i', listing, '-i', MASTER,
            '-map', '0:v:0', '-map', '1:a:0', '-vf', 'fps=60,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', '60',
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
            '-t', data['duration'], VIDEO)
    print('Rendered:', VIDEO)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['validate', 'prepare', 'normalize', 'render'])
    args = parser.parse_args()
    if args.action == 'validate':
        print('Validated', len(scenes()), 'scenes and VO word counts')
    elif args.action == 'prepare':
        prepare()
    elif args.action == 'normalize':
        normalize()
    else:
        render()
