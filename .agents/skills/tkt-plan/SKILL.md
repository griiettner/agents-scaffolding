---
name: tkt-plan
description: "Create or refresh .agents/tasks/TKT-XXX/plan.md when a ticket needs planning. Use only when user explicitly invokes /tkt-plan."
disable-model-invocation: true
---

# /tkt-plan

Use the `tkt-management` skill.

Resolve `TKT-XXX` under `.agents/tasks/`, read existing ticket artifacts and relevant repo context, then write `.agents/tasks/TKT-XXX/plan.md` only when the work needs a decision-complete plan.

Rules:

- Do not create a plan placeholder.
- Ask only for product or implementation preferences that cannot be discovered from the repo.
- If updating an existing real plan, preserve intentional manual decisions unless the user asks for a rewrite.
- `index.yaml` may be refreshed if present, but ticket files remain source of truth.
