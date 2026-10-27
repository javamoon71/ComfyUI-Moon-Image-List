# 업로드한 이미지 목록을 관리하고 index에 해당하는 이미지를 IMAGE/MASK로 출력하는 노드
import json
import os
import random as _random

import numpy as np
import torch
from PIL import Image, ImageOps

# 다른 노드가 전역 random 시드를 고정해도 영향받지 않도록 별도 인스턴스를 쓴다
_rng = _random.Random()


def parse_items(text):
    # 위젯은 파일 이름 목록을 JSON 배열 문자열로 보낸다
    try:
        items = json.loads(text)
    except ValueError:
        items = None
    if not isinstance(items, list):
        items = text.splitlines()
    return [str(item).strip() for item in items if str(item).strip()]


def image_path(name):
    # ComfyUI 밖(테스트)에서도 import할 수 있도록 여기서 불러온다
    import folder_paths

    return folder_paths.get_annotated_filepath(name)


def load_image(path):
    # 기본 Load Image 노드와 같은 형식: IMAGE [1,H,W,3], MASK [1,H,W] (알파가 없으면 64x64 0)
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode == "I":
            img = img.point(lambda i: i * (1 / 255))
        image = torch.from_numpy(np.array(img.convert("RGB")).astype(np.float32) / 255.0)[None,]
        if "A" in img.getbands():
            alpha = np.array(img.getchannel("A")).astype(np.float32) / 255.0
            mask = 1.0 - torch.from_numpy(alpha)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32)
    return image, mask.unsqueeze(0)


class ImageList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE_LIST", {"default": "[]"}),
                "index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}),
                "random": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "select"
    CATEGORY = "image"

    @staticmethod
    def pick(images, index, random=False):
        items = parse_items(images)
        if not items:
            raise ValueError("Moon Image List: 등록된 이미지가 없습니다.")
        if random:
            return _rng.choice(items)
        return items[index % len(items)]

    @classmethod
    def IS_CHANGED(cls, images, index, random=False):
        # NaN은 자기 자신과도 같지 않아서 ComfyUI가 매번 다시 실행한다
        if random:
            return float("nan")
        # 같은 이름의 파일이 덮어써지면 다시 실행되도록 수정 시각을 함께 쓴다
        try:
            name = cls.pick(images, index)
            return f"{name}:{os.path.getmtime(image_path(name))}"
        except (ValueError, OSError):
            return ""

    def select(self, images, index, random=False):
        name = self.pick(images, index, random)
        path = image_path(name)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Moon Image List: 이미지 파일을 찾을 수 없습니다: {name}")
        return load_image(path)
