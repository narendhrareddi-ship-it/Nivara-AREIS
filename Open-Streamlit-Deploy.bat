@echo off
title NIVARA AREIS - Deploy on Streamlit Cloud
echo Opening Streamlit Cloud...
echo.
echo 1. Sign in with GitHub: narendhrareddi-ship-it
echo 2. Create app from: Nivara-AREIS / main / streamlit_app.py
echo 3. Set custom subdomain: nivara-areis  (stable URL forever)
echo 4. Add Secrets (see docs\PERMANENT_SHORTCUT_FIX.md)
echo 5. Run Install-NIVARA-Desktop-Shortcut.bat then Fix-NIVARA-Shortcut.bat
echo.
start "" "https://share.streamlit.io"
start "" "https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py"
timeout /t 8
