# Simple Agents Scaffolding

Sometimes you don’t need a massive agentic framework for your VibeCoding project.

You need a solid foundation like durable memory, planning + execution loops, reusable skills, structured reporting and tooling that doesn’t fight you.

That’s why Simpe Agents Scaffolding was created.

It’s a lightweight scaffolding for building practical AI agents with:

- Durable memory
- A TKT system for AI agents for planning, execution, and reporting
- Basic composable skills
- Clean structure you can actually extend without rewriting everything later

The goal wasn’t to create another “autonomous AGI operating system.”

The goal was to make something practical: A setup where agents can plan work, execute tasks, keep context over time, and report results in a predictable way.

It works with Claude, Codex, and Cursor, so you can plug it into the tools developers are already using instead of forcing a custom ecosystem.

A lot of agent projects become overengineered before they become useful.

This repo tries to go in the opposite direction:

start simple,
keep the primitives clean,
add complexity only when it earns its place.

This repo gives you a starting structure for organizing:

- `AGENTS.md` as a lightweight boot router
- `.agents/memory/` for durable knowledge
- `.agents/skills/` for reusable procedures
- `.agents/tasks/` for ticket or work-unit history
- YAML frontmatter and generated indexes for cheap routing

The sample content is intentionally generic. Clone it, then replace the examples with your own project rules, architecture, and task history.

Implemented compatibility in this repo today:

- Claude Code: automated project-skill discovery bridge through generated `.claude/skills/` stubs
- Codex: project-local `.agents/skills/` with optional `agents/openai.yaml` metadata for `$skill-name` discovery
- Cursor: naming and workflow conventions only; no native auto-discovery bridge is implemented here

## Why this exists

Most agent setups fail for one of two reasons:

1. Everything is stuffed into one giant prompt file.
2. Useful context exists, but agents have no cheap way to find it.

This scaffold solves that by separating routing, memory, procedures, and task history.

## Repository layout

```text
.
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── .claude/
│   ├── commands/
│   │   └── sync-skills.md
│   ├── README.md
│   └── skills/              # generated Claude Code compatibility stubs
└── .agents/
    ├── agents/
    ├── memory/
    │   ├── MEMORY.md
    │   ├── architecture/
    │   │   ├── index.yaml
    │   │   └── overview.md
    │   ├── decisions/
    │   │   ├── index.yaml
    │   │   ├── ADR-001-agent-ticket-lifecycle.md
    │   │   └── ADR-002-memory-routing.md
    │   └── principles/
    │       ├── index.yaml
    │       └── constitution.md
    ├── plans/
    ├── skills/
    │   ├── commit/
    │   ├── commitpush/
    │   ├── plan-exec/
    │   ├── tkt-exec/
    │   ├── tkt-management/
    │   ├── tkt-new/
    │   ├── tkt-plan/
    │   ├── tkt-report/
    │   ├── tkt-sync/
    │   ├── tkt-task/
    │   └── tkt-update/
    ├── tasks/
    │   ├── README.md
    │   ├── index.yaml
    │   ├── indexes/
    │   ├── TKT-001/
    │   └── TKT-002/
    ├── tools/
    │   ├── tkt_sync.py
    │   └── tkt_validate.py
    ├── settings.json
    └── settings.local.json
```

## Core concepts

### `AGENTS.md`

`AGENTS.md` is the boot context.

It should stay short. Its job is to route the agent to the next relevant files, not to contain the whole project memory.

### `.agents/memory/`

This holds durable knowledge that should survive across tickets and sessions.

Use category folders with `index.yaml` files so agents can discover relevant memory before loading full documents.

Recommended rule:

- durable memory files start with YAML frontmatter
- read the index first, then open the smallest relevant file

### `.agents/skills/`

Skills are reusable procedures.

They are not durable memory and they are not ticket history. A skill should answer: "what workflow should the agent follow for this kind of task?"

Each included skill in this scaffold is documented below in [Included Skills](#included-skills).

### `.claude/skills/`

Claude Code officially discovers project skills from `.claude/skills/`, not from `.agents/skills/`.

This scaffold keeps `.agents/skills/` as the canonical location and generates lightweight Claude compatibility stubs under `.claude/skills/`.

Recommended setup:

- treat `.agents/skills/` as the system of record
- expose it to Claude Code through generated stubs at `.claude/skills/`

That gives you:

- a tool-agnostic canonical structure in `.agents/`
- compatibility with Claude Code's documented project-skill discovery path

It does not imply equivalent native integration for Cursor. Codex can use `.agents/skills/` directly in environments that support project-local skill discovery.

Each generated stub should preserve the skill frontmatter Claude needs for discovery and point Claude to the canonical `.agents/skills/<name>/SKILL.md` file.

### `.agents/skills/<name>/agents/openai.yaml`

Codex can use `agents/openai.yaml` files beside canonical skills for display metadata and invocation policy.

Recommended setup:

- treat `.agents/skills/<name>/SKILL.md` as the source of truth
- keep `.agents/skills/<name>/agents/openai.yaml` small
- use `policy.allow_implicit_invocation: false` unless a skill is safe to invoke automatically

### `.agents/tasks/`

Tasks are the canonical store for work-unit history.

Use a folder per ticket or work item. Keep the smallest useful artifact set:

- slim chore: `task.md`, optionally `report.md`
- full ticket: `concept.md`, `plan.md`, `task.md`, `report.md`, optional `updates/`

### YAML frontmatter

All durable memory files and task artifacts should start with YAML frontmatter.

This scaffold intentionally supports a small, explicit subset of YAML in frontmatter:

- scalar fields like `title: Example`
- empty lists like `dependencies: []`
- inline scalar lists like `skills: [tkt-management, tkt-sync]`
- block scalar lists like:

```yaml
areas:
  - AGENTS.md
  - .agents/tasks
```

Unsupported in scaffold frontmatter:

- nested mappings
- lists of objects
- arbitrary YAML structures for scalar fields

The sync and validation scripts now fail or warn on unsupported frontmatter instead of silently dropping metadata.

Example memory frontmatter:

```yaml
---
id: architecture-overview
title: Architecture overview
type: architecture
status: active
created: 2026-05-25
updated: 2026-05-25
tags:
  - architecture
  - routing
read_when:
  - changing folder structure
---
```

Example task frontmatter:

```yaml
---
id: TKT-001
title: Establish agent scaffolding
artifact: task
status: done
owner: repo-agent
created: 2026-05-25
updated: 2026-05-25
dependencies: []
areas:
  - AGENTS.md
  - .agents/memory
skills:
  - tkt-management
---
```

## Included examples

This scaffold includes two example tickets:

- `TKT-001` is a full ticket showing `concept.md`, `plan.md`, `task.md`, and `report.md`.
- `TKT-002` is a slim ticket showing only `task.md` and `report.md`.

These exist to demonstrate structure. Replace them with your own repo history after cloning.

## Skill invocation

This scaffold documents a simple command-style invocation model:

- Claude Code: `/skill-name`
- Cursor: `/skill-name`
- Codex: `$skill-name`

Examples:

- Claude Code: `/tkt-plan 001`
- Cursor: `/tkt-plan 001`
- Codex: `$tkt-plan 001`

For ticket-oriented skills, use the numeric suffix as the argument when the command expects a ticket:

- `001` means `TKT-001`
- `012` means `TKT-012`

So these are equivalent intents:

- `/tkt-exec 001`
- `/tkt-exec TKT-001`
- `$tkt-exec 001`

If your environment uses a different command syntax, keep the skill names and arguments the same and adapt only the prefix.

Codex `$skill-name` discovery depends on the local `.agents/skills/` metadata being present and the current app session having loaded the repository. Cursor invocation examples are conventions unless your Cursor setup adds its own adapter.

## Included skills

This scaffold ships with a small task-management oriented skill set plus two optional git workflow helpers.

#### `skill-new`

Purpose:
- creates a new canonical skill under `.agents/skills/`
- writes `agents/openai.yaml`
- refreshes Claude stubs

Use it when:
- you want to add a reusable project-local workflow and make it discoverable

Invocation example:
```text
# Claude Code or Cursor
/skill-new

# Codex
$skill-new
```

### Core task skills

These are the ones most teams should keep.

#### `tkt-management`

Purpose:
- defines the canonical task lifecycle under `.agents/tasks/`
- explains slim vs full ticket modes
- defines frontmatter expectations, completion gates, reporting, and updates

Use it when:
- you are designing or reviewing how ticket files should work
- other ticket commands need a source of truth for lifecycle rules

Keep it if:
- you want a structured ticket workflow for agent work

Invocation example:
- this is a base skill, usually referenced by other skills rather than invoked directly
- if your tool allows direct invocation:

```text
# Claude Code or Cursor
/tkt-management

# Codex
$tkt-management
```

#### `tkt-new`

Purpose:
- creates the next `TKT-XXX` folder
- chooses between a slim or fuller task shape

Use it when:
- a new work item needs to be recorded
- you want the agent to scaffold a task folder with the minimum useful artifacts

Keep it if:
- you want a repeatable way to open new agent tasks

Invocation example:
```text
# Claude Code or Cursor
/tkt-new

# Codex
$tkt-new
```

#### `tkt-plan`

Purpose:
- creates or refreshes `plan.md` only when a task genuinely needs a decision-complete plan

Use it when:
- a task has open implementation decisions
- a user explicitly asks for a plan for an existing ticket

Do not use it when:
- the task is already obvious and executable from `task.md`

Keep it if:
- you want to separate planning from execution

Invocation example:
```text
# Claude Code or Cursor
/tkt-plan 001

# Codex
$tkt-plan 001
```

#### `tkt-exec`

Purpose:
- executes work from `task.md`
- preserves useful completion context in `report.md` or `updates/`

Use it when:
- a ticket is ready to be implemented
- the user explicitly asks the agent to execute a named ticket

Keep it if:
- you want execution tied to verification and reporting

Invocation example:
```text
# Claude Code or Cursor
/tkt-exec 001

# Codex
$tkt-exec 001
```

#### `tkt-update`

Purpose:
- records follow-up work after a ticket was already completed
- writes `updates/YYYY-MM-DD-<slug>.md` and links it from `report.md`

Use it when:
- a later fix, comment, regression, or follow-up belongs to an existing `TKT-XXX`

Keep it if:
- you want ticket history to remain append-only instead of overwriting old reports

Invocation example:
```text
# Claude Code or Cursor
/tkt-update 001

# Codex
$tkt-update 001
```

#### `tkt-sync`

Purpose:
- reruns index generation and validation

Use it when:
- ticket or memory files were added, removed, or renamed
- you want to refresh helper metadata after reorganizing the scaffold

Keep it if:
- you use generated `index.yaml` files

Invocation example:
```text
# Claude Code or Cursor
/tkt-sync

# Codex
$tkt-sync
```

### Optional git workflow skills

These are convenience skills. They are not required for the task system.

#### `commit`

Purpose:
- reviews staged changes and creates a conventional commit

Use it when:
- the user wants a quick commit of already staged files

Do not use it when:
- files are not staged yet
- the repo has its own release automation or commit policy that conflicts with this workflow

Keep it if:
- your team wants a lightweight commit helper

Invocation example:
```text
# Claude Code or Cursor
/commit

# Codex
$commit
```

#### `commitpush`

Purpose:
- commits staged changes
- pushes the branch
- opens a GitHub pull request

Use it when:
- the user explicitly wants a combined commit, push, and PR workflow

Do not use it when:
- GitHub CLI is unavailable
- your repo uses a different branching model or PR policy than the default assumptions in the skill

Keep it if:
- your team frequently wants an end-to-end GitHub handoff from staged changes

Invocation example:
```text
# Claude Code or Cursor
/commitpush

# Codex
$commitpush
```

### Legacy alias skills

These exist mostly for compatibility with older command names. New projects can keep or delete them depending on whether alias compatibility matters.

#### `plan-exec`

Purpose:
- redirects legacy execution requests to `tkt-exec`

Use it when:
- you still have users or scripts invoking `/plan-exec`

Delete it if:
- you do not need backward compatibility

Invocation example:
```text
# Claude Code or Cursor
/plan-exec 001

# Codex
$plan-exec 001
```

#### `tkt-report`

Purpose:
- marks standalone reporting as deprecated
- redirects users toward `tkt-exec` or `tkt-update`

Use it when:
- legacy command names still exist in your environment

Delete it if:
- you want a smaller skill set and do not need legacy aliases

Invocation example:
```text
# Claude Code or Cursor
/tkt-report 001

# Codex
$tkt-report 001
```

#### `tkt-task`

Purpose:
- redirects generic task requests toward `tkt-new`, `tkt-plan`, or `tkt-exec`

Use it when:
- older workflows still reference `/tkt-task`

Delete it if:
- you prefer only the canonical commands

Invocation example:
```text
# Claude Code or Cursor
/tkt-task 001

# Codex
$tkt-task 001
```

### Which skills to keep

Recommended minimum:

- `tkt-management`
- `skill-new`
- `tkt-new`
- `tkt-plan`
- `tkt-exec`
- `tkt-update`
- `tkt-sync`

Useful optional additions:

- `commit`
- `commitpush`

Safe to delete if you do not need alias compatibility:

- `plan-exec`
- `tkt-report`
- `tkt-task`

## How to use this repo

### 1. Clone it

```bash
git clone <your-fork-or-this-repo>
cd agents-scaffolding
```

### 2. Rewrite the boot context

Update `AGENTS.md` so it describes your actual project and routing rules.

At minimum, replace:

- project summary
- boundaries
- repo conventions
- any example-specific references

Also keep `CLAUDE.md` aligned so Claude users are redirected to `AGENTS.md` and `.agents/`.

### 3. Rewrite durable memory

Start by editing:

- `.agents/memory/architecture/overview.md`
- `.agents/memory/principles/constitution.md`
- `.agents/memory/decisions/*.md`

If a memory file is only placeholder content for the scaffold, replace or delete it.

### 4. Decide which skills you actually want

You may want to keep only a subset of the included skills.

Typical minimal set:

- `tkt-management`
- `tkt-new`
- `tkt-plan`
- `tkt-exec`
- `tkt-update`
- `tkt-sync`

If you do not use `commit` or `commitpush`, delete them.

If you keep Claude Code support, make sure `.claude/skills/` continues to point at the same skill set.

### 5. Replace example tickets

The sample tickets are for demonstration only.

You can:

- delete `TKT-001` and `TKT-002`
- create your own first real ticket
- regenerate indexes

### 6. Regenerate indexes

Whenever you add, remove, or rename task or memory files:

```bash
python3 .agents/tools/sync_claude_skills.py
python3 .agents/tools/tkt_sync.py
python3 .agents/tools/tkt_validate.py .agents/tasks
```

### 7. Preserve Claude compatibility

Claude Code officially loads project skills from `.claude/skills/`.

This scaffold is set up so `.claude/skills/` contains generated stubs that point to `.agents/skills/`.

Regenerate them after changing canonical skills:

```bash
python3 .agents/tools/sync_claude_skills.py
```

Default behavior is non-destructive:

- generated stubs are refreshed
- generated stale stub directories are removed
- user-created `.claude/skills/*` content is preserved

If you want a stricter mirror of canonical skills, use:

```bash
python3 .agents/tools/sync_claude_skills.py --prune
```

`--prune` still preserves user-owned Claude skill directories that were not generated by this scaffold.

If you are inside Claude Code, you can expose the same operation as a project command:

```text
/sync-skills
```

Do not edit files under `.claude/skills/` manually.

### 8. Migrate from an existing `.cursor`/`.claude` repo

If you are adopting this scaffold into a repository that already has agent context in `.cursor/` and/or `.claude/`, refer to [MIGRATION.md](./MIGRATION.md).

When using an AI agent, explicitly instruct it to read `MIGRATION.md` first and execute the migration workflow defined there.

## Recommended workflow

### Create a new ticket

1. Create `.agents/tasks/TKT-XXX/`
2. Add `task.md` or `concept.md` + `task.md`
3. Add YAML frontmatter
4. Add `plan.md` only if the work needs a real plan
5. Regenerate indexes if you use them

### Add durable knowledge

1. Pick the right memory category
2. Create a focused `.md` file with YAML frontmatter
3. Keep the file self-describing and retrieval-friendly
4. Regenerate indexes

### Record later follow-up

If work happens after a ticket was already completed:

1. Create `updates/YYYY-MM-DD-<slug>.md`
2. Link it from `report.md`
3. Regenerate indexes if needed

## Notes on indexes

`index.yaml` files are routing aids, not canonical truth.

That distinction matters:

- memory files are canonical for memory content
- ticket folders are canonical for task history
- indexes should be regenerable from those files

## Notes on Claude Code skills

Claude Code's documented project skill path is `.claude/skills/`.

That means `.agents/skills/` alone is usually not enough for automatic Claude skill discovery.

This scaffold therefore uses a compatibility layer:

- canonical skills live in `.agents/skills/`
- Claude sees them through generated stubs in `.claude/skills/`
- users can refresh those stubs manually through the Claude project command `/sync-skills`

If you stop generating `.claude/skills/`, expect Claude Code to stop discovering project skills automatically unless Anthropic changes that behavior in the future.

## Notes on Codex skills

Codex `$skill-name` suggestions are driven by project-local files under `.agents/skills/`.

The Codex session must be opened at this repository root. If Codex is opened from another workspace and merely edits this folder through absolute paths, these project-local skills will not be part of that session's suggestions.

Check whether Codex has an exact trusted project entry for this repo:

```bash
python3 .agents/tools/trust_codex_project.py --check
```

If it reports `not trusted`, add or repair the trust entry explicitly:

```bash
python3 .agents/tools/trust_codex_project.py
```

After trust is added, start a fresh Codex session at this repository root so the app reloads project-local skills and permissions.

For best discovery, each skill should include:

- `.agents/skills/<name>/SKILL.md`
- `.agents/skills/<name>/agents/openai.yaml`

If newly added skills do not appear immediately, restart or refresh the Codex app session for this repository.

## What to customize first

If you want the fastest path from scaffold to real usage, change these first:

1. `AGENTS.md`
2. `.agents/memory/architecture/overview.md`
3. `.agents/memory/principles/constitution.md`
4. `.agents/skills/tkt-management/SKILL.md`
5. `.agents/tasks/TKT-001/` and `TKT-002/`

## Cleanup after cloning

You will probably want to remove scaffold-only artifacts such as:

- example ticket folders
- example ADRs that do not match your repo
- unused skills
- local permission settings that do not match your toolchain

The default `.agents/settings.json` is conservative about remote git actions. Expand it deliberately if your workflow wants agent-driven commits or pushes.

## License

MIT License

Copyright (c) 2026 Paulo Griiettner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
