#!/bin/bash
# ===========================================
# START.SH - Script de arranque para producción
# ===========================================
# Uso manual:
#   chmod +x start.sh
#   ./start.sh
#
# O bien: exec gunicorn --config gunicorn.conf.py "app:create_app()"
#
# Uso con systemd:
#   ExecStart=/path/to/project/start.sh
#
# Requisitos previos:
#   1. Crear entorno virtual: python3 -m venv venv
#   2. Instalar dependencias: source venv/bin/activate && pip install -r requirements.txt
#   3. Crear archivo de marca: touch venv/.dependencies_installed
#   4. Configurar .env con variables de producción
# ===========================================
set -e

# Verificar que venv existe
if [ ! -d "venv" ]; then
    echo "Error: Requiere 'venv'"
    echo "Crear con: python3 -m venv venv"
    exit 1
fi

# Activar venv
source venv/bin/activate

# Verificar instalación de dependencias
if [ -f "requirements.txt" ] && [ ! -f "venv/.dependencies_installed" ]; then
    echo "Error: Requiere instalar dependencias"
    echo "Ejecutar: pip install -r requirements.txt && touch venv/.dependencies_installed"
    exit 1
fi

# Ejecutar Gunicorn con factory de producción
exec gunicorn --config gunicorn.conf.py "app:create_app()"