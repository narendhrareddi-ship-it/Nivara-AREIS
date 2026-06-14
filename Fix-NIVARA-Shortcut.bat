@echo off
title NIVARA AREIS - Fix Desktop Shortcut
echo.
echo ============================================================
echo   NIVARA AREIS - Fix Desktop Shortcut (permanent)
echo ============================================================
echo.
echo Reinstalling the local launcher shortcut and URL wizard...
echo.

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launchers\Install-Launcher.ps1" -SourceDir "%SCRIPT_DIR%launchers"
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launchers\Open-Dashboard.ps1" -ForceWizard

echo.
echo If the dashboard did not open, deploy on Streamlit Cloud first:
echo   1. https://share.streamlit.io  (GitHub: narendhrareddi-ship-it)
echo   2. Create app from narendhrareddi-ship-it/Nivara-AREIS
echo   3. Branch main, file streamlit_app.py
echo   4. Custom subdomain: nivara-areis
echo.
timeout /t 8
