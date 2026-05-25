#!/usr/bin/env python3
"""Regenerate helper indexes for agent tickets and memory."""

from __future__ import annotations

import sys
from pathlib import Path

from frontmatter_utils import FrontmatterError, load_frontmatter

ARTIFACTS = ("concept", "plan", "task", "report")
TASK_SHARD_SIZE = 25


def main() -> int:
    repo = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")).resolve()
    tasks_root = repo / ".agents/tasks"
    memory_root = repo / ".agents/memory"

    if not tasks_root.is_dir():
        print(f"error: missing tasks root: {tasks_root}", file=sys.stderr)
        return 1

    errors: list[FrontmatterError] = []

    sync_tasks_index(repo, tasks_root, errors)
    sync_memory_indexes(memory_root, errors)

    if errors:
        for error in errors:
            print(f"error: {error.render()}", file=sys.stderr)
        print(f"tkt_sync failed ({len(errors)} frontmatter error(s))", file=sys.stderr)
        return 1

    print("synced .agents task and memory indexes")
    return 0


def sync_tasks_index(repo: Path, tasks_root: Path, errors: list[FrontmatterError]) -> None:
    entries = []

    for ticket_dir in sorted(path for path in tasks_root.iterdir() if path.is_dir()):
        ticket_id = ticket_dir.name
        if not is_ticket_id(ticket_id):
            continue

        artifacts = existing_artifacts(repo, ticket_dir)
        primary = first_existing(ticket_dir, ("task", "concept", "plan", "report"))
        metadata = read_frontmatter(primary, errors) if primary else {}
        report_metadata = read_frontmatter(ticket_dir / "report.md", errors)

        title = metadata.get("title") or title_from_ticket_id(ticket_id)
        status = report_metadata.get("status") or metadata.get("status") or "planning"
        owner = metadata.get("owner") or "codex"
        created = metadata.get("created") or ""
        updated = newest_updated(ticket_dir) or metadata.get("updated") or created
        dependencies = metadata.get("dependencies", [])
        areas = metadata.get("areas", [])
        skills = metadata.get("skills", [])

        entries.append(
            {
                "id": ticket_id,
                "title": title,
                "status": status,
                "owner": owner,
                "priority": "normal",
                "created": created,
                "updated": updated,
                "artifacts": artifacts,
                "dependencies": dependencies,
                "areas": areas,
                "skills": skills,
            }
        )

    write_task_indexes(repo, tasks_root, entries)


def write_task_indexes(repo: Path, tasks_root: Path, entries: list[dict[str, object]]) -> None:
    indexes_dir = tasks_root / "indexes"
    indexes_dir.mkdir(exist_ok=True)

    expected_files = set()
    shards = []

    for start in range(1, max_ticket_number(entries) + 1, TASK_SHARD_SIZE):
        end = start + TASK_SHARD_SIZE - 1
        shard_entries = [
            entry
            for entry in entries
            if start <= ticket_number(str(entry["id"])) <= end
        ]
        if not shard_entries:
            continue

        shard_name = f"TKT-{start:03d}-{end:03d}.yaml"
        expected_files.add(shard_name)
        shard_path = indexes_dir / shard_name
        shard_path.write_text(render_tasks_index(shard_entries), encoding="utf-8")
        shards.append(build_shard_metadata(repo, start, end, shard_path, shard_entries))

    for stale in indexes_dir.glob("TKT-*.yaml"):
        if stale.name not in expected_files:
            stale.unlink()

    tasks_root.joinpath("index.yaml").write_text(render_task_router(shards), encoding="utf-8")


def sync_memory_indexes(memory_root: Path, errors: list[FrontmatterError]) -> None:
    if not memory_root.is_dir():
        return

    for category_dir in sorted(path for path in memory_root.iterdir() if path.is_dir()):
        memories = []
        for memory_file in sorted(category_dir.glob("*.md")):
            if memory_file.name == "index.md":
                continue
            metadata = read_frontmatter(memory_file, errors)
            memory_id = metadata.get("id") or memory_file.stem
            title = metadata.get("title") or title_from_slug(memory_file.stem)
            tags = metadata.get("tags", [])
            read_when = metadata.get("read_when", [])
            memories.append(
                {
                    "id": memory_id,
                    "title": title,
                    "file": memory_file.name,
                    "tags": tags,
                    "read_when": read_when,
                }
            )

        if memories:
            category_dir.joinpath("index.yaml").write_text(render_memory_index(memories), encoding="utf-8")


def existing_artifacts(repo: Path, ticket_dir: Path) -> dict[str, str]:
    artifacts = {}
    for artifact in ARTIFACTS:
        path = ticket_dir / f"{artifact}.md"
        if path.exists():
            artifacts[artifact] = relative_path(repo, path)
    updates_dir = ticket_dir / "updates"
    if updates_dir.is_dir():
        artifacts["updates"] = f"{relative_path(repo, updates_dir)}/"
    return artifacts


def first_existing(ticket_dir: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        path = ticket_dir / f"{name}.md"
        if path.exists():
            return path
    return None


def newest_updated(ticket_dir: Path) -> str:
    values = []
    updates_dir = ticket_dir / "updates"
    update_files = sorted(updates_dir.glob("*.md")) if updates_dir.is_dir() else []
    for path in sorted(ticket_dir.glob("*.md")) + update_files:
        metadata, frontmatter_errors = load_frontmatter(path)
        if frontmatter_errors:
            continue
        if metadata.get("updated"):
            values.append(str(metadata["updated"]))
    return max(values) if values else ""


def read_frontmatter(path: Path, errors: list[FrontmatterError]) -> dict[str, object]:
    metadata, frontmatter_errors = load_frontmatter(path)
    errors.extend(frontmatter_errors)
    return metadata


def render_tasks_index(entries: list[dict[str, object]]) -> str:
    lines = ["tickets:"]
    for entry in entries:
        lines.extend(
            [
                f"  - id: {entry['id']}",
                f"    title: {entry['title']}",
                f"    status: {entry['status']}",
                f"    owner: {entry['owner']}",
                f"    priority: {entry['priority']}",
                f"    created: {entry['created']}",
                f"    updated: {entry['updated']}",
                "    artifacts:",
            ]
        )
        for key, value in entry["artifacts"].items():
            lines.append(f"      {key}: {value}")
        render_list(lines, "dependencies", entry["dependencies"], indent="    ")
        render_list(lines, "areas", entry["areas"], indent="    ")
        render_list(lines, "skills", entry["skills"], indent="    ")
    return "\n".join(lines) + "\n"


def render_task_router(shards: list[dict[str, object]]) -> str:
    lines = []
    for shard in shards:
        lines.extend(
            [
                f"- range: {shard['range']}",
                f"  file: {shard['file']}",
                f"  count: {shard['count']}",
                f"  updated: {shard['updated']}",
                "  statuses:",
            ]
        )
        for status, count in shard["statuses"].items():
            lines.append(f"    - {status}: {count}")
        render_list(lines, "areas", shard["areas"], indent="  ")
    return "\n".join(lines) + "\n"


def render_memory_index(memories: list[dict[str, object]]) -> str:
    lines = ["memories:"]
    for memory in memories:
        lines.extend(
            [
                f"  - id: {memory['id']}",
                f"    title: {memory['title']}",
                f"    file: {memory['file']}",
            ]
        )
        render_list(lines, "tags", memory["tags"], indent="    ")
        render_list(lines, "read_when", memory["read_when"], indent="    ")
    return "\n".join(lines) + "\n"


def render_list(lines: list[str], key: str, values: object, indent: str) -> None:
    if isinstance(values, list) and values:
        lines.append(f"{indent}{key}:")
        for value in values:
            lines.append(f"{indent}  - {value}")
    else:
        lines.append(f"{indent}{key}: []")


def build_shard_metadata(
    repo: Path,
    start: int,
    end: int,
    shard_path: Path,
    entries: list[dict[str, object]],
) -> dict[str, object]:
    statuses: dict[str, int] = {}
    areas = set()
    updated_values = []

    for entry in entries:
        status = str(entry["status"])
        statuses[status] = statuses.get(status, 0) + 1
        if isinstance(entry["areas"], list):
            areas.update(str(area) for area in entry["areas"])
        if entry["updated"]:
            updated_values.append(str(entry["updated"]))

    return {
        "range": f"TKT-{start:03d}-{end:03d}",
        "file": relative_path(repo, shard_path),
        "count": len(entries),
        "updated": max(updated_values) if updated_values else "",
        "statuses": dict(sorted(statuses.items())),
        "areas": sorted(areas),
    }


def relative_path(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo).as_posix()


def max_ticket_number(entries: list[dict[str, object]]) -> int:
    numbers = [ticket_number(str(entry["id"])) for entry in entries]
    return max(numbers) if numbers else 0


def ticket_number(ticket_id: str) -> int:
    return int(ticket_id.split("-")[1])


def is_ticket_id(ticket_id: str) -> bool:
    return ticket_id.startswith("TKT-") and len(ticket_id) == 7 and ticket_id[4:].isdigit()


def title_from_ticket_id(ticket_id: str) -> str:
    return ticket_id


def title_from_slug(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


if __name__ == "__main__":
    raise SystemExit(main())
