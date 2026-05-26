---
name: skill-new
description: "Create a new project-local skill under .agents/skills/ and refresh generated Claude stubs. Use when adding a reusable workflow skill to this repository."
---

# Skill New

Use this skill when a new reusable project workflow should become available as a local skill.

## Workflow

1. Choose a lowercase kebab-case skill name.
2. Write a short discovery description that says when the skill should be used.
3. Run the helper script:

```bash
python3 .agents/tools/create_skill.py <skill-name> "<description>"
```

The helper creates:

- `.agents/skills/<skill-name>/SKILL.md`
- `.agents/skills/<skill-name>/agents/openai.yaml`
- generated Claude stubs under `.claude/skills/`

## After Creation

Edit `.agents/skills/<skill-name>/SKILL.md` to replace the starter workflow with the real procedure.

Then run:

```bash
python3 .agents/tools/sync_claude_skills.py
python3 .agents/tools/tkt_validate.py .agents/tasks
```

If Codex does not show the new `$skill-name` suggestion in the current app session, reopen or refresh the repository session so project-local `.agents/skills/` metadata is reloaded.

## Rules

- `.agents/skills/<skill-name>/SKILL.md` is the canonical source.
- Do not hand-edit generated `.claude/skills/` stubs.
- Keep `agents/openai.yaml` small: display metadata and invocation policy only.
- Prefer explicit invocation by setting `allow_implicit_invocation: false` unless the skill is safe and broadly applicable.
