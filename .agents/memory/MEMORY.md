# Memory Router

This file is the lightweight entrypoint for durable memory. Do not load every memory file by default.

Use the current task to choose the smallest relevant index:

- Architecture context: `.agents/memory/architecture/index.yaml`
- Durable decisions and ADRs: `.agents/memory/decisions/index.yaml`
- Operational runbooks and recurring workflows: `.agents/memory/operations/index.yaml`
- Project principles and non-negotiables: `.agents/memory/principles/index.yaml`
- Ticket history: load the relevant `.agents/tasks/TKT-XXX/` folder directly

Rules:

- Read an index first, then open only the memory files relevant to the task.
- Durable memory `.md` files inside category folders should have YAML frontmatter for sync and indexing.
- Ticket folders are the source of truth for ticket-specific history.
- `index.yaml` files are routing aids, not canonical truth.
- Skills hold reusable procedures; memory holds stable project knowledge.
