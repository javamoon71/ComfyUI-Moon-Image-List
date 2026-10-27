# 여러 줄 문자열을 리스트로 관리하고 index에 해당하는 항목을 출력하는 노드
import json
import random as _random

# 다른 노드가 전역 random 시드를 고정해도 영향받지 않도록 별도 인스턴스를 쓴다
_rng = _random.Random()


def item_pair(item):
    # 제목이 붙은 항목은 {"title", "text"} 객체이고, 예전 문자열 항목은 제목이 없다
    if isinstance(item, dict):
        return str(item.get("title", "")).strip(), str(item.get("text", "")).strip()
    return "", str(item).strip()


def parse_items(text):
    # 위젯은 항목 안의 줄바꿈을 보존하려고 JSON 배열로 보낸다. 예전 워크플로는 줄 단위 문자열이다
    try:
        items = json.loads(text)
    except ValueError:
        items = None
    if not isinstance(items, list):
        items = text.splitlines()
    # 빈 항목 판정은 내용 기준이다. 결과는 (제목, 내용) 쌍의 목록
    pairs = (item_pair(item) for item in items)
    return [p for p in pairs if p[1]]


class TextList:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("TEXT_LIST", {"default": ""}),
                "index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}),
                "random": ("BOOLEAN", {"default": False, "label_on": "On", "label_off": "Off"}),
                # 목록 UI에서 제목을 보일지만 정한다. 출력에는 영향이 없다
                "show_title": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
            }
        }

    # 제목을 내용보다 앞에 둔다(사용자 요청). 예전 워크플로의 출력 링크는 다시 연결해야 한다
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("title", "text", "title_list", "text_list")
    # title_list/text_list는 번호가 붙은 모든 항목의 제목/내용을 같은 순서의 STRING 리스트로 보낸다
    OUTPUT_IS_LIST = (False, False, True, True)
    FUNCTION = "select"
    CATEGORY = "utils/text"
    # 노드 검색은 name/display_name 외에 이 별칭도 본다. "moon"은 이름에 없어서 별칭이 있어야 찾힌다
    SEARCH_ALIASES = ["moon", "text", "textlist", "text list"]

    @classmethod
    def IS_CHANGED(cls, text, index, random=False, show_title=True):
        # NaN은 자기 자신과도 같지 않아서 ComfyUI가 매번 다시 실행한다
        return float("nan") if random else ""

    def select(self, text, index, random=False, show_title=True):
        items = parse_items(text)
        if not items:
            return ("", "", [], [])
        # show_title은 UI 표시만 정하므로 숨겨도 제목은 출력한다
        title, body = _rng.choice(items) if random else items[index % len(items)]
        return (title, body, [p[0] for p in items], [p[1] for p in items])
