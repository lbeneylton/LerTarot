#!/bin/bash
set -e

# Se a variável RUN_MIGRATIONS estiver configurada para falso, pula as migrações
if [ "$RUN_MIGRATIONS" != "false" ] && [ "$1" = "uvicorn" ]; then
    echo "Running Alembic migrations..."
    # Configura o PYTHONPATH se necessário
    export PYTHONPATH=/app/src
    alembic upgrade head
    echo "Migrations applied successfully!"
fi

echo "Starting application with command: $@"
exec "$@"
