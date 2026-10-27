# ComfyUI에 이 팩의 노드를 등록하는 진입점
from .nodes.any_index_switch import AnyIndexSwitch
from .nodes.image_list import ImageList
from .nodes.save_image import MoonSaveImage
from .nodes.text_list import TextList

NODE_CLASS_MAPPINGS = {
    "ImageList": ImageList,
    "TextList": TextList,
    "AnyIndexSwitch": AnyIndexSwitch,
    "MoonSaveImage": MoonSaveImage,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageList": "Moon Image List (ImageList)",
    "TextList": "Text List",
    "AnyIndexSwitch": "Moon Any Index Switch (AnyIndexSwitch)",
    "MoonSaveImage": "Moon Save Image (MoonSaveImage)",
}

WEB_DIRECTORY = "./web"
