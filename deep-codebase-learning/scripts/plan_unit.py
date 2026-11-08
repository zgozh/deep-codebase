"""Task-card budget for one source unit, before writing it.

The gates in `assemble_note.py` and the warnings in `audit_lesson.py` all fire
*after* a part is written. This script moves the same numbers in front of the
author: give it the source range a unit will read, and it prints how much prose
that unit owes, how the blocks will split, and which shapes will be rejected.

It does not read the target note, does not judge content, and does not replace
the gates. Its only claim is arithmetic: N meaningful source lines at 65 CJK per
line is 65N characters the reader is entitled to.

Usage:
  python plan_unit.py --source <file> --first 61 --last 120 [--root <repo>]
  python plan_unit.py --source <file> --first 61 --last 120 --json
"""

import argparse
import json
import re
from pathlib import Path

# Floor from G4; measured median of a conforming long lesson is 64.8, so 65 is the
# starting target rather than the passing line. 50 only proves "not a summary".
FLOOR_PER_LINE = 50
TARGET_PER_LINE = 65
# A unit owes its seven positions regardless of how small the source is.
PRE_SECTION_TARGET = 200
POST_SECTION_TARGET = 250
UNIT_OVERHEAD = 1500          # three pre + three post sections, in CJK
# 5–15 lines per block, with 12 as the observed median split.
BLOCK_MIN, BLOCK_TARGET, BLOCK_MAX = 5, 12, 15

COMMENT_PREFIXES = ("//", "/*", "*/", "*", "#", "--", "<!--")


def meaningful_lines(path, first, last):
    """Count source lines that carry a statement, not a comment or a blank."""
    lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    if first < 1 or last < first or last > len(lines):
        raise ValueError(f"range {first}-{last} outside 1..{len(lines)}")
    selected = lines[first - 1:last]
    kept = [line for line in selected
            if line.strip() and not line.strip().startswith(COMMENT_PREFIXES)]
    return len(selected), len(kept)


def plan(meaningful):
    blocks = max(1, round(meaningful / BLOCK_TARGET))
    return {
        "meaningful_lines": meaningful,
        "floor_cjk": meaningful * FLOOR_PER_LINE,
        "target_cjk": meaningful * TARGET_PER_LINE,
        "unit_total_floor": meaningful * FLOOR_PER_LINE + UNIT_OVERHEAD,
        "unit_total_target": meaningful * TARGET_PER_LINE + UNIT_OVERHEAD,
        "suggested_blocks": blocks,
        "per_block": [{"block_lines": size,
                       "floor_cjk": size * FLOOR_PER_LINE,
                       "target_cjk": size * TARGET_PER_LINE}
                      for size in range(BLOCK_MIN, BLOCK_MAX + 1)],
        "sections": {"pre_each": PRE_SECTION_TARGET, "post_each": POST_SECTION_TARGET,
                     "unit_overhead": UNIT_OVERHEAD},
    }


RULES = [
    "块切在真实动作与求值边界，5–15 行；不拆断表达式、括号或 JSX/JSON 结构。",
    "每块后面先写「怎么读 / 实际触发什么 / 不这样会怎样」，再写两条整组事实（框架契约 + 底层或设计）。",
    "时序图消息标签 ≤20 显示宽度；流程图边标签 ≤14；自消息不要带文字，用 Note over。",
    "参与者 ≤8、子图 ≤5、节点 ≤20；超了先缩标签，再拆图，最后才减步骤。",
    "单元标题写成「谁在什么时候做什么，为什么是这个顺序」，不写成「XXX 方法解析」。",
    "任务卡里的篇幅上限是建议值；与 G4/G5 冲突时先过门禁。",
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="source file the unit will read")
    parser.add_argument("--first", required=True, type=int)
    parser.add_argument("--last", required=True, type=int)
    parser.add_argument("--root", default=".", help="repo root the path is relative to")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = Path(args.root) / args.source
    if not path.is_file():
        raise SystemExit(f"source not found: {path}")
    try:
        total, meaningful = meaningful_lines(path, args.first, args.last)
    except ValueError as error:
        raise SystemExit(str(error))

    result = {"source": str(path), "first": args.first, "last": args.last,
              "range_lines": total, **plan(meaningful), "rules": RULES}

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    print(f"源码范围 {args.source} 原行 {args.first}–{args.last}：{total} 行，"
          f"其中有意义行 {meaningful} 行（去掉空行与纯注释行）")
    print()
    print(f"本单元正文预算：底线 {result['floor_cjk']} 汉字（每行 50）"
          f"，起稿目标 {result['target_cjk']} 汉字（每行 65）")
    print(f"加上七个位置：底线 {result['unit_total_floor']}，目标 {result['unit_total_target']} 汉字")
    print(f"建议切成 {result['suggested_blocks']} 块（每块约 {BLOCK_TARGET} 行）")
    print()
    print("块行数 → 该块至少要写多少字（底线 / 目标）")
    for row in result["per_block"]:
        print(f"  {row['block_lines']:>2} 行 → {row['floor_cjk']:>4} / {row['target_cjk']:>4}")
    print()
    print(f"七个位置：源码前三节各 ≥{PRE_SECTION_TARGET} 字，源码后三节各 ≥{POST_SECTION_TARGET} 字")
    print()
    print("会被退回的形状（现在就避开）：")
    for rule in RULES:
        print(f"  - {rule}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
