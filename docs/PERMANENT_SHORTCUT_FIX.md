# Permanent fix: Streamlit shortcut / access error

## Why this keeps happening

Your shortcuts were opening **https://nivara-areis.streamlit.app/** directly. That URL currently returns **404** — the Streamlit Cloud app is **not deployed** (or was deleted). Streamlit then shows:

> You do not have access to this app or it does not exist

Each redeploy without a fixed subdomain creates a **new random URL**, so hardcoded shortcuts break again.

## Permanent fix (do this once)

### Step 1 — Install the new shortcut system (Windows)

In the project folder, double-click:

```
Install-NIVARA-Desktop-Shortcut.bat
```

This creates a Desktop shortcut that opens a **local launcher** (`%LOCALAPPDATA%\NIVARA\`), not a fragile web URL.

### Step 2 — Deploy on Streamlit Cloud (one time)

1. Open **https://share.streamlit.io**
2. Sign in with GitHub → **narendhrareddi-ship-it** (same as realitynivara@gmail.com)
3. Click **Create app**
4. Paste:

```
https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py
```

5. Set fields:

| Field | Value |
|-------|-------|
| Repository | `narendhrareddi-ship-it/Nivara-AREIS` |
| Branch | `main` |
| Main file | `streamlit_app.py` |
| **Custom subdomain** | **`nivara-areis`** |

6. **Deploy** → wait until status is **Running**

### Step 3 — Add secrets (required)

Settings → Secrets:

```toml
SUPABASE_URL = "https://mxjhwjxxqtkwsrwtqwuc.supabase.co"
DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.mxjhwjxxqtkwsrwtqwuc"
DB_PASSWORD = "YOUR_REAL_SUPABASE_PASSWORD"
ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"
VEO_MCP_URL = "https://nivara-veo-mcp.onrender.com"
AUTO_SYNC_ON_LOAD = "false"
```

Save → **Reboot app**.

### Step 4 — Save URL in launcher

Double-click **Fix-NIVARA-Shortcut.bat** → paste:

```
https://nivara-areis.streamlit.app/
```

Click **Save & Open**.

---

## After this, redeploys will NOT break your shortcut

| What | Behavior |
|------|----------|
| Desktop shortcut | Always opens local launcher |
| URL storage | `%LOCALAPPDATA%\NIVARA\dashboard.url` |
| App redeployed / URL changed | Run Fix-NIVARA-Shortcut.bat once, paste new URL |
| Same subdomain `nivara-areis` | URL stays **https://nivara-areis.streamlit.app/** forever |

---

## If "access denied" (not 404)

1. On share.streamlit.io, confirm workspace is **narendhrareddi-ship-it** (top-right avatar)
2. GitHub → Settings → Applications → Streamlit → grant org/repo access
3. Repo must be **public** OR Streamlit must have private repo OAuth scope
4. Try incognito window after deploy succeeds

---

## Quick repair (Win+R)

After installing the launcher once:

```
%LOCALAPPDATA%\NIVARA\NIVARA-Dashboard.bat
```
