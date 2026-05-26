#!/usr/bin/env python3
"""Ensure the current repository has an exact trusted Codex project entry."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def resolve_repo_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return start.resolve()


def codex_config_path() -> Path:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    return codex_home / "config.toml"


def toml_basic_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def project_header(project_path: Path) -> str:
    return f'[projects."{toml_basic_string(str(project_path))}"]'


def find_section(lines: list[str], header: str) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if line.strip() == header:
            start = index
            break
    if start is None:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            end = index
            break
    return start, end


def section_is_trusted(lines: list[str], section: tuple[int, int]) -> bool:
    start, end = section
    for line in lines[start + 1 : end]:
        if line.strip() == 'trust_level = "trusted"':
            return True
    return False


def ensure_trusted(config_path: Path, project_path: Path) -> bool:
    header = project_header(project_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    text = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    lines = text.splitlines()

    section = find_section(lines, header)
    if section is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([header, 'trust_level = "trusted"'])
        config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return True

    if section_is_trusted(lines, section):
        return False

    start, end = section
    trust_index = None
    for index in range(start + 1, end):
        if lines[index].strip().startswith("trust_level"):
            trust_index = index
            break

    if trust_index is None:
        lines.insert(start + 1, 'trust_level = "trusted"')
    else:
        lines[trust_index] = 'trust_level = "trusted"'

    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def is_trusted(config_path: Path, project_path: Path) -> bool:
    if not config_path.exists():
        return False
    lines = config_path.read_text(encoding="utf-8").splitlines()
    section = find_section(lines, project_header(project_path))
    return section is not None and section_is_trusted(lines, section)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or add the exact Codex trust entry for this repository."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to trust. Defaults to the current directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check trust state. Exit 0 when trusted, 1 when not trusted.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_path = resolve_repo_root(Path(args.path))
    config_path = codex_config_path()

    if args.check:
        if is_trusted(config_path, project_path):
            print(f"trusted: {project_path}")
            return 0
        print(f"not trusted: {project_path}")
        print(f"config: {config_path}")
        return 1

    changed = ensure_trusted(config_path, project_path)
    action = "trusted" if changed else "already trusted"
    print(f"{action}: {project_path}")
    print(f"config: {config_path}")
    if changed:
        print("restart required: start a fresh Codex session at this repository root")
    return 0


if __name__ == "__main__":
    sys.exit(main())
