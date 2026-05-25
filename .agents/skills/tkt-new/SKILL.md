---
name: tkt-new
description: "Create a new agent ticket under .agents/tasks/. Use only when user explicitly invokes /tkt-new."
disable-model-invocation: true
---

# /tkt-new

Use the `tkt-management` skill.

Create the next `TKT-XXX` folder under `.agents/tasks/`.

Default to a slim ticket:

- `task.md` only when the work is already clear.
- `concept.md` + `task.md` when the idea needs a little framing.

Use full lifecycle files only when the work is complex, risky, multi-step, cross-file, or important future context.

Rules:

- Do not create placeholder artifacts.
- `index.yaml` is optional helper metadata, not source of truth.
- Report the new ticket path and chosen mode.
