---
id: constitution
title: Agent constitution
type: principles
status: active
created: 2026-05-25
updated: 2026-05-25
tags:
  - principles
  - boundaries
  - safety
read_when:
  - changing repo-wide rules
  - making workflow decisions
  - deciding whether an implementation violates project boundaries
---

# Agent Constitution

## Principles

- Keep routing files short and explicit.
- Prefer canonical source files over generated indexes.
- Preserve useful context, not ceremony.
- Use the smallest artifact set that still helps future work.
- Keep examples generic unless the repository intentionally encodes domain rules.

## Rules

- Every durable memory file should start with YAML frontmatter.
- Every ticket artifact should start with YAML frontmatter.
- Read indexes first; do not scan entire trees by default.
- Do not create placeholder files just to satisfy structure.
- Regenerated indexes may be replaced at any time; they are not the source of truth.
