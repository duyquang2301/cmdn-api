#!/bin/sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting API Gateway..."
exec uvicorn app.run:make_app --factory --host 0.0.0.0 --port 8000 --loop uvloop
