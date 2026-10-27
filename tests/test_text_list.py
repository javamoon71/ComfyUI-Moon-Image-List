# TextList 노드의 항목 선택 동작을 검증하는 테스트
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nodes.text_list import TextList


class TestTextList(unittest.TestCase):
    def setUp(self):
        self.node = TextList()

    def pick(self, *args, **kwargs):
        # 선택 결과(text, title)만 비교한다. 리스트 출력은 별도 테스트에서 본다
        title, body = self.node.select(*args, **kwargs)[:2]
        return body, title

    def test_select_by_index(self):
        text = "apple\nbanana\ncherry"
        self.assertEqual(self.pick(text, 0), ("apple", ""))
        self.assertEqual(self.pick(text, 2), ("cherry", ""))

    def test_index_wraps(self):
        self.assertEqual(self.pick("a\nb\nc", 3), ("a", ""))
        self.assertEqual(self.pick("a\nb\nc", 7), ("b", ""))

    def test_skips_blank_lines_and_strips(self):
        text = "  first  \n\n   \nsecond\r\n"
        self.assertEqual(self.pick(text, 1), ("second", ""))

    def test_empty_text(self):
        self.assertEqual(self.pick("", 5), ("", ""))
        self.assertEqual(self.pick("\n  \n", 0), ("", ""))

    def test_json_items_keep_newlines(self):
        text = json.dumps(["line1\nline2", "  ", " single \n"])
        self.assertEqual(self.pick(text, 0), ("line1\nline2", ""))
        self.assertEqual(self.pick(text, 1), ("single", ""))
        self.assertEqual(self.pick(text, 2), ("line1\nline2", ""))

    def test_titled_items_output_text_and_title(self):
        text = json.dumps([
            {"title": " Style ", "text": " line1\nline2 "},
            {"title": "제목만", "text": "  "},
            "plain",
            {"text": "no title key"},
        ])
        self.assertEqual(self.pick(text, 0), ("line1\nline2", "Style"))
        self.assertEqual(self.pick(text, 1), ("plain", ""))
        self.assertEqual(self.pick(text, 2), ("no title key", ""))

    def test_random_returns_matching_title(self):
        text = json.dumps([{"title": "A", "text": "a"}, {"title": "B", "text": "b"}])
        for _ in range(50):
            body, title = self.pick(text, 0, random=True)
            self.assertEqual(title, body.upper())

    def test_show_title_off_still_outputs_title(self):
        text = json.dumps([{"title": "Style", "text": "body"}])
        self.assertEqual(self.pick(text, 0, show_title=False), ("body", "Style"))
        self.assertEqual(TextList.IS_CHANGED(text, 0, show_title=False), TextList.IS_CHANGED(text, 0, show_title=True))

    def test_json_empty_list(self):
        self.assertEqual(self.pick("[]", 0), ("", ""))

    def test_random_picks_from_items(self):
        items = {"a", "b", "c"}
        picked = {self.pick("a\n\nb\nc", 0, random=True)[0] for _ in range(200)}
        self.assertEqual(picked, items)

    def test_random_empty_text(self):
        self.assertEqual(self.pick("", 0, random=True), ("", ""))

    def test_text_list_outputs_all_items(self):
        text = json.dumps([{"title": "A", "text": " a "}, {"title": "빈", "text": " "}, "b\nc"])
        self.assertEqual(self.node.select(text, 0)[3], ["a", "b\nc"])
        self.assertEqual(self.node.select(text, 1, random=True)[3], ["a", "b\nc"])
        self.assertEqual(self.node.select("", 0)[3], [])
        self.assertEqual(TextList.OUTPUT_IS_LIST, (False, False, True, True))

    def test_title_list_matches_text_list(self):
        text = json.dumps([{"title": " A ", "text": "a"}, {"title": "빈", "text": " "}, "b", {"text": "c"}])
        out = self.node.select(text, 0)
        self.assertEqual(out[3], ["a", "b", "c"])
        self.assertEqual(out[2], ["A", "", ""])
        self.assertEqual(self.node.select("", 0)[2], [])

    def test_search_aliases(self):
        self.assertEqual(TextList.SEARCH_ALIASES, ["moon", "text", "textlist", "text list"])

    def test_is_changed_only_when_random(self):
        changed = TextList.IS_CHANGED("a\nb", 0, random=True)
        self.assertNotEqual(changed, changed)
        self.assertEqual(TextList.IS_CHANGED("a\nb", 0, random=False), TextList.IS_CHANGED("a\nb", 0, random=False))


if __name__ == "__main__":
    unittest.main()
