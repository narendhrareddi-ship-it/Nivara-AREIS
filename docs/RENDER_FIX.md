# Render deploy failures — fixes applied

## Root causes found

| Service | Issue | Fix |
|---------|-------|-----|
| **nivara-dashboard** | Streamlit listened on **8501**; Render routes to **`$PORT`** → health check failed → deploy loop | `dashboard/start.sh` binds to `$PORT` |
| **nivara-dashboard** | Heavy agents package caused OOM/slow start on free tier | `requirements-render.txt` (no `-e ./agents`) |
| **nivara-dashboard** | No health check path | `healthCheckPath: /_stcore/health` in render.yaml |
| **nivara-orchestrator** | `db_connected: false` | Set **`DB_PASSWORD`** in Render dashboard (all 4 services) |
| **orchestrator / veo** | `fromService: hostport` URLs missing `https://` | Hardcoded `https://nivara-*.onrender.com` |

## After merging — on Render (2 min)

1. **dashboard.render.com** → your blueprint → **Manual Deploy** or wait for auto-deploy from `main`
2. Set **`DB_PASSWORD`** on **every** service if not set:
   - nivara-orchestrator
   - nivara-veo-mcp
   - nivara-social-mcp
   - nivara-dashboard
3. Value = your Supabase database password (pooler user `postgres.mxjhwjxxqtkwsrwtqwuc`)
4. **Save** → **Clear build cache & deploy** on nivara-dashboard

## Verify

```bash
curl https://nivara-dashboard.onrender.com/_stcore/health
curl https://nivara-orchestrator.onrender.com/health
```

Dashboard health should return `ok`. Orchestrator should show `"db_connected": true` after password is set.

## Optional env vars

| Key | Service | Purpose |
|-----|---------|---------|
| `GEMINI_API_KEY` | orchestrator, veo-mcp, dashboard | Real LLM + video |
| `GROQ_API_KEY` | orchestrator, dashboard | LLM fallback |
| `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` | veo-mcp | Storage uploads |
