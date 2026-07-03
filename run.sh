#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║     dLoan Fullstack — Setup + Run   ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Check .env ──
if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "[!] .env not found. Copying from .env.example..."
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
  echo "[!] Edit .env and set your GROQ_API_KEY, then re-run."
  exit 1
fi

# shellcheck disable=SC2046
export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
  echo "[!] GROQ_API_KEY is not set in .env. Get a free key at https://console.groq.com"
  exit 1
fi

# ── 2. Python venv + deps ──
echo "[1/5] Checking Python dependencies..."
cd "$ROOT_DIR"
if [ ! -d ".venv" ]; then
  uv venv
fi
uv sync --quiet 2>/dev/null || uv sync

# ── 3. Frontend deps ──
echo "[2/5] Checking frontend dependencies..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi

# ── 4. Database (migrate + seed) ──
echo "[3/5] Running database migrations..."
cd "$ROOT_DIR"
PYTHONPATH=. uv run python manage.py migrate --run-syncdb 2>/dev/null || PYTHONPATH=. uv run python manage.py migrate

echo "[4/5] Seeding sample applicants..."
PYTHONPATH=. uv run python manage.py seed_data 2>/dev/null || echo "  (already seeded or skipped)"

# ── 5. Create default admin if missing ──
echo "[5/5] Ensuring default accounts..."
PYTHONPATH=. uv run python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin1').exists():
    u = User.objects.create_superuser('admin1', 'admin1@dloan.local', 'admin')
    u.role = 'admin'; u.is_super_admin = True; u.save()
    print('  Created admin1/admin')
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@dloan.local', 'admin123')
    u.role = 'admin'; u.save()
    print('  Created admin/admin123')
" 2>/dev/null

echo ""
echo "╔══════════════════════════════════════╗"
echo "║  Starting services                   ║"
echo "╚══════════════════════════════════════╝"

# ── Start Django ──
cd "$ROOT_DIR"
echo "[django]  http://localhost:8000"
PYTHONPATH=. uv run python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# ── Start Vite ──
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
