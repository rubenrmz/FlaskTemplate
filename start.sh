#!/bin/bash
set -e

# Verificar que venv existe
if [ ! -d "venv" ]; then
    echo "Error: Requiere 'venv'"
    exit 1
fi

# Activar venv
source venv/bin/activate

# Verificar instalacion de dependencias
if [ -f "requirements.txt" ] && [ ! -f "venv/.dependencies_installed" ]; then
    echo "Error: Requiere instalar dependencias"
    exit 1
fi

# Limpiar proceso anterior si existe
if [ -f gunicorn.pid ]; then
    OLD_PID=$(cat gunicorn.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Deteniendo proceso anterior (PID: $OLD_PID)..."
        kill -TERM $OLD_PID
        sleep 2
    fi
    rm -f gunicorn.pid
fi

# Ejecutar Gunicorn
exec gunicorn --config gunicorn_config.py run:app