#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Running seed data..."
python -m seeds.seed_data

echo "Starting server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
