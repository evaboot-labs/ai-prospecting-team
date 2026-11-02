# Run it in n8n

[`n8n/ai-prospecting-team.json`](../n8n/ai-prospecting-team.json) is the same team as n8n nodes, for when you prefer n8n to Claude Code. Each agent is an AI Agent node with its own Claude model and its own tools.

## What runs

1. **Your settings** (Set): the id of an Evaboot export and your brief.
2. **List builder** (Evaboot MCP) and **Keep matching leads** (Code): reads the export and keeps leads where Matches Filters is YES and the email is safe.
3. **Researcher** (AI Agent, once per lead): two tools only, **Search news** (Google News RSS, dated headlines) and **Fetch page** (opens a URL). It returns up to two dated facts with their source.
4. **Qualifier** (AI Agent, once per lead): scores role, company, timing and tenure against your brief. No tools.
5. **One lead per company** (Code): keeps the best-scored lead at each company.
6. **Writer** (AI Agent): one subject and body per kept lead, from your brief and the fact the qualifier picked. No tools.
7. **Email rows** and **Emails CSV**: a CSV file to load into any outreach tool (lemlist, for example).

## Set it up

1. **Run an export** in Evaboot (the Chrome extension, the dashboard or the Evaboot MCP), capped at the number of leads you want. Copy its id from the export page URL or from the MCP's answer.
2. **Import** the JSON: *Workflows > Import from file*.
3. **Add two credentials:**
   - **Bearer Auth** named `Evaboot MCP (Bearer)`: your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/). Select it on **List builder**.
   - **Anthropic**: select it on the three Claude nodes.
4. **Fill in Your settings**: the export id, and your brief from [BRIEF.md](../BRIEF.md).
5. **Test:** click *Execute workflow*, then open **Emails CSV** and download the file.

## Good to know

- Rerunning on the same export costs no Evaboot credits: only the Claude calls are paid.
- Nothing is sent. You load the CSV into your outreach tool after you read it.

Back to the [README](../README.md).
