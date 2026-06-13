# Phase 5 — Production Hardening

Phase 5 closes the gap between the 20-agent prototype and a trustworthy production deployment for **Bangalore real estate**.

## What Changed

| Area | Change |
|------|--------|
| **Cloud LLM** | Ollama-first with automatic fallback to Groq, Gemini, or OpenRouter |
| **WhatsApp MCP URL** | `WhatsAppAgent` reads `WHATSAPP_MCP_URL` (no hardcoded localhost) |
| **Dashboard simulation** | Disabled by default; enable with `ENABLE_DASHBOARD_SIMULATION=true` |
| **API auth** | Optional `ORCHESTRATOR_API_KEY` + `X-API-Key` header on `/orchestrate` |
| **N8N workflows** | Bangalore region, orchestrator port 8000, 20-agent pipeline |
| **Render** | LLM + auth env vars in `render.yaml` |

## Cloud LLM Setup (P0)

On Render (or any cloud host without Ollama), set **one** of these API keys:

```bash
# Recommended: Groq free tier — https://console.groq.com
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# Or reuse Gemini key (same as Veo)
GEMINI_API_KEY=...
GEMINI_LLM_MODEL=gemini-2.0-flash

# Or OpenRouter — https://openrouter.ai
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct

LLM_PROVIDER=auto   # default: try Ollama, then cloud
```

Verify after deploy:

```bash
curl https://your-orchestrator.onrender.com/health
# → "llm_provider": "groq" (or gemini/openrouter)
```

## Dashboard Simulation (P2)

The Streamlit dashboard **no longer fabricates** bot logs, leads, or posts by default.

To re-enable demo mode locally:

```toml
# Streamlit secrets or .env
ENABLE_DASHBOARD_SIMULATION = "true"
```

For a real 20/20 pipeline bar, run the full orchestrator once:

```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_KEY_IF_SET" \
  -d '{"task":"daily_market_analysis","region":"Bangalore"}'
```

Or clear stale 12-agent logs and re-run:

```bash
python scripts/reset-pipeline-logs.py
```

## API Authentication (P3)

Set `ORCHESTRATOR_API_KEY` on Render. All `/orchestrate` calls must include:

```
X-API-Key: your-secret-key
```

`/health` remains public for Render health checks.

## N8N Import

Re-import all workflows from `n8n/workflows/` — they now target:

- Region: **Bangalore**
- Orchestrator: **:8000** (was :8005)
- Full pipeline on daily trigger (no `agents` filter)

## Remaining (Phase 6 preview)

- Real Meta + WhatsApp Business API (replace MCP mocks)
- Deploy `whatsapp-mcp` to Render
- Live Google/Meta ad analytics in N8N
- Automated tests + monitoring

See **[docs/PRODUCTION.md](PRODUCTION.md)** for full deploy checklist.
