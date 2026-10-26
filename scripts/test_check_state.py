"""Read-only state shape checks; no model, source or projection access."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "deep-codebase-learning/scripts/check_state.py"
spec = importlib.util.spec_from_file_location("check_state", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CheckStateTests(unittest.TestCase):
    def setUp(self):
        self.initial = json.loads((ROOT / "deep-codebase-learning/assets/templates/state.json").read_bytes())

    def test_minimal_init_allows_optional_omission_and_unknown_fields(self):
        self.initial["learner"].pop("teaching_default")
        self.initial["future_field"] = {"unknown": True}
        self.assertEqual(checker.check_state(self.initial), [])

    def test_full_state_accepts_unknown_revision_or_hash_without_reading_sources(self):
        state = copy.deepcopy(self.initial)
        refs = [{"path": "missing/source.go", "symbol": None, "revision": None, "evidence_kind": "code"},
                {"path": "other.py", "symbol": "main", "hash": None, "evidence_kind": "code"},
                {"path": "third.sql", "symbol": None, "revision": {"commit": "unknown"}, "hash": "unverified", "evidence_kind": "code", "extra": 1}]
        state["phase"] = "TEACH"
        state["current"] = {"stage": "S01", "topic": "T01", "source_refs": refs}
        state["journal"] = {"active_file": ".codelearn/journal/S01-001.md", "last_event": "E000001", "next_sequence": 2}
        state["awaiting"] = {"kind": "question", "prompt": "Explain", "topic": "T01",
                             "source_refs": refs, "issued_event": "E000001", "rubric_ref": None}
        self.assertEqual(checker.check_state(state), [])

    def test_string_refs_and_invalid_ref_fields_are_rejected(self):
        for refs, position in [(["private/source.go"], "$.current.source_refs[0]"),
                               ([{"path": "a.go", "symbol": None, "evidence_kind": "code"}], "$.current.source_refs[0].revision/hash"),
                               ([{"path": 7, "symbol": [], "hash": 3, "evidence_kind": False}], "$.current.source_refs[0].path")]:
            with self.subTest(position=position):
                state = copy.deepcopy(self.initial)
                state["current"]["source_refs"] = refs
                self.assertIn(position, checker.check_state(state))

    def test_missing_or_bad_core_fields_report_only_positions(self):
        cases = [("current", None, "$.current"), ("next_action", "continue", "$.next_action"),
                 ("journal", [], "$.journal"), ("schema_version", True, "$.schema_version")]
        for key, value, position in cases:
            with self.subTest(key=key):
                state = copy.deepcopy(self.initial)
                state[key] = value
                self.assertIn(position, checker.check_state(state))
        state = copy.deepcopy(self.initial)
        del state["next_action"]["completion_condition"]
        state["next_action"]["load"] = [7]
        state["journal"]["next_sequence"] = 0
        state["current"]["topic"] = []
        errors = checker.check_state(state)
        for position in ("$.next_action.completion_condition", "$.next_action.load[0]",
                         "$.journal.next_sequence", "$.current.topic"):
            self.assertIn(position, errors)
        self.assertTrue(all(position.startswith("$") for position in errors))

    def test_cli_does_not_change_state_or_print_private_values(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            self.initial["current"]["source_refs"] = ["SECRET_SOURCE_VALUE"]
            original = json.dumps(self.initial).encode("utf-8")
            path.write_bytes(original)
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True)
            self.assertEqual(process.returncode, 1)
            self.assertEqual(json.loads(process.stdout), {"valid": False, "errors": ["$.current.source_refs[0]"]})
            self.assertNotIn(b"SECRET_SOURCE_VALUE", process.stdout + process.stderr)
            self.assertEqual(path.read_bytes(), original)
            path.write_bytes(b"\xff")
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True)
            self.assertEqual(process.returncode, 1)
            self.assertEqual(json.loads(process.stdout), {"valid": False, "errors": ["$"]})
            self.assertEqual(path.read_bytes(), b"\xff")

    def test_cli_accepts_utf8_bom_without_rewriting_state(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            original = b"\xef\xbb\xbf" + json.dumps(self.initial).encode("utf-8")
            path.write_bytes(original)
            process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)], capture_output=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(json.loads(process.stdout), {"valid": True, "errors": []})
            self.assertEqual(path.read_bytes(), original)

    def test_cli_rejects_duplicate_keys_without_losing_first_value_or_rewriting(self):
        original = json.dumps(self.initial)
        replacement = dict(self.initial["next_action"], reason="SECRET_DUPLICATE")
        duplicate_action = original[:-1] + ', "next_action": ' + json.dumps(replacement) + '}'
        duplicate_nested = original.replace('"source_refs": []',
                                           '"source_refs": [], "source_refs": []', 1)
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            for text in (duplicate_action, duplicate_nested):
                with self.subTest(text_kind="top" if text == duplicate_action else "nested"):
                    raw = text.encode("utf-8")
                    path.write_bytes(raw)
                    process = subprocess.run([sys.executable, "-B", str(SCRIPT), str(path)],
                                             capture_output=True)
                    self.assertEqual(process.returncode, 1)
                    self.assertEqual(json.loads(process.stdout), {"valid": False, "errors": ["$"]})
                    self.assertNotIn(b"SECRET_DUPLICATE", process.stdout + process.stderr)
                    self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
