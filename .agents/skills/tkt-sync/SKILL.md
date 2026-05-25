---
name: tkt-sync
description: "Regenerate helper ticket and memory indexes. Use only when user explicitly invokes /tkt-sync."
disable-model-invocation: true
---

# /tkt-sync

Run:

```bash
python3 .agents/tools/sync_claude_skills.py
python3 .agents/tools/tkt_sync.py
python3 .agents/tools/tkt_validate.py .agents/tasks
```

The Python files own the behavior; this command is only a launcher.
