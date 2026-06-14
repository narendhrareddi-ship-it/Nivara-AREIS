# Installs a permanent local desktop shortcut — points to launcher, NOT a fragile Streamlit URL.
param(
    [string]$SourceDir = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$TargetDir = Join-Path $env:LOCALAPPDATA "NIVARA"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "NIVARA AREIS.lnk"
$LauncherBat = Join-Path $TargetDir "NIVARA-Dashboard.bat"
$OpenScript = Join-Path $TargetDir "Open-Dashboard.ps1"

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

Copy-Item -Path (Join-Path $SourceDir "Open-Dashboard.ps1") -Destination $OpenScript -Force

$bat = @"
@echo off
title NIVARA AREIS Dashboard
powershell -NoProfile -ExecutionPolicy Bypass -File "%LOCALAPPDATA%\NIVARA\Open-Dashboard.ps1"
"@
Set-Content -Path $LauncherBat -Value $bat -Encoding ASCII

$urlFile = Join-Path $TargetDir "dashboard.url"
if (-not (Test-Path $urlFile)) {
    Set-Content -Path $urlFile -Value "https://nivara-dashboard.onrender.com/" -Encoding UTF8
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($ShortcutPath)
$shortcut.TargetPath = $LauncherBat
$shortcut.WorkingDirectory = $TargetDir
$shortcut.IconLocation = "imageres.dll,109"
$shortcut.Description = "NIVARA AREIS — Bangalore Real Estate AI Dashboard"
$shortcut.Save()

Write-Host "Installed permanent launcher:"
Write-Host "  Shortcut : $ShortcutPath"
Write-Host "  Launcher : $LauncherBat"
Write-Host "  URL file : $urlFile"
Write-Host ""
Write-Host "The shortcut opens the local launcher, which reads dashboard.url and auto-prompts if the app is down."

Start-Process $LauncherBat
