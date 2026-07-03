#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Starting dLoan Fullstack ==="

# Start Django API
echo "[django] Starting on port 8000..."
cd "$ROOT_DIR"
uv run python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Start Vite frontend
echo "[vite]   Starting on port 5173..."
cd "$ROOT_DIR/frontend"
npm run dev &
VITE_PID=$!

echo ""
echo "=== Services ==="
echo "  API:  http://localhost:8000"
echo "  UI:   http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services."

trap "kill $DJANGO_PID $VITE_PID 2>/dev/null; exit" INT TERM
wait
