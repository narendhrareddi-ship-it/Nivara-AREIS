@echo off
title NIVARA AREIS - Install Desktop Shortcut
echo Creating NIVARA AREIS shortcut on your Desktop...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$url='https://nivara-areis-etzshrs4dtzuyqmsnv8bds.streamlit.app/'; ^
   $desk=[Environment]::GetFolderPath('Desktop'); ^
   $lnk=Join-Path $desk 'NIVARA AREIS.lnk'; ^
   $s=(New-Object -ComObject WScript.Shell).CreateShortcut($lnk); ^
   $s.TargetPath=$url; ^
   $s.IconLocation='imageres.dll,109'; ^
   $s.Description='NIVARA AREIS - Bangalore Real Estate AI Dashboard'; ^
   $s.Save(); ^
   Write-Host 'Shortcut created:' $lnk; ^
   Start-Process $url"

echo.
echo Done! Check your Desktop for "NIVARA AREIS"
timeout /t 5
