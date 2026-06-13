# Phase 1 Setup Guide

Step-by-step instructions to run NIVARA REALTY locally using **only free/open-source tools**.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker + Docker Compose (Linux)
- Python 3.11+
- Git
- Free Supabase account: https://supabase.com

## Step 1: Clone / Open Project

```bash
cd ~/Projects/nivara-digital-marketing
cp .env.example .env
```

## Step 2: Supabase (Free Tier)

1. Create a new project at https://supabase.com (free tier)
2. Go to **SQL Editor** → run migrations in order:
   - `supabase/migrations/001_initial_schema.sql`
   - `supabase/migrations/002_phase2_media_and_bot_logs.sql`
3. Optionally run `supabase/seed.sql` for sample Chennai/Andhra data
4. Copy from **Settings → API**:
   - Project URL → `SUPABASE_URL`
   - `anon` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`
5. Paste into `.env` and `agents/.env`

## Step 3: Start Docker Services

```bash
docker compose up -d
```

This starts:
- **N8N** at http://localhost:5678 (admin/changeme — change in `.env`)
- **Ollama** at http://localhost:11434

Pull an Ollama model:

```bash
docker exec -it nivara-ollama ollama pull llama3.2
# Alternative: docker exec -it nivara-ollama ollama pull mistral
```

Update `OLLAMA_MODEL` in `.env` if using Mistral.

## Step 4: Import N8N Workflows

1. Open http://localhost:5678
2. **Settings → Variables** — add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
3. **Workflows → Import from File** — import all JSON from `n8n/workflows/`
4. Activate workflows

Test lead intake:

```bash
curl -X POST http://localhost:5678/webhook/lead-intake \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","phone":"+919999999998","city":"Chennai","budget_min":5000000}'
```

## Step 5: Agent Orchestrator

```bash
cd agents
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -e .
cp .env.example .env        # Add Supabase keys
nivara-orchestrator
```

API docs: http://localhost:8000/docs

Test:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task":"daily_market_analysis","region":"Chennai"}'
```

## Step 6: MCP Servers (Optional)

```bash
pip install fastapi uvicorn python-dotenv httpx supabase psycopg2-binary python-multipart

# Run each in a separate terminal
python mcp-servers/crm-mcp/server.py      # :8001
python mcp-servers/browser-mcp/server.py  # :8002
python mcp-servers/social-mcp/server.py   # :8003
python mcp-servers/whatsapp-mcp/server.py  # :8004
python mcp-servers/higgsfield-mcp/server.py  # :8006
```

## Step 7: Higgsfield Photo-to-Video (Phase 2)

See **[PHASE2_HIGGSFIELD.md](PHASE2_HIGGSFIELD.md)** for site photo upload and social video posting.

Test WhatsApp mock:

```bash
curl -X POST http://localhost:8004/webhook/message \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210","message":"Need 3BHK in OMR budget 80 lakhs site visit"}'
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Ollama offline | `docker compose up -d ollama` + pull model |
| Supabase RLS errors | Use `service_role` key for backend, not `anon` |
| N8N can't reach agents | Use `host.docker.internal` (Windows/Mac) or host IP on Linux |
| Agent stub responses | Ollama not running — agents fall back to stub text |

## Verification Checklist

- [ ] Supabase tables created (10 tables)
- [ ] Seed data visible in Supabase Table Editor
- [ ] N8N accessible, workflows imported
- [ ] Ollama model pulled, `/api/tags` returns models
- [ ] Agent orchestrator `/health` shows ollama: true
- [ ] Lead webhook creates row in `leads` table
- [ ] MCP servers respond on ports 8001-8004, 8006
- [ ] Higgsfield MCP `/health` shows configured or mock mode
- [ ] Dashboard MEDIA tab can upload photos

## Next: Phase 2

See `FREE_TIER_LIMITS.md` and `AGENT_ROSTER.md` for the roadmap.
