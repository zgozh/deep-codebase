"""Calibrate the prose gate against real historical notes.

The gate is only useful if it separates the accepted old note from the rejected
natural output. This test replays the four notes used in the v1.11.31 natural
acceptance and asserts the expected pass/fail split. It skips a note that is not
present instead of failing in a checkout without the archived evidence.
"""

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "deep-codebase-learning/scripts/assemble_note.py"
spec = importlib.util.spec_from_file_location("assemble_note", SOURCE)
assemble = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SOURCE.parent))
spec.loader.exec_module(assemble)

CASES = {
    "old_effective_baseline": {
        "path": "reports/release-p0-v11131-r4/baseline/S00-T03-欢迎页输入到会话地址.md",
        "prose_cjk": 33534, "density": 43.4, "thin_blocks": 0, "verdict": "pass",
    },
    "natural_failed_ragent": {
        "path": "reports/natural-acceptance-v31-20261028/case-A-ragent/frozen-A-codelearn/"
                "notes/S01-前端交互主链/S01-T01-欢迎页输入到会话地址.md",
        "prose_cjk": 16079, "density": 23.1, "thin_blocks": 5, "verdict": "fail",
    },
    "assisted_3654": {
        "path": "reports/release-p0-v11131-r4/project/.codelearn/notes/S00-项目全景/"
                "S00-T01-欢迎页输入到会话地址.md",
        "prose_cjk": 48721, "density": 41.5, "thin_blocks": 5, "verdict": "fail",
    },
    "natural_failed_cobra": {
        "path": "reports/natural-acceptance-v31-20261028/case-C-cobra/project/.codelearn/"
                "notes/S01-项目入口与初始化生成/S01-T01-01-cobra-cli-init-从模块输入到项目骨架生成.md",
        "prose_cjk": 23556, "density": 56.9, "thin_blocks": 2, "verdict": "fail",
    },
}


class GateCalibrationTests(unittest.TestCase):
    def test_historical_notes_keep_their_expected_split(self):
        checked = 0
        for name, case in CASES.items():
            path = ROOT / case["path"]
            if not path.is_file():
                continue
            with self.subTest(case=name):
                metrics = assemble.prose_metrics(path.read_bytes())
                self.assertEqual(metrics["prose_cjk"], case["prose_cjk"])
                self.assertEqual(metrics["density"], case["density"])
                self.assertEqual(len(metrics["thin_blocks"]), case["thin_blocks"])
                failures = assemble.gate_failures(metrics, assemble.DEFAULT_MIN_PROSE_CJK,
                                                  assemble.DEFAULT_MIN_DENSITY, block_floor=False)
                self.assertEqual("fail" if failures else "pass", case["verdict"], failures)
                if name == "old_effective_baseline":
                    # v1.16 adds a per-block floor: the old accepted note is thick in
                    # total but thin after individual blocks, so it must now fail.
                    tightened = assemble.gate_failures(metrics, assemble.DEFAULT_MIN_PROSE_CJK,
                                                       assemble.DEFAULT_MIN_DENSITY)
                    self.assertIn("below_block_density", tightened)
            checked += 1
        if not checked:
            self.skipTest("archived acceptance notes are not present")


if __name__ == "__main__":
    unittest.main()
