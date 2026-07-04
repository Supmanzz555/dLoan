#!/usr/bin/env bash
set -e

echo "[entrypoint] Running migrations..."
PYTHONPATH=. uv run python manage.py migrate --run-syncdb 2>/dev/null || uv run python manage.py migrate

echo "[entrypoint] Seeding data..."
PYTHONPATH=. uv run python manage.py seed_data 2>/dev/null || true

echo "[entrypoint] Creating default accounts..."
PYTHONPATH=. uv run python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin1').exists():
    u = User.objects.create_superuser('admin1', 'admin1@dloan.local', 'admin')
    u.role = 'admin'; u.is_super_admin = True; u.save()
    print('  Created admin1 / admin')
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@dloan.local', 'admin123')
    u.role = 'admin'; u.save()
    print('  Created admin / admin123')
EOF

echo "[entrypoint] Starting gunicorn..."
exec uv run gunicorn django_api.config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
