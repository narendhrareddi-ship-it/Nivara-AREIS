# NIVARA AREIS Launchers

## Permanent fix for "You do not have access to this app"

**Do not** point shortcuts directly at `https://nivara-areis.streamlit.app/` — that URL only works after Streamlit Cloud deploy.

### Windows (recommended)

1. Run **`Install-NIVARA-Desktop-Shortcut.bat`** (repo root)
2. Deploy app on [share.streamlit.io](https://share.streamlit.io) with subdomain **`nivara-areis`**
3. If needed, run **`Fix-NIVARA-Shortcut.bat`** to paste your live URL once

Shortcut target: `%LOCALAPPDATA%\NIVARA\NIVARA-Dashboard.bat` (local launcher)

Saved URL: `%LOCALAPPDATA%\NIVARA\dashboard.url`

Full guide: [docs/PERMANENT_SHORTCUT_FIX.md](../docs/PERMANENT_SHORTCUT_FIX.md)

### Deploy settings

| Field | Value |
|-------|-------|
| Repository | `narendhrareddi-ship-it/Nivara-AREIS` |
| Branch | `main` |
| Main file | `streamlit_app.py` |
| Subdomain | `nivara-areis` |

### Linux / Mac

- Linux: `Install-NIVARA-Desktop-Shortcut.sh`
- Mac: `launchers/Open-NIVARA-Dashboard.command` (opens URL — run Install on Windows for launcher model)

### Files

| File | Purpose |
|------|---------|
| `Open-Dashboard.ps1` | Validates URL, wizard if dead, opens browser |
| `Install-Launcher.ps1` | Copies launcher to `%LOCALAPPDATA%\NIVARA\` |
| `Open-NIVARA-Dashboard.bat` | Fallback if launcher installed |
