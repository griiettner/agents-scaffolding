---
id: TKT-001
title: Establish agent scaffolding
artifact: task
status: done
owner: repo-agent
created: 2026-05-25
updated: 2026-05-25
dependencies: []
areas:
  - AGENTS.md
  - .agents/memory
  - .agents/tasks
  - .agents/tools
  - README.md
skills:
  - tkt-management
---

# TKT-001 Task: Establish agent scaffolding

## Goal

Create a generic repository scaffold that can be cloned and adapted by other projects that want structured agent context.

## Scope

- Add lightweight routing files.
- Add durable memory examples.
- Add reusable task-management skills.
- Add at least one full ticket example and one slim ticket example.
- Add documentation explaining how to adapt the scaffold.

## Out of Scope

- Product-specific implementation details.
- Tooling that depends on a single framework or vendor.
- Large example histories that make the scaffold noisy.

## Verification

- `python3 .agents/tools/tkt_sync.py`
- `python3 .agents/tools/tkt_validate.py .agents/tasks`
- Review for generic naming and reusable examples
