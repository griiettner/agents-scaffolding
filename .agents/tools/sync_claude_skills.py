#!/usr/bin/env python3
"""Generate Claude Code skill stubs from canonical .agents/skills files."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def main() -> int:
    repo = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")).resolve()
    source_root = repo / ".agents/skills"
    target_root = repo / ".claude/skills"

    if not source_root.is_dir():
        print(f"error: missing canonical skills root: {source_root}", file=sys.stderr)
        return 1

    if target_root.exists() and target_root.is_symlink():
        target_root.unlink()

    target_root.mkdir(parents=True, exist_ok=True)

    expected = set()

    for skill_dir in sorted(path for path in source_root.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        expected.add(skill_dir.name)
        target_dir = target_root / skill_dir.name
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "SKILL.md"
        target_file.write_text(render_stub(repo, skill_file), encoding="utf-8")

    for stale in sorted(path for path in target_root.iterdir() if path.is_dir()):
        if stale.name not in expected:
            shutil.rmtree(stale)

    print("synced Claude skill stubs")
    return 0


def render_stub(repo: Path, skill_file: Path) -> str:
    content = skill_file.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter(content)
    rel_path = skill_file.resolve().relative_to(repo).as_posix()

    body = [
        "# Claude Compatibility Stub",
        "",
        "This file exists so Claude Code can discover this project skill.",
        "",
        "Canonical skill content lives at:",
        "",
        f"- `{rel_path}`",
        "",
        "Read the canonical skill file before using this skill.",
        "",
        "Do not edit this stub manually. Regenerate it from the canonical `.agents/skills/` tree.",
        "",
    ]

    if frontmatter:
        return f"{frontmatter}\n\n" + "\n".join(body)
    return "\n".join(body)


def extract_frontmatter(content: str) -> str:
    if not content.startswith("---\n"):
        return ""
    end = content.find("\n---", 4)
    if end == -1:
        return ""
    return content[: end + 4]


if __name__ == "__main__":
    raise SystemExit(main())
