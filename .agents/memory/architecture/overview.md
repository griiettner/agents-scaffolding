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
  - scaffolding
read_when:
  - changing folder structure
  - deciding where project knowledge should live
  - creating new agent workflows
  - evaluating whether a file belongs in skills, memory, or tasks
---

# Architecture Overview

This repository demonstrates an agent-friendly documentation layout.

## Core structure

- `AGENT.md` is the boot router. It should stay short and tell the agent where to look next.
- `.agents/memory/` stores durable cross-task knowledge.
- `.agents/skills/` stores reusable procedures and command-like workflows.
- `.agents/tasks/` stores the lifecycle history for specific work units.
- `.agents/tools/` stores optional maintenance scripts such as index sync and validation.

## Routing model

Agents should not load the entire repository context at startup.

Recommended order:

1. Read `AGENT.md`.
2. Choose the smallest relevant index.
3. Open only the files needed for the current task.
4. Treat task folders as canonical for ticket-specific history.

## Frontmatter and indexes

Durable memory files and task artifacts should start with YAML frontmatter.
This enables lightweight tools to build or refresh `index.yaml` files without parsing the whole document body semantically.

## Adaptation notes

Replace the example categories, tickets, and principles with your own project structure after cloning. The pattern matters more than the sample content.
