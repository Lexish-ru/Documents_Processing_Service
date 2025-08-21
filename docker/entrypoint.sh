#!/bin/sh
set -e

# Wait for DB if needed
if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT..."
  for i in $(seq 1 30); do
    nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}" && break
    sleep 1
  done
fi

python manage.py migrate --noinput || true
python manage.py collectstatic --noinput || true

exec "$@"
