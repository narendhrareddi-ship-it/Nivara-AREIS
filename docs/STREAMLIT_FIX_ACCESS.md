# Fix: "You do not have access to this app or it does not exist"

That error means the **Streamlit Cloud app is not deployed** (or was deleted) under your account. The shortcut URL is dead — not a problem with your desktop icon.

## Fix in 5 minutes (Windows + your GitHub account)

You are signed in as **realitynivara@gmail.com** / **narendhrareddi-ship-it** — use that same GitHub on Streamlit.

### Step 1 — Open Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Sign in with **GitHub** → account **narendhrareddi-ship-it**
3. If asked, authorize Streamlit to access your repos

### Step 2 — Deploy the app (new or redeploy)

**If you see an old broken app:** delete it or open it → **Manage app** → **Reboot** / **Redeploy**

**If no app exists:**

1. Click **Create app**
2. Paste this URL (auto-fills repo + file):

```
https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py
```

3. Or set manually:

| Field | Value |
|-------|-------|
| Repository | `narendhrareddi-ship-it/Nivara-AREIS` |
| Branch | `main` |
| Main file | `streamlit_app.py` |

4. Click **Deploy**

### Step 3 — Add secrets (required or DB won't connect)

While the app is deploying → **Settings** → **Secrets** → paste:

```toml
SUPABASE_URL = "https://mxjhwjxxqtkwsrwtqwuc.supabase.co"
DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_USER = "postgres.mxjhwjxxqtkwsrwtqwuc"
DB_PASSWORD = "YOUR_REAL_SUPABASE_PASSWORD"

ORCHESTRATOR_URL = "https://nivara-orchestrator.onrender.com"
VEO_MCP_URL = "https://nivara-veo-mcp.onrender.com"
AUTO_SYNC_PIPELINE = "true"
```

Replace `YOUR_REAL_SUPABASE_PASSWORD` with your real Supabase database password.

Click **Save** → **Reboot app** (⋮ menu).

### Step 4 — Copy your NEW URL

After deploy succeeds, Streamlit shows a URL like:

```
https://something.streamlit.app
```

Copy that exact URL from the browser address bar.

### Step 5 — Fix your desktop shortcut (Windows)

**Option A — Run the fix script from the repo:**

Double-click **`Fix-NIVARA-Shortcut.bat`** in the project folder. Paste your new URL when prompted.

**Option B — Win + R one-liner** (replace `YOUR-NEW-URL`):

```
powershell -NoProfile -ExecutionPolicy Bypass -Command "$u='YOUR-NEW-URL';$d=[Environment]::GetFolderPath('Desktop');$s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'NIVARA AREIS.lnk'));$s.TargetPath=$u;$s.Save();Start-Process $u"
```

---

## Why this happened

| Cause | Explanation |
|-------|-------------|
| App deleted | Streamlit app was removed from Cloud |
| Never deployed | URL in shortcut was planned but app wasn't live |
| Wrong GitHub link | Streamlit account not linked to repo owner |
| Private app | App exists but your login isn't authorized |

---

## Still stuck?

1. **share.streamlit.io** → confirm app shows **Running** (green)
2. Open the URL in an **Incognito** window (rules out cache/login)
3. Ensure GitHub repo **narendhrareddi-ship-it/Nivara-AREIS** is **public** (or Streamlit has repo access)

---

## Run locally on Windows (no Streamlit Cloud)

If you have Python installed and cloned the repo:

```bat
pip install -r requirements.txt
cd dashboard
streamlit run app.py
```

Then open **http://localhost:8501** — create a shortcut to that URL instead.
