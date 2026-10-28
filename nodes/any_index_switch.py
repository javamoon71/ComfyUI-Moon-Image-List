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
                # 프론트엔드가 생성 후 제어 위젯을 붙인다. 기본 fixed라 예전 워크플로는 index가 바뀌지 않는다.
                # 연결된 입력 범위 안에서 순환시키는 부분은 web/any_index_switch.js에 있다
                "index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF, "control_after_generate": "fixed"}),
            },
            "optional": ValueInputs(value0=(ANY, {"lazy": True})),
        }

    # index 출력은 value 뒤에 둔다. 링크는 슬롯 번호로 저장되므로 기존 value 링크가 그대로 이어진다
    RETURN_TYPES = (ANY, "INT")
    RETURN_NAMES = ("value", "index")
    FUNCTION = "switch"
    CATEGORY = "utils"
    # 리스트 입력이 있어도 항목마다 실행하지 않고 한 번만 실행한다. 모든 입력이 리스트로 들어온다.
    # value는 선택된 입력의 리스트 전체를 그대로 내보내고, index는 값 하나만 내보낸다
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True, False)

    @staticmethod
    def pick(index, values):
        # 연결된 입력만 슬롯 번호 순서로 센다. value10이 value2 뒤에 오도록 숫자로 정렬한다
        names = sorted(values, key=lambda name: int(VALUE_NAME.fullmatch(name)[1]))
        if not names:
            raise ValueError("Moon Any Index Switch: 연결된 입력이 없습니다.")
        return names[index % len(names)]

    def check_lazy_status(self, index, **values):
        # 아직 실행되지 않은 lazy 입력은 (None,)으로 들어온다. 선택된 입력만 실행을 요청한다.
        # 실행된 빈 리스트도 요청 대상이 되지만 ComfyUI가 이미 실행된 입력은 걸러 준다
        name = self.pick(index[0], values)
        return [name] if all(item is None for item in values[name]) else []

    def switch(self, index, **values):
        # 선택된 입력의 리스트 전체를 낸다. 일반 입력은 항목 1개짜리 리스트라 값 하나가 나간다
        # 출력 index는 순환한 뒤 실제로 고른 번호(연결된 입력 기준 0 ~ 개수-1)다. 슬롯 번호(value2의 2)가 아니다
        return values[self.pick(index[0], values)], index[0] % len(values)
