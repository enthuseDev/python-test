# !/usr/bin/env sh
set -e

# Ensure DB is ready (SQLite is local, so just migrate)
python manage.py migrate --noinput

# Optional: collect static (will no-op if not configured)
python manage.py collectstatic --noinput || true

# Start dev server
exec python manage.py runserver 0.0.0.0:8000
