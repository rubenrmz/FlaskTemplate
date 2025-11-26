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

# Ejecutar Gunicorn
exec gunicorn --config gunicorn_config.py run:app