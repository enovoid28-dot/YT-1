"""Generate Short 01 illustrations with the owner's Gemini API key on an internet-enabled machine.

Security: reads GEMINI_API_KEY ONLY from the environment; never accepts a key argument,
never writes a key to files, never adds binary assets to Git. Requires human visual QA.
The Arena sandbox cannot reach Google's Gemini endpoint; run this elsewhere.
"""
import argparse
import io
import os
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from render_short_ep01 import ROOT, scenes

DEFAULT_MODEL = 'gemini-2.5-flash-image'
INTRO = (
    'The SeorangSains mascot appears ONLY in scenes 01–03 and 30: a white round head '
    'with thick black outline, expressive cartoon face, and detailed black sunglasses. '
    'Extremely skinny torso, arms and legs, EACH a single thin black line; simple white '
    'cartoon hands. Absolutely NO clothes, fleshy arms, white glow/halo, or thick limbs. '
)
PASSENGER = (
    'Use the ordinary stickman WITHOUT sunglasses: a white round head with thick black '
    'outline and expressive eyes/mouth, extremely skinny single black line torso/arms/legs, '
    'simple white cartoon hands, no clothing, fleshy limbs or white halo. The same teal '
    'compact car and same passenger when a car is shown, seated safely with seat belt. '
)
NO_CHARACTER = (
    'Anatomy/object-only scene; do not introduce the mascot or an extra character. '
)
STYLE = (
    'Create exactly ONE polished original illustration, portrait 9:16, for one scene '
    'of a chronologically consistent Indonesian educational science video. Crisp, '
    'high-detail 3D-cartoon aesthetic with cinematic lighting, anatomically plausible '
    'when showing the inner ear; dark slate #1E293B for internal anatomy. '
    'No letters, text, numbers, printed pages, icons with lettering, license plates, '
    'labels, signs, captions, logos, watermarks, or typography anywhere. All visible '
    'book pages and phone screens must be completely blank. No gore. '
)
ANATOMY_ONLY = {9, 10, 13, 14}


def selected_rows(rows, scene_numbers, batch, all_scenes):
    if sum(bool(x) for x in (scene_numbers, batch, all_scenes)) != 1:
        raise ValueError('Choose exactly one: --scene, --batch or --all')
    if batch:
        start = (batch - 1) * 10 + 1
        wanted = set(range(start, start + 10))
    elif all_scenes:
        wanted = set(range(1, 31))
    else:
        wanted = set(scene_numbers)
    if not wanted or any(n not in range(1, 31) for n in wanted):
        raise ValueError('Scene numbers must be 01–30')
    return [row for row in rows if row['scene'] in wanted]


def prompt_for(row):
    number = row['scene']
    character = INTRO if number in (1, 2, 3, 30) else (
        NO_CHARACTER if number in ANATOMY_ONLY else PASSENGER
    )
    return (STYLE + character + f'Scene {number:02d} visual direction: {row["visual"]} '
            'Scene must work as a single frame, NOT a grid, collage, '
            'storyboard sheet or multiple variations. Do not depict written text.')


def save_normalized(image_bytes, target):
    # Normalize the generated image; never draw on top of the scene with PIL.
    with Image.open(io.BytesIO(image_bytes)) as source:
        if source.width < 512 or source.height < 512:
            raise ValueError('Image unexpectedly small; review/retry manually')
        normalized = ImageOps.fit(source.convert('RGB'), (1080, 1920), method=Image.Resampling.LANCZOS)
        normalized = normalized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
        target.parent.mkdir(parents=True, exist_ok=True)
        # Write atomically to avoid leaving a truncated scene on failure.
        temporary = target.with_suffix('.tmp')
        try:
            normalized.save(temporary, format='JPEG', quality=96, subsampling=0)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


def generate(client, model, row, target):
    from google.genai import types
    response = client.models.generate_content(
        model=model,
        contents=prompt_for(row),
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(aspect_ratio='9:16'),
        ),
    )
    parts = response.parts or []
    images = [part.inline_data.data for part in parts if part.inline_data is not None]
    if len(images) != 1 or not images[0]:
        raise RuntimeError(f'Scene {row["scene"]}: expected one image; received {len(images)}')
    save_normalized(images[0], target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--scene', type=int, action='append', help='Scene number, repeatable')
    group.add_argument('--batch', type=int, choices=(1, 2, 3), help='Batch of 10 scenes')
    group.add_argument('--all', action='store_true', help='All 30 scenes (may incur charges)')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Image-capable Gemini model')
    parser.add_argument('--dry-run', action='store_true', help='Print prompts and filenames only; no API key required')
    parser.add_argument('--force', action='store_true', help='Regenerate existing image (may incur charges)')
    args = parser.parse_args(argv)
    rows = selected_rows(scenes(), args.scene, args.batch, args.all)
    pending = [(row, ROOT / row['image']) for row in rows]
    if not args.force:
        pending = [(row, path) for row, path in pending if not path.exists()]
    print(f'Planning {len(pending)}/{len(rows)} images; model={args.model}; '
          f'existing files skipped unless --force', flush=True)
    if args.dry_run:
        for row, path in pending:
            print(f'\n#{row["scene"]:02d} {path.relative_to(ROOT)}\n{prompt_for(row)}')
        return 0
    if not pending:
        return 0
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        parser.error('Set GEMINI_API_KEY in your local environment (do not paste it into chat or Git)')
    try:
        from google import genai
    except ImportError:
        parser.error('Install requirements.txt first (google-genai is missing)')
    client = genai.Client(api_key=key)
    try:
        for row, path in pending:
            try:
                generate(client, args.model, row, path)
            except Exception as exc:
                # Do not emit exception bodies: SDK errors could include request details.
                print(f'Failed scene #{row["scene"]:02d} ({type(exc).__name__}). '
                      'Stopped; check model access, quota or account status privately.', file=sys.stderr)
                return 1
            print(f'Saved #{row["scene"]:02d}: {path.relative_to(ROOT)} '
                  '(manual visual inspection required)', flush=True)
    finally:
        client.close()
    print('Done. Inspect EVERY image for text, defects, consistency and scientific accuracy '
          'before generating previews, ZIPs or rendering.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
