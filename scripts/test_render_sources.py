"""Raw source rendering checks using local temporary files only."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "deep-codebase-learning/scripts/render_sources.py"
spec = importlib.util.spec_from_file_location("render_sources", SCRIPT)
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)


class RenderSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        self.workspace = self.project / ".codelearn"
        self.workspace.mkdir()
        (self.project / "cmd").mkdir()
        self.source = self.project / "cmd/root file.go"
        self.source_raw = '// lead\r\n\tvalue := "中文" // 注释\r\n\r\n\ttext := `four ```` ticks`\r\n// EOF'.encode("utf-8")
        self.source.write_bytes(self.source_raw)
        self.input = self.workspace / "unit.md"
        self.output = self.workspace / "rendered.md"
        self.note = Path("notes/阶段/正式课.md")

    def directive(self, **changes):
        value = {"path": "cmd/root file.go", "first": 2, "last": 4,
                 "language": "go", "title": "登记输入"}
        value.update(changes)
        return ("<!-- codelearn-source " + json.dumps(value, ensure_ascii=False) + " -->").encode("utf-8")

    def run_render(self, **changes):
        args = dict(workspace=self.workspace, source_root=self.project,
                    input=Path("unit.md"), output=Path("rendered.md"), note=self.note)
        args.update(changes)
        return render.render_sources(**args)

    def test_exact_source_bytes_fence_post_code_title_link_and_hash(self):
        before = '# 教材 "引号"\r\n\r\n'.encode("utf-8")
        after = '\r\n保留解释 `原样`，无结尾换行'.encode("utf-8")
        original = before + self.directive() + b"\r\n" + after
        self.input.write_bytes(original)
        result = self.run_render()
        self.assertTrue(result["saved"])
        code = b'\tvalue := "' + '中文'.encode() + b'" // ' + '注释'.encode() + b'\r\n\r\n\ttext := `four ```` ticks`\r\n'
        heading = '##### 原行2–4：登记输入（[源码](../../../cmd/root%20file.go#L2-L4)）'.encode("utf-8")
        expected = before + b"`````go\r\n" + code + b"`````\r\n\r\n" + heading + b"\r\n" + after
        self.assertEqual(self.output.read_bytes(), expected)
        self.assertEqual(self.input.read_bytes(), original)
        self.assertEqual(self.source.read_bytes(), self.source_raw)
        self.assertEqual(result["include_count"], 1)
        self.assertEqual(result["source_refs"], [{"path": "cmd/root file.go", "symbol": None,
                         "revision": None, "hash": hashlib.sha256(self.source_raw).hexdigest(),
                         "evidence_kind": "code"}])

    def test_fenced_directives_are_literal_and_source_markers_are_not_recursive(self):
        literal = b'<!-- codelearn-source {"path":"missing"} -->'
        self.source.write_bytes(literal)
        original = b"````markdown\n```text\n" + literal + b"\n```\n````\n~~~html\n" + literal + b"\n~~~\n"
        self.input.write_bytes(original + self.directive(first=1, last=1) + b"\n")
        result = self.run_render()
        self.assertTrue(result["saved"])
        self.assertEqual(result["include_count"], 1)
        self.assertTrue(self.output.read_bytes().startswith(original))
        self.assertIn(b"```go\n" + literal + b"\n```\n", self.output.read_bytes())

    def test_same_file_includes_share_one_buffer(self):
        self.input.write_bytes(self.directive(first=1, last=1) + b"\n" + self.directive(first=5, last=5))
        read_bytes = Path.read_bytes
        reads = []
        def read(path):
            reads.append(path)
            return read_bytes(path)
        with patch.object(Path, "read_bytes", read):
            result = self.run_render()
        self.assertTrue(result["saved"])
        self.assertEqual(reads.count(self.source.resolve()), 1)
        self.assertEqual(result["include_count"], 2)
        self.assertEqual(len(result["source_refs"]), 1)
        self.assertIn(b"// EOF\n```", self.output.read_bytes())

    def test_invalid_directives_ranges_and_sources_do_not_publish(self):
        cases = [(self.directive(first=0), "directive.range"),
                 (self.directive(last=999), "directive.range"),
                 (self.directive(first=True), "directive.range"),
                 (self.directive(title="bad\ntitle"), "directive.title"),
                 (self.directive(language="go\n"), "directive.language"),
                 (self.directive(extra="unknown"), "directive.fields"),
                 (b"<!-- codelearn-source broken -->", "directive.json"),
                 (b"<!-- codelearn-source broken", "directive.syntax"),
                 (self.directive(path="missing.go"), "missing_path"),
                 (self.directive(path="../outside.go"), "source.path_outside_root")]
        for directive, error in cases:
            with self.subTest(error=error, directive=directive):
                original = self.directive(first=1, last=1) + b"\n" + directive
                self.input.write_bytes(original)
                result = self.run_render(output=Path("not-created/bad/rendered.md"))
                self.assertFalse(result["saved"])
                self.assertEqual(result["error"], error)
                self.assertEqual(result["line"], 2)
                self.assertFalse(self.output.exists())
                self.assertFalse((self.workspace / "not-created").exists())
                self.assertEqual(self.input.read_bytes(), original)

    def test_inline_mentions_and_four_space_code_remain_literal(self):
        original = (b"Normal prose mentions " + self.directive() + b"\r\n"
                    + b"Inline example: `<!-- codelearn-source {} -->`\n"
                    + b"    " + self.directive(path="missing.go") + b"\n")
        self.input.write_bytes(original)
        result = self.run_render()
        self.assertTrue(result["saved"])
        self.assertEqual(result["include_count"], 0)
        self.assertEqual(result["source_refs"], [])
        self.assertEqual(self.output.read_bytes(), original)
        self.assertEqual(self.input.read_bytes(), original)

    def test_utf8_failure_in_source_or_input_does_not_publish(self):
        self.input.write_bytes(self.directive(first=1, last=1))
        self.source.write_bytes(b"valid first line\n\xff")
        result = self.run_render()
        self.assertEqual(result["error"], "invalid_utf8")
        self.assertFalse(self.output.exists())
        self.input.write_bytes(b"\xff")
        result = self.run_render()
        self.assertEqual(result["error"], "invalid_utf8")
        self.assertFalse(self.output.exists())

    def test_workspace_escape_and_existing_target_are_rejected(self):
        self.input.write_bytes(self.directive())
        for field in ("input", "output", "note"):
            with self.subTest(field=field):
                result = self.run_render(**{field: Path("../outside.md")})
                self.assertEqual(result["error"], "path_outside_workspace")
                self.assertFalse(result["saved"])
        self.output.write_bytes(b"old note")
        result = self.run_render()
        self.assertEqual(result["error"], "target_exists")
        self.assertEqual(self.output.read_bytes(), b"old note")

    def test_symlink_source_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            link = self.project / "outside"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest("Host cannot create symlinks: " + type(error).__name__)
            self.input.write_bytes(self.directive(path="outside/secret.go"))
            result = self.run_render()
            self.assertEqual(result["error"], "source.path_outside_root")
            self.assertFalse(self.output.exists())

    def test_competing_target_is_preserved(self):
        self.input.write_bytes(self.directive())
        def competing_link(source, destination):
            destination.write_bytes(b"concurrent note")
            raise FileExistsError("target appeared")
        with patch.object(render.os, "link", side_effect=competing_link):
            result = self.run_render()
        self.assertFalse(result["saved"])
        self.assertEqual(result["error"], "target_exists")
        self.assertEqual(self.output.read_bytes(), b"concurrent note")
        self.assertFalse(list(self.workspace.glob(".render-sources-*")))

    def test_cli_outputs_metadata_without_prose(self):
        self.input.write_bytes(self.directive())
        output = Path("新目录/原文.rendered.md")
        process = subprocess.run([sys.executable, "-B", str(SCRIPT), "--workspace", str(self.workspace),
                                  "--source-root", str(self.project), "--input", "unit.md",
                                  "--output", str(output), "--note", str(self.note)], capture_output=True,
                                 env=dict(os.environ, PYTHONIOENCODING="ascii:strict"))
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertTrue(result["saved"])
        self.assertEqual(result["output"], str((self.workspace / output).resolve()))
        self.assertTrue((self.workspace / output).is_file())
        process.stdout.decode("ascii")
        self.assertNotIn('登记输入'.encode(), process.stdout)
        self.assertEqual(self.source.read_bytes(), self.source_raw)


if __name__ == "__main__":
    unittest.main()
