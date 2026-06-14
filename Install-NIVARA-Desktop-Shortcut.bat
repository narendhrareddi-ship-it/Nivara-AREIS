@echo off
title NIVARA AREIS - Install Permanent Desktop Shortcut
echo.
echo ============================================================
echo   NIVARA AREIS - Permanent Desktop Shortcut Installer
echo ============================================================
echo.
echo This creates a shortcut that opens a LOCAL launcher.
echo The launcher reads your saved URL and prompts you only if
echo Streamlit is down — no more broken shortcuts after redeploy.
echo.

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launchers\Install-Launcher.ps1" -SourceDir "%SCRIPT_DIR%launchers"

echo.
echo Done. Your Desktop shortcut "NIVARA AREIS" is ready.
timeout /t 6
