@echo off
setlocal
cd /d "%~dp0"

echo.
echo OLA 360 launcher
echo =================
echo 1. Web app - http://127.0.0.1:6194
echo 2. Desktop app
echo.
set /p choice=Choose mode [1/2]: 

if "%choice%"=="2" goto desktop

:web
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_FLET_WEB.ps1"
goto end

:desktop
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_FLET_DESKTOP.ps1"

:end
endlocal
