# MCP Servers

Local MCP stub servers for NIVARA REALTY Phase 1.

| Server | Port | Status |
|--------|------|--------|
| `crm-mcp` | 8001 | Working (requires Postgres) |
| `browser-mcp` | 8002 | Stub (httpx; Playwright optional) |
| `social-mcp` | 8003 | Mock with video support |
| `whatsapp-mcp` | 8004 | Mock webhook + lead scoring |
| `higgsfield-mcp` | 8006 | Photo upload + image-to-video + social publish |

## Quick Start

```bash
# From project root, with .env configured
pip install fastapi uvicorn python-dotenv httpx supabase

# Terminal 1-4
python mcp-servers/crm-mcp/server.py
python mcp-servers/browser-mcp/server.py
python mcp-servers/social-mcp/server.py
python mcp-servers/whatsapp-mcp/server.py
python mcp-servers/higgsfield-mcp/server.py
```

Each server exposes:
- `GET /health` — health check
- `GET /tools` — tool descriptors
- `POST /call` — invoke a tool by name

## Cursor Integration

See individual server READMEs for MCP config examples.
