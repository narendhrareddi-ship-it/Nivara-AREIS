# Installs a permanent NIVARA AREIS desktop shortcut with custom icon.
param(
    [string]$SourceDir = $PSScriptRoot
)

$ErrorActionPreference = "Stop"
$TargetDir = Join-Path $env:LOCALAPPDATA "NIVARA"
$Desktop = [Environment]::GetFolderPath("Desktop")
$StartMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$ShortcutName = "NIVARA AREIS.lnk"
$DesktopShortcut = Join-Path $Desktop $ShortcutName
$StartShortcut = Join-Path $StartMenu $ShortcutName
$LauncherBat = Join-Path $TargetDir "NIVARA-Dashboard.bat"
$OpenScript = Join-Path $TargetDir "Open-Dashboard.ps1"
$IconFile = Join-Path $TargetDir "nivara.ico"

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
}

Copy-Item -Path (Join-Path $SourceDir "Open-Dashboard.ps1") -Destination $OpenScript -Force
$iconSrc = Join-Path $SourceDir "nivara.ico"
if (Test-Path $iconSrc) {
    Copy-Item -Path $iconSrc -Destination $IconFile -Force
}

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

function New-NivaraShortcut([string]$Path) {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Path)
    $shortcut.TargetPath = $LauncherBat
    $shortcut.WorkingDirectory = $TargetDir
    $shortcut.WindowStyle = 1
    if (Test-Path $IconFile) {
        $shortcut.IconLocation = "$IconFile,0"
    } else {
        $shortcut.IconLocation = "imageres.dll,109"
    }
    $shortcut.Description = "NIVARA AREIS — Bangalore Real Estate AI Dashboard"
    $shortcut.Save()
}

New-NivaraShortcut $DesktopShortcut
New-NivaraShortcut $StartShortcut

Write-Host ""
Write-Host "=========================================="
Write-Host "  NIVARA AREIS shortcut installed"
Write-Host "=========================================="
Write-Host "  Desktop  : $DesktopShortcut"
Write-Host "  Start Menu: $StartShortcut"
Write-Host "  Launcher : $LauncherBat"
Write-Host "  Icon     : $IconFile"
Write-Host "  URL      : $(Get-Content $urlFile -Raw)"
Write-Host ""
Write-Host "Double-click the desktop icon anytime — it never breaks on redeploy."

Start-Process $LauncherBat
