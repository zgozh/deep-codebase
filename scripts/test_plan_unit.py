"""Unit-budget arithmetic checks; no model, no network."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "deep-codebase-learning/scripts/plan_unit.py"
sys.path.insert(0, str(SOURCE.parent))
spec = importlib.util.spec_from_file_location("plan_unit", SOURCE)
plan_unit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plan_unit)


class MeaningfulLinesTest(unittest.TestCase):
    def write(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".java", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return handle.name

    def test_skips_blank_and_comment_only_lines(self):
        path = self.write("\n".join([
            "// license header",
            "public class A {",          # 1 kept
            "",                          # blank
            "    /**",                   # comment block
            "     * does things",        # comment block
            "     */",
            "    int x = 1;",            # 2 kept
            "}",
        ]))
        total, meaningful = plan_unit.meaningful_lines(path, 1, 8)
        self.assertEqual(total, 8)
        self.assertEqual(meaningful, 3)

    def test_range_is_relative_to_whole_file(self):
        path = self.write("a\nb\nc\nd\n")
        total, meaningful = plan_unit.meaningful_lines(path, 2, 3)
        self.assertEqual((total, meaningful), (2, 2))

    def test_out_of_bounds_range_raises(self):
        path = self.write("a\n")
        with self.assertRaises(ValueError):
            plan_unit.meaningful_lines(path, 1, 9)


class BudgetTest(unittest.TestCase):
    def test_floor_and_target_use_measured_numbers(self):
        result = plan_unit.plan(40)
        self.assertEqual(result["floor_cjk"], 40 * 50)
        self.assertEqual(result["target_cjk"], 40 * 65)
        self.assertEqual(result["unit_total_floor"], 40 * 50 + plan_unit.UNIT_OVERHEAD)

    def test_suggested_blocks_track_median_split(self):
        self.assertEqual(plan_unit.plan(12)["suggested_blocks"], 1)
        self.assertEqual(plan_unit.plan(48)["suggested_blocks"], 4)

    def test_block_table_spans_five_to_fifteen(self):
        table = plan_unit.plan(30)["per_block"]
        self.assertEqual([row["block_lines"] for row in table], list(range(5, 16)))
        self.assertEqual(table[0]["target_cjk"], 5 * 65)

    def test_empty_range_still_plans_one_unit(self):
        self.assertEqual(plan_unit.plan(0)["suggested_blocks"], 1)


if __name__ == "__main__":
    unittest.main()
