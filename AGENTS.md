# Agent instructions

This repo is a prospecting team of four Claude Code subagents with one job each: the list builder exports leads from Sales Navigator with the Evaboot MCP, researchers find one sourced fact per company in parallel, the qualifier scores each lead against the brief, and the writer drafts one email per kept lead. They hand work to each other through files in `runs/`. Nothing is sent.

1. Follow the skill in `skills/ai-prospecting-team/SKILL.md` step by step. You are the manager: hand each step to its subagent in `agents/`.
2. The brief all four agents read is `BRIEF.md`. If it says `Status: EXAMPLE`, ask the user for their ICP, disqualifiers and offer, and rewrite it.
3. If the Evaboot MCP is not connected, follow `docs/connect-your-agent.md`.
4. To change what a team member does, edit its file in `agents/`; `docs/agents.md` explains each field.
5. If the user wants n8n instead of Claude Code, follow `docs/n8n.md` with them one step at a time.

Confirm with the user before every call that spends credits (1 Evaboot credit per exported lead), and never export more leads than they approved. Never send an email and never import leads into another tool without an explicit yes. Never ask for or handle another tool's API key: the user writes keys into `.env`. Never commit `.env` or `runs/`: they hold secrets and real people's data.
