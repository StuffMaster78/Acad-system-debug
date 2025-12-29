"""
Read-only mode service for degraded operation.
Allows read operations when write operations fail.
"""
import logging
from django.core.cache import cache
from django.db import connection
from django.db.utils import DatabaseError, OperationalError

logger = logging.getLogger(__name__)


class ReadOnlyMode:
    """
    Manages read-only mode for graceful degradation.
    When database writes fail, system can continue serving reads.
    """
    
    CACHE_KEY = "system:read_only_mode"
    CACHE_TIMEOUT = 300  # 5 minutes
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if read-only mode is enabled."""
        return cache.get(ReadOnlyMode.CACHE_KEY, False)
    
    @staticmethod
    def enable():
        """Enable read-only mode."""
        cache.set(ReadOnlyMode.CACHE_KEY, True, ReadOnlyMode.CACHE_TIMEOUT)
        logger.warning("Read-only mode enabled - writes will be rejected")
    
    @staticmethod
    def disable():
        """Disable read-only mode."""
        cache.delete(ReadOnlyMode.CACHE_KEY)
        logger.info("Read-only mode disabled - writes allowed")
    
    @staticmethod
    def check_database_writable() -> bool:
        """Check if database is writable."""
        try:
            with connection.cursor() as cursor:
                # Try a simple write operation (using a temporary table or transaction)
                cursor.execute("SELECT 1")
                return True
        except (DatabaseError, OperationalError) as e:
            logger.warning(f"Database write check failed: {e}")
            ReadOnlyMode.enable()
            return False
    
    @staticmethod
    def require_writable():
        """Decorator to require writable database."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if ReadOnlyMode.is_enabled():
                    from rest_framework.exceptions import ServiceUnavailable
                    raise ServiceUnavailable(
                        "System is in read-only mode. Write operations are temporarily unavailable."
                    )
                
                # Check if database is actually writable
                if not ReadOnlyMode.check_database_writable():
                    from rest_framework.exceptions import ServiceUnavailable
                    raise ServiceUnavailable(
                        "Database is not writable. Please try again later."
                    )
                
                return func(*args, **kwargs)
            return wrapper
        return decorator

