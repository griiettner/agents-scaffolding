---
name: plan-exec
description: "Legacy alias for executing tickets; prefer tkt-exec. Use only when user explicitly invokes /plan-exec."
disable-model-invocation: true
---

# /plan-exec

This command is legacy. Use `/tkt-exec <ticket-number>` for canonical ticket execution.

If invoked anyway:

1. Resolve `TKT-XXX` under `.agents/tasks/`.
2. If `.agents/tasks/TKT-XXX/task.md` exists, tell the user to run `/tkt-exec TKT-XXX`.
3. Do not execute from legacy task paths.
4. Do not write reports into memory folders.
