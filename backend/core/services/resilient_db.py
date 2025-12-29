"""
Resilient database operations with fallbacks.
Allows read operations to continue even when database has issues.
"""
import logging
from typing import Any, Optional, Callable
from django.core.cache import cache
from django.db import connection, transaction
from django.db.utils import DatabaseError, OperationalError
from core.services.circuit_breaker import database_breaker, CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class ResilientDatabase:
    """
    Wrapper for database operations with fallback mechanisms.
    """
    
    @staticmethod
    @database_breaker
    def execute_query(query_func: Callable, cache_key: Optional[str] = None, 
                     cache_timeout: int = 300, fallback_to_cache: bool = True):
        """
        Execute a database query with fallback to cache.
        
        Args:
            query_func: Function that executes the query
            cache_key: Optional cache key for fallback
            cache_timeout: Cache timeout in seconds
            fallback_to_cache: Whether to use cache as fallback
        
        Returns:
            Query result
        """
        try:
            # Try database first
            result = query_func()
            
            # Cache the result if cache key provided
            if cache_key and result is not None:
                try:
                    cache.set(cache_key, result, cache_timeout)
                except Exception as e:
                    logger.warning(f"Failed to cache result: {e}")
            
            return result
            
        except (DatabaseError, OperationalError) as e:
            logger.warning(f"Database query failed: {e}")
            
            # Try cache fallback
            if fallback_to_cache and cache_key:
                try:
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        logger.info(f"Using cached result for {cache_key}")
                        return cached_result
                except Exception as cache_error:
                    logger.warning(f"Cache fallback also failed: {cache_error}")
            
            # Re-raise if no fallback available
            raise
    
    @staticmethod
    def safe_read(query_func: Callable, cache_key: Optional[str] = None,
                 cache_timeout: int = 300, default_value: Any = None):
        """
        Safe read operation with multiple fallbacks.
        
        Args:
            query_func: Function that executes the query
            cache_key: Optional cache key
            cache_timeout: Cache timeout
            default_value: Default value if all fallbacks fail
        
        Returns:
            Query result or default value
        """
        try:
            return ResilientDatabase.execute_query(
                query_func, cache_key, cache_timeout, fallback_to_cache=True
            )
        except (DatabaseError, OperationalError, CircuitBreakerOpenError) as e:
            logger.error(f"All database fallbacks failed: {e}")
            return default_value
    
    @staticmethod
    @transaction.atomic
    def safe_write(write_func: Callable, retry_count: int = 3):
        """
        Safe write operation with retries.
        
        Args:
            write_func: Function that performs the write
            retry_count: Number of retries
        
        Returns:
            Write result
        """
        last_exception = None
        
        for attempt in range(retry_count):
            try:
                return write_func()
            except (DatabaseError, OperationalError) as e:
                last_exception = e
                logger.warning(f"Write attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    import time
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
        
        # All retries failed
        logger.error(f"Write operation failed after {retry_count} attempts")
        raise last_exception

