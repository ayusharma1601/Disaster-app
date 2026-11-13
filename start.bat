@echo off
title Disaster Intelligence Platform (Auto-Launch)
echo ===============================================================
echo   Disaster Intelligence & Emergency Response Platform
echo   Auto-starting server and opening your browser...
echo ===============================================================

:: 1. Force kill any stray processes holding port 8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 2. Launch browser automatically in the background after 2 seconds
start /b "" powershell -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"

:: 3. Launch Uvicorn in the disaster-app directory (0.0.0.0 enables access from phones/tablets on local Wi-Fi)
cd /d "%~dp0"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
