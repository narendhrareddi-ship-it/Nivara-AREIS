@echo off
title NIVARA AREIS - Deploy on Streamlit Cloud
echo Opening Streamlit Cloud...
echo.
echo 1. Sign in with GitHub: narendhrareddi-ship-it
echo 2. Create app from: Nivara-AREIS / main / streamlit_app.py
echo 3. Add Secrets (see docs\STREAMLIT_FIX_ACCESS.md)
echo 4. After deploy, run Fix-NIVARA-Shortcut.bat with your new URL
echo.
start "" "https://share.streamlit.io"
start "" "https://github.com/narendhrareddi-ship-it/Nivara-AREIS/blob/main/streamlit_app.py"
timeout /t 8
