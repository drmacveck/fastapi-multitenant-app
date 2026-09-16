#!/bin/bash
set -e

echo "Applying Alembic database migrations..."
alembic upgrade head

echo "Starting FastAPI ASGI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
