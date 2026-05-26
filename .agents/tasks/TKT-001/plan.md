---
id: TKT-001
title: Establish agent scaffolding
artifact: plan
status: done
owner: repo-agent
created: 2026-05-25
updated: 2026-05-25
dependencies: []
areas:
  - AGENT.md
  - .agents/memory
  - .agents/tasks
  - .agents/tools
skills:
  - tkt-management
---

# TKT-001 Plan: Establish agent scaffolding

## Summary

Build a generic repository scaffold that shows how to separate routing, memory, reusable procedures, and ticket history without tying the structure to a specific product or stack.

## Decisions

- Keep `AGENT.md` short and route-focused.
- Keep `MEMORY.md` short and route-focused.
- Use YAML frontmatter for durable memory files and task artifacts.
- Use generated `index.yaml` files as helper metadata only.
- Include one full ticket example and one slim ticket example.

## Deliverables

- Generic `AGENT.md`
- Generic memory examples under `.agents/memory/`
- Task workflow skills under `.agents/skills/`
- Example tickets under `.agents/tasks/`
- Sync and validation scripts under `.agents/tools/`
- Top-level `README.md`

## Verification

- `python3 .agents/tools/tkt_sync.py`
- `python3 .agents/tools/tkt_validate.py .agents/tasks`
- Manual review that no product-specific references remain in the examples
