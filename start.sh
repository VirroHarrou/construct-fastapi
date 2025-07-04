#!/bin/bash

echo "Running migrations..."
alembic revision --autogenerate -m "migration"
alembic upgrade head

echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000