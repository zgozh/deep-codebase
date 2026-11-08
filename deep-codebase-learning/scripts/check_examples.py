"""Read-only guard for the bundled writing examples.

Authoring rules have one cheap way to fail silently: the example a rule points at
drifts away from the rule. That already happened here — the default source-writing
example explained 47 CJK per source line while the gate demands 50, so an author who
copied it produced blocks the gate rejects. This script re-measures every bundled
example with `audit_lesson`, and fails when an example no longer passes the checks it
is supposed to demonstrate.

It also verifies that every relative Markdown link inside the skill resolves, so
removing or renaming a reference cannot leave a dead pointer behind.

Usage: python check_examples.py [--json]
Exit: 0 all examples conform and all links resolve; 1 otherwise.
"""

import argparse
import json
import re
from pathlib import Path

from audit_lesson import audit

ROOT = Path(__file__).resolve().parent.parent

# Whole-lesson checks: an excerpt is one or two units, not a ten-chapter lesson, so
# these three cannot apply to it. Every other problem type is a real defect, because
# authors copy the excerpt's block shape verbatim.
WHOLE_LESSON_ONLY = {"title", "chapters", "units", "concepts"}

# name -> how to judge it
EXAMPLES = {
    "references/unit-example.md": {"kind": "fragment", "max_thin_share": 0.10},
    "references/value-binding.md": {"kind": "statement"},
}

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def block_summary(result):
    blocks = [b for b in result["blocks"] if b.get("per_line")]
    if not blocks:
        return None
    per_line = sorted(b["per_line"] for b in blocks)
    ratios = [b["cjk_per_quote"] for b in blocks if b.get("cjk_per_quote")]
    middle = per_line[len(per_line) // 2]
    return {
        "blocks": len(blocks),
        "per_line_min": round(per_line[0], 1),
        "per_line_p50": round(middle, 1),
        "thin": sum(1 for value in per_line if value < 50),
        "thin_share": round(sum(1 for value in per_line if value < 50) / len(per_line), 3),
        "quote_ratio_min": round(min(ratios), 2) if ratios else None,
        "quote_below_g5": sum(1 for value in ratios if value < 1.2),
    }


def check_example(name, spec):
    path = ROOT / name
    problems, report = [], {"file": name, "kind": spec["kind"]}
    if not path.is_file():
        return [f"{name}: missing"], report

    result = audit(path)
    hard = [p for p in result["problems"] if p["check"] not in WHOLE_LESSON_ONLY]
    problems += [f"{name}: {p['check']} {p.get('unit', '')} {p['detail']}".strip() for p in hard]

    summary = block_summary(result)
    report["blocks"] = summary
    if spec["kind"] == "fragment":
        if not result["units"]:
            problems.append(f"{name}: no source unit found; a fragment must keep at least one ### 5.x unit")
        if summary is None:
            problems.append(f"{name}: no measured source block; the example demonstrates nothing")
        elif summary["thin_share"] > spec["max_thin_share"]:
            problems.append(
                f"{name}: {summary['thin']}/{summary['blocks']} blocks explain <50 CJK per source line "
                f"({summary['thin_share']:.0%} > {spec['max_thin_share']:.0%}); the example is below the gate it documents"
            )
    else:
        fences = path.read_text(encoding="utf-8").count("\n```")
        report["code_fences"] = fences
        if fences < 2:
            problems.append(f"{name}: no fenced code block; a statement-level contrast must show the source")
    return problems, report


def check_links():
    # Only the shipped skill is scanned: docs/ and reports/ keep historical records that
    # legitimately quote paths as they existed at the time, so their links may dangle.
    problems = []
    checked = 0
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            checked += 1
            if not (path.parent / file_part).exists():
                problems.append(f"{path.relative_to(ROOT)}: dead link -> {target}")
    return problems, checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    problems, reports = [], []
    for name, spec in EXAMPLES.items():
        found, report = check_example(name, spec)
        problems += found
        reports.append(report)
    link_problems, link_count = check_links()
    problems += link_problems

    payload = {"passed": not problems, "examples": reports, "links_checked": link_count, "problems": problems}
    print(json.dumps(payload, ensure_ascii=False, indent=1) if args.json
          else json.dumps(payload, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
