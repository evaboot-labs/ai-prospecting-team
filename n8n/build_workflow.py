"""Builds n8n/ai-prospecting-team.json. Run: python3 n8n/build_workflow.py

The same four-agent team as the Claude Code version: the list builder reads an Evaboot export and keeps the
leads that match your filters with a safe email, a researcher agent finds one dated, sourced fact per company,
a qualifier agent scores each lead against your brief, and a writer agent drafts one email per kept lead.
The result is a CSV for any outreach tool. Nothing is sent.
"""
import json
import uuid
from pathlib import Path

EVABOOT_MCP = "https://mcp.evaboot.com/mcp"
EVABOOT_CRED = {"httpBearerAuth": {"id": "", "name": "Evaboot MCP (Bearer)"}}
ANTHROPIC_CRED = {"anthropicApi": {"id": "", "name": "Anthropic"}}
MODEL = "claude-sonnet-5-5"

nodes, connections = [], {}


def node(name, type_, version, params, pos, creds=None, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
         "typeVersion": version, "position": pos, **extra}
    if creds:
        n["credentials"] = creds
    nodes.append(n)


def link(a, b, kind="main", out=0):
    connections.setdefault(a, {}).setdefault(kind, [])
    while len(connections[a][kind]) <= out:
        connections[a][kind].append([])
    connections[a][kind][out].append({"node": b, "type": kind, "index": 0})


def agent(name, text, system, schema, pos):
    """One team member: an AI Agent node with its own Claude model and a structured output."""
    node(name, "@n8n/n8n-nodes-langchain.agent", 2.2, {
        "promptType": "define", "text": text, "hasOutputParser": True,
        "options": {"systemMessage": system, "maxIterations": 12},
    }, pos, retryOnFail=True, maxTries=2, waitBetweenTries=3000)
    node(f"Claude ({name.lower()})", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.3, {
        "model": {"__rl": True, "mode": "list", "value": MODEL, "cachedResultName": MODEL},
        "options": {"maxTokensToSample": 4000},
    }, [pos[0] - 80, pos[1] + 220], ANTHROPIC_CRED)
    node(f"{name} output", "@n8n/n8n-nodes-langchain.outputParserStructured", 1.3, {
        "schemaType": "manual", "inputSchema": json.dumps(schema, indent=2)}, [pos[0] + 60, pos[1] + 220])
    link(f"Claude ({name.lower()})", name, "ai_languageModel")
    link(f"{name} output", name, "ai_outputParser")


S = "$('Your settings').first().json"

KEEP_JS = r"""
// List builder: keep leads that match your filters with a safe email. Time in role = years + months.
const num = v => { const n = parseFloat(String(v ?? '').replace(/,/g, '')); return isNaN(n) ? null : n; };
const all = $json.structuredContent?.result?.prospects || [];
const kept = all.filter(p => p['Matches Filters'] === 'YES' && p['Email Status'] === 'safe');
return kept.map((p, i) => ({ json: {
  id: `lead-${String(i + 1).padStart(2, '0')}`,
  first_name: p['First Name'] || '', last_name: p['Last Name'] || '', email: p['Email'],
  title: String(p['Current Job'] || '').trim(), linkedin_url: p['Linkedin URL Public'] || '',
  months_in_role: (num(p['Years in Position']) || 0) * 12 + (num(p['Months in Position']) || 0),
  company: p['Company Name'] || '', company_domain: p['Company Domain'] || '',
  company_website: p['Company Website'] || '', company_headcount: num(p['Company Employee Exact Count']),
  company_industry: p['Company Industry'] || '', company_hq: p['Company Headquarters (Full Address)'] || '',
} }));
"""

ONE_PER_COMPANY_JS = r"""
// Qualifier rule: one lead per company, the highest score wins. Then keep score >= 60 and no disqualifier.
// Each row is joined to the lead it came from (paired items), never by position.
const rows = $input.all().map((it, i) => ({
  ...$('Keep matching leads').itemMatching(i).json,
  research: $('Researcher').itemMatching(i).json.output,
  ...it.json.output,
}));
const best = {};
for (const r of rows) if (r.keep && (!best[r.company] || r.score > best[r.company].score)) best[r.company] = r;
return Object.values(best).map(r => ({ json: r }));
"""

CSV_JS = r"""
return $input.all().map((it, i) => {
  const lead = $('One lead per company').itemMatching(i).json;
  return { json: {
    email: lead.email, first_name: lead.first_name, last_name: lead.last_name, company: lead.company,
    score: lead.score, subject: it.json.output.subject, body: it.json.output.body, source: lead.opener_source || '',
  } };
});
"""

RESEARCH_SYSTEM = """You are the researcher of a prospecting team. You find facts. You do not judge fit and you do not write emails.
For the company in the lead JSON: first call Search news with the company name in quotes; its results are dated headlines with links.
Then open the company website, or a news link, with Fetch page to confirm a fact (at most 6 calls in total).
Keep at most two facts from the last 12 months, newest first. A fact is something that happened, with the date the page shows and its URL.
"Opened 3 SDR roles, posted 2026-10-14" is a fact. "Growing fast" is not. Never guess a date. If nothing is found, set no_fact_found to true.
Also say in one line what the company sells, from its own site."""

QUALIFY_SYSTEM = """=You are the qualifier of a prospecting team. You judge. Use only the lead and research JSON.
Score 0 to 100: role 40 (the title is a buyer named in the brief), company 30 (industry, headcount and region match),
timing 20 (a dated, sourced fact gives a reason to talk now), tenure 10 (3 to 24 months in the role).
A missing field scores 0, never a guess. Then apply the brief's disqualifiers, and only those: any match sets keep to false.
Keep when the score is 60 or more and no disqualifier applies. The reason names the fields and facts used.
opener_fact is the research fact the writer should use (empty if none); opener_source is its URL.

Brief:
{{ """ + S + """.brief }}"""

WRITE_SYSTEM = """=You are the writer of a prospecting team. Write one first email from the brief and the opener fact. Never send.
Subject: 2 to 5 words, lower case. Line 1: the opener fact, said plainly. Line 2: why it matters to this role.
Line 3: the offer in one sentence, naming the product, with the proof from the brief. Line 4: one low-effort question.
Under 100 words, no links, blank line between paragraphs, signed with the sender name from the brief.
Never invent a fact, a number or a name. If opener_fact is empty, open on the role and company instead.

Brief:
{{ """ + S + """.brief }}"""

node("Run the team", "n8n-nodes-base.manualTrigger", 1, {}, [0, 0])
node("Your settings", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": str(uuid.uuid4()), "name": "export_id", "type": "string", "value": "PASTE_YOUR_EVABOOT_EXPORT_ID"},
    {"id": str(uuid.uuid4()), "name": "brief", "type": "string",
     "value": "PASTE YOUR BRIEF (see BRIEF.md): who you sell to, what disqualifies a lead, your offer, the sender name."},
]}, "options": {}}, [220, 0])
node("List builder", "@n8n/n8n-nodes-langchain.mcpClient", 1.1, {
    "endpointUrl": EVABOOT_MCP, "authentication": "bearerAuth",
    "tool": {"__rl": True, "mode": "list", "value": "get_export", "cachedResultName": "get_export"},
    "inputMode": "json", "jsonInput": "={{ JSON.stringify({ extraction_id: " + S + ".export_id }) }}",
    "options": {"timeout": 120000},
}, [440, 0], EVABOOT_CRED)
node("Keep matching leads", "n8n-nodes-base.code", 2, {"jsCode": KEEP_JS}, [660, 0])

agent("Researcher", "={{ JSON.stringify($json) }}", RESEARCH_SYSTEM, {
    "type": "object", "required": ["what_they_sell", "facts", "no_fact_found"], "properties": {
        "what_they_sell": {"type": "string"}, "no_fact_found": {"type": "boolean"},
        "facts": {"type": "array", "items": {"type": "object", "required": ["fact", "source", "date"], "properties": {
            "fact": {"type": "string"}, "source": {"type": "string"}, "date": {"type": "string"}}}}}}, [900, 0])
node("Fetch page", "n8n-nodes-base.httpRequestTool", 4.2, {
    "toolDescription": "Open a web page and return its text. Give the full URL.",
    "url": "={{ $fromAI('url', 'The full URL of the page to open', 'string') }}",
    "options": {"response": {"response": {"responseFormat": "text"}}, "timeout": 20000},
    "optimizeResponse": True, "responseType": "html", "cssSelector": "body", "onlyContent": True,
    "truncateResponse": True, "maxLength": 12000,
}, [1100, 220])
link("Fetch page", "Researcher", "ai_tool")
node("Search news", "n8n-nodes-base.httpRequestTool", 4.2, {
    "toolDescription": "Search recent news about a company. Give a query such as \"Acme Ltd\". Returns dated headlines with links.",
    "url": "=https://news.google.com/rss/search?q={{ encodeURIComponent($fromAI('query', 'The company name in quotes', 'string')) }}&hl=en-GB&gl=GB&ceid=GB:en",
    "options": {"response": {"response": {"responseFormat": "text"}}, "timeout": 20000},
    "optimizeResponse": True, "responseType": "text", "truncateResponse": True, "maxLength": 8000,
}, [1240, 220])
link("Search news", "Researcher", "ai_tool")

agent("Qualifier",
      "={{ JSON.stringify({ lead: $('Keep matching leads').item.json, research: $json.output }) }}",
      QUALIFY_SYSTEM, {
          "type": "object", "required": ["score", "keep", "reason", "opener_fact", "opener_source"], "properties": {
              "score": {"type": "number"}, "keep": {"type": "boolean"}, "reason": {"type": "string"},
              "opener_fact": {"type": "string"}, "opener_source": {"type": "string"}}}, [1480, 0])
node("One lead per company", "n8n-nodes-base.code", 2, {"jsCode": ONE_PER_COMPANY_JS}, [1720, 0])
agent("Writer", "={{ JSON.stringify($json) }}", WRITE_SYSTEM, {
    "type": "object", "required": ["subject", "body"], "properties": {
        "subject": {"type": "string"}, "body": {"type": "string"}}}, [1960, 0])
node("Email rows", "n8n-nodes-base.code", 2, {"jsCode": CSV_JS}, [2200, 0])
node("Emails CSV", "n8n-nodes-base.convertToFile", 1.1, {
    "operation": "csv", "options": {"fileName": "emails.csv"}}, [2420, 0])

for a, b in [("Run the team", "Your settings"), ("Your settings", "List builder"),
             ("List builder", "Keep matching leads"), ("Keep matching leads", "Researcher"),
             ("Researcher", "Qualifier"), ("Qualifier", "One lead per company"),
             ("One lead per company", "Writer"), ("Writer", "Email rows"), ("Email rows", "Emails CSV")]:
    link(a, b)

workflow = {"name": "AI prospecting team (Evaboot + Claude)", "nodes": nodes, "connections": connections,
            "settings": {"executionOrder": "v1"}, "pinData": {}}
out = Path(__file__).with_name("ai-prospecting-team.json")
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(out, len(nodes), "nodes")
