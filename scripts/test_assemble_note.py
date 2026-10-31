"""Local byte transport checks; no CLI author or model calls."""

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch


SOURCE = Path(__file__).resolve().parents[1] / "deep-codebase-learning/scripts/assemble_note.py"
spec = importlib.util.spec_from_file_location("assemble_note", SOURCE)
assemble = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SOURCE.parent))
spec.loader.exec_module(assemble)


class AssembleNoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.first = '# 中文 "双引号"与\'单引号\'\r\n\r\n```js\r\n  const a = `值 ${x}`;\r\n```\r\n\r\n'.encode("utf-8")
        self.second = '## 后一章\n\n```python\n    print("你好")\n```\n'.encode("utf-8")
        (self.root / "first.md").write_bytes(self.first)
        (self.root / "second.md").write_bytes(self.second)
        (self.root / "old.md").write_bytes(b"existing formal note")

    def run_assemble(self, parts=None, output=Path("candidate.md")):
        if parts is None:
            parts = [Path("first.md"), Path("second.md")]
        return assemble.assemble_note(self.root, parts, output)

    def assert_sources_unchanged(self):
        self.assertEqual((self.root / "first.md").read_bytes(), self.first)
        self.assertEqual((self.root / "second.md").read_bytes(), self.second)
        self.assertEqual((self.root / "old.md").read_bytes(), b"existing formal note")

    def test_caller_order_duplicate_parts_and_all_bytes_preserved(self):
        result = self.run_assemble([Path("second.md"), Path("first.md"), Path("second.md")])
        expected = self.second + b"\n\n" + self.first + b"\n\n" + self.second
        self.assertTrue(result["saved"])
        self.assertEqual(result["bytes"], len(expected))
        self.assertEqual(result["parts"], 3)
        self.assertEqual((self.root / "candidate.md").read_bytes(), expected)
        self.assertFalse(list(self.root.glob(".assemble-note-*")))
        self.assert_sources_unchanged()

    def test_existing_candidate_is_not_changed(self):
        (self.root / "candidate.md").write_bytes(b"another candidate")
        with patch.object(assemble.os, "link") as link:
            result = self.run_assemble()
            link.assert_not_called()
        self.assertEqual(result["error"], "target_exists")
        self.assertFalse(result["saved"])
        self.assertEqual((self.root / "candidate.md").read_bytes(), b"another candidate")
        self.assert_sources_unchanged()

    def test_raw_parts_render_latest_prose_share_source_buffer_and_publish_raw(self):
        source = self.root / '源码.go'
        source_raw = '\tvalue := "中文" // 注释\r\ntext := `four ```` ticks`\r\n'.encode()
        source.write_bytes(source_raw)
        directive = ('<!-- codelearn-source ' + json.dumps({"path": source.name,
                     "first": 1, "last": 2, "language": "go", "title": "实际输入"}) + ' -->\r\n').encode()
        first = self.root / 'first.md'
        first.write_bytes('## 新正文\r\n'.encode() + directive)
        (self.root / 'second.md').write_bytes(directive + '保留 `值`。'.encode())
        # An obsolete preview must never be an implicit assembly input.
        (self.root / 'first.rendered.md').write_bytes(b'obsolete preview')
        reads = []
        read_bytes = Path.read_bytes
        def read(path):
            reads.append(path)
            return read_bytes(path)
        with patch.object(Path, 'read_bytes', read):
            result = assemble.assemble_note(self.root, [Path('first.md'), Path('second.md')],
                         Path('candidates/new.md'), source_root=self.root,
                         final_note=Path('notes/stage/final.md'))
        self.assertTrue(result['saved'], result)
        body = (self.root / 'candidates/new.md').read_bytes()
        self.assertTrue(body.startswith('## 新正文\r\n'.encode()))
        self.assertEqual(body.count(source_raw), 2)
        self.assertIn(b'`````go\r\n', body)
        self.assertIn(b'../../%E6%BA%90%E7%A0%81.go#L1-L2', body)
        self.assertNotIn(b'codelearn-source', body)
        self.assertNotIn(b'obsolete preview', body)
        self.assertEqual(reads.count(source.resolve()), 1)
        self.assertEqual(result['include_count'], 2)
        self.assertEqual(len(result['source_refs']), 1)
        self.assertEqual(result['source_refs'][0]['hash'], hashlib.sha256(source_raw).hexdigest())
        # Publishing the reviewed candidate uses the unchanged three-argument raw API.
        source.unlink()
        published = assemble.assemble_note(self.root, [Path('candidates/new.md')], Path('formal.md'))
        self.assertTrue(published['saved'])
        self.assertEqual((self.root / 'formal.md').read_bytes(), body)

    def test_source_mode_cli_pair_scope_errors_and_no_partial_output(self):
        (self.root / 'bad.md').write_bytes(b'<!-- codelearn-source broken -->')
        for options, error in [({'source_root': self.root}, 'source_root_and_final_note_required'),
                               ({'final_note': Path('final.md')}, 'source_root_and_final_note_required'),
                               ({'source_root': self.root, 'final_note': Path('../escape.md')}, 'path_outside_workspace'),
                               ({'source_root': self.root, 'final_note': Path('final.md')}, 'directive.json')]:
            result = assemble.assemble_note(self.root, [Path('first.md'), Path('bad.md')],
                                           Path('absent/candidate.md'), **options)
            self.assertFalse(result['saved'])
            self.assertEqual(result['error'], error)
            self.assertFalse((self.root / 'absent').exists())
            self.assert_sources_unchanged()
        (self.root / 'source.txt').write_bytes(b'actual source\n')
        (self.root / 'cli.md').write_bytes(b'<!-- codelearn-source {"path":"source.txt","first":1,"last":1,"language":"text","title":"actual"} -->\n')
        process = subprocess.run([sys.executable, '-B', str(SOURCE), '--workspace', str(self.root),
                 '--part', 'cli.md', '--output', 'candidate.md', '--source-root', str(self.root),
                 '--final-note', 'notes/final.md', '--no-content-gate'], capture_output=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)['include_count'], 1)
        self.assertIn(b'actual source\n', (self.root / 'candidate.md').read_bytes())

    def test_source_mode_rejects_zero_expansion_before_creating_output_parent(self):
        raw = ('# 中文\\n\\n<!-- codelearn-source {"path":"missing.go",'
               '"first":1,"last":2,"language":"go","title":"原行"} -->\\n').encode('utf-8')
        source = self.root / 'literal-newlines.md'
        source.write_bytes(raw)
        self.assertNotIn(b'\n', raw)
        self.assertIn(b'\\n', raw)
        with patch.object(assemble.tempfile, 'NamedTemporaryFile') as create:
            result = assemble.assemble_note(self.root, [Path('first.md'), source],
                        Path('not-created/candidate.md'), source_root=self.root,
                        final_note=Path('notes/final.md'))
            create.assert_not_called()
        self.assertEqual(result['error'], 'no_source_includes')
        self.assertEqual(result['include_count'], 0)
        self.assertFalse(result['saved'])
        self.assertFalse((self.root / 'not-created').exists())
        self.assertEqual(source.read_bytes(), raw)
        self.assert_sources_unchanged()
        # Raw publication remains byte transport, with no implicit rendering or repair.
        copied = assemble.assemble_note(self.root, [source], Path('raw-copy.md'))
        self.assertTrue(copied['saved'])
        self.assertEqual((self.root / 'raw-copy.md').read_bytes(), raw)

    def test_single_part_publication_preserves_all_bytes(self):
        result = self.run_assemble([Path("first.md")], Path("formal.md"))
        self.assertTrue(result["saved"])
        self.assertEqual((self.root / "formal.md").read_bytes(), self.first)
        self.assertEqual(result["bytes"], len(self.first))
        self.assert_sources_unchanged()

    def test_cli_accepts_grouped_and_repeated_parts_in_order(self):
        output = Path("新目录/原文.md")
        process = subprocess.run([sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                                  "--part", "second.md", "first.md", "--part", "second.md",
                                  "--output", str(output), "--no-content-gate"], capture_output=True,
                                 env=dict(os.environ, PYTHONIOENCODING="ascii:strict"))
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertTrue(result["saved"])
        self.assertEqual(result["output"], str((self.root / output).resolve()))
        process.stdout.decode("ascii")
        self.assertEqual((self.root / output).read_bytes(),
                         self.second + b"\n\n" + self.first + b"\n\n" + self.second)
        self.assert_sources_unchanged()

    def test_invalid_empty_and_missing_parts_are_rejected(self):
        for body, error in [(b"\xff", "invalid_utf8"), (b"", "empty_part"),
                            (b" \n\t", "empty_part"), (None, "missing_path")]:
            with self.subTest(error=error, body=body):
                bad = self.root / "bad.md"
                if body is None:
                    bad.unlink(missing_ok=True)
                else:
                    bad.write_bytes(body)
                result = self.run_assemble([Path("first.md"), Path("bad.md")], Path("not-created/bad/candidate.md"))
                self.assertEqual(result["error"], error)
                self.assertFalse(result["saved"])
                self.assertFalse((self.root / "candidate.md").exists())
                self.assertFalse((self.root / "not-created").exists())
                self.assert_sources_unchanged()
                if body is not None:
                    self.assertEqual(bad.read_bytes(), body)
        self.assertEqual(self.run_assemble([])["error"], "missing_parts")

    def test_path_escapes_are_rejected_before_reading_or_writing(self):
        outside = self.root.parent / "outside.md"
        for parts, output in [([outside], Path("candidate.md")),
                              ([Path("../outside.md")], Path("candidate.md")),
                              ([Path("first.md")], outside),
                              ([Path("first.md")], Path("../outside.md"))]:
            with self.subTest(parts=parts, output=output):
                with patch.object(assemble.tempfile, "NamedTemporaryFile") as create:
                    result = self.run_assemble(parts, output)
                    create.assert_not_called()
                self.assertEqual(result["error"], "path_outside_workspace")
                self.assertFalse(result["saved"])
                self.assert_sources_unchanged()

    def test_failed_write_does_not_publish_partial_candidate(self):
        create = assemble.tempfile.NamedTemporaryFile
        def failing_file(**kwargs):
            candidate = create(**kwargs)
            candidate.write = Mock(side_effect=OSError("simulated write failure"))
            return candidate
        with patch.object(assemble.tempfile, "NamedTemporaryFile", side_effect=failing_file):
            result = self.run_assemble()
        self.assertEqual(result["error"], "io_error")
        self.assertFalse(result["saved"])
        self.assertFalse((self.root / "candidate.md").exists())
        self.assertFalse(list(self.root.glob(".assemble-note-*")))
        self.assert_sources_unchanged()

    def test_commit_failure_does_not_publish_candidate(self):
        with patch.object(assemble.os, "link", side_effect=OSError("unsupported filesystem")):
            result = self.run_assemble()
        self.assertEqual(result["error"], "io_error")
        self.assertFalse(result["saved"])
        self.assertFalse((self.root / "candidate.md").exists())
        self.assertFalse(list(self.root.glob(".assemble-note-*")))
        self.assert_sources_unchanged()

    def test_competing_candidate_is_not_overwritten(self):
        def competing_link(source, destination):
            destination.write_bytes(b"concurrent candidate")
            raise FileExistsError("target appeared")
        with patch.object(assemble.os, "link", side_effect=competing_link):
            result = self.run_assemble()
        self.assertEqual(result["error"], "target_exists")
        self.assertFalse(result["saved"])
        self.assertEqual((self.root / "candidate.md").read_bytes(), b"concurrent candidate")
        self.assertFalse(list(self.root.glob(".assemble-note-*")))
        self.assert_sources_unchanged()

    def test_min_lines_rejects_short_result_without_output_side_effects(self):
        raw = b"# title\nbody\n"
        (self.root / "short.md").write_bytes(raw)
        with patch.object(assemble.tempfile, "NamedTemporaryFile") as create:
            result = assemble.assemble_note(self.root, [Path("short.md")],
                        Path("absent/deep/candidate.md"), min_lines=3)
            create.assert_not_called()
        self.assertFalse(result["saved"])
        self.assertEqual(result["error"], "below_min_lines")
        self.assertEqual((result["lines"], result["min_lines"], result["bytes"]), (2, 3, 0))
        self.assertFalse((self.root / "absent").exists())
        self.assertFalse(list(self.root.rglob(".assemble-note-*")))
        self.assertEqual((self.root / "short.md").read_bytes(), raw)
        existing = assemble.assemble_note(self.root, [Path("short.md")],
                                         Path("old.md"), min_lines=3)
        self.assertEqual(existing["error"], "target_exists")
        self.assert_sources_unchanged()

    def test_min_lines_exact_boundary_preserves_line_endings_and_final_line(self):
        for index, raw in enumerate([b"a\nb\n", b"a\r\nb\r\n", b"a\nb", b"a\r\nb"]):
            with self.subTest(raw=raw):
                (self.root / "boundary.md").write_bytes(raw)
                output = Path(f"boundary-{index}.md")
                result = assemble.assemble_note(self.root, [Path("boundary.md")],
                                               output, min_lines=2)
                self.assertTrue(result["saved"], result)
                self.assertEqual((result["lines"], result["min_lines"]), (2, 2))
                self.assertEqual((self.root / output).read_bytes(), raw)

    def test_min_lines_counts_joined_parts_after_source_rendering(self):
        source = b"one\ntwo\nthree\n"
        directive = b'<!-- codelearn-source {"path":"source.txt","first":1,"last":3,"language":"text","title":"source"} -->\n'
        (self.root / "source.txt").write_bytes(source)
        (self.root / "include.md").write_bytes(directive)
        options = {"source_root": self.root, "final_note": Path("notes/final.md")}
        minimum = len((directive + b"\n\n" + self.second).splitlines()) + 1
        result = assemble.assemble_note(self.root, [Path("include.md"), Path("second.md")],
                                       Path("rendered.md"), min_lines=minimum, **options)
        self.assertTrue(result["saved"], result)
        rendered = (self.root / "rendered.md").read_bytes()
        actual_lines = len(rendered.splitlines())
        self.assertGreater(actual_lines, 3)
        self.assertEqual(result["lines"], actual_lines)
        rejected = assemble.assemble_note(self.root, [Path("include.md"), Path("second.md")],
                       Path("not-created/short.md"), min_lines=actual_lines + 1, **options)
        self.assertEqual(rejected["error"], "below_min_lines")
        self.assertEqual(rejected["lines"], actual_lines)
        self.assertFalse((self.root / "not-created").exists())
        published = assemble.assemble_note(self.root, [Path("rendered.md")],
                                          Path("formal.md"), min_lines=actual_lines)
        self.assertTrue(published["saved"], published)
        self.assertEqual((self.root / "formal.md").read_bytes(), rendered)
        self.assertEqual((self.root / "include.md").read_bytes(), directive)
        self.assertEqual((self.root / "source.txt").read_bytes(), source)

    def test_min_lines_is_explicit_and_requires_positive_integer(self):
        legacy = self.run_assemble(output=Path("legacy.md"))
        self.assertEqual(set(legacy), {"saved", "output", "bytes", "parts"})
        for threshold in [0, -1, 1.5, True, "2"]:
            with self.subTest(threshold=threshold):
                result = assemble.assemble_note(self.root, [Path("first.md")],
                                   Path("invalid/output.md"), min_lines=threshold)
                self.assertEqual(result["error"], "invalid_min_lines")
                self.assertFalse(result["saved"])
                self.assertFalse((self.root / "invalid").exists())

    def test_min_lines_cli_reports_failure_then_accepts_exact_boundary(self):
        (self.root / "short.md").write_bytes(b"a\nb")
        command = [sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                   "--part", "short.md", "--output", "cli/candidate.md", "--no-content-gate",
                   "--min-lines"]
        rejected = subprocess.run(command + ["3"], capture_output=True)
        self.assertEqual(rejected.returncode, 1, rejected.stderr)
        result = json.loads(rejected.stdout)
        self.assertEqual((result["error"], result["lines"], result["min_lines"]),
                         ("below_min_lines", 2, 3))
        self.assertFalse((self.root / "cli").exists())
        accepted = subprocess.run(command + ["2"], capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertTrue(json.loads(accepted.stdout)["saved"])
        self.assertEqual((self.root / "cli/candidate.md").read_bytes(), b"a\nb")


class ContentGateTests(unittest.TestCase):
    """The gate must measure teaching prose, never physical lines."""

    PROSE = "这段解释先读语句，再说明参数从哪里来、值怎样变化、结果交给谁消费、失败时停在哪里。"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def note(self, blocks):
        parts = ["# 课\n"]
        for index, (code, prose) in enumerate(blocks):
            parts.append("```java\n" + code + "\n```\n")
            parts.append("##### 原行%d–%d：当前动作\n" % (index * 10 + 1, index * 10 + len(code.splitlines())))
            parts.append(prose + "\n")
        return "\n".join(parts).encode("utf-8")

    def code(self, lines):
        return "\n".join("int value%d = %d;" % (i, i) for i in range(lines))

    def test_long_code_block_with_short_summary_is_rejected(self):
        (self.root / "thin.md").write_bytes(self.note([(self.code(30), "这里只是概述。")]))
        with patch.object(assemble.tempfile, "NamedTemporaryFile") as create:
            result = assemble.assemble_note(self.root, [Path("thin.md")],
                                            Path("candidate.md"), content_gate=True)
            create.assert_not_called()
        self.assertEqual(result["error"], "below_content_gate")
        self.assertIn("thin_source_blocks", result["gates"])
        self.assertEqual(result["thin_blocks"][0]["code_lines"], 30)
        self.assertGreaterEqual(result["thin_blocks"][0]["need"], 200)
        self.assertFalse((self.root / "candidate.md").exists())

    def test_dense_long_block_passes_when_thresholds_are_met(self):
        prose = self.PROSE * 45
        (self.root / "dense.md").write_bytes(self.note([(self.code(30), prose)]))
        result = assemble.assemble_note(self.root, [Path("dense.md")], Path("candidate.md"),
                                        content_gate=True, min_prose_cjk=100, min_density=1)
        self.assertTrue(result["saved"], result)
        self.assertEqual(result["thin_blocks"], [])
        self.assertGreater(result["prose_cjk"], 100)
        self.assertEqual(result["code_lines"], 30)

    def test_chapter5_block_below_fifty_per_line_is_rejected(self):
        text = ("# 课\n\n### 5.1 示例单元\n\n```java\n" + self.code(10)
                + "\n```\n\n" + "这段只讲值。\n")
        (self.root / "thin5.md").write_bytes(text.encode("utf-8"))
        result = assemble.assemble_note(self.root, [Path("thin5.md")], Path("candidate.md"),
                                        content_gate=True, min_prose_cjk=1, min_density=1)
        self.assertEqual(result["error"], "below_content_gate")
        self.assertIn("below_block_density", result["gates"])
        self.assertEqual(result["low_density_blocks"][0]["need"], 500)

    def test_quote_dominant_block_is_rejected(self):
        prose = ("`" + "aaaaaaaaaa" * 10 + "` ") * 10 + "解释" * 250
        text = ("# 课\n\n### 5.1 示例单元\n\n```java\n" + self.code(10)
                + "\n```\n\n" + prose + "\n")
        (self.root / "quoted.md").write_bytes(text.encode("utf-8"))
        result = assemble.assemble_note(self.root, [Path("quoted.md")], Path("candidate.md"),
                                        content_gate=True, min_prose_cjk=1, min_density=1)
        self.assertEqual(result["error"], "below_content_gate")
        self.assertIn("below_quote_ratio", result["gates"])
        self.assertLess(result["low_quote_blocks"][0]["cjk_per_quote"], 1.2)

    def test_non_chapter5_block_is_exempt_from_the_block_floor(self):
        text = ("# 课\n\n### 3.1 示例概念\n\n```java\n" + self.code(10)
                + "\n```\n\n" + "这段只讲值。\n")
        (self.root / "ch3.md").write_bytes(text.encode("utf-8"))
        result = assemble.assemble_note(self.root, [Path("ch3.md")], Path("candidate.md"),
                                        content_gate=True, min_prose_cjk=1, min_density=1)
        self.assertNotIn("below_block_density", result.get("gates", []))

    def test_many_code_lines_without_prose_fail_density(self):
        blocks = [("int value%d;" % i, "值。") for i in range(200)]
        (self.root / "density.md").write_bytes(self.note(blocks))
        result = assemble.assemble_note(self.root, [Path("density.md")], Path("candidate.md"),
                                        content_gate=True, min_prose_cjk=100, min_density=30)
        self.assertEqual(result["error"], "below_content_gate")
        self.assertIn("below_min_density", result["gates"])
        self.assertLess(result["density"], 30)

    def test_prose_metrics_exclude_code_and_headings(self):
        content = ("# 标题中文\n\n```java\n// 中文注释\nString a = \"中文\";\n```\n\n"
                   "##### 原行1–2：中文标题\n\n正文解释。\n").encode("utf-8")
        metrics = assemble.prose_metrics(content)
        self.assertEqual(metrics["prose_cjk"], 4)
        self.assertEqual(metrics["code_lines"], 2)
        self.assertEqual(metrics["code_blocks"], 1)

    def test_check_mode_reports_without_writing(self):
        (self.root / "dense.md").write_bytes(self.note([(self.code(30), self.PROSE * 45)]))
        (self.root / "thin.md").write_bytes(self.note([(self.code(30), "概述。")]))
        command = [sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                   "--check", "--min-prose-cjk", "100", "--min-density", "1"]
        accepted = subprocess.run(command + ["--part", "dense.md"], capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        payload = json.loads(accepted.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["checked"])
        self.assertFalse((self.root / "check-only").exists())
        rejected = subprocess.run(command + ["--part", "thin.md"], capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        failed = json.loads(rejected.stdout)
        self.assertFalse(failed["ok"])
        self.assertIn("thin_source_blocks", failed["gates"])

    def test_check_mode_allows_parts_without_includes(self):
        (self.root / "intro.md").write_bytes(self.note([(self.code(30), self.PROSE * 45)]))
        process = subprocess.run(
            [sys.executable, "-B", str(SOURCE), "--workspace", str(self.root), "--check",
             "--part", "intro.md", "--source-root", str(self.root),
             "--final-note", "notes/final.md", "--min-density", "1"], capture_output=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue(json.loads(process.stdout)["ok"])

    def test_gate_runs_after_source_rendering(self):
        source = "\n".join("line %d" % i for i in range(30)).encode("utf-8")
        (self.root / "source.txt").write_bytes(source)
        directive = ('<!-- codelearn-source {"path":"source.txt","first":1,"last":30,'
                     '"language":"text","title":"实际实现"} -->\n').encode("utf-8")
        (self.root / "thin.md").write_bytes(directive + "##### 原行1–30：实现\n\n概述。\n".encode("utf-8"))
        options = {"source_root": self.root, "final_note": Path("notes/final.md")}
        thin = assemble.assemble_note(self.root, [Path("thin.md")], Path("thin-out.md"),
                                      content_gate=True, min_prose_cjk=100, min_density=1, **options)
        self.assertEqual(thin["error"], "below_content_gate")
        self.assertEqual(thin["include_count"], 1)
        (self.root / "full.md").write_bytes(directive + ("##### 原行1–30：实现\n\n"
                                         + self.PROSE * 45 + "\n").encode("utf-8"))
        full = assemble.assemble_note(self.root, [Path("full.md")], Path("full-out.md"),
                                      content_gate=True, min_prose_cjk=100, min_density=1, **options)
        self.assertTrue(full["saved"], full)
        self.assertEqual(full["code_lines"], 30)

    def test_no_prose_floor_keeps_block_gates(self):
        (self.root / "local.md").write_bytes(self.note([(self.code(30), self.PROSE * 45)]))
        command = [sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                   "--part", "local.md", "--output", "local-out.md"]
        rejected = subprocess.run(command, capture_output=True)
        self.assertEqual(rejected.returncode, 1)
        self.assertIn("below_min_prose", json.loads(rejected.stdout)["gates"])
        accepted = subprocess.run(command + ["--no-prose-floor"], capture_output=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertTrue(json.loads(accepted.stdout)["saved"])

    def test_check_mode_skips_the_whole_lesson_prose_floor(self):
        (self.root / "unit.md").write_bytes(self.note([(self.code(30), self.PROSE * 45)]))
        process = subprocess.run([sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                                  "--check", "--part", "unit.md"], capture_output=True)
        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["ok"])
        self.assertIsNone(payload["min_prose_cjk"])
        self.assertGreaterEqual(payload["density"], 30)

    def test_cli_enforces_the_gate_by_default(self):
        (self.root / "tiny.md").write_bytes(b"# t\n\nbody\n")
        process = subprocess.run([sys.executable, "-B", str(SOURCE), "--workspace", str(self.root),
                                  "--part", "tiny.md", "--output", "tiny-out.md"], capture_output=True)
        self.assertEqual(process.returncode, 1)
        self.assertEqual(json.loads(process.stdout)["error"], "below_content_gate")
        self.assertFalse((self.root / "tiny-out.md").exists())


class SourceOverlapTests(unittest.TestCase):
    """Units are separate parts, so a split can quote the same lines twice unnoticed."""

    def test_reports_overlap_between_two_parts(self):
        found = assemble.source_overlaps([
            ("05-08.md", [("a.java", 99, 109)]),
            ("05-09.md", [("a.java", 108, 120)]),
        ])
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["overlap"], [108, 109])
        self.assertEqual(found[0]["first_part"][0], "05-08.md")

    def test_ignores_disjoint_ranges_and_other_files(self):
        self.assertEqual(assemble.source_overlaps([
            ("p1", [("a.java", 1, 10)]),
            ("p2", [("a.java", 11, 20), ("b.java", 1, 10)]),
        ]), [])

    def test_marker_parsing_skips_broken_json(self):
        body = ('<!-- codelearn-source {"path":"a.java","first":3,"last":9} -->\n'
                '<!-- codelearn-source {not json} -->\n').encode("utf-8")
        self.assertEqual(assemble.include_spans(body), [("a.java", 3, 9)])


if __name__ == "__main__":
    unittest.main()
