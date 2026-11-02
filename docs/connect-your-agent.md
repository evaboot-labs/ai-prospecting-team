# Connect your AI Agent

The team needs one MCP server: Evaboot. Only the list builder uses it.

## 1. Account

An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=ai-prospecting-team-repo) with credits, and a Sales Navigator seat connected to it through the Evaboot Chrome extension.

## 2. Get the repo

```bash
git clone https://github.com/evaboot-labs/ai-prospecting-team
cd ai-prospecting-team
cp .env.example .env
```

## 3. Connect the Evaboot MCP

**Claude Code:** write your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/) into `.env` as `EVABOOT_API_KEY`, load it (`set -a; . ./.env; set +a`), then start Claude Code from this folder. It reads `.mcp.json` and asks you to approve the `evaboot` server. Or sign in with a Claude account that already has the Evaboot connector (*Settings > Connectors > Add custom connector*, URL `https://mcp.evaboot.com/mcp`).

**Claude Code plugin** (installed with `/plugin install`, no clone): export your key before you start Claude Code, `export EVABOOT_API_KEY=<your key>`. Without it the `evaboot` server does not connect.

**Codex, Cursor:** add `https://mcp.evaboot.com/mcp` as an HTTP MCP server with the header `Authorization: Bearer <your key>`. These agents have no subagents: the skill then runs the four steps itself, one after the other, with the same files.

## 4. Check

Ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected." Then type `/agents` in Claude Code: `list-builder`, `researcher`, `qualifier` and `writer` must be listed.

Back to the [README](../README.md).
