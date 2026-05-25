# Claude Entry Point

This file is a redirect, not the source of truth.

## Authority

For this repository, the authoritative project context lives in:

1. `AGENTS.md`
2. `.agents/memory/`
3. `.agents/skills/`
4. `.agents/tasks/`

Claude Code compatibility skills may also appear under `.claude/skills/`, but those files are generated stubs. The canonical skill content still lives under `.agents/skills/`.

If this file conflicts with `AGENTS.md` or anything under `.agents/`, follow `AGENTS.md` and `.agents/`.

## Required startup behavior

When starting work in this repository:

1. Read `AGENTS.md` first.
2. Use `AGENTS.md` as the routing file.
3. Read only the smallest relevant files under `.agents/`.
4. Treat generated `index.yaml` files as routing aids, not canonical truth.

## Claude-specific command

If Claude Code needs refreshed project skill discovery metadata, run:

- `/sync-skills`

That command regenerates `.claude/skills/` stubs from the canonical `.agents/skills/` tree.
By default it refreshes generated stubs and preserves Claude-only user content under `.claude/skills/`.

## Writing rules

- Store durable project knowledge under `.agents/memory/`.
- Store reusable procedures under `.agents/skills/`.
- Store task and ticket history under `.agents/tasks/`.
- If a skill is visible under `.claude/skills/`, edit the canonical copy under `.agents/skills/`.
- Do not hand-edit generated Claude skill stubs.
- Do not store canonical project knowledge in `.claude/`.

## Practical rule

`AGENTS.md` is the ruler.
`.agents/` is the system of record.
`CLAUDE.md` only exists to make that explicit.
