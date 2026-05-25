---
name: commit
description: Commit staged changes with an auto-generated conventional commit message. Use when the user wants to quickly commit what is already staged. Invoked via /commit.
---

# commit – Quick Commit

## Workflow

### 1. Check staged files

Run `git status`. If there are **no staged files**, stop and ask:
> "No staged files found. Please stage your changes with `git add` and try again."

Do NOT run `git add` automatically.

### 2. Review changes and write commit message

Run `git --no-pager diff --cached --stat` and `git --no-pager diff --cached` to understand the staged changes.

Write a conventional commit message (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, etc.) with:

- A concise subject line (≤72 chars)
- A body with bullet points describing what changed and why

**NEVER add a Co-Authored-By line or any AI/Warp, Cursor, Codex, Claude attribution.**

### 3. Commit

Run `git commit -m "<message>"` with the generated message.

### 4. Report

If successful, output the commit hash and a brief confirmation.
If it failed, show the error and suggest next steps.