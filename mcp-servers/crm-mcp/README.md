# CRM MCP Server

Supabase-backed MCP server for NIVARA REALTY CRM operations.

## Tools

- `list_leads` — Filter leads by status
- `get_lead` — Fetch lead by ID
- `create_lead` — Insert new lead
- `update_lead` — Update status/score
- `log_activity` — Log CRM activity
- `list_campaigns` — List active campaigns

## Setup

```bash
pip install fastapi uvicorn python-dotenv supabase httpx
export SUPABASE_URL=...
export SUPABASE_SERVICE_ROLE_KEY=...
python server.py
```

Runs on port **8001** (configurable via `CRM_MCP_PORT`).

## Cursor MCP Config (example)

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "nivara-crm": {
      "url": "http://localhost:8001"
    }
  }
}
```

Tool descriptors: `tools.json`
