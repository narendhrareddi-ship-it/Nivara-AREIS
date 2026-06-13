# Permanent Dashboard Deployment

The NIVARA dashboard is a **Streamlit** Python app. It needs a persistent server with WebSocket support.

## Can I use Vercel?

**No — not for the current Streamlit dashboard.**

| Platform | Works with Streamlit? | Why |
|----------|----------------------|-----|
| **Vercel** | No | Serverless functions timeout; no persistent WebSockets |
| **Render** | Yes | Long-running process, WebSockets, custom domain |
| **Streamlit Community Cloud** | Yes | Built for Streamlit, free tier, GitHub deploy |
| **Railway / Fly.io** | Yes | Container hosting with persistent processes |
| **Docker on VPS** | Yes | Full control |

### If you must use Vercel

You would need to **rebuild the dashboard as Next.js** (React frontend + API routes calling your orchestrator/MCP backends). That is a separate project — not a config change.

**Recommended Vercel stack (future):**
- Next.js 15 + Tailwind on Vercel (frontend)
- API routes proxy to Render/Railway-hosted MCP servers
- Supabase for database (already in project)

---

## Option 1 — Streamlit Community Cloud (fastest permanent URL)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set **Main file path**: `dashboard/app.py`
4. Add secrets in the dashboard:

```toml
DB_HOST = "your-db-host"
DB_PORT = "5432"
DB_USER = "nivara"
DB_PASSWORD = "your-password"
ORCHESTRATOR_URL = "https://your-orchestrator.onrender.com"
VEO_MCP_URL = "https://your-veo-mcp.onrender.com"
```

5. Deploy → you get a permanent URL like `https://nivara-areis.streamlit.app`

**Pros:** Free, zero DevOps, auto-redeploy on git push  
**Cons:** Backend services (Postgres, MCP) must be reachable from the internet

---

## Option 2 — Render (recommended for full stack)

This repo includes `render.yaml` for one-click deploy.

1. Create account at [render.com](https://render.com)
2. **New → Blueprint** → connect GitHub repo
3. Set environment variables for DB and MCP URLs
4. Deploy

You get a permanent URL: `https://nivara-dashboard.onrender.com`

Add a **custom domain** in Render dashboard (e.g. `dashboard.nivara.ai`).

**Pros:** Custom domain, always-on on paid tier, health checks  
**Cons:** Free tier has cold starts (~30s)

---

## Option 3 — Docker (production)

```bash
docker build -t nivara-dashboard ./dashboard
docker run -p 8501:8501 \
  -e DB_HOST=your-host \
  -e VEO_MCP_URL=http://veo-mcp:8006 \
  nivara-dashboard
```

Use with Railway, Fly.io, AWS ECS, or any VPS.

---

## Environment variables

| Variable | Required | Example |
|----------|----------|---------|
| `DB_HOST` | Yes | `dpg-xxxxx.render.com` |
| `DB_PORT` | Yes | `5432` |
| `ORCHESTRATOR_URL` | For pipeline | `https://nivara-orchestrator.onrender.com` |
| `VEO_MCP_URL` | For Media tab | `https://nivara-veo.onrender.com` |
| `OLLAMA_BASE_URL` | Optional | `http://localhost:11434` |

---

## Permanent URL checklist

- [ ] Deploy dashboard to Streamlit Cloud or Render
- [ ] Deploy `veo-mcp` and `social-mcp` (Render/Railway)
- [ ] Use Supabase or Render Postgres (not localhost)
- [ ] Set custom domain in hosting panel
- [ ] Remove temporary Cloudflare tunnels (`dashboard.url`)

---

## Architecture (production)

```mermaid
flowchart LR
    User[Browser] --> Dashboard[Streamlit on Render]
    Dashboard --> DB[(Supabase Postgres)]
    Dashboard --> Orch[Orchestrator API]
    Dashboard --> Veo[veo-mcp]
    Veo --> Gemini[Gemini Veo API]
    Veo --> Social[social-mcp]
```

Temporary `trycloudflare.com` / `loca.lt` URLs are for development only. Use Streamlit Cloud or Render for a permanent fix.
