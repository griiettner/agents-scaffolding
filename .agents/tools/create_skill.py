#!/usr/bin/env python3
"""Create a canonical project skill and refresh generated adapters."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


MAX_NAME_LENGTH = 64


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    skill_name = normalize_name(args.name)
    validate_name(skill_name)

    skill_dir = repo / ".agents" / "skills" / skill_name
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"

    if skill_file.exists() and not args.force:
        raise SystemExit(f"error: skill already exists: {skill_file}")

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(
        render_skill(
            name=skill_name,
            description=args.description,
            title=args.title or display_name(skill_name),
        ),
        encoding="utf-8",
    )

    if not args.no_openai:
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.write_text(
            render_openai_yaml(
                name=skill_name,
                description=args.description,
                title=args.title or display_name(skill_name),
            ),
            encoding="utf-8",
        )

    if not args.no_sync:
        run(repo, "python3", ".agents/tools/sync_claude_skills.py")

    print(f"created skill: .agents/skills/{skill_name}/SKILL.md")
    if not args.no_openai:
        print(f"created Codex metadata: .agents/skills/{skill_name}/agents/openai.yaml")
    if not args.no_sync:
        print("synced Claude stubs")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a project-local agent skill.")
    parser.add_argument("name", help="Skill name; normalized to lowercase kebab-case")
    parser.add_argument("description", help="Skill discovery description")
    parser.add_argument("--title", help="Human-readable heading/display name")
    parser.add_argument("--repo", default=".", help="Repository root")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing skill")
    parser.add_argument("--no-openai", action="store_true", help="Do not create agents/openai.yaml")
    parser.add_argument("--no-sync", action="store_true", help="Do not refresh generated adapters")
    return parser.parse_args()


def normalize_name(raw_name: str) -> str:
    normalized = raw_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized


def validate_name(name: str) -> None:
    if not name:
        raise SystemExit("error: skill name must contain at least one letter or digit")
    if len(name) > MAX_NAME_LENGTH:
        raise SystemExit(f"error: skill name must be {MAX_NAME_LENGTH} characters or fewer")


def render_skill(*, name: str, description: str, title: str) -> str:
    return "\n".join(
        [
            "---",
            f"name: {name}",
            f"description: {quote_yaml(description)}",
            "---",
            "",
            f"# {title}",
            "",
            "## Purpose",
            "",
            description,
            "",
            "## Workflow",
            "",
            "1. Read `AGENT.md`.",
            "2. Gather only the context needed for the requested work.",
            "3. Follow this skill's workflow and keep changes scoped.",
            "4. Run relevant validation before reporting completion.",
            "",
            "## Output",
            "",
            "- State what changed.",
            "- Report validation performed.",
            "- Call out unresolved follow-up or risk.",
            "",
        ]
    )


def render_openai_yaml(*, name: str, description: str, title: str) -> str:
    return "\n".join(
        [
            "interface:",
            f"  display_name: {quote_yaml(title)}",
            f"  short_description: {quote_yaml(short_description(description))}",
            f"  default_prompt: {quote_yaml(f'Use ${name} in this repository.')}",
            "policy:",
            "  allow_implicit_invocation: false",
            "",
        ]
    )


def run(repo: Path, *command: str) -> None:
    subprocess.run(command, cwd=repo, check=True)


def display_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def short_description(description: str) -> str:
    normalized = " ".join(description.split())
    return normalized if len(normalized) <= 120 else normalized[:117].rstrip() + "..."


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


if __name__ == "__main__":
    raise SystemExit(main())
