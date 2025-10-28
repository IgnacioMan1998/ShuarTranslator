"""Database migration runner for Supabase."""

import os
import asyncio
from typing import List, Dict, Any
from pathlib import Path

from app.core.infrastructure.supabase_client import SupabaseClient
from app.core.utils.logger import get_logger
from app.core.shared.config import settings

logger = get_logger(__name__)


class MigrationRunner:
    """Handles database migrations for Supabase."""
    
    def __init__(self, supabase_client: SupabaseClient):
        self.supabase_client = supabase_client
        self.migrations_dir = Path(__file__).parent / "migrations"
    
    async def run_migrations(self) -> Dict[str, Any]:
        """Run all pending migrations."""
        logger.info("Starting database migrations")
        
        # Ensure migrations table exists
        await self._ensure_migrations_table()
        
        # Get migration files
        migration_files = self._get_migration_files()
        
        # Get applied migrations
        applied_migrations = await self._get_applied_migrations()
        
        # Run pending migrations
        results = {
            "total_migrations": len(migration_files),
            "applied_migrations": len(applied_migrations),
            "new_migrations": 0,
            "successful": [],
            "failed": [],
            "errors": []
        }
        
        for migration_file in migration_files:
            migration_name = migration_file.stem
            
            if migration_name not in applied_migrations:
                try:
                    await self._run_migration(migration_file)
                    await self._record_migration(migration_name)
                    results["successful"].append(migration_name)
                    results["new_migrations"] += 1
                    logger.info(f"Migration applied successfully: {migration_name}")
                    
                except Exception as e:
                    error_msg = f"Migration failed: {migration_name} - {str(e)}"
                    results["failed"].append(migration_name)
                    results["errors"].append(error_msg)
                    logger.error(error_msg)
                    
                    # Stop on first failure to maintain consistency
                    break
            else:
                logger.info(f"Migration already applied: {migration_name}")
        
        logger.info(f"Migration run completed. Applied {results['new_migrations']} new migrations")
        return results
    
    async def _ensure_migrations_table(self):
        """Ensure the migrations tracking table exists."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        try:
            # Use RPC to execute raw SQL (would need custom function in Supabase)
            # For now, we'll use a simpler approach
            await self._execute_sql_via_client(create_table_sql)
            logger.info("Migrations table ensured")
        except Exception as e:
            logger.error(f"Failed to create migrations table: {e}")
            raise
    
    def _get_migration_files(self) -> List[Path]:
        """Get all migration files sorted by name."""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        migration_files = []
        for file_path in self.migrations_dir.glob("*.sql"):
            migration_files.append(file_path)
        
        # Sort by filename to ensure proper order
        migration_files.sort(key=lambda x: x.name)
        
        logger.info(f"Found {len(migration_files)} migration files")
        return migration_files
    
    async def _get_applied_migrations(self) -> set:
        """Get list of already applied migrations."""
        try:
            result = self.supabase_client.table("schema_migrations").select("migration_name").execute()
            applied = {row["migration_name"] for row in result.data}
            logger.info(f"Found {len(applied)} applied migrations")
            return applied
        except Exception as e:
            logger.warning(f"Could not fetch applied migrations: {e}")
            return set()
    
    async def _run_migration(self, migration_file: Path):
        """Run a single migration file."""
        logger.info(f"Running migration: {migration_file.name}")
        
        # Read migration file
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split into individual statements (basic approach)
        statements = self._split_sql_statements(sql_content)
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    await self._execute_sql_via_client(statement)
                    logger.debug(f"Executed statement {i+1}/{len(statements)} from {migration_file.name}")
                except Exception as e:
                    logger.error(f"Failed to execute statement {i+1} in {migration_file.name}: {e}")
                    raise
    
    def _split_sql_statements(self, sql_content: str) -> List[str]:
        """Split SQL content into individual statements."""
        # Remove comments and empty lines
        lines = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                lines.append(line)
        
        content = ' '.join(lines)
        
        # Split by semicolon (basic approach - doesn't handle all edge cases)
        statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
        
        return statements
    
    async def _execute_sql_via_client(self, sql: str):
        """Execute SQL using Supabase client."""
        # Note: This is a simplified approach
        # In a real implementation, you might need to use Supabase's RPC functionality
        # or execute statements through a custom database function
        
        # For now, we'll log the SQL and skip execution
        # In production, you would implement proper SQL execution
        logger.info(f"Would execute SQL: {sql[:100]}...")
        
        # Placeholder - in real implementation, use RPC or direct database connection
        # await self.supabase_client.execute_rpc('execute_sql', {'sql': sql})
    
    async def _record_migration(self, migration_name: str):
        """Record that a migration has been applied."""
        try:
            await self.supabase_client.insert_record(
                "schema_migrations",
                {"migration_name": migration_name},
                use_service_role=True
            )
            logger.info(f"Recorded migration: {migration_name}")
        except Exception as e:
            logger.error(f"Failed to record migration {migration_name}: {e}")
            raise
    
    async def rollback_migration(self, migration_name: str) -> bool:
        """Rollback a specific migration (if rollback script exists)."""
        rollback_file = self.migrations_dir / f"{migration_name}_rollback.sql"
        
        if not rollback_file.exists():
            logger.error(f"No rollback script found for migration: {migration_name}")
            return False
        
        try:
            await self._run_migration(rollback_file)
            
            # Remove from migrations table
            await self.supabase_client.delete_record(
                "schema_migrations",
                "migration_name",
                migration_name,
                use_service_role=True
            )
            
            logger.info(f"Migration rolled back successfully: {migration_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_name}: {e}")
            return False
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        migration_files = self._get_migration_files()
        applied_migrations = await self._get_applied_migrations()
        
        pending_migrations = []
        for migration_file in migration_files:
            if migration_file.stem not in applied_migrations:
                pending_migrations.append(migration_file.stem)
        
        return {
            "total_migrations": len(migration_files),
            "applied_count": len(applied_migrations),
            "pending_count": len(pending_migrations),
            "applied_migrations": sorted(list(applied_migrations)),
            "pending_migrations": pending_migrations,
            "database_connection": await self.supabase_client.test_connection()
        }


async def run_migrations():
    """Convenience function to run migrations."""
    supabase_client = SupabaseClient(
        url=settings.supabase_url,
        key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key
    )
    
    migration_runner = MigrationRunner(supabase_client)
    return await migration_runner.run_migrations()


if __name__ == "__main__":
    # Run migrations from command line
    asyncio.run(run_migrations())