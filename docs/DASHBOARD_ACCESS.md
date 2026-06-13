# Dashboard Access

## Permanent URL (recommended)

Deploy to **Streamlit Community Cloud** for a fixed public URL:

**https://your-app-name.streamlit.app**

Setup guide: **[docs/DEPLOYMENT.md](DEPLOYMENT.md)**

---

## Local development

```bash
pip install -r dashboard/requirements.txt
cp dashboard/.streamlit/secrets.toml.example dashboard/.streamlit/secrets.toml
./scripts/start-dashboard.sh
```

Open http://localhost:8501

---

## Temporary preview (dev only)

For quick previews during agent development, a temporary tunnel may be used. These URLs **expire** — use Streamlit Cloud for production.

```bash
./scripts/start-dashboard-public.sh   # dev tunnel only
```

---

## Verify locally

```bash
curl http://localhost:8501/_stcore/health   # → ok
curl http://localhost:8006/health           # veo-mcp
curl http://localhost:8003/health           # social-mcp
```
