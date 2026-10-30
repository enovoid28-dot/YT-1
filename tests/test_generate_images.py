"""Offline, no-credential tests for the external Gemini image generator."""
import io
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pipeline'))
from generate_images_gemini import prompt_for, save_normalized, selected_rows, scenes


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.rows = scenes()

    def test_batches_and_scene_count(self):
        self.assertEqual(len(self.rows), 30)
        self.assertEqual([s['scene'] for s in selected_rows(self.rows, None, 2, False)], list(range(11, 21)))
        self.assertEqual([s['scene'] for s in selected_rows(self.rows, [3, 30], None, False)], [3, 30])
        with self.assertRaises(ValueError):
            selected_rows(self.rows, [31], None, False)

    def test_mascot_only_opening_and_close(self):
        for s in self.rows:
            text = prompt_for(s)
            self.assertIn('No letters, text, numbers', text)
            if s['scene'] in (1, 2, 3, 30):
                self.assertIn('detailed black sunglasses', text)
            else:
                self.assertNotIn('detailed black sunglasses', text)

    def test_normalized_jpeg(self):
        source = Image.new('RGB', (900, 1600), (28, 41, 59))
        buffer = io.BytesIO()
        source.save(buffer, 'PNG')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'scene.jpg'
            save_normalized(buffer.getvalue(), target)
            with Image.open(target) as result:
                self.assertEqual(result.size, (1080, 1920))
                self.assertEqual(result.format, 'JPEG')
            self.assertFalse(target.with_suffix('.tmp').exists())


if __name__ == '__main__':
    unittest.main()
