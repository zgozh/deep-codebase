"""Read-only release checks. Not part of the installed skill runtime."""

import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "deep-codebase-learning"
ROOT_FILES = {
    ".gitignore", ".gitattributes", "README.md", "README.en.md", "LICENSE",
    "CONTRIBUTING.md", "CHANGELOG.md", "requirements-dev.txt",
}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def local_targets(content):
    prose = re.sub(r"```[\s\S]*?```|`[^`\n]*`", "", content)
    return re.findall(r"(?<!!)\[[^\]\n]*\]\(([^)]+)\)", prose)


def heading_ids(content):
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
    ids, counts = set(), {}
    for heading in headings:
        slug = re.sub(r"[^\w\s-]", "", heading.lower()).strip().replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        ids.add(slug if count == 0 else f"{slug}-{count}")
    return ids


def validate():
    files = {ROOT / name for name in ROOT_FILES}
    files.update(p for folder in (SKILL, ROOT / "docs", ROOT / "scripts", ROOT / ".github")
                 for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    for path in files:
        check(path.is_file(), f"Missing release file: {path.relative_to(ROOT)}")
        check(not path.is_symlink(), f"Symlink in release: {path.relative_to(ROOT)}")

    texts = {path: path.read_text(encoding="utf-8") for path in files}
    links = 0
    for path, content in texts.items():
        relative = path.relative_to(ROOT)
        check("\ufffd" not in content and not content.startswith("\ufeff"), f"Invalid UTF-8/BOM: {relative}")
        if path.suffix == ".json":
            json.loads(content)
        elif path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(content)
        if path.suffix != ".md":
            continue
        check(content.count("```") % 2 == 0, f"Unclosed code fence: {relative}")
        check("[TODO:" not in content, f"Unfinished scaffold: {relative}")
        check(not re.search(r"[A-Za-z]:[/\\](?:Users|develop)[/\\]", content), f"Personal path: {relative}")
        for target in local_targets(content):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            filename, _, fragment = unquote(target.strip("<>")).partition("#")
            destination = (path.parent / filename).resolve() if filename else path
            check(destination in files, f"Missing/unpublished link: {relative} -> {target}")
            if fragment and destination.suffix == ".md":
                check(fragment in heading_ids(texts[destination]), f"Missing anchor: {relative} -> {target}")
            links += 1

    content = texts[SKILL / "SKILL.md"]
    match = re.match(r"^---\n(.*?)\n---(?:\n|$)", content, re.DOTALL)
    check(match is not None, "Missing SKILL frontmatter")
    metadata = yaml.safe_load(match.group(1))
    check(metadata["name"] == SKILL.name, "Skill folder/name mismatch")
    check(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]) is not None, "Invalid skill name")
    description = metadata["description"]
    check(isinstance(description, str) and 0 < len(description) <= 1024, "Invalid description")
    check(metadata["license"] == "MIT", "License metadata mismatch")
    version = metadata["metadata"]["version"]
    check(isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+", version), "Invalid version")
    check(f"## {version}" in texts[ROOT / "CHANGELOG.md"], "Version missing in changelog")

    state = json.loads(texts[SKILL / "assets/templates/state.json"])
    required = {"schema_version", "skill_version", "project", "learner", "mode", "phase", "current",
                "return_points", "awaiting", "next_action", "focus_files", "journal", "open_loops",
                "pending_commit", "updated_at"}
    check(required <= state.keys(), "State fields missing")
    check(state["schema_version"] == 1 and state["skill_version"] == version, "State version mismatch")
    check(state["phase"] == "INIT" and state["mode"] == "learning", "Initial state mismatch")
    check(state["awaiting"] is None and state["pending_commit"] is None, "Fake pending learning")
    check(state["journal"]["next_sequence"] == 1 and state["journal"]["last_event"] is None, "Fake initial events")
    mastery = json.loads(texts[SKILL / "assets/templates/mastery.json"])
    concept = json.loads(texts[SKILL / "assets/templates/concept.json"])
    check(mastery["schema_version"] == 1 and mastery["concepts"] == [], "Fake initial mastery")
    check(type(concept["level"]) is int and 0 <= concept["level"] <= 6, "Invalid mastery level")
    check(type(concept["target"]) is int and 0 <= concept["target"] <= 6, "Invalid mastery target")
    check(concept["concept_id"] is None and concept["evidence"] == [], "Fake concept evidence")
    check(concept["last_checked"] is None and concept["review_due"] is None, "Fake review dates")

    ui = yaml.safe_load(texts[SKILL / "agents/openai.yaml"])
    check(25 <= len(ui["interface"]["short_description"]) <= 64, "Invalid UI description")
    check("$" + SKILL.name in ui["interface"]["default_prompt"], "Default prompt missing skill invocation")
    check(ui["policy"]["allow_implicit_invocation"] is True, "Implicit invocation disabled")

    if shutil.which("git"):
        git = subprocess.run(["git", "ls-files", "--cached", "-z"], cwd=ROOT,
                             capture_output=True, check=False)
        if git.returncode == 0:
            published = {path.relative_to(ROOT).as_posix() for path in files}
            tracked = set(filter(None, git.stdout.decode("utf-8").split("\0")))
            check(tracked <= published, "Unrelated staged/tracked files: " + ", ".join(sorted(tracked - published)))
    print(f"PASS: {len(files)} release files; UTF-8, JSON/YAML, {links} local links/anchors")
    print(f"PASS: skill {SKILL.name} v{version}, schema v1, UI and initial memory contracts")
    print("PASS: staged/tracked publication scope (when Git is available)")


if __name__ == "__main__":
    validate()
