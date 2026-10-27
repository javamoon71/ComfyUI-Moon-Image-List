# AnyIndexSwitch 노드의 입력 선택, lazy 평가, 타입 선언을 검증하는 테스트
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.any_index_switch import ANY, AnyIndexSwitch


class TestAnyIndexSwitch(unittest.TestCase):
    def setUp(self):
        self.node = AnyIndexSwitch()

    def test_switch_by_index_wraps(self):
        self.assertEqual(self.node.switch(1, value0="a", value1=2), (2,))
        self.assertEqual(self.node.switch(3, value0="a", value1=2), (2,))

    def test_counts_connected_in_slot_order(self):
        # value1은 연결되지 않았고, value10은 value2 뒤에 온다
        values = {"value10": "c", "value0": "a", "value2": "b"}
        self.assertEqual([self.node.switch(i, **values)[0] for i in range(3)], ["a", "b", "c"])

    def test_no_inputs_raises(self):
        with self.assertRaises(ValueError):
            self.node.switch(0)
        with self.assertRaises(ValueError):
            self.node.check_lazy_status(0)

    def test_lazy_requests_only_selected(self):
        self.assertEqual(self.node.check_lazy_status(1, value0=None, value1=None), ["value1"])
        self.assertEqual(self.node.check_lazy_status(1, value0=None, value1="b"), [])

    def test_dynamic_inputs_are_lazy(self):
        optional = AnyIndexSwitch.INPUT_TYPES()["optional"]
        self.assertIn("value7", optional)
        self.assertNotIn("index", optional)
        self.assertEqual(optional["value7"], (ANY, {"lazy": True}))
        with self.assertRaises(KeyError):
            optional["index"]
        # 프론트엔드에 보내는 노드 정의에는 value0만 들어간다
        self.assertEqual(list(json.loads(json.dumps(optional))), ["value0"])

    def test_index_has_control_after_generate(self):
        # 문자열이면 프론트엔드가 그 값을 기본 모드로 쓴다. True면 randomize가 기본이 된다
        options = AnyIndexSwitch.INPUT_TYPES()["required"]["index"][1]
        self.assertEqual(options["control_after_generate"], "fixed")

    def test_any_type_matches_everything(self):
        self.assertFalse("IMAGE" != ANY)
        self.assertFalse(ANY != "MODEL")
        self.assertEqual(json.dumps(ANY), '"*"')


if __name__ == "__main__":
    unittest.main()
