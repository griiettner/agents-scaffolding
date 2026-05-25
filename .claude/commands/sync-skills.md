# /sync-skills

Regenerate Claude Code skill stubs from the canonical `.agents/skills/` tree.

Run:

```bash
python3 .agents/tools/sync_claude_skills.py
```

Use this command when:

- a canonical skill was added
- a canonical skill was removed
- a canonical skill frontmatter block changed
- Claude Code is not seeing the latest project skill metadata

Do not edit `.claude/skills/` files manually. They are generated compatibility stubs.
