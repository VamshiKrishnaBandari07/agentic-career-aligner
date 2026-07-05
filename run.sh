#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo ""
echo "  ============================================"
echo "   Career Aligner — AI Career Agent"
echo "  ============================================"
echo ""

if [ ! -d ".venv" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv .venv
fi

echo "[2/3] Installing dependencies..."
.venv/bin/pip install -e . -q

if [ ! -f ".env" ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
fi

echo "[3/3] Starting server..."
echo ""
echo "  Open in browser:  http://127.0.0.1:8000"
echo "  API docs:         http://127.0.0.1:8000/docs"
echo ""
echo "  Works immediately in free mode. Add OPENAI_API_KEY for AI matching."
echo "  Press Ctrl+C to stop"
echo ""
.venv/bin/uvicorn job_matcher.main:app --host 127.0.0.1 --port 8000
