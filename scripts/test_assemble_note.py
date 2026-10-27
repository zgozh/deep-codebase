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
                 '--final-note', 'notes/final.md'], capture_output=True)
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
                                  "--output", str(output)], capture_output=True,
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


if __name__ == "__main__":
    unittest.main()
