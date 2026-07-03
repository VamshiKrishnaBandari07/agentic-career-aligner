#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo ""
echo "  ============================================"
echo "   Career Aligner - Free Local CV Review"
echo "   No subscription. No API key. 100% private."
echo "  ============================================"
echo ""

if [ ! -d ".venv" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv .venv
fi

echo "[2/3] Installing dependencies..."
.venv/bin/pip install -e . -q

echo "[3/3] Starting server..."
echo ""
echo "  Open in browser: http://127.0.0.1:8000"
echo "  Press Ctrl+C to stop"
echo ""
.venv/bin/job-matcher
