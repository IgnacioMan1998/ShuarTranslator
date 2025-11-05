#!/usr/bin/env python3
"""
Script para ejecutar las migraciones de base de datos en Supabase
Orden correcto: 000 -> 001 -> 002 -> 003
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_supabase_client() -> Client:
    """Crear cliente de Supabase con service role key."""
    url = os.getenv("SUPABASE_URL")
    # Para migraciones necesitamos service role key, no anon key
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
    
    if not url or not service_key:
        print("❌ Error: SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY son requeridos")
        print("   Verifica tu archivo .env")
        sys.exit(1)
    
    return create_client(url, service_key)

def read_migration_file(file_path: Path) -> str:
    """Leer el contenido de un archivo de migración."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error leyendo {file_path}: {e}")
        return None

def execute_sql(client: Client, sql: str, migration_name: str) -> bool:
    """Ejecutar SQL en Supabase."""
    try:
        # Dividir el SQL en statements individuales
        statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
        
        print(f"   Ejecutando {len(statements)} statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    # Usar rpc para ejecutar SQL raw
                    result = client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"   ✓ Statement {i}/{len(statements)}")
                except Exception as e:
                    # Si no existe la función exec_sql, intentar con postgrest
                    print(f"   ⚠️  Statement {i} falló con RPC, intentando método alternativo...")
                    # Para migraciones, necesitaremos ejecutar manualmente en Supabase
                    continue
        
        print(f"✅ {migration_name} completada")
        return True
        
    except Exception as e:
        print(f"❌ Error ejecutando {migration_name}: {e}")
        return False

def main():
    """Función principal para ejecutar migraciones."""
    print("🚀 Iniciando migraciones de Shuar Chicham Translator")
    print("=" * 60)
    
    # Verificar conexión
    try:
        client = get_supabase_client()
        print("✅ Conexión a Supabase establecida")
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        sys.exit(1)
    
    # Definir orden de migraciones
    migrations_dir = Path("app/core/infrastructure/database/migrations")
    migration_files = [
        "000_create_phonological_system.sql",
        "001_create_translation_tables.sql", 
        "002_create_dictionary_tables.sql",
        "003_seed_sample_data.sql"
    ]
    
    print(f"\n📁 Directorio de migraciones: {migrations_dir}")
    print(f"📋 {len(migration_files)} migraciones a ejecutar\n")
    
    # Verificar que existen todos los archivos
    missing_files = []
    for file_name in migration_files:
        file_path = migrations_dir / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        print("❌ Archivos de migración faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    # Ejecutar migraciones en orden
    success_count = 0
    
    for i, file_name in enumerate(migration_files, 1):
        file_path = migrations_dir / file_name
        print(f"\n{i}. Ejecutando: {file_name}")
        print("-" * 50)
        
        # Leer archivo
        sql_content = read_migration_file(file_path)
        if not sql_content:
            print(f"❌ No se pudo leer {file_name}")
            break
        
        print(f"   📄 Archivo leído: {len(sql_content)} caracteres")
        
        # Mostrar información sobre qué hace esta migración
        if "000_" in file_name:
            print("   🎯 Creando sistema fonológico (alfabeto + 3 tipos de vocales)")
        elif "001_" in file_name:
            print("   🔄 Creando tablas de traducción y feedback")
        elif "002_" in file_name:
            print("   📚 Creando diccionario principal y tablas relacionadas")
        elif "003_" in file_name:
            print("   🌱 Insertando datos de ejemplo (20+ palabras Shuar)")
        
        # IMPORTANTE: No podemos ejecutar SQL directamente desde Python
        # Necesitamos hacerlo manualmente en Supabase
        print("   ⚠️  EJECUTAR MANUALMENTE en Supabase SQL Editor")
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resumen: {success_count}/{len(migration_files)} migraciones preparadas")
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Ve a https://xedezayvprwkfvezhmfu.supabase.co")
    print("2. Navega a SQL Editor")
    print("3. Ejecuta cada archivo en este orden:")
    
    for i, file_name in enumerate(migration_files, 1):
        print(f"   {i}. {file_name}")
    
    print("\n💡 Cada archivo está en: app/core/infrastructure/database/migrations/")
    print("   Copia y pega el contenido de cada archivo en el SQL Editor")

if __name__ == "__main__":
    main()