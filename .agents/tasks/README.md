# Agent Tasks

This directory is the canonical ticket lifecycle store for agents.

Load only the specific ticket folder needed for the current work. `.agents/tasks/index.yaml`, when present, is a shard router and not the source of truth.

Use `.agents/tasks/index.yaml` only to choose the relevant shard under `.agents/tasks/indexes/`. Do not read every shard.

Ticket folders may be slim or full. Slim chores can have only `task.md` plus a useful `report.md` after completion. Complex tickets can use the full lifecycle:

- `concept.md` - initial idea, motivation, rough scope, and unknowns.
- `plan.md` - decision-complete plan.
- `task.md` - executable agent contract.
- `report.md` - stable completion report optimized for future agent context.
- `updates/` - later ticket-specific fixes, improvements, comments, or regressions.

Do not create placeholder artifacts just to fill the structure.

Validate ticket structure with:

```bash
python3 .agents/tools/tkt_sync.py
python3 .agents/tools/tkt_validate.py .agents/tasks
```
