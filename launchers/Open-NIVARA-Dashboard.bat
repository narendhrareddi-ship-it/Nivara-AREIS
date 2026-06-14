@echo off
title NIVARA AREIS Dashboard
if exist "%LOCALAPPDATA%\NIVARA\NIVARA-Dashboard.bat" (
    call "%LOCALAPPDATA%\NIVARA\NIVARA-Dashboard.bat"
    exit /b 0
)
echo Local launcher not installed. Run Install-NIVARA-Desktop-Shortcut.bat first.
pause
