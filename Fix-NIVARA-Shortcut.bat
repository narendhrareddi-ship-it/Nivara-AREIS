@echo off
title NIVARA AREIS - Fix Desktop Shortcut
echo.
echo ============================================================
echo   NIVARA AREIS - Update Desktop Shortcut
echo ============================================================
echo.
echo Updating shortcut to: https://nivara-areis.streamlit.app/
echo.
set APPURL=https://nivara-areis.streamlit.app/

if "%APPURL%"=="" (
    echo No URL entered. Opening Streamlit Cloud to deploy...
    start "" "https://share.streamlit.io"
    echo Deploy the app first, then run this script again.
    pause
    exit /b 1
)

echo.
echo Creating shortcut for: %APPURL%

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$u='%APPURL%'; ^
   if (-not $u.EndsWith('/')) { $u += '/' }; ^
   $d=[Environment]::GetFolderPath('Desktop'); ^
   $lnk=Join-Path $d 'NIVARA AREIS.lnk'; ^
   $s=(New-Object -ComObject WScript.Shell).CreateShortcut($lnk); ^
   $s.TargetPath=$u; ^
   $s.IconLocation='imageres.dll,109'; ^
   $s.Description='NIVARA AREIS - Bangalore Real Estate AI Dashboard'; ^
   $s.Save(); ^
   Write-Host 'Shortcut updated:' $lnk; ^
   Start-Process $u"

echo.
echo Done! Opening dashboard...
timeout /t 4
