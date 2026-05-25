---
id: ADR-002
title: Memory routing
status: accepted
date: 2026-05-25
related_ticket: TKT-001
---

# ADR-002: Memory Routing

## Decision

Use `.agents/memory/MEMORY.md` as a lightweight router. Store durable memory in indexed subfolders, and load memory files only when relevant to the current task.

Every durable memory `.md` file inside a memory category must start with YAML frontmatter. This lets sync tools build routing indexes without reading entire memory files. Generated `index.yaml` files and the top-level router `.agents/memory/MEMORY.md` are the exceptions.

## Rationale

The agent should not load architecture, principles, decisions, and all ticket history into initial context. Small indexes let agents discover relevant memory without paying the token cost for unrelated material.

## Consequences

- `MEMORY.md` should stay short.
- Subfolder `index.yaml` files describe available memories and when to read them.
- Durable memory `.md` files should be self-describing with frontmatter fields such as `id`, `title`, `type`, `status`, `created`, `updated`, `tags`, and `read_when`.
- Ticket-specific history stays in `.agents/tasks/TKT-XXX/`.
- Skills hold reusable procedures; memory holds stable project knowledge.
