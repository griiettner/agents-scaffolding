---
name: tkt-exec
description: "Execute a ticket from .agents/tasks/TKT-XXX/task.md and preserve completion context. Use only when user explicitly invokes /tkt-exec."
disable-model-invocation: true
---

# /tkt-exec

Use the `tkt-management` skill.

Resolve `TKT-XXX` under `.agents/tasks/`, read `task.md`, and execute directly or through the owner agent.

Completion is not optional:

1. Run verification from `task.md`.
2. Answer the `tkt-management` Completion Gate.
3. Create or update `report.md` when the result is useful future context.
4. If this is post-completion work, create `updates/YYYY-MM-DD-<slug>.md` and link it from `report.md`.
5. Refresh helper indexes only if they are currently maintained; never treat them as source of truth.

Do not commit, push, or open PRs.
