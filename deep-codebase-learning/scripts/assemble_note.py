"""Join UTF-8 parts into a new candidate; measure teaching prose, not physical lines.

The content gate counts CJK characters (U+3400-4DBF, U+4E00-9FFF) outside fenced
code blocks and heading lines, and checks how much explanation follows each code
block. Physical lines, blank lines and code volume never satisfy the gate.
No semantic quality assessment happens here.
"""

import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from render_sources import SourceError, physical_lines, render_bytes


CJK = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF]")
FENCE_OPEN = re.compile(rb"^ {0,3}(`{3,}|~{3,})")
HEADING = re.compile(rb"^ {0,3}#{1,6}[ \t]")

DEFAULT_MIN_PROSE_CJK = 15000
DEFAULT_MIN_DENSITY = 30
DENSITY_MIN_CODE_LINES = 150
LONG_BLOCK_LINES = 25
LONG_BLOCK_MIN_PER_LINE = 8
LONG_BLOCK_MIN_PROSE = 200
BLOCK_DENSITY_FLOOR = 50
QUOTE_RATIO_FLOOR = 1.2
BLOCK_DENSITY_MIN_LINES = 5
NON_SOURCE_LANGUAGES = ("mermaid", "text", "plain")


def prose_metrics(content):
    """Return prose/block metrics for rendered Markdown bytes."""
    prose_cjk = 0
    code_lines = 0
    blocks = []
    in_fence = False
    fence = None
    current_code = 0
    pending = None
    pending_heading = None
    pending_prose = 0
    pending_quote = 0
    fence_language = ""
    chapter5 = False
    for number, line in enumerate(physical_lines(content), 1):
        marker = FENCE_OPEN.match(line)
        if marker:
            if not in_fence:
                if pending is not None:
                    pending["prose_cjk"] = pending_prose
                    pending["quoted"] = pending_quote
                    pending["heading"] = pending_heading
                    blocks.append(pending)
                pending, pending_heading, pending_prose, pending_quote = None, None, 0, 0
                in_fence = True
                fence = (marker[1][:1], len(marker[1]))
                fence_language = line[len(marker[1]):].strip().decode("utf-8", "replace")
                current_code = 0
            else:
                closing = re.fullmatch(rb" {0,3}" + fence[0] + b"{" + str(fence[1]).encode()
                                       + rb",}[ \t]*(?:\r\n|\r|\n)?", line)
                if closing:
                    in_fence = False
                    pending = {"line": number, "code_lines": current_code,
                               "language": fence_language, "chapter5": chapter5}
                continue
            continue
        if in_fence:
            if line.strip():
                code_lines += 1
                current_code += 1
            continue
        if not line.strip():
            continue
        if HEADING.match(line):
            level = len(line) - len(line.lstrip(b"#"))
            if level <= 3:
                text = line.lstrip(b"#").strip().decode("utf-8", "replace")
                chapter5 = bool(re.match(r"^5[.、\s]", text))
            if pending is not None and pending_heading is None:
                pending_heading = line.strip().lstrip(b"#").strip().decode("utf-8", "replace")
            continue
        decoded = line.decode("utf-8")
        count = len(CJK.findall(decoded))
        prose_cjk += count
        pending_prose += count
        pending_quote += sum(len(span) for span in re.findall(r"`([^`\n]+)`", decoded))
    if pending is not None:
        pending["prose_cjk"] = pending_prose
        pending["quoted"] = pending_quote
        pending["heading"] = pending_heading
        blocks.append(pending)
    thin = []
    low_density = []
    low_quote = []
    for block in blocks:
        if (block.get("chapter5")
                and block["code_lines"] >= BLOCK_DENSITY_MIN_LINES
                and block.get("language", "") not in NON_SOURCE_LANGUAGES):
            per_line = block["prose_cjk"] / block["code_lines"]
            if per_line < BLOCK_DENSITY_FLOOR:
                low_density.append({
                    "line": block["line"],
                    "heading": block["heading"],
                    "code_lines": block["code_lines"],
                    "prose_cjk": block["prose_cjk"],
                    "per_line": round(per_line, 1),
                    "need": int(BLOCK_DENSITY_FLOOR * block["code_lines"]),
                })
            quoted = block.get("quoted", 0)
            ratio = block["prose_cjk"] / quoted if quoted else 99
            if quoted and ratio < QUOTE_RATIO_FLOOR:
                low_quote.append({
                    "line": block["line"],
                    "heading": block["heading"],
                    "code_lines": block["code_lines"],
                    "prose_cjk": block["prose_cjk"],
                    "quoted": quoted,
                    "cjk_per_quote": round(ratio, 2),
                    "need_cjk": int(QUOTE_RATIO_FLOOR * quoted) + 1,
                })
        if block["code_lines"] < LONG_BLOCK_LINES:
            continue
        need = max(LONG_BLOCK_MIN_PROSE, block["code_lines"] * LONG_BLOCK_MIN_PER_LINE)
        if block["prose_cjk"] < need:
            thin.append({"line": block["line"], "heading": block["heading"],
                         "code_lines": block["code_lines"],
                         "prose_cjk": block["prose_cjk"], "need": need})
    metrics = {"prose_cjk": prose_cjk, "code_lines": code_lines,
               "density": round(prose_cjk / code_lines, 1) if code_lines else None,
               "code_blocks": len(blocks), "thin_blocks": thin,
               "low_density_blocks": low_density, "low_quote_blocks": low_quote}
    return metrics


def gate_failures(metrics, min_prose_cjk, min_density, density_min_lines=DENSITY_MIN_CODE_LINES,
                  block_floor=True):
    failures = []
    if min_prose_cjk is not None and metrics["prose_cjk"] < min_prose_cjk:
        failures.append("below_min_prose")
    if (min_density is not None and metrics["code_lines"] >= density_min_lines
            and (metrics["density"] or 0) < min_density):
        failures.append("below_min_density")
    if metrics["thin_blocks"]:
        failures.append("thin_source_blocks")
    if block_floor and metrics.get("low_density_blocks"):
        failures.append("below_block_density")
    if block_floor and metrics.get("low_quote_blocks"):
        failures.append("below_quote_ratio")
    return failures


def assemble_note(workspace, parts, output, *, source_root=None, final_note=None, min_lines=None,
                  content_gate=False, min_prose_cjk=None, min_density=None, prose_floor=True,
                  check_only=False, block_floor=True):
    result = {"saved": False, "output": str(output), "bytes": 0, "parts": len(parts)}
    temporary = None
    try:
        if min_lines is not None and (type(min_lines) is not int or min_lines <= 0):
            result["error"] = "invalid_min_lines"
            return result
        for name, value in (("min_prose_cjk", min_prose_cjk), ("min_density", min_density)):
            if value is not None and (type(value) not in (int, float) or value <= 0):
                result["error"] = "invalid_min_" + name
                return result
        if check_only:
            content_gate = True
        workspace = Path(workspace).resolve()
        output = (workspace / output).resolve()
        paths = [(workspace / part).resolve() for part in parts]
        result["output"] = str(output)
        if (source_root is None) != (final_note is None):
            result["error"] = "source_root_and_final_note_required"
            return result
        if source_root is not None:
            source_root = Path(source_root).resolve()
            final_note = (workspace / final_note).resolve()
        try:
            output.relative_to(workspace)
            if final_note is not None:
                final_note.relative_to(workspace)
            for path in paths:
                path.relative_to(workspace)
        except ValueError:
            result["error"] = "path_outside_workspace"
            return result
        if not check_only and output.exists():
            result["error"] = "target_exists"
            return result
        if not paths:
            result["error"] = "missing_parts"
            return result
        bodies = []
        sources = {}
        if source_root is not None:
            result.update(include_count=0, source_refs=[])
        for path in paths:
            body = path.read_bytes()
            if not body.decode("utf-8").strip():
                result["error"] = "empty_part"
                return result
            if source_root is not None:
                body, metadata = render_bytes(body, source_root, final_note, sources)
                result["include_count"] += metadata["include_count"]
                result["source_refs"] = metadata["source_refs"]
            bodies.append(body)
        if source_root is not None and result["include_count"] == 0 and not check_only:
            result["error"] = "no_source_includes"
            return result
        content = b"\n\n".join(bodies)
        if min_lines is not None:
            result.update(lines=len(physical_lines(content)), min_lines=min_lines)
            if result["lines"] < min_lines:
                result["error"] = "below_min_lines"
                return result
        if content_gate:
            metrics = prose_metrics(content)
            result.update(metrics)
            # A single unit part is checked for block quality; the whole-lesson
            # prose floor applies at assembly (or when the caller passes it).
            if min_density is None:
                min_density = DEFAULT_MIN_DENSITY
            if min_prose_cjk is None and not check_only and prose_floor:
                min_prose_cjk = DEFAULT_MIN_PROSE_CJK
            result.update(min_prose_cjk=min_prose_cjk, min_density=min_density)
            density_min_lines = 20 if check_only else DENSITY_MIN_CODE_LINES
            failures = gate_failures(metrics, min_prose_cjk, min_density, density_min_lines,
                                     block_floor)
            if failures:
                result["gates"] = failures
                result["error"] = "below_content_gate"
                if check_only:
                    result["ok"] = False
                return result
            if check_only:
                result["ok"] = True
                result["checked"] = True
                return result
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".assemble-note-",
                                         delete=False) as candidate:
            temporary = Path(candidate.name)
            candidate.write(content)
        # A same-directory hard link commits complete bytes without replacing a competing target.
        os.link(temporary, output)
        result["saved"] = True
        result["bytes"] = len(content)
    except SourceError as error:
        result.update(error.result)
        result["part"] = str(path)
    except UnicodeError:
        result["error"] = "invalid_utf8"
    except FileExistsError:
        result["error"] = "target_exists"
    except FileNotFoundError:
        result["error"] = "missing_path"
    except (OSError, ValueError):
        result["error"] = "io_error"
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                result["cleanup_error"] = "io_error"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--part", required=True, action="extend", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--final-note", type=Path)
    parser.add_argument("--min-lines", type=int)
    parser.add_argument("--min-prose-cjk", type=int, default=None)
    parser.add_argument("--min-density", type=float, default=None)
    parser.add_argument("--no-content-gate", action="store_true")
    parser.add_argument("--no-prose-floor", action="store_true",
                        help="exempt local/short notes from the whole-lesson prose floor; G2/G3/G4 still apply")
    parser.add_argument("--no-block-floor", action="store_true",
                        help="legacy only: re-assemble an old note without the per-block 50-CJK/line floor")
    parser.add_argument("--check", action="store_true",
                        help="report prose metrics for the given parts; write nothing")
    args = parser.parse_args()
    if args.check and args.output is not None:
        parser.error("--check writes nothing; drop --output")
    if not args.check and args.output is None:
        parser.error("--output is required unless --check is used")
    output = args.output if args.output is not None else Path("check-only")
    result = assemble_note(args.workspace, args.part, output,
                           source_root=args.source_root, final_note=args.final_note,
                           min_lines=args.min_lines,
                           content_gate=not args.no_content_gate,
                           min_prose_cjk=args.min_prose_cjk,
                           min_density=args.min_density,
                           prose_floor=not args.no_prose_floor,
                           check_only=args.check,
                           block_floor=not args.no_block_floor)
    print(json.dumps(result))
    if args.check:
        return 0 if result.get("ok") else 1
    return 0 if result["saved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
