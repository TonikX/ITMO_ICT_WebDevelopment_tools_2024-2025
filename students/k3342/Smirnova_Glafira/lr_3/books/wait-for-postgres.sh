#!/bin/sh

echo "Waiting for PostgreSQL at db:5432..."

until nc -z db 5432; do
  sleep 0.5
done

echo "PostgreSQL is available, starting app"
exec "$@"