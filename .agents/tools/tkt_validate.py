#!/usr/bin/env python3
"""Validate agent ticket folders without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from frontmatter_utils import LIST_FIELDS, load_frontmatter


KNOWN_ARTIFACTS = ("concept", "plan", "task", "report")
REQUIRED_FIELDS = ("id", "title", "artifact", "status", "created", "updated")
TICKET_RE = re.compile(r"^TKT-\d{3}$")
INDEX_ID_RE = re.compile(r"^\s*-\s+id:\s+(TKT-\d{3})\s*$", re.MULTILINE)
INDEX_PATH_RE = re.compile(r"\.agents/tasks/[^\s,\]\}]+")
SHARD_PATH_RE = re.compile(r"\.agents/tasks/indexes/TKT-\d{3}-\d{3}\.yaml")
ALLOWED_STATUSES = {"concept", "planning", "ready", "in_progress", "done", "blocked", "cancelled"}
ALLOWED_ARTIFACTS = {"concept", "plan", "task", "report", "update"}


class Outcome:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def main() -> int:
    root = (Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".agents/tasks")).resolve()
    repo_root = root.parent.parent if root.name == "tasks" and root.parent.name == ".agents" else root.parent
    outcome = Outcome()

    if not root.is_dir():
        outcome.error(f"tasks root does not exist: {root}")
        return finish(outcome)

    ticket_ids = validate_ticket_folders(root, outcome)
    validate_memory_frontmatter(repo_root / ".agents/memory", outcome)
    validate_optional_index(root, repo_root, ticket_ids, outcome)
    return finish(outcome)


def validate_ticket_folders(root: Path, outcome: Outcome) -> set[str]:
    ticket_ids: set[str] = set()

    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        if path.name == "indexes":
            continue

        ticket_id = path.name
        if not TICKET_RE.match(ticket_id):
            outcome.error(f"invalid ticket folder name: {path}")
            continue

        ticket_ids.add(ticket_id)
        validate_ticket_folder(path, ticket_id, outcome)

    return ticket_ids


def validate_ticket_folder(path: Path, ticket_id: str, outcome: Outcome) -> None:
    artifacts_found: set[str] = set()

    for artifact in KNOWN_ARTIFACTS:
        artifact_path = path / f"{artifact}.md"
        if artifact_path.exists():
            artifacts_found.add(artifact)
            validate_artifact(artifact_path, ticket_id, artifact, outcome)

    updates_dir = path / "updates"
    if updates_dir.exists():
        if not updates_dir.is_dir():
            outcome.error(f"updates path is not a directory: {updates_dir}")
        else:
            for update_path in sorted(updates_dir.glob("*.md")):
                validate_artifact(update_path, ticket_id, "update", outcome)

    if not artifacts_found:
        outcome.error(f"{ticket_id} has no lifecycle artifacts")
    elif "task" not in artifacts_found:
        outcome.warn(f"{ticket_id} has no task.md; valid for early concepts, but not executable")


def validate_artifact(path: Path, ticket_id: str, expected_artifact: str, outcome: Outcome) -> None:
    metadata, parse_errors = load_frontmatter(path)
    if parse_errors:
        for parse_error in parse_errors:
            outcome.error(parse_error.render())
        return

    if not metadata:
        outcome.error(f"missing YAML frontmatter: {path}")
        return

    for field in REQUIRED_FIELDS:
        if not metadata.get(field):
            outcome.error(f"missing `{field}` in {path}")

    if metadata.get("id") and metadata["id"] != ticket_id:
        outcome.error(f"id mismatch in {path}: expected {ticket_id}, got {metadata['id']}")

    if metadata.get("artifact") and metadata["artifact"] not in ALLOWED_ARTIFACTS:
        outcome.error(f"unsupported artifact value in {path}: {metadata['artifact']}")

    if metadata.get("artifact") and metadata["artifact"] != expected_artifact:
        outcome.error(
            f"artifact mismatch in {path}: expected {expected_artifact}, got {metadata['artifact']}"
        )

    if metadata.get("status") and metadata["status"] not in ALLOWED_STATUSES:
        outcome.warn(f"suspicious status value in {path}: {metadata['status']}")

    for field in LIST_FIELDS:
        value = metadata.get(field)
        if value is not None and not isinstance(value, list):
            outcome.error(f"field `{field}` must be a list in {path}")


def validate_memory_frontmatter(memory_root: Path, outcome: Outcome) -> None:
    if not memory_root.is_dir():
        return

    for category_dir in sorted(path for path in memory_root.iterdir() if path.is_dir()):
        for memory_path in sorted(category_dir.glob("*.md")):
            if memory_path.name == "index.md":
                continue
            metadata, parse_errors = load_frontmatter(memory_path)
            for parse_error in parse_errors:
                outcome.warn(parse_error.render())
            if not metadata:
                outcome.warn(f"memory file is missing YAML frontmatter: {memory_path}")
                continue
            if not metadata.get("id"):
                outcome.warn(f"memory file is missing `id`: {memory_path}")
            if not metadata.get("title"):
                outcome.warn(f"memory file is missing `title`: {memory_path}")


def validate_optional_index(root: Path, repo_root: Path, ticket_ids: set[str], outcome: Outcome) -> None:
    index_path = root / "index.yaml"
    if not index_path.exists():
        outcome.warn("index.yaml is missing; this is allowed because ticket folders are source of truth")
        return

    try:
        content = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        outcome.warn(f"cannot read optional index {index_path}: {exc}")
        return

    indexed_ids = set(INDEX_ID_RE.findall(content))

    if SHARD_PATH_RE.search(content):
        validate_sharded_index(root, repo_root, content, ticket_ids, outcome)
        return

    if not indexed_ids:
        outcome.warn("optional index.yaml has no recognizable ticket ids")

    for ticket_id in sorted(indexed_ids - ticket_ids):
        outcome.warn(f"optional index references missing ticket folder: {ticket_id}")

    for ticket_id in sorted(ticket_ids - indexed_ids):
        outcome.warn(f"optional index omits existing ticket folder: {ticket_id}")

    for raw_path in INDEX_PATH_RE.findall(content):
        normalized = raw_path.rstrip("/")
        path = resolve_index_path(repo_root, normalized)
        exists = path.is_dir() if raw_path.endswith("/") else path.exists()
        if not exists:
            outcome.warn(f"optional index references missing artifact path: {raw_path}")


def validate_sharded_index(root: Path, repo_root: Path, content: str, ticket_ids: set[str], outcome: Outcome) -> None:
    shard_paths = SHARD_PATH_RE.findall(content)
    if not shard_paths:
        outcome.warn("optional sharded index.yaml has no recognizable shard paths")
        return

    indexed_ids: set[str] = set()
    for raw_path in shard_paths:
        shard_path = resolve_index_path(repo_root, raw_path)
        if not shard_path.exists():
            outcome.warn(f"optional index references missing shard path: {raw_path}")
            continue
        try:
            shard_content = shard_path.read_text(encoding="utf-8")
        except OSError as exc:
            outcome.warn(f"cannot read optional shard {raw_path}: {exc}")
            continue
        indexed_ids.update(INDEX_ID_RE.findall(shard_content))
        for artifact_path in INDEX_PATH_RE.findall(shard_content):
            normalized = artifact_path.rstrip("/")
            path = resolve_index_path(repo_root, normalized)
            exists = path.is_dir() if artifact_path.endswith("/") else path.exists()
            if not exists:
                outcome.warn(f"optional shard references missing artifact path: {artifact_path}")

    for ticket_id in sorted(indexed_ids - ticket_ids):
        outcome.warn(f"optional shard index references missing ticket folder: {ticket_id}")

    for ticket_id in sorted(ticket_ids - indexed_ids):
        outcome.warn(f"optional shard indexes omit existing ticket folder: {ticket_id}")


def resolve_index_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def finish(outcome: Outcome) -> int:
    for warning in outcome.warnings:
        print(f"warning: {warning}", file=sys.stderr)

    if not outcome.errors:
        plural = "" if len(outcome.warnings) == 1 else "s"
        print(f"tkt_validate ok ({len(outcome.warnings)} warning{plural})")
        return 0

    for error in outcome.errors:
        print(f"error: {error}", file=sys.stderr)

    error_plural = "" if len(outcome.errors) == 1 else "s"
    warning_plural = "" if len(outcome.warnings) == 1 else "s"
    print(
        f"tkt_validate failed ({len(outcome.errors)} error{error_plural}, "
        f"{len(outcome.warnings)} warning{warning_plural})",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
