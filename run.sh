#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║     dLoan — Starting Services        ║"
echo "╚══════════════════════════════════════╝"

# ── Django API ──
cd "$ROOT_DIR"
echo "[django]  http://localhost:8000"
PYTHONPATH=. uv run python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# ── Vite frontend ──
cd "$ROOT_DIR/frontend"
echo "[vite]    http://localhost:5173"
npx vite --host 0.0.0.0 &
VITE_PID=$!

echo ""
echo "  Open http://localhost:5173"
echo "  Login: admin1 / admin"
echo ""
echo "Press Ctrl+C to stop both services."

trap "kill $DJANGO_PID $VITE_PID 2>/dev/null; exit" INT TERM
wait
