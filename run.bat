@echo off
title Career Aligner - Free CV Review
echo.
echo  ============================================
echo   Career Aligner - Free Local CV Review
echo   No subscription. No API key. 100%% private.
echo  ============================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python not found. Install Python 3.10+ from https://python.org
        pause
        exit /b 1
    )
)

echo [2/3] Installing dependencies...
.venv\Scripts\pip install -e . -q

echo [3/3] Starting server...
echo.
echo  Open in browser: http://127.0.0.1:8000
echo  Press Ctrl+C to stop
echo.
.venv\Scripts\job-matcher
