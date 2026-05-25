---
name: tkt-update
description: "Record a later ticket-specific comment, fix, improvement, or regression update. Use only when user explicitly invokes /tkt-update."
disable-model-invocation: true
---

# /tkt-update

Use the `tkt-management` skill.

Only create an update when the user explicitly references `TKT-XXX` or the command argument resolves one.

Write `.agents/tasks/TKT-XXX/updates/YYYY-MM-DD-<slug>.md`, then add the update link to the ticket's `report.md` `## Updates` section in reverse chronological order. If `report.md` does not exist yet, create a concise one.

Capture:

- trigger
- changed files or affected behavior
- failure or edge case observed
- fix or decision made
- validation performed
- remaining follow-up
