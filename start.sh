#!/bin/bash
# Iniciar servicio Flask con Gunicorn
set -e

# Obtener directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Crear directorios necesarios
mkdir -p logs tmp

# Verificar que venv existe
if [ ! -d "venv" ]; then
    echo "Error: El entorno virtual 'venv' no existe"
    exit 1
fi

# Verificar que venv/bin/activate existe
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: venv/bin/activate no encontrado"
    exit 1
fi

# Activar venv
source venv/bin/activate
VENV_DIR="venv"

# Instalar/actualizar dependencias si requirements.txt existe
if [ -f "requirements.txt" ]; then
    # Verificar si necesita instalar dependencias
    NEEDS_INSTALL=false
    
    # Si no existe el flag de instalación, instalar
    if [ ! -f "$VENV_DIR/.dependencies_installed" ]; then
        NEEDS_INSTALL=true
    # Si requirements.txt es más reciente que el flag, reinstalar
    elif [ "requirements.txt" -nt "$VENV_DIR/.dependencies_installed" ]; then
        NEEDS_INSTALL=true
    fi
    
    if [ "$NEEDS_INSTALL" = true ]; then
        echo "Instalando dependencias desde requirements.txt..."
        pip install --upgrade pip
        pip install -r requirements.txt
        if [ $? -eq 0 ]; then
            # Crear flag de instalación exitosa
            touch "$VENV_DIR/.dependencies_installed"
            echo "Dependencias instaladas correctamente"
        else
            echo "Error al instalar dependencias"
            exit 1
        fi
    fi
fi

# Verificar Gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "Error: Gunicorn no está instalado"
    exit 1
fi

# Cargar variables de entorno
if [ -f .env.production ]; then
    set -a; source .env.production; set +a
elif [ -f .env ]; then
    set -a; source .env; set +a
fi

# Configurar entorno
export FLASK_ENV=production
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Limpiar proceso anterior si existe
if [ -f gunicorn.pid ]; then
    OLD_PID=$(cat gunicorn.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        kill -TERM $OLD_PID
        sleep 2
    fi
    rm -f gunicorn.pid
fi

# Ejecutar Gunicorn
exec gunicorn --config gunicorn_config.py run:app \
    --access-logfile "$SCRIPT_DIR/logs/access.log" \
    --error-logfile "$SCRIPT_DIR/logs/error.log" \
    --pid gunicorn.pid