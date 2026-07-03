#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════╗"
echo "║     dLoan — First-Time Setup        ║"
echo "╚══════════════════════════════════════╝"

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
echo "[1/4] Python virtual environment + dependencies..."
cd "$ROOT_DIR"
if [ ! -d ".venv" ]; then
  uv venv
fi
uv sync --quiet 2>/dev/null || uv sync

# ── 3. Frontend deps ──
echo "[2/4] Frontend dependencies..."
cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi

# ── 4. Database ──
echo "[3/4] Database migrations..."
cd "$ROOT_DIR"
PYTHONPATH=. uv run python manage.py migrate

echo "[4/4] Seeding data + default accounts..."
PYTHONPATH=. uv run python manage.py seed_data

PYTHONPATH=. uv run python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin1').exists():
    u = User.objects.create_superuser('admin1', 'admin1@dloan.local', 'admin')
    u.role = 'admin'; u.is_super_admin = True; u.save()
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@dloan.local', 'admin123')
    u.role = 'admin'; u.save()
" 2>/dev/null

echo ""
echo "Done. Run ./run.sh to start the services."
echo "  Login: admin1 / admin"
