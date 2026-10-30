"""Read-only lesson audit: structure, concept depth, and explanation coverage.

Checks a finished note against the teaching contract's mechanically visible
parts. It does not judge truth or teaching quality; it only reports where the
shape is missing, so the author knows which unit to reopen.

Usage: python audit_lesson.py <note.md> [--json]
"""

import argparse
import json
import re
from pathlib import Path


CJK = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")

POSITIONS = [
    ("problem", "实际问题与实现思路"),
    ("context", "架构位置"),
    ("locate", "源码定位与阅读准备"),
    ("code", "4–5"),
    ("run", "运行"),
    ("mechanism", "机制"),
    ("usage", "怎么用"),
]

UNDERLYING_MARKERS = ("线程", "事件循环", "序列化", "字节码", "GC", "索引", "协议", "TCP", "HTTP",
                      "锁", "内存", "连接池", "协程", "栈", "缓冲", "事务", "socket", "epoll", "页")
DESIGN_MARKERS = ("替代", "代价", "取舍", "权衡", "否则", "如果", "删掉", "换一种", "不这样", "另一种")
FRAMEWORK_MARKERS = ("Spring", "MyBatis", "Hutool", "Jackson", "React", "Zustand", "Redisson",
                     "OkHttp", "Guava", "Lombok", "Servlet", "Tomcat", "FastAPI", "SQLAlchemy",
                     "Pydantic", "框架", "容器", "注解", "生命周期", "自动配置", "starter")
LANGUAGE_MARKERS = ("求值", "绑定", "可见性", "精度", "短路", "默认值", "浅拷贝", "作用域",
                    "重载", "泛型", "溢出", "同步", "异步")
INLINE_CODE = re.compile(r"`([^`\n]+)`")

EXAMPLE_MARKERS = ("例如", "比如", "举例", "示意", "就像", "设想", "假设", "想象", "示例", "演示",
                   "长这样", "写出去", "代入")
PROJECT_MARKERS = ("本项目", "项目里", "代码里", "本课", "当前文件", "这个文件", "Ragent")
BOUNDARY_MARKERS = ("代价", "不能", "否则", "区别", "误", "坑", "局限", "边界", "风险", "失败", "如果", "一旦", "避免")
DEFINITION_MARKERS = ("是", "指", "叫", "称为", "表示", "就是", "所谓", "即", "意味着")

TERMS = [
    "受控组件", "合成事件", "批处理", "闭包", "浅合并", "快照", "幂等", "切面",
    "注解", "信号量", "SSE", "emitter", "雪花", "record", "乐观更新", "虚拟列表",
    "竞态", "退避", "流式", "SpEL", "Bean Validation", "序列化", "代理", "AOP",
]


def cjk(text):
    return len(CJK.findall(text))


def display_width(text):
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def composition(text):
    """How a block's post-code prose is built: pasted code vs stated knowledge."""
    spans = INLINE_CODE.findall(text)
    span_chars = sum(len(s) for s in spans)
    compact = re.sub(r"\s", "", text)
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    total = cjk(text)
    insight = any(marker in text for marker in
                  UNDERLYING_MARKERS + FRAMEWORK_MARKERS + LANGUAGE_MARKERS)
    return {
        "paras": len(paras),
        "cjk": total,
        "avg_para": round(total / len(paras), 1) if paras else 0,
        "quote_ratio": round(span_chars / len(compact), 3) if compact else 0,
        "code_openers": sum(1 for p in paras if p.lstrip().startswith("`")),
        "whole_line_quotes": sum(1 for s in spans if len(s) >= 40),
        "insight": insight,
    }


def diagram_findings(fences):
    """Flag labels wide enough to collide with lifelines or subgraph borders."""
    found = []
    seen = 0
    for fence in fences:
        if fence["language"] != "mermaid":
            continue
        body = fence.get("body", [])
        if not body:
            continue
        seen += 1
        kind = body[0].split()[0]
        entry = {"index": seen, "kind": kind, "line": fence["start"] + 1,
                 "labels": 0, "widest": 0, "samples": [], "warnings": []}
        participants = [line for line in body if re.match(r"^\s*participant\s+", line)]
        subgraphs = [line for line in body if re.match(r"^\s*subgraph\b", line)]
        if kind.startswith("sequence"):
            if len(participants) > 8:
                entry["warnings"].append(f"{len(participants)} participants crowd the lifelines")
            for line in body:
                match = re.match(r"^\s*(\w+)\s*(?:-->>|->>|-->|->|--x|-x|--\)|-\))\s*(\w+)\s*:\s*(.+?)\s*$", line)
                if not match:
                    continue
                label = match.group(3).strip().strip('"')
                if match.group(1) == match.group(2):
                    # Mermaid draws a self-message label across its own lifeline.
                    entry["warnings"].append(
                        f"self-message {label[:12]!r} sits on its lifeline; use Note over")
                    entry["labels"] += 1
                    continue
                width = display_width(label)
                entry["labels"] += 1
                if width > 20:
                    entry["samples"].append((width, label))
                    entry["widest"] = max(entry["widest"], width)
        else:
            if len(subgraphs) > 5:
                entry["warnings"].append(f"{len(subgraphs)} subgraphs crowd the layout")
            for line in body:
                if "-->" not in line and "---" not in line:
                    continue
                for label in re.findall(r"\|([^|]+)\|", line):
                    label = label.strip().strip('"')
                    if not label:
                        continue
                    width = display_width(label)
                    entry["labels"] += 1
                    if width > 14:
                        entry["samples"].append((width, label))
                        entry["widest"] = max(entry["widest"], width)
        if entry["samples"]:
            entry["samples"].sort(reverse=True)
            worst = ", ".join(repr(label[:12]) + f" ({width})" for width, label in entry["samples"][:3])
            entry["warnings"].append(
                f"{len(entry['samples'])}/{entry['labels']} labels exceed the gap; widest: {worst}")
            entry["samples"] = [{"width": width, "label": label} for width, label in entry["samples"][:5]]
        if entry["warnings"]:
            found.append(entry)
    return found


def parse(text):
    lines = text.split("\n")
    headings = []
    fences = []
    in_fence = False
    fence_start = None
    language = ""
    for index, line in enumerate(lines):
        stripped = line.strip()
        marker = FENCE.match(line)
        if marker:
            if not in_fence:
                in_fence = True
                fence_start = index
                language = stripped[len(marker.group(1)):].strip()
            else:
                in_fence = False
                body = [l for l in lines[fence_start + 1:index] if l.strip()]
                fences.append({"start": fence_start, "end": index, "language": language,
                               "lines": len(body), "body": body})
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if match:
            headings.append({"index": index, "level": len(match.group(1)),
                             "text": match.group(2).strip()})
    return lines, headings, fences


def section_text(lines, start, end):
    return "\n".join(lines[start + 1:end])


def audit(path):
    lines, headings, fences = parse(Path(path).read_text(encoding="utf-8"))
    problems = []
    warnings = []

    h1 = [h for h in headings if h["level"] == 1]
    h2 = [h for h in headings if h["level"] == 2]
    if len(h1) != 1:
        problems.append({"check": "title", "detail": f"expected one H1, found {len(h1)}"})
    if len(h2) < 10:
        problems.append({"check": "chapters", "detail": f"expected >=10 H2, found {len(h2)}"})

    # Chapter 5 units: H3 under the H2 whose title starts with "5."
    chapter5 = None
    for position, heading in enumerate(headings):
        if heading["level"] == 2 and re.match(r"^5[.、\s]", heading["text"]):
            chapter5 = position
            break
    units = []
    if chapter5 is not None:
        end = next((h["index"] for h in headings[chapter5 + 1:] if h["level"] <= 2), len(lines))
        start = headings[chapter5]["index"]
        h3s = [h for h in headings if h["level"] == 3 and start < h["index"] < end]
        for order, h3 in enumerate(h3s):
            next_index = h3s[order + 1]["index"] if order + 1 < len(h3s) else end
            h4s = [h for h in headings if h["level"] == 4 and h3["index"] < h["index"] < next_index]
            unit_fences = [f for f in fences if h3["index"] < f["start"] < next_index]
            units.append({"title": h3["text"], "h3": h3["index"], "end": next_index,
                          "h4s": h4s, "fences": unit_fences})
    if len(units) < 1:
        problems.append({"check": "units", "detail": "no source unit found under chapter 5"})

    compositions = []
    for unit in units:
        title = unit["title"][:40]
        names = [h["text"] for h in unit["h4s"]]
        for key, needle in POSITIONS:
            if not any(needle in name for name in names):
                problems.append({"check": "position", "unit": title, "detail": f"missing {key}"})
        if not unit["fences"]:
            problems.append({"check": "source", "unit": title, "detail": "no source block"})
            continue
        unit_text = section_text(lines, unit["h3"], unit["end"])
        if any(marker in unit_text for marker in UNDERLYING_MARKERS) is False:
            warnings.append({"check": "layer_gap", "unit": title,
                             "detail": "no underlying mechanism (threads/serialization/protocol/index)"})
        if not any(marker in unit_text for marker in DESIGN_MARKERS):
            warnings.append({"check": "layer_gap", "unit": title,
                             "detail": "no tradeoff/alternative reasoning in this unit"})
        code_h4 = next((h for h in unit["h4s"] if "4–5" in h["text"] or "4-5" in h["text"]), None)
        if code_h4 is not None:
            before = [h for h in unit["h4s"] if h["index"] < code_h4["index"]]
            after = [h for h in unit["h4s"] if h["index"] > code_h4["index"]]
            if len(before) < 3:
                problems.append({"check": "pre_block", "unit": title,
                                 "detail": f"expected 3 sections before code, found {len(before)}"})
            if len(after) < 3:
                problems.append({"check": "post_block", "unit": title,
                                 "detail": f"expected 3 sections after code, found {len(after)}"})
            for heading in before:
                end = min(next((h["index"] for h in headings if h["index"] > heading["index"]),
                               unit["end"]), unit["end"])
                size = cjk(section_text(lines, heading["index"], end))
                if size < 120:
                    problems.append({"check": "pre_depth", "unit": title,
                                     "detail": f"{heading['text'][:20]} only {size} CJK"})
                elif size < 200:
                    warnings.append({"check": "pre_depth", "unit": title,
                                     "detail": f"{heading['text'][:20]} has {size} CJK, target 200"})
            for heading in after:
                end = min(next((h["index"] for h in headings if h["index"] > heading["index"]),
                               unit["end"]), unit["end"])
                size = cjk(section_text(lines, heading["index"], end))
                if size < 150:
                    problems.append({"check": "post_depth", "unit": title,
                                     "detail": f"{heading['text'][:20]} only {size} CJK"})
                elif size < 250:
                    warnings.append({"check": "post_depth", "unit": title,
                                     "detail": f"{heading['text'][:20]} has {size} CJK, target 250"})
        first_fence = unit["fences"][0]["start"]
        if code_h4 is not None and first_fence < code_h4["index"]:
            problems.append({"check": "order", "unit": title,
                             "detail": "code before the 4–5 region"})
        # Explanation after each block, until the next block or unit end.
        for order, fence in enumerate(unit["fences"]):
            next_block = (unit["fences"][order + 1]["start"] if order + 1 < len(unit["fences"])
                          else unit["end"])
            next_section = next((h["index"] for h in headings
                                 if h["index"] > fence["end"] and h["level"] <= 4), unit["end"])
            boundary = min(next_block, next_section, unit["end"])
            prose = [line for line in lines[fence["end"] + 1:boundary]
                     if not HEADING.match(line)]
            block_text = "\n".join(prose)
            size = cjk(block_text)
            paragraphs = len([p for p in re.split(r"\n\s*\n", block_text) if p.strip()])
            need = max(200, fence["lines"] * 8)
            if fence["language"] in ("mermaid", "text", "plain"):
                continue
            if size < need:
                problems.append({"check": "explain", "unit": title,
                                 "detail": f"{fence['lines']}-line block has {size} CJK, need {need}"})
            if paragraphs < max(2, (fence["lines"] + 14) // 15):
                problems.append({"check": "paragraphs", "unit": title,
                                 "detail": f"{fence['lines']}-line block has {paragraphs} paragraphs"})
            entry = composition(block_text)
            entry["line"] = fence["start"] + 1
            entry["unit"] = title
            compositions.append(entry)

    # Composition summary: four signals, each capped so a broken draft stays readable.
    def sample(items):
        return ", ".join(str(item["line"]) for item in items[:6])

    heavy = [c for c in compositions if c["quote_ratio"] > 0.35]
    if heavy:
        worst = max(heavy, key=lambda c: c["quote_ratio"])
        warnings.append({"check": "composition",
                         "detail": f"{len(heavy)}/{len(compositions)} blocks spend >35% of their prose "
                                   f"inside inline code (worst line {worst['line']}: "
                                   f"{int(worst['quote_ratio'] * 100)}%); lines {sample(heavy)}"})
    fragmented = [c for c in compositions if c["paras"] >= 3 and c["avg_para"] < 100]
    if fragmented:
        worst = min(fragmented, key=lambda c: c["avg_para"])
        warnings.append({"check": "composition",
                         "detail": f"{len(fragmented)}/{len(compositions)} blocks average <100 CJK per "
                                   f"paragraph (worst line {worst['line']}: {worst['avg_para']}); "
                                   f"lines {sample(fragmented)}"})
    openers = [c for c in compositions
               if c["paras"] >= 3 and c["code_openers"] / c["paras"] > 0.5]
    if openers:
        warnings.append({"check": "composition",
                         "detail": f"{len(openers)}/{len(compositions)} blocks open most paragraphs with "
                                   f"a code quote; lines {sample(openers)}"})
    blind = [c for c in compositions if not c["insight"]]
    if blind:
        warnings.append({"check": "composition",
                         "detail": f"{len(blind)} blocks state no framework/underlying/language fact; "
                                   f"lines {sample(blind)}"})

    # Non-source chapters still owe real teaching: replay, tradeoffs, review, boundaries.
    CHAPTER_FLOORS = {"1": 800, "2": 800, "4": 800, "6": 800, "7": 1200,
                      "8": 800, "9": 800, "10": 700}
    for position, heading in enumerate(headings):
        if heading["level"] != 2:
            continue
        match = re.match(r"^(\d{1,2})[.、\s]", heading["text"])
        if not match or match.group(1) not in CHAPTER_FLOORS:
            continue
        end = next((h["index"] for h in headings[position + 1:] if h["level"] <= 2), len(lines))
        size = cjk(section_text(lines, heading["index"], end))
        floor = CHAPTER_FLOORS[match.group(1)]
        if size < floor:
            warnings.append({"check": "chapter_depth",
                             "detail": f"chapter {match.group(1)} has {size} CJK, target {floor}"})

    # Chapter 3 concepts.
    chapter3 = None
    for position, heading in enumerate(headings):
        if heading["level"] == 2 and re.match(r"^3[.、\s]", heading["text"]):
            chapter3 = position
            break
    concepts = []
    if chapter3 is not None:
        end = next((h["index"] for h in headings[chapter3 + 1:] if h["level"] <= 2), len(lines))
        start = headings[chapter3]["index"]
        h3s = [h for h in headings if h["level"] == 3 and start < h["index"] < end]
        for order, h3 in enumerate(h3s):
            next_index = h3s[order + 1]["index"] if order + 1 < len(h3s) else end
            text = section_text(lines, h3["index"], next_index)
            size = cjk(text)
            entry = {"title": h3["text"][:40], "cjk": size}
            if size < 250:
                problems.append({"check": "concept_depth", "detail": f"{entry['title']} only {size} CJK"})
            elif size < 400:
                warnings.append({"check": "concept_depth", "detail": f"{entry['title']} has {size} CJK, core target 400"})
            if not any(marker in text for marker in EXAMPLE_MARKERS):
                problems.append({"check": "concept_example", "detail": f"{entry['title']} lacks an example"})
            if not any(marker in text for marker in PROJECT_MARKERS):
                problems.append({"check": "concept_mapping", "detail": f"{entry['title']} lacks a project mapping"})
            if not any(marker in text for marker in BOUNDARY_MARKERS):
                problems.append({"check": "concept_boundary", "detail": f"{entry['title']} lacks a boundary"})
            concepts.append(entry)
    if not concepts:
        problems.append({"check": "concepts", "detail": "no concept section found"})

    # First-use definitions of common jargon.
    full = Path(path).read_text(encoding="utf-8")
    for term in TERMS:
        index = full.find(term)
        if index < 0:
            continue
        window = full[max(0, index - 250):index + 250]
        if not any(marker in window for marker in DEFINITION_MARKERS):
            warnings.append({"check": "term", "detail": f"{term} first used without a nearby definition"})

    # Diagram labels that will collide once rendered.
    diagrams = diagram_findings(fences)
    for diagram in diagrams:
        for detail in diagram["warnings"]:
            warnings.append({"check": "diagram",
                             "detail": f"mermaid #{diagram['index']}: {detail}"})

    return {"file": str(path), "units": len(units), "concepts": concepts,
            "diagrams": diagrams, "composition": compositions,
            "problems": problems, "warnings": warnings,
            "passed": not problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = audit(args.note)
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json
          else json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
