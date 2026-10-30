# MoonRemoveBackground 노드가 기본 배경 제거 모델의 마스크를 알파로 붙이는지 검증하는 테스트
import os
import sys
import unittest

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.remove_background import MoonRemoveBackground


class FakeModel:
    # ComfyUI BackgroundRemovalModel.encode_image처럼 (B, H, W) 피사체 마스크를 돌려준다. 왼쪽 절반이 피사체
    def __init__(self, dtype=torch.float32):
        self.dtype = dtype
        self.calls = []

    def encode_image(self, image):
        self.calls.append(image)
        mask = torch.zeros(image.shape[:3], dtype=self.dtype)
        mask[:, :, : image.shape[2] // 2] = 1.0
        return mask


class TestMoonRemoveBackground(unittest.TestCase):
    def setUp(self):
        self.node = MoonRemoveBackground()

    def test_rgba_keeps_rgb_and_uses_mask_as_alpha(self):
        image = torch.rand((2, 3, 4, 3))
        model = FakeModel()
        mask, rgba = self.node.remove(model, image)
        self.assertEqual(tuple(rgba.shape), (2, 3, 4, 4))
        self.assertTrue(torch.equal(rgba[..., :3], image))
        self.assertTrue(torch.equal(rgba[..., 3], mask))
        # 마스크는 모델 출력 그대로(기본 Remove Background와 같음)
        self.assertEqual(mask[0, 0].tolist(), [1.0, 1.0, 0.0, 0.0])
        self.assertIs(model.calls[0], image)

    def test_rgba_input_alpha_is_replaced(self):
        image = torch.rand((1, 3, 4, 4))
        mask, rgba = self.node.remove(FakeModel(), image)
        self.assertEqual(tuple(rgba.shape), (1, 3, 4, 4))
        self.assertTrue(torch.equal(rgba[..., :3], image[..., :3]))
        self.assertTrue(torch.equal(rgba[..., 3], mask))

    def test_mask_dtype_follows_image(self):
        # 모델이 다른 dtype(intermediate_dtype)으로 내도 이미지와 이어 붙일 수 있다
        _, rgba = self.node.remove(FakeModel(dtype=torch.float16), torch.rand((1, 2, 2, 3)))
        self.assertEqual(rgba.dtype, torch.float32)

    def test_node_definition(self):
        required = MoonRemoveBackground.INPUT_TYPES()["required"]
        self.assertEqual(list(required), ["bg_removal_model", "image"])
        self.assertEqual(required["bg_removal_model"], ("BACKGROUND_REMOVAL",))
        # 기본 Remove Background와 입력이 같고 첫 출력이 mask라 바꿔 끼울 수 있다
        self.assertEqual(MoonRemoveBackground.RETURN_TYPES, ("MASK", "IMAGE"))
        self.assertEqual(MoonRemoveBackground.RETURN_NAMES, ("mask", "image"))


if __name__ == "__main__":
    unittest.main()
