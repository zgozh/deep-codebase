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


def audit(path, collect_fixes=False):
    lines, headings, fences = parse(Path(path).read_text(encoding="utf-8"))
    problems = []
    warnings = []
    fixes = []

    def fix(kind, line, where, action, have=None, target=None):
        item = {"kind": kind, "line": line, "where": where, "action": action}
        if have is not None:
            item["have"] = have
            item["target"] = target
            item["need_cjk"] = max(1, target - have)
        fixes.append(item)

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

    block_stats = []
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
                if size < 200:
                    fix("pre_depth", heading["index"] + 1, f"{title} / {heading['text'][:20]}",
                        "补这一小节的正文：实际输入与值、由谁在何时触发、这段代码解决的具体问题", size, 200)
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
                if size < 250:
                    fix("post_depth", heading["index"] + 1, f"{title} / {heading['text'][:20]}",
                        "补这一小节的正文：给定输入的运行结果、失败路径、机制判断或上下游接法", size, 250)
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
            insight = any(marker in block_text for marker in
                          UNDERLYING_MARKERS + FRAMEWORK_MARKERS + LANGUAGE_MARKERS)
            quoted = sum(len(span) for span in re.findall(r"`([^`\n]+)`", block_text))
            block_stats.append({
                "line": fence["start"] + 1,
                "unit": title,
                "lines": fence["lines"],
                "cjk": size,
                "per_line": round(size / max(1, fence["lines"]), 1),
                "quoted": quoted,
                "cjk_per_quote": round(size / quoted, 2) if quoted else None,
                "insight": insight,
            })

    # How thick each block's explanation is: the thing readers notice as "讲得比引用的代码还少".
    def sample(items):
        return ", ".join(str(item["line"]) for item in items[:6])

    thin = [b for b in block_stats if b["per_line"] < 50]
    deep_thin = [b for b in block_stats if b["per_line"] < 35]
    if thin:
        worst = min(thin, key=lambda b: b["per_line"])
        warnings.append({"check": "density",
                         "detail": f"{len(thin)}/{len(block_stats)} blocks explain <50 CJK per source "
                                   f"line ({len(deep_thin)} of them <35; worst line {worst['line']}: "
                                   f"{worst['per_line']}); lines {sample(thin)}"})
    for block in thin:
        fix("density", block["line"], f"{block['unit']} / {block['lines']} 行块",
            "按每行 65 字补：怎么读、实际触发什么、不这样会怎样；缺的是具体类名/默认值/异常/失败后果",
            block["cjk"], block["lines"] * 65)
    blind = [b for b in block_stats if not b["insight"]]
    if blind:
        warnings.append({"check": "knowledge_gap",
                         "detail": f"{len(blind)} blocks state no framework/underlying/language fact; "
                                   f"lines {sample(blind)}"})
    for block in blind:
        fix("knowledge_gap", block["line"], f"{block['unit']} / {block['lines']} 行块",
            "补两条读者看不出来的事实：一条框架/语言契约，一条底层机制或设计取舍", block["cjk"], block["cjk"] + 80)
    quote_heavy = [b for b in block_stats
                   if b["lines"] >= 5 and b["cjk_per_quote"] is not None
                   and b["cjk_per_quote"] < 1.2]
    if quote_heavy:
        worst = min(quote_heavy, key=lambda b: b["cjk_per_quote"])
        warnings.append({"check": "quote_dominance",
                         "detail": f"{len(quote_heavy)}/{len(block_stats)} blocks explain less Chinese than "
                                   f"the code they quote (worst line {worst['line']}: "
                                   f"{worst['cjk_per_quote']} CJK per quoted char); lines {sample(quote_heavy)}"})
    for block in quote_heavy:
        target = int(block["quoted"] * 1.2) + 1
        fix("quote_dominance", block["line"], f"{block['unit']} / {block['lines']} 行块",
            "补齐讲解，让正文汉字多于引用字符（比值 ≥1.2）", block["cjk"], target)

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
            fix("chapter_depth", heading["index"] + 1, f"第 {match.group(1)} 章",
                "补本章职责：这一章要让读者改变什么认识（路径/失败/取舍/边界），不是加小标题", size, floor)

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
                fix("concept_depth", h3["index"] + 1, entry["title"],
                    "补这个概念的定义、一个具体例子、在本项目的落点和一个边界", size, 400)
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
            fix("term", full[:index].count("\n") + 1, term,
                "首现处就地短释一句（这是什么、在这里指什么），不要求展开成概念课")

    # Diagram labels that will collide once rendered.
    diagrams = diagram_findings(fences)
    for diagram in diagrams:
        for detail in diagram["warnings"]:
            warnings.append({"check": "diagram",
                             "detail": f"mermaid #{diagram['index']}: {detail}"})
            if "self-message" in detail:
                action = "把这个自消息改成 Note over，或拆成两次跨参与者消息"
            elif "participants" in detail:
                action = "参与者压到 8 个以内：合并同层，或拆成两张图"
            elif "subgraphs" in detail:
                action = "子图压到 5 个以内：合并同层，或拆成两张图"
            elif "labels exceed" in detail:
                action = "缩短标签：时序图 ≤20 显示宽度、流程图边标签 ≤14（汉字算 2）"
            else:
                action = "按 diagrams.md 的标签宽度规则处理"
            fix("diagram", diagram["line"], f"mermaid #{diagram['index']}（{diagram['kind']}）", action)

    return {"file": str(path), "units": len(units), "concepts": concepts,
            "diagrams": diagrams, "blocks": block_stats,
            "problems": problems, "warnings": warnings,
            "passed": not problems,
            "fixes": sorted(fixes, key=lambda item: item["line"]) if collect_fixes else []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("note")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fix-list", action="store_true",
                        help="emit one actionable item per finding, ordered by line")
    args = parser.parse_args()
    result = audit(args.note, collect_fixes=args.fix_list)
    if args.fix_list:
        payload = {"file": result["file"],
                   "count": len(result["fixes"]),
                   "fixes": sorted(result["fixes"], key=lambda item: item["line"])}
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json
          else json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
