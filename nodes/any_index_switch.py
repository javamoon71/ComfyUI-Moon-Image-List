# 연결된 여러 입력(타입 무관) 중 index에 해당하는 값 하나만 실행해 출력하는 스위치 노드
import re

VALUE_NAME = re.compile(r"value(\d+)")


class AnyType(str):
    # ComfyUI는 타입을 != 로 비교하므로 항상 같다고 답해 어떤 타입과도 연결되게 한다 ("*"를 직접 지원하지 않는 예전 버전 호환)
    def __ne__(self, other):
        return False


ANY = AnyType("*")


class ValueInputs(dict):
    # 프론트엔드가 추가한 value1, value2...도 선언된 lazy 입력으로 인정한다. 노드 정의(JSON)에는 value0만 나간다
    def __contains__(self, key):
        return isinstance(key, str) and VALUE_NAME.fullmatch(key) is not None

    def __getitem__(self, key):
        if key in self:
            return (ANY, {"lazy": True})
        raise KeyError(key)


class AnyIndexSwitch:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 프론트엔드가 생성 후 제어 위젯을 붙인다. 기본 fixed라 예전 워크플로는 index가 바뀌지 않는다
                "index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "control_after_generate": "fixed"}),
            },
            "optional": ValueInputs(value0=(ANY, {"lazy": True})),
        }

    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("value",)
    FUNCTION = "switch"
    CATEGORY = "utils"

    @staticmethod
    def pick(index, values):
        # 연결된 입력만 슬롯 번호 순서로 센다. value10이 value2 뒤에 오도록 숫자로 정렬한다
        names = sorted(values, key=lambda name: int(VALUE_NAME.fullmatch(name)[1]))
        if not names:
            raise ValueError("Moon Any Index Switch: 연결된 입력이 없습니다.")
        return names[index % len(names)]

    def check_lazy_status(self, index, **values):
        # 아직 실행되지 않은 lazy 입력은 None으로 들어온다. 선택된 입력만 실행을 요청한다
        name = self.pick(index, values)
        return [name] if values[name] is None else []

    def switch(self, index, **values):
        return (values[self.pick(index, values)],)
