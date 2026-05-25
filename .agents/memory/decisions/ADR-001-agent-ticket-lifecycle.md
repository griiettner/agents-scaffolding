---
id: ADR-001
title: Agent ticket lifecycle
status: accepted
date: 2026-05-25
related_ticket: TKT-001
---

# ADR-001: Agent Ticket Lifecycle

## Decision

Use `.agents/tasks/TKT-XXX/` as the canonical store for ticket-specific context.

Ticket folders can be slim or full:

- Slim chore: `task.md`, plus `report.md` after completion when useful.
- Full ticket: `concept.md`, `plan.md`, `task.md`, `report.md`, and optional `updates/`.

Do not create placeholder artifacts just to satisfy structure.

## Rationale

Small chores should not pay a full process cost. Complex work still benefits from complete context from idea to report.

## Consequences

- Ticket folder contents are source of truth.
- `.agents/tasks/index.yaml`, when present, is helper metadata only.
- Later ticket-specific comments require explicit `TKT-XXX` and should create update files.
