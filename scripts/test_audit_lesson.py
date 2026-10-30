"""Audit-parser checks; no model or network calls."""

import importlib.util
from pathlib import Path
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "deep-codebase-learning/scripts/audit_lesson.py"
spec = importlib.util.spec_from_file_location("audit_lesson", SOURCE)
audit_module = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SOURCE.parent))
spec.loader.exec_module(audit_module)


def filler(size):
    text = "这一段说明当前问题、真实输入与结果，例如具体值，项目里这样用，代价是不能乱用。"
    while audit_module.cjk(text) < size:
        text += "它还把边界、失败与消费者讲清楚。"
    text += "这段代码跑在模型线程上，框架在启动时创建对象，序列化结果交给下游。"
    return text


def unit(name, pre_overrides=None, explain_size=420):
    pre_overrides = pre_overrides or {}
    sections = []
    for title, key in [("#### 实际问题与实现思路", "problem"),
                       ("#### 架构位置、真实触发与输入准备", "context"),
                       ("#### 源码定位与阅读准备", "locate")]:
        sections.append(title + "\n\n" + filler(pre_overrides.get(key, 240)) + "\n")
    code = "```ts\n" + "\n".join("const value%d = %d;" % (i, i) for i in range(6)) + "\n```\n"
    explain = filler(explain_size)
    half = explain[: len(explain) // 2]
    body = ("### " + name + "\n\n"
            + sections[0] + sections[1] + sections[2]
            + "#### 4–5 连续源码与紧邻逐行推导\n\n" + code + "\n"
            + half + "\n\n" + explain[len(explain) // 2:] + "\n"
            + "#### 这一段怎样运行：边界与失败\n\n" + filler(260) + "\n"
            + "#### 运行机制与工程判断\n\n" + filler(260) + "\n"
            + "#### 怎么用、上下游、接入与修改影响\n\n" + filler(260) + "\n")
    return body


def concept(name):
    return ("### " + name + "\n\n" + filler(320) + "\n")


def note(**options):
    chapters = ["# 课\n"]
    for number in range(1, 11):
        chapters.append("## %d. 章%d\n\n%s\n" % (number, number, filler(60)))
        if number == 3:
            chapters.append(concept("3.1 示例概念") + concept("3.2 另一个概念"))
        if number == 5:
            chapters.append(unit("5.1 示例单元", **options))
    return "\n".join(chapters)


class AuditLessonTests(unittest.TestCase):
    def run_audit(self, text):
        path = Path(self.temp.name) / "note.md"
        path.write_text(text, encoding="utf-8")
        return audit_module.audit(path)

    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_complete_note_passes(self):
        result = self.run_audit(note())
        self.assertTrue(result["passed"], result["problems"])

    def test_missing_position_is_reported(self):
        text = note().replace("#### 源码定位与阅读准备", "#### 其他小节")
        result = self.run_audit(text)
        self.assertIn("position", {p["check"] for p in result["problems"]})

    def test_short_pre_section_is_reported(self):
        result = self.run_audit(note(pre_overrides={"context": 40}))
        self.assertIn("pre_depth", {p["check"] for p in result["problems"]})

    def test_thin_block_explanation_is_reported(self):
        result = self.run_audit(note(explain_size=60))
        self.assertIn("explain", {p["check"] for p in result["problems"]})

    def test_concept_without_example_is_reported(self):
        text = note().replace("例如", "相关")
        result = self.run_audit(text)
        self.assertIn("concept_example", {p["check"] for p in result["problems"]})

    def test_warnings_do_not_fail_the_note(self):
        result = self.run_audit(note(pre_overrides={"problem": 180}))
        self.assertTrue(result["passed"], result["problems"])
        self.assertTrue(result["warnings"])

    def test_wide_sequence_label_is_a_warning(self):
        diagram = ("## 2. 章2\n\n```mermaid\nsequenceDiagram\n"
                   "    participant A as 用户\n    participant B as 服务端\n"
                   "    A->>B: currentSessionId = 新 ID，sessions 插入该会话\n```\n")
        text = note().replace("## 2. 章2\n\n", "")
        text = text.replace("## 3. 章3", diagram + "\n## 3. 章3")
        result = self.run_audit(text)
        self.assertTrue(result["passed"], result["problems"])
        self.assertIn("diagram", {w["check"] for w in result["warnings"]})
        self.assertEqual(1, result["diagrams"][0]["widest"] >= 44)

    def test_short_labels_and_low_participant_count_are_silent(self):
        diagram = ("## 2. 章2\n\n```mermaid\nsequenceDiagram\n"
                   "    participant A as 用户\n    participant B as 服务端\n"
                   "    A->>B: 提交问题\n    B-->>A: 返回结果\n```\n")
        text = note().replace("## 2. 章2\n\n", "")
        text = text.replace("## 3. 章3", diagram + "\n## 3. 章3")
        result = self.run_audit(text)
        self.assertEqual([], result["diagrams"])
        self.assertNotIn("diagram", {w["check"] for w in result["warnings"]})

    def test_unit_without_underlying_layer_warns(self):
        text = note().replace("线程", "").replace("底层", "").replace("协议", "").replace("序列化", "")
        result = self.run_audit(text)
        self.assertIn("layer_gap", {w["check"] for w in result["warnings"]})

    def test_chapter_depth_warns_without_failing(self):
        result = self.run_audit(note())
        self.assertTrue(result["passed"], result["problems"])
        self.assertIn("chapter_depth", {w["check"] for w in result["warnings"]})

    def test_self_message_label_is_flagged(self):
        diagram = ("## 2. 章2\n\n```mermaid\nsequenceDiagram\n"
                   "    participant A as 用户\n    participant B as 服务端\n"
                   "    A->>A: 乐观插入\n    A->>B: 提交\n```\n")
        text = note().replace("## 2. 章2\n\n", "")
        text = text.replace("## 3. 章3", diagram + "\n## 3. 章3")
        result = self.run_audit(text)
        self.assertTrue(result["passed"], result["problems"])
        self.assertIn("self-message",
                      str([d["warnings"] for d in result["diagrams"]]))

    def test_crowded_participants_are_a_warning(self):
        lines = ["## 2. 章2\n", "```mermaid", "sequenceDiagram"]
        lines += ["    participant P%d as 参与方%d" % (i, i) for i in range(9)]
        lines += ["    P0->>P1: 调用", "```"]
        text = note().replace("## 2. 章2\n\n", "")
        text = text.replace("## 3. 章3", "\n".join(lines) + "\n## 3. 章3")
        result = self.run_audit(text)
        self.assertIn("participants crowd", " ".join(
            d for item in result["diagrams"] for d in item["warnings"]))


    def test_thin_per_line_explanation_warns(self):
        result = self.run_audit(note(explain_size=180))
        self.assertTrue(result["passed"], result["problems"])
        checks = {w["check"] for w in result["warnings"]}
        self.assertIn("density", checks)

    def test_default_note_has_no_density_warning(self):
        result = self.run_audit(note())
        checks = {w["check"] for w in result["warnings"]}
        self.assertNotIn("density", checks)
        self.assertNotIn("knowledge_gap", checks)


if __name__ == "__main__":
    unittest.main()
