# Dashboard Access Guide

## Why `http://localhost:8501` may not work in your browser

`localhost` always means **the machine where the browser is running**.

| Where you open the link | What `localhost:8501` means |
|-------------------------|-----------------------------|
| Your laptop browser | Your laptop — dashboard is **not** there |
| Cursor Cloud Agent VM | The VM — dashboard **is** there |

The NIVARA dashboard runs on the **cloud VM** where the agent works. Unless you use port forwarding or a public tunnel, typing `localhost:8501` on your laptop will not reach it.

That is a networking limitation, not a missing dashboard update.

---

## Direct link (no Cursor port forwarding)

A public HTTPS tunnel is running so you can open the dashboard directly:

**Current dashboard URL:** see [`dashboard.url`](../dashboard.url) in the repo root.

As of the last agent run:

**https://untitled-measurement-formation-algorithm.trycloudflare.com**

Open that link in any browser. Go to the **MEDIA** tab to test photo → Veo video → social post.

> Note: Cloudflare quick-tunnel URLs change when the tunnel restarts. Re-run the script below to get a fresh link.

### Regenerate the public URL

```bash
./scripts/start-dashboard-public.sh
```

This prints the new URL and saves it to `dashboard.url`.

---

## Option: Cursor port forwarding

If you prefer localhost on your machine:

1. Open this agent in the **Cursor Agents** window.
2. Click the **plug icon** (Ports) in the top-right.
3. Forward port **8501**.
4. Open the forwarded URL Cursor shows.

---

## Option: Run locally on your laptop

```bash
git clone https://github.com/narendhrareddi-ship-it/Nivara-AREIS.git
cd Nivara-AREIS
pip install -r dashboard/requirements.txt
./scripts/start-dashboard.sh
```

Then `http://localhost:8501` works because the dashboard runs on **your** machine.

---

## Verify services

```bash
curl http://localhost:8501/_stcore/health          # → ok
curl http://localhost:8006/health                  # veo-mcp
curl http://localhost:8003/health                  # social-mcp
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Public URL expired | Run `./scripts/start-dashboard-public.sh` |
| Page won't load on laptop localhost | Use the public URL in `dashboard.url` |
| MEDIA tab upload fails | Ensure `veo-mcp` is running on :8006 |
| No data shown | Ensure PostgreSQL is running and migrations applied |
