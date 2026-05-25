---
name: tkt-task
description: "Legacy alias; prefer tkt-new, tkt-plan, or tkt-exec. Use only when user explicitly invokes /tkt-task."
disable-model-invocation: true
---

# /tkt-task

This command is deprecated as a standalone workflow.

Use:

- `/tkt-new` to create a slim or full ticket.
- `/tkt-plan` when a ticket genuinely needs a decision-complete plan.
- `/tkt-exec` to execute from `task.md` and preserve completion context.

Do not create `task.md` as a placeholder.
