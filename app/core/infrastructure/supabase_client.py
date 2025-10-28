"""Supabase client configuration and connection management."""

from typing import Optional, Dict, Any, List, Union
from supabase import create_client, Client
import asyncio
from contextlib import asynccontextmanager
import time
from datetime import datetime

from app.core.utils.logger import get_logger
from app.core.shared.exceptions import ValidationError

logger = get_logger(__name__)


class SupabaseQueryBuilder:
    """Query builder for Supabase operations."""
    
    def __init__(self, client: Client, table_name: str):
        self.client = client
        self.table_name = table_name
        self.table_ref = client.table(table_name)
        self._select_columns = "*"
        self._filters = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
    
    def select(self, columns: str = "*"):
        """Set columns to select."""
        self._select_columns = columns
        return self
    
    def eq(self, column: str, value: Any):
        """Add equality filter."""
        self._filters.append(("eq", column, value))
        return self
    
    def neq(self, column: str, value: Any):
        """Add not equal filter."""
        self._filters.append(("neq", column, value))
        return self
    
    def gt(self, column: str, value: Any):
        """Add greater than filter."""
        self._filters.append(("gt", column, value))
        return self
    
    def gte(self, column: str, value: Any):
        """Add greater than or equal filter."""
        self._filters.append(("gte", column, value))
        return self
    
    def lt(self, column: str, value: Any):
        """Add less than filter."""
        self._filters.append(("lt", column, value))
        return self
    
    def lte(self, column: str, value: Any):
        """Add less than or equal filter."""
        self._filters.append(("lte", column, value))
        return self
    
    def like(self, column: str, pattern: str):
        """Add LIKE filter."""
        self._filters.append(("like", column, pattern))
        return self
    
    def ilike(self, column: str, pattern: str):
        """Add case-insensitive LIKE filter."""
        self._filters.append(("ilike", column, pattern))
        return self
    
    def in_(self, column: str, values: List[Any]):
        """Add IN filter."""
        self._filters.append(("in", column, values))
        return self
    
    def is_(self, column: str, value: Any):
        """Add IS filter (for null checks)."""
        self._filters.append(("is", column, value))
        return self
    
    def order(self, column: str, ascending: bool = True):
        """Add order by clause."""
        self._order_by.append((column, ascending))
        return self
    
    def limit(self, count: int):
        """Set limit."""
        self._limit_value = count
        return self
    
    def offset(self, count: int):
        """Set offset."""
        self._offset_value = count
        return self
    
    def execute(self):
        """Execute the query."""
        query = self.table_ref.select(self._select_columns)
        
        # Apply filters
        for filter_type, column, value in self._filters:
            if filter_type == "eq":
                query = query.eq(column, value)
            elif filter_type == "neq":
                query = query.neq(column, value)
            elif filter_type == "gt":
                query = query.gt(column, value)
            elif filter_type == "gte":
                query = query.gte(column, value)
            elif filter_type == "lt":
                query = query.lt(column, value)
            elif filter_type == "lte":
                query = query.lte(column, value)
            elif filter_type == "like":
                query = query.like(column, value)
            elif filter_type == "ilike":
                query = query.ilike(column, value)
            elif filter_type == "in":
                query = query.in_(column, value)
            elif filter_type == "is":
                query = query.is_(column, value)
        
        # Apply ordering
        for column, ascending in self._order_by:
            query = query.order(column, desc=not ascending)
        
        # Apply limit and offset
        if self._limit_value:
            query = query.limit(self._limit_value)
        if self._offset_value:
            query = query.offset(self._offset_value)
        
        return query.execute()


class SupabaseClient:
    """Supabase client wrapper with connection management and query building."""
    
    def __init__(self, url: str, key: str, service_role_key: str):
        self.url = url
        self.key = key
        self.service_role_key = service_role_key
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
        self._connection_pool_size = 10
        self._query_timeout = 30  # seconds
        self._retry_attempts = 3
        self._retry_delay = 1  # seconds
    
    @property
    def client(self) -> Client:
        """Get the standard Supabase client."""
        if self._client is None:
            self._client = create_client(self.url, self.key)
            logger.info("Supabase client initialized")
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get the service role Supabase client (for admin operations)."""
        if self._service_client is None:
            self._service_client = create_client(self.url, self.service_role_key)
            logger.info("Supabase service client initialized")
        return self._service_client
    
    def table(self, table_name: str, use_service_role: bool = False) -> SupabaseQueryBuilder:
        """Get a query builder for a table."""
        client = self.service_client if use_service_role else self.client
        return SupabaseQueryBuilder(client, table_name)
    
    async def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            # Try a simple query to test connection
            result = self.client.table('palabras_detalladas').select('id').limit(1).execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error("Supabase connection test failed", error=str(e))
            return False
    
    async def execute_with_retry(self, operation_func, *args, **kwargs):
        """Execute an operation with retry logic."""
        last_exception = None
        
        for attempt in range(self._retry_attempts):
            try:
                return await operation_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self._retry_attempts - 1:
                    logger.warning(
                        f"Operation failed, retrying in {self._retry_delay}s",
                        attempt=attempt + 1,
                        error=str(e)
                    )
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(
                        "Operation failed after all retry attempts",
                        attempts=self._retry_attempts,
                        error=str(e)
                    )
        
        raise last_exception
    
    async def insert_record(
        self, 
        table: str, 
        data: Dict[str, Any], 
        use_service_role: bool = False
    ) -> Dict[str, Any]:
        """Insert a single record."""
        try:
            client = self.service_client if use_service_role else self.client
            result = client.table(table).insert(data).execute()
            
            if result.data:
                logger.info(f"Record inserted successfully", table=table)
                return result.data[0]
            else:
                raise ValidationError("Insert operation returned no data")
                
        except Exception as e:
            logger.error(f"Insert operation failed", table=table, error=str(e))
            raise
    
    async def insert_records(
        self, 
        table: str, 
        data: List[Dict[str, Any]], 
        use_service_role: bool = False
    ) -> List[Dict[str, Any]]:
        """Insert multiple records."""
        try:
            client = self.service_client if use_service_role else self.client
            result = client.table(table).insert(data).execute()
            
            logger.info(f"Bulk insert successful", table=table, count=len(data))
            return result.data
            
        except Exception as e:
            logger.error(f"Bulk insert failed", table=table, count=len(data), error=str(e))
            raise
    
    async def update_record(
        self, 
        table: str, 
        data: Dict[str, Any], 
        match_column: str, 
        match_value: Any,
        use_service_role: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Update a record."""
        try:
            client = self.service_client if use_service_role else self.client
            result = client.table(table).update(data).eq(match_column, match_value).execute()
            
            if result.data:
                logger.info(f"Record updated successfully", table=table)
                return result.data[0]
            else:
                logger.warning(f"No record found to update", table=table, match_column=match_column)
                return None
                
        except Exception as e:
            logger.error(f"Update operation failed", table=table, error=str(e))
            raise
    
    async def delete_record(
        self, 
        table: str, 
        match_column: str, 
        match_value: Any,
        use_service_role: bool = False
    ) -> bool:
        """Delete a record."""
        try:
            client = self.service_client if use_service_role else self.client
            result = client.table(table).delete().eq(match_column, match_value).execute()
            
            success = len(result.data) > 0
            if success:
                logger.info(f"Record deleted successfully", table=table)
            else:
                logger.warning(f"No record found to delete", table=table, match_column=match_column)
            
            return success
            
        except Exception as e:
            logger.error(f"Delete operation failed", table=table, error=str(e))
            raise
    
    async def execute_rpc(
        self, 
        function_name: str, 
        params: Optional[Dict[str, Any]] = None,
        use_service_role: bool = False
    ) -> Any:
        """Execute a stored procedure/function."""
        try:
            client = self.service_client if use_service_role else self.client
            result = client.rpc(function_name, params or {}).execute()
            
            logger.info(f"RPC executed successfully", function=function_name)
            return result.data
            
        except Exception as e:
            logger.error(f"RPC execution failed", function=function_name, error=str(e))
            raise
    
    async def execute_raw_sql(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None,
        use_service_role: bool = True  # Raw SQL usually needs elevated permissions
    ) -> Any:
        """Execute raw SQL query."""
        try:
            client = self.service_client if use_service_role else self.client
            # Note: Supabase Python client doesn't directly support raw SQL
            # This would need to be implemented via RPC or custom function
            logger.warning("Raw SQL execution not directly supported by Supabase Python client")
            raise NotImplementedError("Raw SQL execution requires custom RPC function")
            
        except Exception as e:
            logger.error(f"Raw SQL execution failed", error=str(e))
            raise
    
    async def get_table_info(self, table: str) -> Dict[str, Any]:
        """Get information about a table structure."""
        try:
            # This would typically require a custom RPC function
            # For now, return basic info
            return {
                "table_name": table,
                "connection_status": await self.test_connection()
            }
        except Exception as e:
            logger.error(f"Failed to get table info", table=table, error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "database_connection": False,
            "service_role_connection": False,
            "response_time_ms": 0
        }
        
        start_time = time.time()
        
        try:
            # Test regular connection
            health_status["database_connection"] = await self.test_connection()
            
            # Test service role connection
            try:
                result = self.service_client.table('palabras_detalladas').select('id').limit(1).execute()
                health_status["service_role_connection"] = True
            except:
                health_status["service_role_connection"] = False
            
            health_status["response_time_ms"] = int((time.time() - start_time) * 1000)
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            health_status["error"] = str(e)
        
        return health_status
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions (placeholder for future implementation)."""
        # Note: Supabase doesn't have explicit transaction support in Python client
        # This is a placeholder for future implementation or alternative approach
        try:
            yield self.client
        except Exception as e:
            logger.error("Transaction failed", error=str(e))
            raise
    
    def close(self):
        """Close the database connections."""
        # Supabase client doesn't require explicit closing
        # This method is here for interface consistency
        self._client = None
        self._service_client = None
        logger.info("Supabase client connections closed")