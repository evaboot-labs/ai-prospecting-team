# The four agents

Each agent is one Markdown file in [`agents/`](../agents/), linked from `.claude/agents/` so Claude Code loads it as a subagent. The skill in [`skills/ai-prospecting-team/SKILL.md`](../skills/ai-prospecting-team/SKILL.md) is the manager: it starts each agent in turn and checks its file.

| Agent | Tools | Reads | Writes |
|---|---|---|---|
| `list-builder` | All, including the Evaboot MCP | `BRIEF.md` | `1-leads.json` |
| `researcher` | `Read, Write, WebFetch, WebSearch` | `1-leads.json` | `2-research-<batch>.json` |
| `qualifier` | `Read, Write` | `BRIEF.md`, `1-leads.json`, `2-research-*.json` | `3-qualified.json` |
| `writer` | `Read, Write` | `BRIEF.md`, `1-leads.json`, `3-qualified.json` | `4-emails.md`, `4-emails.csv` |

Every run gets its own folder, `runs/<date>-<name>/`, so you can open each handoff and see where a lead was dropped.

## The fields in each file

```yaml
---
name: researcher          # the name the manager calls
description: ...          # when Claude Code should use it
tools: Read, Write, WebFetch, WebSearch   # leave out to give every tool
model: sonnet             # sonnet, opus, haiku or inherit
---
The instructions the agent follows.
```

- **`tools`** is the safety line. Only the list builder can reach the Evaboot MCP, so only it can spend credits. The qualifier and the writer cannot open the web, so they can only use facts a researcher wrote down with a source.
- **`model`**: the list builder, qualifier and writer follow rules, so a smaller model is fine; give the writer a bigger one if the emails read flat.

## Change the team

- **Change a rule:** edit the agent's file, then restart Claude Code. Rerun only that step on the same run folder: it costs no credits.
- **Add an agent:** for example `crm-checker` with your CRM's MCP, to drop leads you already talk to. Add a file in `agents/` and a step in the skill between the qualifier and the writer.
- **More researchers:** the manager splits leads into batches of 3 and starts one researcher per batch at the same time. Change the batch size in the skill.

Back to the [README](../README.md).
