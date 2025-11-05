#!/bin/bash

# Script simple para ejecutar migraciones con Supabase CLI
echo "🚀 Ejecutando migraciones Shuar Chicham Translator"
echo "================================================="

# Verificar CLI
if ! command -v supabase &> /dev/null; then
    echo "❌ Instala Supabase CLI: npm install -g supabase"
    exit 1
fi

# Cargar variables
source .env
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/https:\/\/\([^.]*\).*/\1/')

echo "✅ Project ID: $PROJECT_ID"
echo "📁 Migraciones: $(ls supabase/migrations/*.sql | wc -l) archivos"

# Login si es necesario
echo ""
echo "🔐 Verificando autenticación..."
if ! supabase projects list &> /dev/null; then
    echo "   Iniciando sesión..."
    supabase login
fi

# Vincular proyecto
echo "🔗 Vinculando proyecto..."
supabase link --project-ref $PROJECT_ID

# Ejecutar migraciones
echo ""
echo "🚀 Ejecutando migraciones..."
supabase db push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Migraciones completadas!"
    echo ""
    echo "🎯 Próximos pasos:"
    echo "1. python3 run.py"
    echo "2. http://localhost:8000/docs"
    echo "3. Probar /api/health"
else
    echo "❌ Error en migraciones. Revisa los logs arriba."
fi