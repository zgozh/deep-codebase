"""Render explicit local source includes into a new Markdown part; no quality assessment."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote


def physical_lines(raw):
    lines = re.findall(rb"[^\r\n]*(?:\r\n|\r|\n|$)", raw)
    return lines[:-1] if lines and lines[-1] == b"" else lines


class SourceError(ValueError):
    def __init__(self, result):
        self.result = result


def render_bytes(raw, source_root, note, sources=None):
    """Render one UTF-8 part, optionally sharing a source buffer cache for this assembly."""
    if not raw.decode("utf-8").strip():
        raise SourceError({"error": "empty_input"})
    result = {"include_count": 0, "source_refs": []}
    rendered = []
    sources = {} if sources is None else sources
    fence = None
    for number, line in enumerate(physical_lines(raw), 1):
        marker = re.match(rb" {0,3}(`{3,}|~{3,})([^\r\n]*)", line)
        if fence:
            if re.fullmatch(rb" {0,3}" + fence[0] + b"{" + str(fence[1]).encode()
                            + rb",}[ \t]*(?:\r\n|\r|\n)?", line):
                fence = None
            rendered.append(line)
            continue
        if marker:
            fence = (marker[1][:1], len(marker[1]))
            rendered.append(line)
            continue
        if not re.match(rb" {0,3}<!-- codelearn-source", line):
            rendered.append(line)
            continue
        result["line"] = number
        directive = re.fullmatch(rb" {0,3}<!-- codelearn-source (.+) -->[ \t]*(?:\r\n|\r|\n)?", line)
        if not directive:
            result["error"] = "directive.syntax"
            raise SourceError(result)
        try:
            spec = json.loads(directive[1])
        except ValueError:
            result["error"] = "directive.json"
            raise SourceError(result)
        if type(spec) is not dict or set(spec) != {"path", "first", "last", "language", "title"}:
            result["error"] = "directive.fields"
            raise SourceError(result)
        for field in ("path", "language", "title"):
            value = spec[field]
            if type(value) is not str or any(char in value for char in "\r\n\0"):
                result["error"] = "directive." + field
                raise SourceError(result)
        if not spec["path"].strip() or not spec["title"].strip() or "`" in spec["language"]:
            result["error"] = "directive.text"
            raise SourceError(result)
        if type(spec["first"]) is not int or type(spec["last"]) is not int:
            result["error"] = "directive.range"
            raise SourceError(result)
        source = (source_root / spec["path"]).resolve()
        try:
            relative_source = source.relative_to(source_root).as_posix()
        except ValueError:
            result["error"] = "source.path_outside_root"
            raise SourceError(result)
        if source not in sources:
            try:
                source_raw = source.read_bytes()
                source_raw.decode("utf-8")
            except (OSError, UnicodeError) as error:
                result["error"] = ("invalid_utf8" if isinstance(error, UnicodeError)
                                   else "missing_path" if isinstance(error, FileNotFoundError)
                                   else "io_error")
                raise SourceError(result) from error
            sources[source] = (physical_lines(source_raw), {"path": relative_source, "symbol": None,
                                          "revision": None,
                                          "hash": hashlib.sha256(source_raw).hexdigest(),
                                          "evidence_kind": "code"})
        first, last = spec["first"], spec["last"]
        if first < 1 or last < first or last > len(sources[source][0]):
            result["error"] = "directive.range"
            raise SourceError(result)
        code = b"".join(sources[source][0][first - 1:last])
        size = max([3] + [len(run) + 1 for run in re.findall(rb"`+", code)])
        border = b"`" * size
        ending = b"\r\n" if line.endswith(b"\r\n") else b"\r" if line.endswith(b"\r") else b"\n"
        link = quote(Path(os.path.relpath(source, note.parent)).as_posix(), safe="/")
        heading = "##### 原行" + str(first) + "–" + str(last) + "：" + spec["title"]
        heading += "（[源码](" + link + "#L" + str(first) + "-L" + str(last) + ")）"
        rendered.append(border + spec["language"].encode("utf-8") + ending + code
                        + (b"" if code.endswith((b"\r", b"\n")) else ending)
                        + border + ending + ending + heading.encode("utf-8") + ending)
        result["include_count"] += 1
    content = b"".join(rendered)
    result.pop("line", None)
    result["source_refs"] = [entry[1] for entry in sources.values()]
    return content, result


def render_sources(workspace, source_root, input, output, note):
    result = {"saved": False, "output": str(output), "include_count": 0, "source_refs": []}
    temporary = None
    try:
        workspace, source_root = Path(workspace).resolve(), Path(source_root).resolve()
        input, output, note = [(workspace / path).resolve() for path in (input, output, note)]
        result["output"] = str(output)
        for path in (input, output, note):
            try:
                path.relative_to(workspace)
            except ValueError:
                result["error"] = "path_outside_workspace"
                return result
        if output.exists():
            result["error"] = "target_exists"
            return result
        raw = input.read_bytes()
        if not raw.decode("utf-8").strip():
            result["error"] = "empty_input"
            return result
        content, metadata = render_bytes(raw, source_root, note)
        result.update(metadata)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".render-sources-", delete=False) as target:
            temporary = Path(target.name)
            target.write(content)
        os.link(temporary, output)
        result["saved"] = True
        result.pop("line", None)
    except SourceError as error:
        result.update(error.result)
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
    for name in ("workspace", "source-root", "input", "output", "note"):
        parser.add_argument("--" + name, required=True, type=Path)
    result = render_sources(**vars(parser.parse_args()))
    print(json.dumps(result))
    return 0 if result["saved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
