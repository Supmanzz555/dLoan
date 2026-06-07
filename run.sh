#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

API_LOG="/tmp/dloan_api.log"
UI_LOG="/tmp/dloan_ui.log"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $API_PID $UI_PID 2>/dev/null
    wait $API_PID $UI_PID 2>/dev/null
    echo "Done."
}
trap cleanup EXIT INT TERM

echo "Starting API (port 8000)..."
PYTHONPATH=. uv run uvicorn api.routes:app --reload --port 8000 --host 0.0.0.0 &>"$API_LOG" &
API_PID=$!

echo "Starting UI (port 8501)..."
PYTHONPATH=. uv run streamlit run ui/app.py --server.port 8501 --server.headless true &>"$UI_LOG" &
UI_PID=$!

sleep 3

if ! kill -0 $API_PID 2>/dev/null; then
    echo "ERROR: API failed to start. Check $API_LOG"
    cat "$API_LOG"
    exit 1
fi

if ! kill -0 $UI_PID 2>/dev/null; then
    echo "ERROR: UI failed to start. Check $UI_LOG"
    cat "$UI_LOG"
    exit 1
fi

echo ""
echo "Both services running:"
echo "  API  → http://localhost:8000  (log: $API_LOG)"
echo "  UI   → http://localhost:8501  (log: $UI_LOG)"
echo ""
echo "Press Ctrl+C to stop both."
echo ""

tail -f "$API_LOG" "$UI_LOG"
