@echo off
title NIVARA AREIS - Create Desktop Icon
color 0A
echo.
echo  ============================================================
echo    NIVARA AREIS - Permanent Desktop Icon
echo  ============================================================
echo.
echo  Creates:
echo    - Desktop icon "NIVARA AREIS" (custom building logo)
echo    - Start Menu entry
echo    - Local launcher (survives URL / redeploy changes)
echo.

set "SCRIPT_DIR=%~dp0"
if exist "%SCRIPT_DIR%launchers\Install-Launcher.ps1" (
    set "LAUNCHER_DIR=%SCRIPT_DIR%launchers"
) else if exist "%SCRIPT_DIR%Install-Launcher.ps1" (
    set "LAUNCHER_DIR=%SCRIPT_DIR%"
) else (
    echo ERROR: Run this from the Nivara-AREIS project folder.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%LAUNCHER_DIR%\Install-Launcher.ps1" -SourceDir "%LAUNCHER_DIR%"

echo.
echo  Done! Look on your Desktop for the NIVARA AREIS icon.
echo.
pause
