# One-click Render setup (dashboard + backend)

The dashboard is now defined in `render.yaml` as **nivara-dashboard**.

Stable URL after deploy: **https://nivara-dashboard.onrender.com**

## What was done automatically (in this repo)

- Merged PR #5 to `main` (speed fixes, video UI, permanent shortcut launcher)
- Pipeline synced to **20/20** agents in Supabase
- Added `nivara-dashboard` service to `render.yaml`
- Default shortcut URL → Render (not dead Streamlit URL)
- Bootstrap script: `python3 scripts/bootstrap-all.py`

## One step you must do on Render (2 minutes)

Render cannot be controlled from this agent without your Render login.

1. Open **https://dashboard.render.com**
2. Open your **Nivara** blueprint (or connect repo `narendhrareddi-ship-it/Nivara-AREIS`)
3. Click **Sync Blueprint** / **Apply** — creates `nivara-dashboard`
4. For **each** service missing env vars, set:

| Key | Value |
|-----|-------|
| `DB_PASSWORD` | Your Supabase DB password |
| `GEMINI_API_KEY` | Your Gemini key (optional, for LLM/video) |
| `GROQ_API_KEY` | Your Groq key (optional) |

5. Wait until **nivara-dashboard** shows **Live**
6. Open **https://nivara-dashboard.onrender.com**

## Windows shortcut (after Render is live)

```
Install-NIVARA-Desktop-Shortcut.bat
```

Uses local launcher → opens `https://nivara-dashboard.onrender.com`

## Optional: Streamlit Cloud

Only if you prefer Streamlit over Render:

1. https://share.streamlit.io → deploy `streamlit_app.py`
2. Subdomain: `nivara-areis`
3. Paste secrets from `generated/streamlit-secrets.toml` (run bootstrap script locally)

## Verify everything

```bash
python3 scripts/bootstrap-all.py
```

All checks should show `[OK]`.
