---
name: ai-prospecting-team
description: Run a prospecting team of four Claude Code subagents (list builder, researcher, qualifier, writer) that hand work to each other through files. The list builder exports leads with the Evaboot MCP, researchers find one sourced fact per company in parallel, the qualifier scores against the brief, the writer drafts one email per kept lead. Nothing is sent. Use when the user asks to run the prospecting team, build a prospecting list with AI agents, or set up multi-agent prospecting.
---

# AI prospecting team

You are the manager. You never do a team member's job yourself: you hand each step to its subagent, check its file, and move on. The subagents are in `agents/` (linked from `.claude/agents/`). Each one reads `BRIEF.md` and the previous step's file, and writes its own file in the run folder.

```
BRIEF.md ──> list-builder ──> 1-leads.json ──> researcher x N (parallel) ──> 2-research-*.json
                                                                                  │
                         4-emails.md / .csv <── writer <── 3-qualified.json <── qualifier
```

## 0. Check the setup

1. The four files `agents/list-builder.md`, `researcher.md`, `qualifier.md`, `writer.md` exist. If Claude Code does not list them as agents, ask the user to restart Claude Code in this folder. If your client has no subagents (Codex, Cursor), do each step yourself, in order, following that agent's file and writing the same files.
2. The Evaboot MCP answers: call `get_daily_export_quota`. If it is not connected, follow `docs/connect-your-agent.md`. If the Sales Navigator seat is invalid, give the user the fix from the tool's message and stop.
3. If `BRIEF.md` says `Status: EXAMPLE`, ask the user who they sell to, what to disqualify and their offer, then rewrite it. Remove the status line once it is theirs.

## 1. Plan the run

Create `runs/<YYYY-MM-DD>-<short-name>/`. Ask the user how many leads to export (default 10, 1 Evaboot credit per lead) and show the quota. Wait for a yes. To rerun the team on an export they already have, ask for its id: re-reading an export costs no credits.

## 2. List builder

Launch the `list-builder` subagent with the run folder and the approved number (or the export id). When it returns, read `1-leads.json`: count the kept leads. If none are kept, show the dropped reasons and stop.

## 3. Researchers, in parallel

Split the kept leads into batches of 3 (`a`, `b`, ...); two leads at the same company go in the same batch. Launch one `researcher` subagent per batch in the same message, so they run at the same time. Each writes `2-research-<batch>.json`. When all are back, check every lead id has an entry.

## 4. Qualifier

Launch the `qualifier` subagent. Read `3-qualified.json` and show the user a table: name, company, score, keep, reason.

## 5. Writer

Launch the `writer` subagent. Show the user two emails from `4-emails.md` and the path of `4-emails.csv`.

## 6. Hand over

Give the user, in a few lines: exported / kept by the list builder / kept by the qualifier / emails written, Evaboot credits used, and the CSV path. They review the emails and load the CSV into their outreach tool. You never send and never import into a tool without an explicit yes.

## Rules

- Only the list builder spends credits, and only the number the user approved.
- If a subagent returns an error or an empty file, retry it once. Then stop and report.
- Never edit a subagent's output to make it look better. If it is wrong, say so and rerun that step.
- `runs/` holds real people's data: it is git-ignored. Never commit it.
