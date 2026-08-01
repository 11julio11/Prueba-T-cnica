#!/bin/bash
set -e

echo "Ejecutando migraciones Alembic..."
alembic upgrade head

echo "Iniciando servidor FastAPI..."
exec uvicorn app.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}"
