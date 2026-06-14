# One-click Render setup

## Fully automated (recommended)

### Step 1 — Add GitHub secrets (one time)

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `RENDER_API_KEY` | From https://dashboard.render.com/u/settings#api-keys |
| `DB_PASSWORD` | Your Supabase database password |
| `GEMINI_API_KEY` | Optional — from `.env` |
| `GROQ_API_KEY` | Optional |
| `SUPABASE_URL` | `https://mxjhwjxxqtkwsrwtqwuc.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | From Supabase project settings |

### Step 2 — Run workflow

GitHub → **Actions → Render Auto-Setup → Run workflow**

This sets env vars on all 4 services and triggers deploys.

---

## Local automation

```bash
cp .env.render.example .env.render
# Edit .env.render → add RENDER_API_KEY=rnd_...
python3 scripts/render-setup.py
```

Reads `DB_PASSWORD` and other secrets from `.env`.

---

## Manual fallback (no API key)

1. https://dashboard.render.com → Blueprints → **Sync** repo `nivara-AREIS`
2. When prompted, fill **nivara-secrets** group once:
   - `DB_PASSWORD` = your Supabase password
   - `GEMINI_API_KEY` = optional
3. Wait for **nivara-dashboard** → Live
4. Open https://nivara-dashboard.onrender.com

---

## Verify

```bash
python3 scripts/bootstrap-all.py
```

Dashboard: https://nivara-dashboard.onrender.com  
Orchestrator should show `"db_connected": true` after password is set.
