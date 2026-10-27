# ImageList 노드의 이미지 선택과 로드 동작을 검증하는 테스트
import json
import os
import sys
import tempfile
import types
import unittest

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.image_list import ImageList

# ComfyUI의 folder_paths 대신 임시 폴더를 input 폴더로 쓴다
_input_dir = tempfile.TemporaryDirectory()
sys.modules["folder_paths"] = types.SimpleNamespace(
    get_annotated_filepath=lambda name: os.path.join(_input_dir.name, name)
)


def save(name, size, mode="RGB", color=(255, 0, 0)):
    Image.new(mode, size, color).save(os.path.join(_input_dir.name, name))


class TestImageList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        save("a.png", (4, 3))
        save("b.png", (2, 5), mode="RGBA", color=(0, 255, 0, 0))
        save("c.jpg", (6, 6))

    def setUp(self):
        self.node = ImageList()
        self.images = json.dumps(["a.png", "b.png", "c.jpg"])

    def test_pick_by_index_wraps(self):
        self.assertEqual(ImageList.pick(self.images, 1), "b.png")
        self.assertEqual(ImageList.pick(self.images, 4), "b.png")

    def test_pick_skips_blank(self):
        self.assertEqual(ImageList.pick(json.dumps(["", " a.png ", "  "]), 0), "a.png")

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            self.node.select("[]", 0)

    def test_random_picks_from_items(self):
        picked = {ImageList.pick(self.images, 0, random=True) for _ in range(200)}
        self.assertEqual(picked, {"a.png", "b.png", "c.jpg"})

    def test_load_rgb(self):
        image, mask = self.node.select(self.images, 0)
        self.assertEqual(tuple(image.shape), (1, 3, 4, 3))
        self.assertAlmostEqual(image[0, 0, 0, 0].item(), 1.0)
        self.assertEqual(tuple(mask.shape), (1, 64, 64))

    def test_load_alpha_mask(self):
        image, mask = self.node.select(self.images, 1)
        self.assertEqual(tuple(image.shape), (1, 5, 2, 3))
        self.assertEqual(tuple(mask.shape), (1, 5, 2))
        self.assertAlmostEqual(mask.min().item(), 1.0)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.node.select(json.dumps(["nope.png"]), 0)

    def test_is_changed(self):
        changed = ImageList.IS_CHANGED(self.images, 0, random=True)
        self.assertNotEqual(changed, changed)
        self.assertEqual(ImageList.IS_CHANGED(self.images, 0), ImageList.IS_CHANGED(self.images, 3))
        self.assertNotEqual(ImageList.IS_CHANGED(self.images, 0), ImageList.IS_CHANGED(self.images, 1))


if __name__ == "__main__":
    unittest.main()
