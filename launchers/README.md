# NIVARA AREIS Launchers

## Permanent fix for "You do not have access to this app"

**Do not** point shortcuts directly at `https://nivara-areis.streamlit.app/` — that URL only works after Streamlit Cloud deploy.

### Windows (recommended)

**Double-click either file in the repo root:**

- **`CREATE-DESKTOP-SHORTCUT.bat`** ← easiest
- **`Install-NIVARA-Desktop-Shortcut.bat`**

Creates:
- Desktop icon **NIVARA AREIS** (custom `nivara.ico` building logo)
- Start Menu entry
- Local launcher at `%LOCALAPPDATA%\NIVARA\`

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
