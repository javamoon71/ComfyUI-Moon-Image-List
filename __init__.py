# ComfyUI에 Moon Image List 노드를 등록하는 진입점
from .nodes.image_list import ImageList

NODE_CLASS_MAPPINGS = {"ImageList": ImageList}
NODE_DISPLAY_NAME_MAPPINGS = {"ImageList": "Moon Image List (ImageList)"}

WEB_DIRECTORY = "./web"
