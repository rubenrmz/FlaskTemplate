#!/bin/bash
# Aplica permisos estándar para proyecto Flask

BASE="${1:-.}"  # Usa el directorio actual si no se pasa argumento

echo "📁 Aplicando permisos en: $BASE"

# Directorios → 755
find "$BASE" -type d -exec chmod 755 {} +
echo "✅ Directorios:  755"

# Archivos → 644
find "$BASE" -type f -exec chmod 644 {} +
echo "✅ Archivos:     644"

# Scripts .sh → 700
find "$BASE" -name "*.sh" -exec chmod 700 {} +
echo "✅ Scripts .sh:  700"

echo "🎉 Listo."
