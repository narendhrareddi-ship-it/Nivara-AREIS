# Render — One-Time Environment Setup

After merging to `main`, Render auto-rebuilds Docker images. **DB host/user are baked into the image.** Only the password must be set manually once.

## 1. Set DB_PASSWORD on all 3 services

Go to [Render Dashboard](https://dashboard.render.com) → each service → **Environment**:

| Service | Variable | Value |
|---------|----------|-------|
| `nivara-orchestrator` | `DB_PASSWORD` | Your Supabase database password |
| `nivara-veo-mcp` | `DB_PASSWORD` | Same password |
| `nivara-social-mcp` | `DB_PASSWORD` | Same password |

Optional (recommended):

| Variable | Value |
|----------|-------|
| `GROQ_API_KEY` | Groq API key (free tier) |
| `GEMINI_API_KEY` | Gemini key (Veo + LLM) |

Click **Save Changes** → **Manual Deploy** on each service.

## 2. Verify

```bash
curl https://nivara-orchestrator.onrender.com/health
```

Expected:

```json
{
  "agent_count": 20,
  "db_connected": true,
  "pipeline_version": "20-agent"
}
```

## 3. Run full pipeline

```bash
curl -X POST https://nivara-orchestrator.onrender.com/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task":"daily_market_analysis","region":"Bangalore"}'
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `db_connected: false` + localhost | Redeploy from latest `main` (fixed in Dockerfile) |
| `ECIRCUITBREAKER` auth failures | Wrong `DB_PASSWORD` on Render — fix password, wait 5 min, redeploy |
| `agent_count: 12` | Old image — Manual Deploy from latest `main` |
| Pipeline 12/20 on dashboard | Streamlit auto-syncs in-process; reboot app from latest `main` |

## Streamlit Cloud

Reboot after `main` merge: [share.streamlit.io](https://share.streamlit.io) → your app → ⋮ → **Reboot app**

Secrets should include:

```toml
DB_PASSWORD = "your-supabase-password"
ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"
AUTO_SYNC_PIPELINE = "true"
GROQ_API_KEY = "..."  # optional
```
