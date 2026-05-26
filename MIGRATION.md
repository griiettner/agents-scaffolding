# Migration Runbook

This document is for AI agents (and humans) running repository migration from legacy `.cursor` and/or `.claude` setup into canonical `.agents/`.

## Goal

Migrate source repo context into:

- `.agents/skills/`
- `.agents/agents/`
- `.agents/memory/`

Then verify sync/index/validation tooling reports a healthy state.

## Inputs

- Target repo (this repository clone)
- Source repo path with existing `.cursor` and/or `.claude` configuration

Required argument:

- `--source /absolute/path/to/source-repo`

## 1) Preflight

Run from target repo root:

```bash
git status --short
python3 .agents/tools/migrate_cursor_setup.py --help
```

Checks:

- Confirm you are in the intended target repository.
- Confirm the migrator script is available.
- Confirm you understand existing uncommitted local changes before migration.

## 2) Dry-Run Migration

```bash
python3 .agents/tools/migrate_cursor_setup.py --source /absolute/path/to/source-repo --dry-run
```

Review dry-run output:

- `writes`: expected non-zero for first migration
- `skipped`: expected when destination files already exist and are not migrator-owned
- `ambiguous`: expected for low-confidence memory classification

If you need to intentionally replace non-migrator-owned destination files:

```bash
python3 .agents/tools/migrate_cursor_setup.py --source /absolute/path/to/source-repo --dry-run --force
```

## 3) Execute Migration

```bash
python3 .agents/tools/migrate_cursor_setup.py --source /absolute/path/to/source-repo
```

Expected immediate outcomes:

- Canonical skills exist under `.agents/skills/<name>/SKILL.md`.
- Skill metadata exists under `.agents/skills/<name>/agents/openai.yaml`.
- Agent profiles exist under `.agents/agents/*.md` with frontmatter.
- Durable memory entries exist under `.agents/memory/<category>/*.md`.
- Memory and task indexes are regenerated.
- Migration report artifacts are written under `.agents/migrations/`.
- Existing target-native structures remain intact:
  - `.agents/tools/` remains usable
  - `.agents/tasks/` keeps valid structure and indexing
  - existing target skills are preserved unless explicitly overwritten (`--force`)

Default behavior includes maintenance commands:

1. `python3 .agents/tools/sync_claude_skills.py`
2. `python3 .agents/tools/tkt_sync.py`
3. `python3 .agents/tools/tkt_validate.py .agents/tasks`

To skip maintenance (not recommended except debugging):

```bash
python3 .agents/tools/migrate_cursor_setup.py --source /absolute/path/to/source-repo --no-sync
```

## 4) Post-Migration Validation

Run explicitly even if maintenance was enabled:

```bash
python3 .agents/tools/sync_claude_skills.py
python3 .agents/tools/tkt_sync.py
python3 .agents/tools/tkt_validate.py .agents/tasks
```

Expected result:

- `sync_claude_skills.py`: "synced Claude skill stubs"
- `tkt_sync.py`: "synced .agents task and memory indexes"
- `tkt_validate.py`: "tkt_validate ok"

## 5) Review Artifacts

Open migration reports:

- `.agents/migrations/cursor-migration-report.md`
- `.agents/migrations/cursor-migration-manifest.json`

Review for:

- Migrated items list is complete and matches expectations.
- `Skipped` items are intentional.
- `Ambiguous` memory items are reviewed manually for correct category/content.
- Maintenance command return codes are all `0`.

## 5.1) AGENTS.md / CLAUDE.md Reconciliation (Required)

Migration must explicitly evaluate root routing files in the target repository:

1. Check whether `AGENTS.md` exists.
2. Check whether `CLAUDE.md` exists.

If missing:

- Create the missing file(s) with repository-appropriate routing guidance aligned to `.agents/` canonical structure.

If present:

- Read both existing files fully before editing.
- Preserve important target-specific policies and constraints.
- Propose an adaptation plan before applying major structural rewrites.
- Merge authoritative routing guidance into the target `AGENTS.md` rather than replacing blindly.

Memory extraction rule from routing docs:

- Move durable, cross-task knowledge out of `AGENTS.md`/`CLAUDE.md` into `.agents/memory/<category>/...`.
- Keep only boot routing and operating rules in `AGENTS.md`/`CLAUDE.md`.
- Ensure extracted durable knowledge uses YAML frontmatter and appears in relevant memory indexes after `tkt_sync.py`.

Definition of what to preserve in merge:

- Non-negotiable repo constraints
- Tooling commands relied on by the project
- Safety and workflow boundaries
- Existing startup routing conventions that are still valid

## 6) Functional Spot Checks

Check migrated structure:

```bash
find .agents/skills -maxdepth 3 -type f | sort
find .agents/agents -maxdepth 2 -type f | sort
find .agents/memory -maxdepth 3 -type f | sort
```

Confirm:

- Skills have canonical files at `.agents/skills/<name>/SKILL.md`.
- Skills include metadata at `.agents/skills/<name>/agents/openai.yaml`.
- Memory files include YAML frontmatter and are indexed by category `index.yaml`.
- Agent profiles exist under `.agents/agents/` with frontmatter.

## 7) Idempotence Check

Re-run migration:

```bash
python3 .agents/tools/migrate_cursor_setup.py --source /absolute/path/to/source-repo
```

Expected:

- No errors.
- Deterministic behavior.
- Migration-owned files are safely updated in place.

## 8) Final Git Review

```bash
git status --short
git diff --stat
```

Review that changes are scoped to migration outputs and expected indexes/docs.

## 9) Troubleshooting

- Script fails with missing source path:
  - Verify `--source` uses an absolute path and points to a directory.
- Many skipped files:
  - Existing destination files are not migrator-owned. Re-run with `--force` only if overwrite is intended.
- Ambiguous memory too high:
  - Manually curate category and digest content in `.agents/memory/*`.
- Validation warnings/errors:
  - Fix frontmatter fields and rerun `tkt_sync.py` + `tkt_validate.py`.

## 10) Safety Rules

- Treat source repo as read-only input.
- Prefer dry-run before any real migration.
- Do not delete unrelated repo files during migration review.
- Do not assume generated indexes are canonical truth; source files remain canonical.
