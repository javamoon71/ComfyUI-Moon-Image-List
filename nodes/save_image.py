# 입력 IMAGE를 png/jpg/webp 파일로 저장하고 미리보기를 보여 주는 노드
import json
import os
import re
import uuid
from datetime import datetime

import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo


def format_date(fmt, now):
    # ComfyUI 프론트엔드의 %date:...% 형식과 같은 토큰을 쓴다
    def part(match):
        token = match.group(0)
        if token == "yyyy":
            return str(now.year)
        if token == "yy":
            return str(now.year)[2:]
        value = {"d": now.day, "M": now.month, "h": now.hour, "m": now.minute, "s": now.second}[token[0]]
        return str(value).zfill(len(token))

    return re.sub(r"yyyy|yy|dd?|MM?|hh?|mm?|ss?", part, fmt)


def apply_tokens(text, width, height, now):
    # 프론트엔드는 기본 Save 노드에만 치환을 적용하므로 여기서 직접 바꾼다
    text = re.sub(r"%date:([^%]*)%", lambda m: format_date(m.group(1), now), text)
    return text.replace("%width%", str(width)).replace("%height%", str(height))


def next_counter(folder, filename):
    # 기본 SaveImage와 같은 규칙: {filename}_{번호}_.{확장자} 중 가장 큰 번호 + 1
    pattern = re.compile(re.escape(filename) + r"_(\d+)_\.", re.IGNORECASE)
    counters = [int(m.group(1)) for name in os.listdir(folder) if (m := pattern.match(name))]
    return max(counters, default=0) + 1


def relative_subfolder(folder, base):
    # folder가 base 안이면 /view에 넘길 하위 폴더, 밖이면 None
    try:
        rel = os.path.relpath(folder, base)
    except ValueError:  # Windows에서 드라이브가 다르면 상대 경로를 만들 수 없다
        return None
    if rel == os.pardir or rel.startswith(os.pardir + os.sep):
        return None
    return "" if rel == os.curdir else rel.replace(os.sep, "/")


def to_pil(image):
    array = 255.0 * image.cpu().numpy()
    return Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))


def save_file(img, path, file_format, quality, metadata):
    if file_format == "png":
        info = None
        if metadata:
            info = PngInfo()
            for key, value in metadata.items():
                info.add_text(key, json.dumps(value))
        img.save(path, pnginfo=info, compress_level=4)
    elif file_format == "webp":
        # SaveAnimatedWEBP와 같은 형식이라 ComfyUI에 끌어다 놓으면 워크플로가 열린다
        exif = Image.Exif()
        tag = 0x0110
        for key, value in metadata.items():
            exif[tag] = f"{key}:{json.dumps(value)}"
            tag -= 1
        img.save(path, quality=quality, exif=exif)
    else:
        # JPEG EXIF는 64KB 제한이 있어 워크플로를 넣지 않는다
        img.convert("RGB").save(path, quality=quality)


def save_preview(img, temp_dir):
    # output 밖에 저장한 파일은 /view로 열 수 없어서 temp 폴더에 사본을 둔다
    os.makedirs(temp_dir, exist_ok=True)
    name = f"MoonSaveImage_{uuid.uuid4().hex[:8]}.png"
    img.save(os.path.join(temp_dir, name), compress_level=1)
    return {"filename": name, "subfolder": "", "type": "temp"}


class MoonSaveImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "output_path": ("STRING", {"default": ""}),
                "file_format": (["png", "jpg", "webp"], {"default": "png"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100}),
                "save_metadata": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "save"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def save(self, images, filename_prefix, output_path, file_format, quality, save_metadata,
             prompt=None, extra_pnginfo=None):
        # ComfyUI 밖(테스트)에서도 import할 수 있도록 여기서 불러온다
        import folder_paths

        output_dir = folder_paths.get_output_directory()
        height, width = images.shape[1:3]
        now = datetime.now()
        target = os.path.join(
            output_dir,
            apply_tokens(output_path, width, height, now),
            apply_tokens(filename_prefix, width, height, now),
        )
        folder, filename = os.path.split(os.path.normpath(target))
        os.makedirs(folder, exist_ok=True)

        metadata = {}
        if save_metadata:
            if prompt is not None:
                metadata["prompt"] = prompt
            metadata.update(extra_pnginfo or {})

        counter = next_counter(folder, filename)
        subfolder = relative_subfolder(folder, output_dir)
        results = []
        for image in images:
            img = to_pil(image)
            file = f"{filename}_{counter:05}_.{file_format}"
            save_file(img, os.path.join(folder, file), file_format, quality, metadata)
            if subfolder is None:
                results.append(save_preview(img, folder_paths.get_temp_directory()))
            else:
                results.append({"filename": file, "subfolder": subfolder, "type": "output"})
            counter += 1

        return {"ui": {"images": results}, "result": (images,)}
