# Phase 3 — Growth Agents & Production Hosting

Phase 3 adds four marketing agents and production deployment configs so the Streamlit dashboard can reach backend services over HTTPS.

## New agents (16 total)

| Agent | Role | Inserted in pipeline |
|-------|------|----------------------|
| **LocationScout** | OMR/ECR/Amaravati micro-market analysis | After MarketAnalyst |
| **Copywriter** | Ad copy, landing pages, email sequences | After ContentStrategist |
| **PaidAdsManager** | Google/Meta budget and CPL optimization | After SocialMediaManager |
| **EmailMarketer** | Drip campaigns and newsletters | After WhatsAppAgent |

### Updated pipeline

```
MarketAnalyst → LocationScout → CompetitorSpy → ContentStrategist → Copywriter
  → SEOAgent → VisualDesigner → SocialMediaManager → PaidAdsManager
  → LeadQualification → WhatsAppAgent → EmailMarketer → AppointmentScheduler
  → CRM → Analytics → CEO
```

## Supabase Storage for media

Site photos and videos can be stored in a Supabase Storage bucket instead of local disk (required for Render/cloud hosting).

### Setup

1. In Supabase Dashboard → **Storage** → create bucket `media` (public read).
2. Add env vars to `veo-mcp` and local `.env`:

```bash
USE_SUPABASE_STORAGE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=media
```

3. Set `MEDIA_PUBLIC_BASE_URL` to the bucket public URL prefix if serving via CDN.

When storage is configured, `veo-mcp` uploads photos to `photos/` and records `metadata.storage_path` on `media_assets` rows.

## Render deployment

[`render.yaml`](../render.yaml) defines three web services:

| Service | Port | Purpose |
|---------|------|---------|
| `nivara-orchestrator` | 8000 | LangGraph agent API |
| `nivara-veo-mcp` | 8006 | Photo upload + Gemini Veo |
| `nivara-social-mcp` | 8003 | Social post logging |

### Deploy steps

1. Push this repo to GitHub.
2. In [Render](https://render.com) → **New → Blueprint** → connect repo.
3. Set secret env vars when prompted:
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD` (Supabase pooler)
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
   - `OLLAMA_BASE_URL` (cloud Ollama or disable stub mode)
4. After deploy, copy service URLs into Streamlit secrets:

```toml
ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"
VEO_MCP_URL = "https://nivara-veo-mcp.onrender.com"
```

5. Reboot the Streamlit app.

## Email integration (optional)

`EmailMarketer` logs CRM activities and can call an external API when configured:

```bash
EMAIL_API_URL=https://api.resend.com/emails
EMAIL_API_KEY=re_xxxx
```

Without these vars, emails are logged as mock sends in agent output.

## Phase 4 (next)

- COO, CMO, SalesCoach, RegulatoryWatch
- Real Meta/WhatsApp APIs (replace social-mcp mocks)
- Playwright browser scraping in browser-mcp
