@echo off
title Career Aligner
echo.
echo  ============================================
echo   Career Aligner — AI Career Agent
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
if errorlevel 1 (
    echo ERROR: Install failed. Check your internet connection and try again.
    pause
    exit /b 1
)

if not exist ".env" (
    echo Creating .env from .env.example...
    copy /Y ".env.example" ".env" >nul
)

echo [3/3] Starting server...
echo.
echo  Open in browser:  http://127.0.0.1:8000
echo  API docs:         http://127.0.0.1:8000/docs
echo.
echo  Works immediately in free mode. Add OPENAI_API_KEY for AI matching.
echo  Press Ctrl+C to stop
echo.

.venv\Scripts\uvicorn job_matcher.main:app --host 127.0.0.1 --port 8000
