# ComfyUI 기본 배경 제거 모델로 마스크를 만들고 원본에 알파로 붙여 배경이 투명한 이미지를 내는 노드
import torch


class MoonRemoveBackground:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # ComfyUI 기본 Load Background Removal Model 노드의 출력(bg_model)을 연결받는다
                "bg_removal_model": ("BACKGROUND_REMOVAL",),
                "image": ("IMAGE",),
            },
        }

    # 기본 Remove Background를 이 노드로 바꿔 끼울 수 있게 입력과 첫 출력(mask)을 기본 노드와 같게 둔다
    RETURN_TYPES = ("MASK", "IMAGE")
    RETURN_NAMES = ("mask", "image")
    FUNCTION = "remove"
    CATEGORY = "image/background removal"

    def remove(self, bg_removal_model, image):
        # 마스크는 기본 Remove Background 노드와 같은 방법으로 만든다. (B, H, W), 피사체가 1
        mask = bg_removal_model.encode_image(image)
        # HF Space의 image.putalpha(mask)처럼 원본 RGB는 그대로 두고 마스크를 알파 채널로 붙인다
        rgba = torch.cat((image[..., :3], mask.to(image).unsqueeze(-1)), dim=-1)
        return (mask, rgba)
