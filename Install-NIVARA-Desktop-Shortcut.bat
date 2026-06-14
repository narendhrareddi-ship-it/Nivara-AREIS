@echo off
title NIVARA AREIS - Install Permanent Desktop Shortcut
echo.
echo ============================================================
echo   NIVARA AREIS - Permanent Desktop Shortcut + Icon
echo ============================================================
echo.
echo Creates Desktop + Start Menu icon with NIVARA building logo.
echo Shortcut opens local launcher (never breaks on redeploy).
echo.

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%launchers\Install-Launcher.ps1" -SourceDir "%SCRIPT_DIR%launchers"

echo.
echo Done. Desktop icon: NIVARA AREIS
echo.
pause
