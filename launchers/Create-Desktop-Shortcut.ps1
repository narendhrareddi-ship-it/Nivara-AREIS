# Run once in PowerShell: right-click → Run with PowerShell
# Or: powershell -ExecutionPolicy Bypass -File Create-Desktop-Shortcut.ps1

$AppUrl = "https://nivara-areis-etzshrs4dtzuyqmsnv8bds.streamlit.app/"
$Desktop = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $Desktop "NIVARA AREIS.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $AppUrl
$Shortcut.IconLocation = "imageres.dll,109"
$Shortcut.Description = "NIVARA AREIS — Bangalore Real Estate AI Dashboard"
$Shortcut.Save()

Write-Host "Desktop shortcut created:" $ShortcutPath
Start-Process $AppUrl
