# Dashboard Access Guide

The NIVARA dashboard is a **Streamlit app on port 8501**. It runs on the same machine as the agents and MCP servers.

## Cloud Agent (Cursor VM)

If this project is running in a **Cursor Cloud Agent**, `localhost:8501` in the VM is **not** the same as `localhost` in your browser unless port forwarding is active.

### Option A — Cursor port forwarding (recommended)

1. Open this agent in the **Cursor Agents** window (not only the PR on GitHub).
2. Click the **plug icon** (Ports) in the top-right of the agent panel.
3. Confirm port **8501** is forwarded. If not, add it manually.
4. Open the forwarded URL (usually `http://localhost:8501` on your machine).

If port 8501 is already in use locally, Cursor may map it to another port (e.g. `8502`) — use the port shown in the Ports panel.

### Option B — Run the dashboard on your own machine

```bash
# From repo root
cp .env.example .env   # set DB_* if using local Postgres
pip install -r dashboard/requirements.txt
./scripts/start-dashboard.sh
```

Then open http://localhost:8501 in your browser.

## Start / restart dashboard (on the VM)

```bash
./scripts/start-dashboard.sh
```

Or with tmux:

```bash
tmux -f /exec-daemon/tmux.portal.conf new-session -d -s nivara-dashboard -c /workspace \
  './scripts/start-dashboard.sh'
```

## Verify it is running

```bash
curl -s http://localhost:8501/_stcore/health
# Expected: ok
```

## Required services for MEDIA tab

| Service | Port | Health check |
|---------|------|--------------|
| Dashboard | 8501 | `curl localhost:8501/_stcore/health` |
| veo-mcp | 8006 | `curl localhost:8006/health` |
| social-mcp | 8003 | `curl localhost:8003/health` |
| PostgreSQL | 5432 | `psql -h localhost -U nivara -d nivara` |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Page won't load | Use Cursor Ports panel; don't use the VM's public IP |
| Blank / spinning forever | Restart dashboard: `./scripts/start-dashboard.sh` |
| MEDIA tab upload fails | Ensure `veo-mcp` is running on :8006 |
| No projects/leads data | Check Postgres is up and migrations are applied |
