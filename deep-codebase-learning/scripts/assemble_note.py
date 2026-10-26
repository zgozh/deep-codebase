"""Join existing UTF-8 parts with two LF bytes into a new candidate; no quality assessment."""

import argparse
import json
import os
from pathlib import Path
import tempfile

from render_sources import SourceError, render_bytes


def assemble_note(workspace, parts, output, *, source_root=None, final_note=None):
    result = {"saved": False, "output": str(output), "bytes": 0, "parts": len(parts)}
    temporary = None
    try:
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
        if output.exists():
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
        content = b"\n\n".join(bodies)
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
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--final-note", type=Path)
    args = parser.parse_args()
    result = assemble_note(args.workspace, args.part, args.output,
                           source_root=args.source_root, final_note=args.final_note)
    print(json.dumps(result))
    return 0 if result["saved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
