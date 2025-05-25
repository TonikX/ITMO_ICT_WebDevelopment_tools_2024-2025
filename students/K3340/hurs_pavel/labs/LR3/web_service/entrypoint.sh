#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
    sleep 1
    echo "Still waiting for PostgreSQL..."
done
echo "PostgreSQL is ready!"

# Give PostgreSQL a moment to complete initialization
sleep 5

# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head

# Start the FastAPI application
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 8000