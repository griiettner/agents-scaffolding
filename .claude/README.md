# Claude Compatibility Layer

This directory exists for Claude-specific project discovery.

In this scaffold:

- canonical agent context lives in `AGENT.md` and `.agents/`
- canonical skills live in `.agents/skills/`
- Claude Code compatibility is provided through generated stubs in `.claude/skills/`

Each generated Claude skill should:

- preserve the canonical skill frontmatter Claude uses for discovery
- point Claude to the real skill file in `.agents/skills/`
- avoid duplicating the full canonical skill body

Do not edit generated files under `.claude/skills/` manually.

Regenerate them with:

```bash
python3 .agents/tools/sync_claude_skills.py
```

Or, from Claude Code, run:

```text
/sync-skills
```
