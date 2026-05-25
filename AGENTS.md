# Agents Context

This file is the lightweight boot context for agents. Use it as a routing map, not as the full project memory.

## Project Summary

This repository is a generic scaffold for organizing agent-friendly project context.

It demonstrates a minimal but scalable pattern built around:

- `AGENTS.md` as the boot router
- `.agents/memory/` for durable knowledge
- `.agents/skills/` for reusable procedures
- `.agents/tasks/` for ticket or work-unit history
- YAML frontmatter and generated `index.yaml` files for cheap routing

Replace the examples with your own project context after cloning.

## Context Routing

- Task or ticket work: read `.agents/tasks/index.yaml` only to choose the relevant shard, then read the specific `.agents/tasks/TKT-XXX/` folder.
- Ticket workflow rules: read `.agents/skills/tkt-management/SKILL.md`.
- Durable memory router: read `.agents/memory/MEMORY.md`.
- Architecture context: read `.agents/memory/architecture/index.yaml` first.
- Durable decisions: read `.agents/memory/decisions/index.yaml` first.
- Project principles: read `.agents/memory/principles/index.yaml` first.

Only load files relevant to the current task.

## Boundaries

- Do not treat this scaffold's example files as product truth after cloning.
- Replace example owners, areas, constraints, and decisions with repo-specific values.
- Keep routing files short; do not turn `AGENTS.md` or `MEMORY.md` into dump files.
- Do not erase unrelated user changes.

## Repo Conventions

- Prefer `rg` and `rg --files` for searches.
- Use YAML frontmatter in durable memory files and task artifacts.
- Keep frontmatter to the scaffold's supported subset: scalars, `[]`, inline scalar lists, and block scalar lists.
- Read indexes first, then the smallest relevant file set.
- Keep helper indexes regenerable from canonical files.
- Validate ticket structure with `python3 .agents/tools/tkt_validate.py .agents/tasks`.
- Regenerate helper indexes with `python3 .agents/tools/tkt_sync.py`.
