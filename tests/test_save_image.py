# MoonSaveImage 노드의 파일 이름, 저장 형식, 메타데이터, 미리보기 동작을 검증하는 테스트
import json
import os
import sys
import tempfile
import types
import unittest
from datetime import datetime

import torch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.save_image import MoonSaveImage, apply_tokens

PROMPT = {"1": {"class_type": "MoonSaveImage", "inputs": {}}}
EXTRA = {"workflow": {"nodes": []}}


def batch(count=1, channels=3):
    # IMAGE 형식: [개수, 높이 3, 너비 4, 채널]
    return torch.rand((count, 3, 4, channels))


def make_dir(test):
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return folder.name


class TestMoonSaveImage(unittest.TestCase):
    def setUp(self):
        # ComfyUI의 folder_paths 대신 임시 폴더를 output/temp 폴더로 쓴다
        self.output = make_dir(self)
        self.temp = make_dir(self)
        # Image List 테스트가 넣어 둔 가짜 모듈을 테스트가 끝나면 되돌린다
        self.addCleanup(sys.modules.__setitem__, "folder_paths", sys.modules.get("folder_paths"))
        sys.modules["folder_paths"] = types.SimpleNamespace(
            get_output_directory=lambda: self.output,
            get_temp_directory=lambda: self.temp,
        )
        self.node = MoonSaveImage()

    def save(self, images=None, prefix="test", path="", file_format="png", metadata=True):
        images = batch() if images is None else images
        return self.node.save(images, prefix, path, file_format, 90, metadata, prompt=PROMPT, extra_pnginfo=EXTRA)

    def test_png_batch_and_passthrough(self):
        images = batch(2)
        result = self.save(images)
        self.assertIs(result["result"][0], images)
        self.assertEqual(result["ui"]["images"], [
            {"filename": "test_00001_.png", "subfolder": "", "type": "output"},
            {"filename": "test_00002_.png", "subfolder": "", "type": "output"},
        ])
        for entry in result["ui"]["images"]:
            self.assertTrue(os.path.isfile(os.path.join(self.output, entry["filename"])))

    def test_counter_continues_across_formats(self):
        for name in ("test_00007_.jpg", "other_00099_.png", "test_extra_00050_.png"):
            open(os.path.join(self.output, name), "wb").close()
        result = self.save()
        self.assertEqual(result["ui"]["images"][0]["filename"], "test_00008_.png")

    def test_png_metadata(self):
        self.save()
        with Image.open(os.path.join(self.output, "test_00001_.png")) as img:
            self.assertEqual(json.loads(img.text["prompt"]), PROMPT)
            self.assertEqual(json.loads(img.text["workflow"]), EXTRA["workflow"])

    def test_metadata_off(self):
        self.save(metadata=False)
        self.save(file_format="webp", metadata=False)
        with Image.open(os.path.join(self.output, "test_00001_.png")) as img:
            self.assertNotIn("prompt", img.text)
        with Image.open(os.path.join(self.output, "test_00002_.webp")) as img:
            self.assertEqual(len(img.getexif()), 0)

    def test_webp_metadata(self):
        self.save(file_format="webp")
        with Image.open(os.path.join(self.output, "test_00001_.webp")) as img:
            self.assertEqual(img.format, "WEBP")
            exif = img.getexif()
            self.assertEqual(exif[0x0110], "prompt:" + json.dumps(PROMPT))
            self.assertEqual(exif[0x010F], "workflow:" + json.dumps(EXTRA["workflow"]))

    def test_jpg_converts_alpha(self):
        self.save(batch(channels=4), file_format="jpg")
        with Image.open(os.path.join(self.output, "test_00001_.jpg")) as img:
            self.assertEqual(img.format, "JPEG")
            self.assertEqual(img.mode, "RGB")

    def test_relative_output_path(self):
        result = self.save(prefix="a/name", path="sub/dir")
        self.assertEqual(result["ui"]["images"][0], {"filename": "name_00001_.png", "subfolder": "sub/dir/a", "type": "output"})
        self.assertTrue(os.path.isfile(os.path.join(self.output, "sub", "dir", "a", "name_00001_.png")))

    def test_absolute_path_previews_from_temp(self):
        outside = make_dir(self)
        result = self.save(path=outside)
        self.assertTrue(os.path.isfile(os.path.join(outside, "test_00001_.png")))
        entry = result["ui"]["images"][0]
        self.assertEqual(entry["type"], "temp")
        self.assertTrue(os.path.isfile(os.path.join(self.temp, entry["filename"])))

    def test_size_tokens_in_prefix(self):
        result = self.save(prefix="%width%x%height%")
        self.assertEqual(result["ui"]["images"][0]["filename"], "4x3_00001_.png")


class TestApplyTokens(unittest.TestCase):
    def test_date_formats(self):
        now = datetime(2026, 3, 5, 7, 8, 9)
        self.assertEqual(apply_tokens("%date:yyyy-MM-dd_hh-mm-ss%", 0, 0, now), "2026-03-05_07-08-09")
        self.assertEqual(apply_tokens("%date:yy.M.d h.m.s%/img", 0, 0, now), "26.3.5 7.8.9/img")

    def test_unknown_tokens_kept(self):
        self.assertEqual(apply_tokens("%seed%_%width%", 640, 480, datetime.now()), "%seed%_640")


if __name__ == "__main__":
    unittest.main()
