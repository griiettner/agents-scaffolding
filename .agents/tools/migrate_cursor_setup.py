#!/usr/bin/env python3
"""Migrate local Cursor/Claude setup into the canonical .agents structure."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


MIGRATION_MARKER = "<!-- MIGRATED BY migrate_cursor_setup.py -->"
MEMORY_CATEGORIES = ("architecture", "decisions", "principles", "operations")
SKILL_SOURCE_DIRS = (
    ".cursor/commands",
    ".cursor/skills",
    ".cursor/prompts",
    ".claude/commands",
    ".claude/skills",
)
AGENT_SOURCE_DIRS = (
    ".cursor/agents",
    ".cursor/agent",
    ".claude/agents",
    ".claude/agent",
)
MEMORY_SOURCE_DIRS = (
    ".cursor/rules",
    ".cursor/memory",
    ".cursor/memories",
    ".cursor/context",
    ".claude/rules",
    ".claude/memory",
    ".claude/memories",
    ".claude/context",
)
SUPPORTED_EXTENSIONS = {".md", ".mdc", ".txt"}


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    rel_path: str
    stem: str
    frontmatter: dict[str, str]
    body: str
    title: str
    description: str


@dataclass(frozen=True)
class PlannedWrite:
    destination: Path
    content: str
    kind: str
    source: str
    confidence: str = "high"
    ambiguous_reason: str = ""


@dataclass
class MigrationReport:
    migrated: list[PlannedWrite] = field(default_factory=list)
    skipped: list[dict[str, str]] = field(default_factory=list)
    ambiguous: list[PlannedWrite] = field(default_factory=list)
    commands: list[dict[str, object]] = field(default_factory=list)


def main() -> int:
    args = parse_args()
    repo = resolve_repo(Path(args.repo))
    source = Path(args.source).expanduser().resolve()

    if not source.is_dir():
        print(f"error: source repo does not exist: {source}", file=sys.stderr)
        return 1
    if source == repo:
        print("error: source and target repo must be different paths", file=sys.stderr)
        return 1

    report = MigrationReport()
    writes = plan_migration(repo, source, report, force=args.force)
    writes.extend(plan_reports(repo, source, writes, report))

    if args.dry_run:
        print(render_console_summary(writes, report, dry_run=True))
        return 0

    apply_writes(writes, report, force=args.force)

    if not args.no_sync:
        run_maintenance(repo, source, report)

    print(render_console_summary(writes, report, dry_run=False))
    return 1 if any(command["returncode"] for command in report.commands) else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate local Cursor/Claude setup into this repository's .agents layout."
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Full path to the existing repository that contains .cursor and/or .claude configuration.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Target repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan the migration and print a summary without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files that were not created by this migrator.",
    )
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Do not run sync_claude_skills.py, tkt_sync.py, and tkt_validate.py after writing.",
    )
    return parser.parse_args()


def resolve_repo(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip()).resolve()
    return path.expanduser().resolve()


def plan_migration(repo: Path, source: Path, report: MigrationReport, *, force: bool) -> list[PlannedWrite]:
    writes: list[PlannedWrite] = []
    seen_sources: set[Path] = set()

    for doc in discover_docs(source, SKILL_SOURCE_DIRS, seen_sources):
        writes.extend(plan_skill(repo, doc, force=force, report=report))

    for doc in discover_docs(source, AGENT_SOURCE_DIRS, seen_sources):
        writes.extend(plan_agent(repo, doc, force=force, report=report))

    for doc in discover_docs(source, MEMORY_SOURCE_DIRS, seen_sources):
        writes.extend(plan_memory(repo, doc, force=force, report=report))

    return writes


def discover_docs(source: Path, source_dirs: tuple[str, ...], seen_sources: set[Path]) -> list[SourceDoc]:
    docs: list[SourceDoc] = []

    for raw_dir in source_dirs:
        root = source / raw_dir
        if not root.is_dir():
            continue
        for path in sorted(file for file in root.rglob("*") if file.is_file()):
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            resolved = path.resolve()
            if resolved in seen_sources:
                continue
            seen_sources.add(resolved)
            docs.append(load_source_doc(source, path))

    return docs


def load_source_doc(source: Path, path: Path) -> SourceDoc:
    content = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(content)
    rel_path = path.resolve().relative_to(source).as_posix()
    title = extract_title(body) or frontmatter.get("name") or frontmatter.get("description") or path.stem
    description = frontmatter.get("description") or first_sentence(body) or title
    return SourceDoc(
        path=path,
        rel_path=rel_path,
        stem=path.stem,
        frontmatter=frontmatter,
        body=body.strip(),
        title=title.strip(),
        description=description.strip(),
    )


def split_frontmatter(content: str) -> tuple[dict[str, str], str]:
    if not content.startswith("---\n"):
        return {}, content

    end = content.find("\n---", 4)
    if end == -1:
        return {}, content

    frontmatter: dict[str, str] = {}
    for raw_line in content[4:end].splitlines():
        key, separator, value = raw_line.partition(":")
        if not separator:
            continue
        clean_key = key.strip()
        clean_value = value.strip().strip("\"'")
        if clean_key and clean_value and not clean_value.startswith("["):
            frontmatter[clean_key] = clean_value
    return frontmatter, content[end + 4 :].lstrip()


def plan_skill(repo: Path, doc: SourceDoc, *, force: bool, report: MigrationReport) -> list[PlannedWrite]:
    source_system = detect_source_system(doc.rel_path)
    skill_name = slugify(doc.frontmatter.get("name") or doc.stem)
    skill_dir = repo / ".agents" / "skills" / skill_name
    skill_file = skill_dir / "SKILL.md"
    agent_file = skill_dir / "agents" / "openai.yaml"
    description = compact(doc.description, 180)
    body = doc.body or f"# {display_name(skill_name)}\n\n{description}"

    skill_content = "\n".join(
        [
            "---",
            f"name: {skill_name}",
            f"description: {quote_yaml(description)}",
            "---",
            "",
            MIGRATION_MARKER,
            f"<!-- source: {doc.rel_path} -->",
            f"<!-- source_system: {source_system} -->",
            "",
            normalize_heading(body, display_name(skill_name)),
            "",
        ]
    )
    agent_content = "\n".join(
        [
            f"# {MIGRATION_MARKER}",
            f"# source: {doc.rel_path}",
            f"# source_system: {source_system}",
            "interface:",
            f"  display_name: {quote_yaml(display_name(skill_name))}",
            f"  short_description: {quote_yaml(compact(description, 120))}",
            f"  default_prompt: {quote_yaml(f'Use ${skill_name} in this repository.')}",
            "policy:",
            "  allow_implicit_invocation: false",
            "",
        ]
    )

    writes = [
        PlannedWrite(skill_file, skill_content, "skill", doc.rel_path),
        PlannedWrite(agent_file, agent_content, "skill-agent-metadata", doc.rel_path),
    ]
    return filter_existing(writes, report, force=force)


def plan_agent(repo: Path, doc: SourceDoc, *, force: bool, report: MigrationReport) -> list[PlannedWrite]:
    source_system = detect_source_system(doc.rel_path)
    agent_id = slugify(doc.frontmatter.get("name") or doc.stem)
    destination = repo / ".agents" / "agents" / f"{agent_id}.md"
    today = date.today().isoformat()
    content = "\n".join(
        [
            "---",
            f"id: {agent_id}",
            f"title: {quote_yaml(display_name(agent_id))}",
            "type: agent",
            "status: active",
            f"created: {today}",
            f"updated: {today}",
            "tags:",
            "  - imported",
            f"  - {source_system}",
            "---",
            "",
            MIGRATION_MARKER,
            f"<!-- source: {doc.rel_path} -->",
            f"<!-- source_system: {source_system} -->",
            "",
            normalize_heading(doc.body, display_name(agent_id)),
            "",
        ]
    )
    return filter_existing([PlannedWrite(destination, content, "agent", doc.rel_path)], report, force=force)


def plan_memory(repo: Path, doc: SourceDoc, *, force: bool, report: MigrationReport) -> list[PlannedWrite]:
    source_system = detect_source_system(doc.rel_path)
    category, confidence, reason = classify_memory(doc)
    memory_id = slugify(doc.frontmatter.get("id") or doc.stem)
    destination = repo / ".agents" / "memory" / category / f"{memory_id}.md"
    today = date.today().isoformat()
    tags = ["imported", source_system, category]
    body = render_memory_body(doc, category=category, confidence=confidence, reason=reason)
    content = "\n".join(
        [
            "---",
            f"id: {memory_id}",
            f"title: {quote_yaml(doc.title)}",
            f"type: {category}",
            "status: active",
            f"created: {today}",
            f"updated: {today}",
            "tags:",
            *[f"  - {tag}" for tag in tags],
            "read_when:",
            f"  - reviewing imported {source_system} context from {doc.rel_path}",
            "---",
            "",
            MIGRATION_MARKER,
            f"<!-- source: {doc.rel_path} -->",
            f"<!-- source_system: {source_system} -->",
            "",
            body,
            "",
        ]
    )
    write = PlannedWrite(destination, content, "memory", doc.rel_path, confidence, reason)
    filtered = filter_existing([write], report, force=force)
    if filtered and confidence != "high":
        report.ambiguous.append(write)
    return filtered


def classify_memory(doc: SourceDoc) -> tuple[str, str, str]:
    text = f"{doc.rel_path}\n{doc.title}\n{doc.description}\n{doc.body}".lower()
    scores = {
        "decisions": count_matches(text, ("adr", "decision", "decided", "rationale", "tradeoff")),
        "principles": count_matches(
            text,
            ("rule", "principle", "boundary", "must", "never", "always", "policy", "security"),
        ),
        "operations": count_matches(
            text,
            ("command", "run ", "workflow", "deploy", "release", "maintenance", "debug", "incident"),
        ),
        "architecture": count_matches(
            text,
            ("architecture", "structure", "routing", "component", "service", "system", "data flow"),
        ),
    }
    category = max(MEMORY_CATEGORIES, key=lambda candidate: scores[candidate])
    best = scores[category]
    tied = [name for name, score in scores.items() if score == best]

    if best == 0:
        return "architecture", "low", "no strong category keywords found"
    if len(tied) > 1:
        return category, "medium", f"category tie: {', '.join(sorted(tied))}"
    return category, "high", ""


def render_memory_body(doc: SourceDoc, *, category: str, confidence: str, reason: str) -> str:
    summary = compact(first_paragraph(doc.body) or doc.description or doc.title, 360)
    lines = [
        f"# {doc.title}",
        "",
        "## Digest",
        "",
        f"- Category: `{category}`",
        f"- Classification confidence: `{confidence}`",
    ]
    if reason:
        lines.append(f"- Review note: {reason}")
    lines.extend(
        [
            f"- Source: `{doc.rel_path}`",
            "",
            "## Durable Memory",
            "",
            summary,
            "",
            "## Imported Source",
            "",
            doc.body.strip() or doc.description,
        ]
    )
    return "\n".join(lines)


def plan_reports(repo: Path, source: Path, writes: list[PlannedWrite], report: MigrationReport) -> list[PlannedWrite]:
    report_dir = repo / ".agents" / "migrations"
    markdown = report_dir / "cursor-migration-report.md"
    manifest = report_dir / "cursor-migration-manifest.json"
    migrated_for_report = report.migrated + writes
    markdown_content = render_report_markdown(repo, source, migrated_for_report, report)
    manifest_content = render_manifest_json(repo, source, migrated_for_report, report)
    return [
        PlannedWrite(markdown, markdown_content, "migration-report", str(source)),
        PlannedWrite(manifest, manifest_content, "migration-manifest", str(source)),
    ]


def render_report_markdown(repo: Path, source: Path, writes: list[PlannedWrite], report: MigrationReport) -> str:
    lines = [
        "# Cursor/Claude Migration Report",
        "",
        MIGRATION_MARKER,
        "",
        f"- Source: `{source}`",
        f"- Target: `{repo}`",
        f"- Generated: `{date.today().isoformat()}`",
        f"- Planned writes: `{len(writes)}`",
        f"- Skipped: `{len(report.skipped)}`",
        f"- Ambiguous: `{len(report.ambiguous)}`",
        "",
        "## Migrated",
        "",
    ]
    if writes:
        for write in sorted(writes, key=lambda item: str(item.destination)):
            lines.append(f"- `{write.kind}` `{relative_to_repo(repo, write.destination)}` from `{write.source}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Skipped", ""])
    if report.skipped:
        for skipped in report.skipped:
            lines.append(f"- `{skipped['destination']}` from `{skipped['source']}`: {skipped['reason']}")
    else:
        lines.append("- None")

    lines.extend(["", "## Ambiguous", ""])
    if report.ambiguous:
        for write in report.ambiguous:
            lines.append(
                f"- `{relative_to_repo(repo, write.destination)}` from `{write.source}`: "
                f"{write.ambiguous_reason or 'review recommended'}"
            )
    else:
        lines.append("- None")

    lines.extend(["", "## Maintenance Commands", ""])
    if report.commands:
        for command in report.commands:
            lines.append(
                f"- `{' '.join(str(part) for part in command['argv'])}` -> "
                f"`{command['returncode']}`"
            )
    else:
        lines.append("- Not run yet")

    return "\n".join(lines) + "\n"


def render_manifest_json(repo: Path, source: Path, writes: list[PlannedWrite], report: MigrationReport) -> str:
    payload = {
        "migration_marker": MIGRATION_MARKER,
        "source": str(source),
        "target": str(repo),
        "generated": date.today().isoformat(),
        "migrated": [
            {
                "kind": write.kind,
                "destination": relative_to_repo(repo, write.destination),
                "source": write.source,
                "confidence": write.confidence,
                "ambiguous_reason": write.ambiguous_reason,
            }
            for write in sorted(writes, key=lambda item: str(item.destination))
        ],
        "skipped": report.skipped,
        "ambiguous": [
            {
                "destination": relative_to_repo(repo, write.destination),
                "source": write.source,
                "reason": write.ambiguous_reason,
            }
            for write in report.ambiguous
        ],
        "commands": report.commands,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def filter_existing(writes: list[PlannedWrite], report: MigrationReport, *, force: bool) -> list[PlannedWrite]:
    planned: list[PlannedWrite] = []
    for write in writes:
        if write.destination.exists() and not force and not is_migrated_file(write.destination):
            report.skipped.append(
                {
                    "destination": str(write.destination),
                    "source": write.source,
                    "reason": "destination exists and is not migrator-owned; rerun with --force to overwrite",
                }
            )
            continue
        planned.append(write)
    return planned


def apply_writes(writes: list[PlannedWrite], report: MigrationReport, *, force: bool) -> None:
    for write in writes:
        if write.destination.exists() and not force and not is_migrated_file(write.destination):
            report.skipped.append(
                {
                    "destination": str(write.destination),
                    "source": write.source,
                    "reason": "destination appeared before write and is not migrator-owned",
                }
            )
            continue
        write.destination.parent.mkdir(parents=True, exist_ok=True)
        write.destination.write_text(write.content, encoding="utf-8")
        report.migrated.append(write)


def run_maintenance(repo: Path, source: Path, report: MigrationReport) -> None:
    commands = [
        ["python3", ".agents/tools/sync_claude_skills.py"],
        ["python3", ".agents/tools/tkt_sync.py"],
        ["python3", ".agents/tools/tkt_validate.py", ".agents/tasks"],
    ]
    for argv in commands:
        result = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
        report.commands.append(
            {
                "argv": argv,
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
        )

    report_writes = plan_reports(repo, source, [], report)
    for write in report_writes:
        write.destination.parent.mkdir(parents=True, exist_ok=True)
        write.destination.write_text(write.content, encoding="utf-8")


def render_console_summary(writes: list[PlannedWrite], report: MigrationReport, *, dry_run: bool) -> str:
    action = "planned" if dry_run else "migrated"
    failed = [command for command in report.commands if command["returncode"]]
    lines = [
        f"cursor/claude migration {action}",
        f"writes: {len(writes)}",
        f"skipped: {len(report.skipped)}",
        f"ambiguous: {len(report.ambiguous)}",
    ]
    if failed:
        lines.append(f"maintenance failures: {len(failed)}")
    return "\n".join(lines)


def is_migrated_file(path: Path) -> bool:
    try:
        return MIGRATION_MARKER in path.read_text(encoding="utf-8")
    except OSError:
        return False


def extract_title(body: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def first_sentence(body: str) -> str:
    paragraph = first_paragraph(body)
    match = re.search(r"(.+?[.!?])(?:\s|$)", paragraph)
    return match.group(1) if match else paragraph


def first_paragraph(body: str) -> str:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body.strip()) if part.strip()]
    for paragraph in paragraphs:
        if not paragraph.startswith("#"):
            return " ".join(paragraph.split())
    return ""


def normalize_heading(body: str, fallback_title: str) -> str:
    clean = body.strip()
    if not clean:
        return f"# {fallback_title}"
    if clean.startswith("#"):
        return clean
    return f"# {fallback_title}\n\n{clean}"


def compact(value: str, limit: int) -> str:
    normalized = " ".join(value.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def count_matches(text: str, needles: tuple[str, ...]) -> int:
    return sum(text.count(needle) for needle in needles)


def slugify(raw: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", raw.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "imported"


def display_name(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def relative_to_repo(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo).as_posix()
    except ValueError:
        return str(path)


def detect_source_system(rel_path: str) -> str:
    if rel_path.startswith(".cursor/"):
        return "cursor"
    if rel_path.startswith(".claude/"):
        return "claude"
    return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
