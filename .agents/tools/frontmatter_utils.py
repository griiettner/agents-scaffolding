#!/usr/bin/env python3
"""Parse a small, explicit subset of YAML frontmatter."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FrontmatterError:
    path: Path
    message: str

    def render(self) -> str:
        return f"{self.path}: {self.message}"


LIST_FIELDS = {"dependencies", "areas", "skills", "tags", "read_when"}
SUPPORTED_FIELDS = {
    "id",
    "title",
    "type",
    "artifact",
    "status",
    "date",
    "related_ticket",
    "owner",
    "priority",
    "created",
    "updated",
    "dependencies",
    "areas",
    "skills",
    "tags",
    "read_when",
}


def load_frontmatter(path: Path) -> tuple[dict[str, object], list[FrontmatterError]]:
    if not path.exists():
        return {}, []

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [FrontmatterError(path, f"cannot read file: {exc}")]

    return parse_frontmatter_document(path, content)


def parse_frontmatter_document(path: Path, content: str) -> tuple[dict[str, object], list[FrontmatterError]]:
    if not content.startswith("---\n"):
        return {}, []

    end = content.find("\n---", 4)
    if end == -1:
        return {}, [FrontmatterError(path, "frontmatter starts with `---` but does not close")]

    return parse_frontmatter_block(path, content[4:end])


def parse_frontmatter_block(path: Path, frontmatter: str) -> tuple[dict[str, object], list[FrontmatterError]]:
    result: dict[str, object] = {}
    errors: list[FrontmatterError] = []
    current_list: str | None = None

    for line_number, raw_line in enumerate(frontmatter.splitlines(), start=2):
        if not raw_line.strip():
            continue

        if raw_line.startswith("  - "):
            if not current_list:
                errors.append(
                    FrontmatterError(path, f"line {line_number}: list item without a list field")
                )
                continue
            value = raw_line[4:].strip()
            if not value or ":" in value:
                errors.append(
                    FrontmatterError(
                        path,
                        f"line {line_number}: only scalar list items are supported in `{current_list}`",
                    )
                )
                continue
            result.setdefault(current_list, []).append(clean_scalar(value))
            continue

        current_list = None

        if raw_line.startswith(" "):
            errors.append(
                FrontmatterError(
                    path,
                    f"line {line_number}: nested mappings are not supported in scaffold frontmatter",
                )
            )
            continue

        key, separator, value = raw_line.partition(":")
        if not separator:
            errors.append(FrontmatterError(path, f"line {line_number}: expected `key: value`"))
            continue

        key = key.strip()
        value = value.strip()

        if key not in SUPPORTED_FIELDS:
            errors.append(FrontmatterError(path, f"line {line_number}: unsupported field `{key}`"))
            continue

        if key in LIST_FIELDS:
            parsed_list, list_errors = parse_list_value(path, line_number, key, value)
            errors.extend(list_errors)
            if not list_errors:
                result[key] = parsed_list
                if value == "":
                    current_list = key
            continue

        if value.startswith("[") or value.startswith("{"):
            errors.append(
                FrontmatterError(
                    path,
                    f"line {line_number}: structured values are not supported for scalar field `{key}`",
                )
            )
            continue

        result[key] = clean_scalar(value)

    return result, errors


def parse_list_value(
    path: Path, line_number: int, key: str, value: str
) -> tuple[list[str], list[FrontmatterError]]:
    if value == "":
        return [], []

    if value == "[]":
        return [], []

    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return [], []
        items = [part.strip() for part in inner.split(",")]
        if any(not item for item in items):
            return [], [FrontmatterError(path, f"line {line_number}: malformed inline list for `{key}`")]
        if any(":" in item for item in items):
            return [], [
                FrontmatterError(
                    path,
                    f"line {line_number}: only scalar inline list items are supported for `{key}`",
                )
            ]
        return [clean_scalar(item) for item in items], []

    return [], [
        FrontmatterError(
            path,
            (
                f"line {line_number}: unsupported list syntax for `{key}`; "
                "use `[]`, `[a, b]`, or block list items"
            ),
        )
    ]


def clean_scalar(value: str) -> str:
    return value.strip().strip("\"'")
