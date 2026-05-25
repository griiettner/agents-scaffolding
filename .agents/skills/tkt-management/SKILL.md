---
name: tkt-management
description: Manage agent tickets under .agents/tasks/. Use when creating, planning, executing, reporting, updating, validating, migrating, or referencing any TKT-XXX lifecycle artifact.
---

# TKT Management

This skill owns the agent-ticket lifecycle. Keep the system useful, not ceremonial.

## Canonical Store

Ticket context lives under `.agents/tasks/TKT-XXX/`. Ticket folder contents are the source of truth.

`.agents/tasks/index.yaml`, when present, is only a helper router. It is not canonical and may be regenerated or corrected from ticket folders. Agents should use it to choose the relevant shard, then read only that shard and the specific ticket files needed.

Legacy task paths are migration-only references if your repo still has them. Do not create new ticket context outside `.agents/tasks/`.

## Ticket Modes

Use the smallest mode that preserves useful future context.

### Slim Chore

Use for small, low-risk, localized work.

```txt
.agents/tasks/TKT-009/
  task.md
  report.md      # after completion, only when future context is useful
```

### Full Ticket

Use for complex, risky, multi-step, cross-file, or future-reference-heavy work.

```txt
.agents/tasks/TKT-010/
  concept.md
  plan.md
  task.md
  report.md
  updates/
```

Do not create placeholder artifacts just to satisfy structure. Missing `plan.md` or `report.md` is valid when the ticket has not needed that artifact yet.

## Artifacts

- `concept.md`: initial idea, user problem, rough scope, unknowns, and success criteria.
- `plan.md`: decision-complete plan that leaves no implementation choices open.
- `task.md`: executable contract for the owner agent, including inputs, constraints, checklist, and verification.
- `report.md`: concise completion summary optimized for future agent retrieval.
- `updates/YYYY-MM-DD-<slug>.md`: later ticket-specific comments, fixes, improvements, regressions, or follow-ups.

Every existing artifact starts with YAML frontmatter:

```yaml
---
id: TKT-010
title: Short title
artifact: task
status: ready
owner: repo-agent
created: 2026-05-25
updated: 2026-05-25
---
```

Allowed `artifact` values: `concept`, `plan`, `task`, `report`, `update`.
Allowed `status` values: `concept`, `planning`, `ready`, `in_progress`, `done`, `blocked`, `cancelled`.

## Lifecycle

1. **New**: create `TKT-XXX/` and at least `task.md` or `concept.md`.
2. **Plan**: create `plan.md` only when the work needs a decision-complete plan.
3. **Execute**: run from `task.md`; keep implementation scoped to the ticket.
4. **Report**: after meaningful execution, create or refresh `report.md`.
5. **Update**: for later explicit `TKT-XXX` comments or fixes, create an update file and link it from `report.md`.

## Execution Completion

Any command or agent executing a ticket must preserve completion context:

1. Run the task verification steps.
2. Complete the **Completion Gate** below.
3. Capture pass/fail and important failures or fixes.
4. Create or update `report.md` when the result is useful future context.
5. If `report.md` already describes an earlier completion, create `updates/YYYY-MM-DD-<slug>.md` instead of rewriting history.
6. Refresh helper indexes only if the project is currently using them; never trust indexes over ticket files.

## Completion Gate

Before reporting a ticket as complete, answer these in the report or update file with a verdict, evidence, and next action when needed:

1. Acceptance: Are all acceptance criteria satisfied?
2. Scope: Did the work stay within the ticket or request boundaries?
3. Validation: What checks passed, failed, or were not run?
4. Security and safety: Did the change introduce unsafe file or network access, injection risk, auth or policy bypass, dependency risk, data exposure, or destructive behavior?
5. Regression risk: What existing behavior could be affected, and what mitigates that risk?
6. Follow-up: What remains incomplete, deferred, or worth a later ticket?

If any answer is `no`, `partial`, or `not run`, record the concrete next action instead of calling the work fully done.

## Report Format

`report.md` should stay concise and retrieval-friendly:

```md
# TKT-XXX Report: Title

## Summary

## Key Decisions

## Edge Cases and Failures

## Validation

## Completion Gate

- Acceptance:
- Scope:
- Validation:
- Security and safety:
- Regression risk:
- Follow-up:

## Follow-up

## Updates

- [YYYY-MM-DD short update](updates/YYYY-MM-DD-short-update.md)
```

Do not paste long logs. Summarize failure causes, fixes, and remaining risks.

## Update Files

Require an explicit `TKT-XXX` before creating an update file. If a user comment does not name a ticket, ask which ticket it belongs to.

Each update file captures:

- trigger
- changed files or affected behavior
- failure or edge case observed
- fix or decision made
- validation performed
- remaining follow-up

After creating an update file, add or refresh the `## Updates` list in `report.md` in reverse chronological order.

## Validation

Sync helper indexes when ticket or memory files are added, removed, or renamed:

```bash
python3 .agents/tools/tkt_sync.py
```

Use the dependency-free Python validator:

```bash
python3 .agents/tools/tkt_validate.py .agents/tasks
```

The validator checks existing artifacts. It does not require placeholder files, and stale helper-index entries are warnings unless an existing artifact is malformed.
