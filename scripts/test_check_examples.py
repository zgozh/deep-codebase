"""Tests for the bundled-example guard (check_examples.py)."""

import importlib.util
from pathlib import Path
import sys
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "deep-codebase-learning/scripts/check_examples.py"
sys.path.insert(0, str(SOURCE.parent))
spec = importlib.util.spec_from_file_location("check_examples", SOURCE)
check_examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_examples)


class BundledExamplesTest(unittest.TestCase):
    def test_every_bundled_example_conforms(self):
        for name, spec in check_examples.EXAMPLES.items():
            with self.subTest(example=name):
                problems, report = check_examples.check_example(name, spec)
                self.assertEqual(problems, [], report)

    def test_unit_example_keeps_a_measured_unit(self):
        _, report = check_examples.check_example(
            "references/unit-example.md", check_examples.EXAMPLES["references/unit-example.md"]
        )
        blocks = report["blocks"]
        self.assertIsNotNone(blocks)
        self.assertGreaterEqual(blocks["blocks"], 8)
        self.assertEqual(blocks["thin"], 0)

    def test_links_inside_the_skill_resolve(self):
        problems, checked = check_examples.check_links()
        self.assertEqual(problems, [])
        self.assertGreater(checked, 50)


class BlockSummaryTest(unittest.TestCase):
    def test_thin_share_counts_explanation_shortfall(self):
        result = {"blocks": [
            {"per_line": 64.8, "cjk_per_quote": 1.5},
            {"per_line": 32.2, "cjk_per_quote": 0.94},
            {"per_line": 51.0, "cjk_per_quote": 1.2},
            {"per_line": 70.0, "cjk_per_quote": 1.4},
        ]}
        summary = check_examples.block_summary(result)
        self.assertEqual(summary["blocks"], 4)
        self.assertEqual(summary["thin"], 1)
        self.assertEqual(summary["thin_share"], 0.25)
        self.assertEqual(summary["quote_below_g5"], 1)

    def test_missing_blocks_is_none(self):
        self.assertIsNone(check_examples.block_summary({"blocks": []}))


if __name__ == "__main__":
    unittest.main()
