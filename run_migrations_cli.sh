#!/bin/bash

# Script para ejecutar migraciones usando Supabase CLI
# Shuar Chicham Translator

echo "🚀 Ejecutando migraciones con Supabase CLI"
echo "=========================================="

# Verificar que el CLI esté instalado
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI no está instalado"
    echo "   Instálalo con: npm install -g supabase"
    exit 1
fi

echo "✅ Supabase CLI encontrado: $(supabase --version)"

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado"
    echo "   Asegúrate de que existe y contiene las credenciales de Supabase"
    exit 1
fi

# Cargar variables de entorno
source .env

# Verificar variables requeridas
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_ANON_KEY" ]; then
    echo "❌ Variables de entorno faltantes"
    echo "   Verifica SUPABASE_URL y SUPABASE_ANON_KEY en .env"
    exit 1
fi

echo "✅ Variables de entorno cargadas"
echo "   URL: $SUPABASE_URL"

# Extraer project ID de la URL
PROJECT_ID=$(echo $SUPABASE_URL | sed 's/https:\/\/\([^.]*\).*/\1/')
echo "   Project ID: $PROJECT_ID"

# Hacer login (si no está logueado)
echo ""
echo "🔐 Verificando autenticación..."
if ! supabase projects list &> /dev/null; then
    echo "⚠️  No estás logueado. Iniciando sesión..."
    echo "   Se abrirá el navegador para autenticarte"
    supabase login
    
    if [ $? -ne 0 ]; then
        echo "❌ Error en la autenticación"
        exit 1
    fi
else
    echo "✅ Ya estás autenticado"
fi

# Listar proyectos para verificar acceso
echo ""
echo "📋 Proyectos disponibles:"
supabase projects list

# Vincular al proyecto remoto
echo ""
echo "🔗 Vinculando al proyecto remoto..."
supabase link --project-ref $PROJECT_ID

if [ $? -ne 0 ]; then
    echo "❌ Error vinculando al proyecto"
    echo "   Verifica que el PROJECT_ID sea correcto: $PROJECT_ID"
    exit 1
fi

echo "✅ Proyecto vinculado exitosamente"

# Verificar migraciones
echo ""
echo "📁 Verificando migraciones..."
if [ ! -d "supabase/migrations" ]; then
    echo "❌ Directorio de migraciones no encontrado"
    exit 1
fi

MIGRATION_COUNT=$(ls supabase/migrations/*.sql 2>/dev/null | wc -l)
echo "   Encontradas $MIGRATION_COUNT migraciones"

if [ $MIGRATION_COUNT -eq 0 ]; then
    echo "❌ No se encontraron archivos de migración"
    exit 1
fi

# Listar migraciones
echo ""
echo "📋 Migraciones a ejecutar:"
ls -la supabase/migrations/

# Ejecutar migraciones
echo ""
echo "🚀 Ejecutando migraciones en el proyecto remoto..."
echo "   Esto puede tomar unos minutos..."

supabase db push

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Migraciones ejecutadas exitosamente!"
    echo ""
    echo "🎯 Verificando el resultado..."
    
    # Verificar algunas tablas clave
    echo "   Verificando tablas creadas..."
    
    # Usar psql para verificar (si está disponible)
    if command -v psql &> /dev/null; then
        echo "   Conectando a la base de datos..."
        
        # Construir URL de conexión
        DB_URL="postgresql://postgres:[PASSWORD]@db.$PROJECT_ID.supabase.co:5432/postgres"
        
        echo "   Para verificar manualmente, usa:"
        echo "   psql '$DB_URL'"
        echo "   SELECT COUNT(*) FROM alfabeto_shuar;"
        echo "   SELECT COUNT(*) FROM tipos_vocales_shuar;"
        echo "   SELECT COUNT(*) FROM palabras_detalladas;"
    fi
    
    echo ""
    echo "🌟 ¡Configuración completa!"
    echo ""
    echo "Próximos pasos:"
    echo "1. Inicia la aplicación: python3 run.py"
    echo "2. Ve a: http://localhost:8000/docs"
    echo "3. Prueba el endpoint: /api/health"
    
else
    echo ""
    echo "❌ Error ejecutando migraciones"
    echo ""
    echo "Posibles soluciones:"
    echo "1. Verifica que tengas permisos en el proyecto"
    echo "2. Revisa que las migraciones no tengan errores de sintaxis"
    echo "3. Ejecuta manualmente en Supabase Dashboard si persiste el error"
    
    exit 1
fi